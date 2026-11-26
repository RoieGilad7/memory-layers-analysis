"""How far would a self-supervised fact loss reach into the Pile? (analysis only)

    .venv/bin/python bench/fact_anchor_reach.py [--tokens 10000000]

Pairing rule (self-supervised: text only, no generator labels):
  rare token   a token id NOT among the 10,000 most frequent ids in data/v1 train.bin
  name         a capitalized run (a token whose text starts, after an optional space,
               with an uppercase letter, plus following tokens that continue the word
               without a leading space, plus further capitalized words) that contains
               at least one rare token
  anchor       position t such that, among tokens t+1..t+3, there is a rare token,
               and a name ends within the 64 tokens before t (same EOT-delimited
               document; the nearest such name is used)
  value        tokens t+1..t+v: from t+1 up to and including the last rare token
               among t+1..t+3. Anchors whose value starts a name run are dropped (the
               "value" would be a name, usually the subject's own name repeated).
  key          (name tokens, value tokens)
  partner      another anchor with the same key in a DIFFERENT document, at most W
               tokens of the same subject before it in (shuffled) training order.
               W = 8M training tokens x the subject's share of train.bin (a bank of
               ~500 steps holds that many tokens of this subject); W8M = 8M subject
               tokens is also reported.

Per subject (5 Pile subjects + bio), on ~10M tokens of whole documents in random order:
anchors per 1k tokens, the fraction with a partner, and 50 random partner pairs printed
for hand checking. Then on pkm-s0's final checkpoint, the share of held-out NLL (test
split, per subject) that falls on anchor value tokens.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EOT = 50256
N_COMMON = 10_000
LOOKBACK = 64
BANK_TRAIN_TOKENS = 8_000_000


def token_tables(enc, counts):
    order = np.argsort(-counts)
    common = np.zeros(len(counts), dtype=bool)
    common[order[:N_COMMON]] = True
    cap = np.zeros(len(counts), dtype=bool)  # starts a capitalized word
    cont = np.zeros(
        len(counts), dtype=bool
    )  # continues a word (no leading space, alpha)
    for i in range(min(len(counts), enc.n_vocab)):
        try:
            s = enc.decode([i])
        except Exception:
            continue
        st = s[1:] if s.startswith(" ") else s
        if st[:1].isupper() and st[:1].isalpha():
            cap[i] = True
        if s and not s.startswith(" ") and s[:1].isalpha():
            cont[i] = True
    return ~common, cap, cont


def name_runs(toks, rare, cap, cont):
    """(starts, ends) of capitalized runs containing a rare token."""
    n = len(toks)
    c, o = cap[toks], cont[toks]
    starts, ends = [], []
    i = 0
    capi = np.nonzero(c)[0]
    p = 0
    while p < len(capi):
        i = capi[p]
        j = i + 1
        while j < n and (o[j] or c[j]):
            j += 1
        if rare[toks[i:j]].any():
            starts.append(i)
            ends.append(j)
        p = np.searchsorted(capi, j)
    return np.array(starts, dtype=np.int64), np.array(ends, dtype=np.int64)


def find_anchors_arr(toks, rare, cap, cont):
    """Vectorized: arrays (t, name_start, name_end, value_len) for one document."""
    n = len(toks)
    empty = (np.zeros(0, np.int64),) * 4
    if n < 3:
        return empty
    ns, ne = name_runs(toks, rare, cap, cont)
    if not len(ns):
        return empty
    r = rare[toks]
    rp = np.concatenate([r, np.zeros(3, bool)])
    t = np.arange(n - 1)
    r1, r2, r3 = rp[t + 1], rp[t + 2], rp[t + 3]
    ok = r1 | r2 | r3
    k = np.where(r3, 3, np.where(r2, 2, 1))
    idx = np.searchsorted(ne, t + 1, side="right") - 1
    ok &= idx >= 0
    idx = np.clip(idx, 0, None)
    e = ne[idx]
    ok &= (t - e + 1) <= LOOKBACK
    k = np.minimum(k, n - 1 - t)
    t, idx, k = t[ok], idx[ok], k[ok]
    # drop anchors whose value starts a capitalized name run (the "value" would be a
    # name, typically the subject's own name repeated, not a fact)
    starts_name = np.zeros(n + 1, bool)
    starts_name[ns] = True
    keep = ~starts_name[t + 1]
    t, idx, k = t[keep], idx[keep], k[keep]
    return t, ns[idx], ne[idx], k


def find_anchors(toks, rare, cap, cont):
    t, s, e, k = find_anchors_arr(toks, rare, cap, cont)
    return [
        (
            int(a),
            tuple(int(x) for x in toks[b:c]),
            tuple(int(x) for x in toks[a + 1 : a + 1 + d]),
        )
        for a, b, c, d in zip(t, s, e, k)
    ]


_P = np.uint64(1000003)


def span_hash_direct(toks, s, e):
    """Polynomial hash of toks[s:e] for arrays of spans (uint64, wrapping)."""
    L = e - s
    h = np.zeros(len(s), np.uint64)
    tp = np.concatenate([toks, np.zeros(int(L.max()) + 1 if len(L) else 1, np.int64)])
    with np.errstate(over="ignore"):
        for o in range(int(L.max()) if len(L) else 0):
            m = o < L
            v = (tp[s + o] + 1).astype(np.uint64)
            h = np.where(m, h * _P + v, h)
        h = h ^ (L.astype(np.uint64) << np.uint64(56))
    return h


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", type=int, default=10_000_000)
    ap.add_argument("--heldout-docs", type=int, default=300)
    ap.add_argument("--out", default="reports/fact_anchor_reach.json")
    ap.add_argument("--pairs-out", default="reports/fact_anchor_pairs.txt")
    a = ap.parse_args(argv)
    import tiktoken

    enc = tiktoken.get_encoding("gpt2")
    tok = np.memmap(ROOT / "data/v1/tokens/train.bin", dtype=np.uint16, mode="r")
    counts = np.bincount(np.asarray(tok), minlength=enc.n_vocab)
    rare, cap, cont = token_tables(enc, counts)
    idx = pd.read_parquet(ROOT / "data/v1/tokens/train.idx.parquet")
    share = (idx.groupby("subject")["length"].sum() / idx["length"].sum()).to_dict()
    res = {
        "rule": {
            "n_common": N_COMMON,
            "lookback": LOOKBACK,
            "bank_train_tokens": BANK_TRAIN_TOKENS,
        },
        "subjects": {},
    }
    pair_lines = []
    rng = random.Random(0)
    for subj, g in idx.groupby("subject"):
        g = g.sample(frac=1.0, random_state=0)
        n_tok = 0
        keys, poss, docs, meta = [], [], [], []
        stream = 0
        for di, (_, d) in enumerate(g.iterrows()):
            if n_tok >= a.tokens:
                break
            toks = np.asarray(tok[d.start : d.start + d.length]).astype(np.int64)
            t, ns_, ne_, k = find_anchors_arr(toks, rare, cap, cont)
            if len(t):
                hn = span_hash_direct(toks, ns_, ne_)
                hv = span_hash_direct(toks, t + 1, t + 1 + k)
                with np.errstate(over="ignore"):
                    key = (
                        hn * np.uint64(0x9E3779B97F4A7C15)
                        ^ hv
                        ^ (k.astype(np.uint64) << np.uint64(60))
                    )
                keys.append(key)
                poss.append(stream + t)
                docs.append(np.full(len(t), di, np.int64))
                meta.append((d.doc_id, int(d.start), t, ns_, ne_, k))
            stream += len(toks)
            n_tok += len(toks)
        keys = np.concatenate(keys) if keys else np.zeros(0, np.uint64)
        poss = np.concatenate(poss) if poss else np.zeros(0, np.int64)
        docs = np.concatenate(docs) if docs else np.zeros(0, np.int64)
        n_anch = len(keys)
        W = int(BANK_TRAIN_TOKENS * share[subj])
        order = np.lexsort((poss, keys))
        ks, ps, ds = keys[order], poss[order], docs[order]
        # previous element in the same key group from a different document
        newgrp = np.ones(n_anch, bool)
        newgrp[1:] = ks[1:] != ks[:-1]
        newrun = newgrp.copy()
        newrun[1:] |= ds[1:] != ds[:-1]
        run_start = np.maximum.accumulate(np.where(newrun, np.arange(n_anch), 0))
        grp_start = np.maximum.accumulate(np.where(newgrp, np.arange(n_anch), 0))
        prev = run_start - 1
        valid = prev >= grp_start
        prevc = np.clip(prev, 0, None)
        gap = ps - ps[prevc]
        hasW = valid & (gap <= W)
        has8m = valid & (gap <= 8_000_000)
        has, has8 = int(hasW.sum()), int(has8m.sum())
        # flat index -> (meta doc, position) for printing pairs
        flat = []
        for mi, (doc_id, start, t, ns_, ne_, k) in enumerate(meta):
            for z in range(len(t)):
                flat.append((mi, z))
        partners = [(int(order[prevc[i]]), int(order[i])) for i in np.nonzero(hasW)[0]]
        anchors_n = n_anch
        rec = {
            "tokens": n_tok,
            "anchors": anchors_n,
            "anchors_per_1k": 1000 * anchors_n / max(1, n_tok),
            "window_tokens_W": W,
            "with_partner_W": has / max(1, anchors_n),
            "with_partner_8M": has8 / max(1, anchors_n),
            "partner_anchors_per_1k_W": 1000 * has / max(1, n_tok),
        }
        res["subjects"][subj] = rec
        print(subj, json.dumps(rec), flush=True)
        pair_lines.append(
            f"\n===== {subj}: {len(partners)} partner anchors; 50 random pairs ====="
        )
        for pi, (i, j) in enumerate(rng.sample(partners, min(50, len(partners)))):
            lines = []
            for fk in (i, j):
                mi, z = flat[fk]
                doc, start, t, ns_, ne_, k = meta[mi]
                tt, kk = int(t[z]), int(k[z])
                ctx = np.asarray(
                    tok[start + max(0, tt - 25) : start + tt + 1 + kk + 3]
                ).tolist()
                lines.append(f"   [{doc}] ...{enc.decode(ctx)!r}")
            mi, z = flat[j]
            doc, start, t, ns_, ne_, k = meta[mi]
            nm = np.asarray(tok[start + ns_[z] : start + ne_[z]]).tolist()
            vl = np.asarray(tok[start + t[z] + 1 : start + t[z] + 1 + k[z]]).tolist()
            pair_lines.append(
                f"{pi:02d} name={enc.decode(nm)!r} value={enc.decode(vl)!r}\n"
                + "\n".join(lines)
            )
    Path(a.pairs_out).write_text("\n".join(pair_lines) + "\n")

    # held-out NLL share on anchor value tokens, pkm-s0 final
    from memlayers.model import GPT, GPTConfig

    ck = torch.load(
        ROOT / "runs/pilot/ckpt/pkm-s0/checkpoints/step_009156.pt",
        map_location="cpu",
        weights_only=False,
    )
    model = GPT(GPTConfig(**ck["config"]["model"]))
    model.load_state_dict(ck["model"])
    model.eval()
    dev = (
        torch.device("mps")
        if torch.backends.mps.is_available()
        else torch.device("cpu")
    )
    model.to(dev)
    ttok = np.memmap(ROOT / "data/v1/heldout/test.bin", dtype=np.uint16, mode="r")
    tidx = pd.read_parquet(ROOT / "data/v1/heldout/test.idx.parquet")
    res["heldout_share"] = {}
    for subj, g in tidx.groupby("subject"):
        g = g.sample(n=min(a.heldout_docs, len(g)), random_state=0)
        tot, on_val, n_all, n_val = 0.0, 0.0, 0, 0
        for _, d in g.iterrows():
            toks = np.asarray(ttok[d.start : d.start + d.length]).astype(np.int64)
            for s0 in range(0, len(toks) - 1, 512):
                x = toks[s0 : s0 + 513]
                if len(x) < 2:
                    continue
                with torch.no_grad():
                    logits, _ = model(
                        torch.tensor([x[:-1]], device=dev), all_logits=True
                    )
                nll = (
                    F.cross_entropy(
                        logits[0].float(),
                        torch.tensor(x[1:], device=dev),
                        reduction="none",
                    )
                    .cpu()
                    .numpy()
                )
                val = np.zeros(len(x) - 1, dtype=bool)
                for t, name, value in find_anchors(x, rare, cap, cont):
                    for u in range(t + 1, t + 1 + len(value)):
                        if 1 <= u <= len(x) - 1:
                            val[u - 1] = True  # nll[u-1] predicts token u
                tot += float(nll.sum())
                on_val += float(nll[val].sum())
                n_all += len(nll)
                n_val += int(val.sum())
        res["heldout_share"][subj] = {
            "docs": len(g),
            "tokens": n_all,
            "value_token_fraction": n_val / max(1, n_all),
            "nll_share_on_value_tokens": on_val / max(1e-9, tot),
        }
        print("heldout", subj, json.dumps(res["heldout_share"][subj]), flush=True)
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
