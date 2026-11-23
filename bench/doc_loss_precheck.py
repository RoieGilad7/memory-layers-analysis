"""Phase 2 pre-check: what the same-document gap is made of, and whether the doc loss
changes which memory slots the two halves of a document read.

    .venv/bin/python bench/doc_loss_precheck.py [--device cpu] [--out reports/doc_loss_precheck.json]

For each checkpoint (the pilot's step-1,500 weights for every lambda, plus the
lambda = 0 run's step-0 weights as a reference), on the pilot's 20 fixed batches
(first 20 batches of 32 x 512 windows of data/v1 train.bin, loader seed 12345),
model in eval mode, no grad:

  halves      find_halves(x, 50256, 32), as in training
  labels      each half's document, Pile subject and bio person id, from
              data/v1/tokens/train.idx.parquet -- used ONLY here, never in training
  query cos   cosine of the two halves' mean memory queries (the vectors doc_loss uses)
  jaccard     per head, |S_a & S_b| / |S_a | S_b| where S = the set of slots the
              half's tokens read (union over tokens of each token's top-32);
              averaged over the 4 heads
  weighted    per head, sum_s min(p_a(s), p_b(s)) where p = the half's gate mass per
              slot normalized to sum 1 (histogram intersection, 1 - total variation);
              averaged over the heads
  retrieval   per half, whether its partner is its nearest other half in the batch

Pairs are all unordered pairs of halves within a batch, grouped into: partner
(same piece), Pile same subject, Pile different subject, bio-bio different person,
bio-bio same person (another rewording of the same biography), bio-Pile, and
adjacent across EOT (last half of a piece and the first half of the next piece in
the same row: neighbours in the text, different documents).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.loader import PackedDataset  # noqa: E402
from memlayers.doc_loss import find_halves, half_vectors  # noqa: E402
from memlayers.model import GPT, GPTConfig  # noqa: E402

EOT = 50256
BLOCK = 512
BATCH = 32
N_BATCHES = 20
GAP_SEED = 12345
MIN_PIECE = 32
CATS = [
    "partner",
    "pile_same_subject",
    "pile_diff_subject",
    "bio_bio_diff_person",
    "bio_bio_same_person",
    "bio_pile",
    "adjacent_across_eot",
]


def load_model(path, device):
    ck = torch.load(path, map_location="cpu", weights_only=False)
    cfg = GPTConfig(**ck["config"]["model"])
    m = GPT(cfg)
    m.load_state_dict(ck["model"])
    return m.to(device).eval(), int(ck["step"])


def fixed_batches(bin_path):
    ds = PackedDataset(bin_path, block_size=BLOCK, seed=GAP_SEED)
    order = ds.sequence_order(0)[: BATCH * N_BATCHES]
    check = PackedDataset(bin_path, block_size=BLOCK, seed=GAP_SEED)
    batches = []
    for b in range(N_BATCHES):
        x, _ = check.get_batch(b, BATCH)
        seqs = order[b * BATCH : (b + 1) * BATCH]
        # the loader's batch b really is these windows
        tok = np.stack(
            [np.asarray(ds.tokens[s * BLOCK : s * BLOCK + BLOCK]) for s in seqs]
        )
        assert np.array_equal(tok.astype(np.int64), x.numpy()), "window order mismatch"
        batches.append((x, seqs))
    return batches


class DocIndex:
    def __init__(self, idx_path):
        import pandas as pd

        d = pd.read_parquet(idx_path).sort_values("start").reset_index(drop=True)
        self.start = d["start"].to_numpy()
        self.end = self.start + d["length"].to_numpy()
        self.doc = d["doc_id"].astype(str).to_numpy()
        self.subject = d["subject"].astype(str).to_numpy()
        self.person = d["person_id"].astype(object).to_numpy()

    def rows(self, pos):
        r = np.searchsorted(self.start, pos, side="right") - 1
        ok = (r >= 0) & (pos < self.end[np.clip(r, 0, None)])
        return np.where(ok, r, -1)


def half_meta(half_id, n, seqs, index):
    """Per half: doc row (from its tokens), is the half inside one doc, row, first pos."""
    B, T = half_id.shape
    pos = (np.asarray(seqs)[:, None] * BLOCK + np.arange(T)[None, :]).reshape(-1)
    rows = index.rows(pos).reshape(B, T)
    hid = half_id.numpy()
    meta = []
    for i in range(n):
        bb, tt = np.nonzero(hid == i)
        r = rows[bb, tt]
        vals, counts = np.unique(r, return_counts=True)
        main = vals[np.argmax(counts)]
        meta.append(
            {
                "row": int(main),
                "pure": bool(len(vals) == 1 and main >= 0),
                "batch_row": int(bb[0]),
                "first": int(tt.min()),
                "last": int(tt.max()),
            }
        )
    return meta


def slot_profiles(read, half_id, n):
    """Per half and head: (sorted unique slots, normalized gate mass on them)."""
    idx = read.indices.cpu()  # [B, T, h, k]
    w = read.weights.cpu().float()
    H = idx.shape[2]
    hid = half_id.cpu()
    out = []
    for i in range(n):
        sel = hid == i
        per_head = []
        for h in range(H):
            s = idx[:, :, h][sel].reshape(-1).numpy()
            g = w[:, :, h][sel].reshape(-1).numpy()
            u, inv = np.unique(s, return_inverse=True)
            mass = np.bincount(inv, weights=g, minlength=len(u))
            per_head.append((u, mass / mass.sum()))
        out.append(per_head)
    return out


def pair_overlap(pa, pb):
    jac, wov = [], []
    for (ua, ma), (ub, mb) in zip(pa, pb):
        common, ia, ib = np.intersect1d(ua, ub, assume_unique=True, return_indices=True)
        inter = len(common)
        jac.append(inter / (len(ua) + len(ub) - inter))
        wov.append(float(np.minimum(ma[ia], mb[ib]).sum()))
    return float(np.mean(jac)), float(np.mean(wov))


def category(i, j, meta, index):
    a, b = meta[i], meta[j]
    if j == (i ^ 1):
        return "partner"
    ra, rb = a["row"], b["row"]
    if ra < 0 or rb < 0 or not (a["pure"] and b["pure"]):
        return None
    if index.doc[ra] == index.doc[rb]:
        return None  # same document, not partners (a doc split over windows)
    sa, sb = index.subject[ra], index.subject[rb]
    ba, bb_ = sa == "bio", sb == "bio"
    if ba and bb_:
        same = index.person[ra] == index.person[rb]
        return "bio_bio_same_person" if same else "bio_bio_diff_person"
    if ba != bb_:
        return "bio_pile"
    return "pile_same_subject" if sa == sb else "pile_diff_subject"


def summarize(vals):
    v = np.asarray(vals, dtype=np.float64)
    if v.size == 0:
        return {"n": 0}
    return {
        "n": int(v.size),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "p10": float(np.percentile(v, 10)),
        "p90": float(np.percentile(v, 90)),
    }


@torch.no_grad()
def analyse(model, batches, index, layer, device):
    mem = model.memory_layers[layer]
    mem.set_keep_queries(True)
    mem.set_read_logging(True)
    vals = {c: {"cos": [], "jac": [], "wov": []} for c in CATS}
    retr = {"cos": [], "jac": [], "wov": []}
    purity, n_halves = [], []
    for x, seqs in batches:
        model(x.to(device))
        q = mem.kept_queries()
        read = mem.last_read()
        hid, n = find_halves(x, EOT, MIN_PIECE)
        v = half_vectors(q, hid.to(q.device), n).cpu()
        cos = (v @ v.T).numpy()
        meta = half_meta(hid, n, seqs, index)
        prof = slot_profiles(read, hid, n)
        purity += [m["pure"] for m in meta]
        n_halves.append(n)
        J = np.full((n, n), np.nan)
        W = np.full((n, n), np.nan)
        for i in range(n):
            for j in range(i + 1, n):
                J[i, j], W[i, j] = pair_overlap(prof[i], prof[j])
                J[j, i], W[j, i] = J[i, j], W[i, j]
                c = category(i, j, meta, index)
                if c is None:
                    continue
                vals[c]["cos"].append(cos[i, j])
                vals[c]["jac"].append(J[i, j])
                vals[c]["wov"].append(W[i, j])
        # adjacent across EOT: second half of piece k, first half of piece k+1, same row
        for k in range(n // 2 - 1):
            i, j = 2 * k + 1, 2 * k + 2
            if meta[i]["batch_row"] == meta[j]["batch_row"]:
                ri, rj = meta[i]["row"], meta[j]["row"]
                if ri >= 0 and rj >= 0 and index.doc[ri] != index.doc[rj]:
                    vals["adjacent_across_eot"]["cos"].append(cos[i, j])
                    vals["adjacent_across_eot"]["jac"].append(J[i, j])
                    vals["adjacent_across_eot"]["wov"].append(W[i, j])
        for name, M in (("cos", cos.copy()), ("jac", J), ("wov", W)):
            M = np.array(M, dtype=np.float64)
            np.fill_diagonal(M, -np.inf)
            best = np.argmax(M, axis=1)
            retr[name] += [bool(best[i] == (i ^ 1)) for i in range(n)]
    mem.set_read_logging(False)
    mem.set_keep_queries(False)
    return {
        "pairs": {
            c: {m: summarize(vals[c][m]) for m in ("cos", "jac", "wov")} for c in CATS
        },
        "partner_retrieval_top1": {k: float(np.mean(v)) for k, v in retr.items()},
        "halves_per_batch": float(np.mean(n_halves)),
        "halves_single_doc_fraction": float(np.mean(purity)),
        "chance_retrieval": float(np.mean([1 / (n - 1) for n in n_halves])),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--pilot", default="runs/pilot_doc")
    ap.add_argument("--lambdas", default="0,0.003,0.01,0.03")
    ap.add_argument("--out", default="reports/doc_loss_precheck.json")
    a = ap.parse_args(argv)
    torch.set_grad_enabled(False)
    dev = torch.device(a.device)
    index = DocIndex(ROOT / "data/v1/tokens/train.idx.parquet")
    batches = fixed_batches(ROOT / "data/v1/tokens/train.bin")
    ckpts = [("init (step 0)", Path(a.pilot) / "l0" / "init_weights.pt")]
    for lam in a.lambdas.split(","):
        ckpts.append(
            (
                f"lambda {float(lam):g}",
                Path(a.pilot) / f"l{float(lam):g}" / "step_001500.pt",
            )
        )
    res = {
        "batches": N_BATCHES,
        "batch": [BATCH, BLOCK],
        "loader_seed": GAP_SEED,
        "min_piece_tokens": MIN_PIECE,
        "device": str(dev),
        "models": {},
    }
    for name, path in ckpts:
        t0 = time.perf_counter()
        model, step = load_model(path, dev)
        layer = next(iter(model.memory_layers))
        r = analyse(model, batches, index, layer, dev)
        r.update(
            {
                "checkpoint": str(path),
                "step": step,
                "layer": layer,
                "seconds": time.perf_counter() - t0,
            }
        )
        res["models"][name] = r
        p = r["pairs"]
        print(
            f"{name}: partner cos {p['partner']['cos']['mean']:.3f} "
            f"same-subj {p['pile_same_subject']['cos']['mean']:.3f} "
            f"diff-subj {p['pile_diff_subject']['cos']['mean']:.3f} | jac partner "
            f"{p['partner']['jac']['mean']:.3f} diff-subj {p['pile_diff_subject']['jac']['mean']:.3f}"
            f" | retrieval {r['partner_retrieval_top1']}  ({r['seconds']:.0f}s)",
            flush=True,
        )
        Path(a.out).write_text(json.dumps(res, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
