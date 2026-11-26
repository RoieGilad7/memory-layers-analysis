"""Is fact recall limited by where the memory looks? Checks 1 and 2, no training.

    .venv/bin/python bench/fact_addressing_check.py [--runs pkm-s0,pkm-s1,pkm-s2,pkm_doc-s0,pkm_doc-s1]

For every Q2 prompt of the cohort slice (the exact rows of runs/final/cohort/<run>/,
with their recorded top-1 outcome), the model reads the prompt and we take the memory
read at its LAST token -- the position whose next token is the answer's first token:
the set of top-32 slots per head, and their gate weights.

Check 1 (paraphrase gap): for the same fact, how much do the reads of two prompts
overlap? Pairs:
  test vs discovery       same fact, two training-style prompts (different rewordings)
  test vs paraphrase      same fact, training-style vs held-out-template prompt
  test vs test, other person, same attribute   (baseline: what an unrelated fact shares)
  test vs test, same person, other attribute
Measures: per head Jaccard of the 32-slot sets and gate-mass overlap (sum of min of the
normalized gate weights), averaged over the heads.

Check 2 (success vs failure): within a tier and role, is a prompt's overlap with the
same fact's training-style reads higher when the fact is recalled (top-1) than when
it is missed?
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from memlayers.model import GPT, GPTConfig  # noqa: E402

CKPT = {
    "pkm-s0": "runs/pilot/ckpt/pkm-s0/checkpoints/step_009156.pt",
    "pkm-s1": "runs/pilot/ckpt/pkm-s1/checkpoints/step_009156.pt",
    "pkm-s2": "runs/pilot/ckpt/pkm-s2/checkpoints/step_009156.pt",
    "pkm_doc-s0": "runs/pkm_doc-s0/checkpoints/step_009156.pt",
    "pkm_doc-s1": "runs/pkm_doc-s1/checkpoints/step_009156.pt",
}


def load(path):
    ck = torch.load(path, map_location="cpu", weights_only=False)
    m = GPT(GPTConfig(**ck["config"]["model"]))
    m.load_state_dict(ck["model"])
    return m.eval()


def overlap(a, b):
    """a, b: (idx [h,k], w [h,k]) -> (mean Jaccard, mean gate-mass overlap)."""
    jac, wov = [], []
    for h in range(a[0].shape[0]):
        ia, ib = a[0][h], b[0][h]
        wa = a[1][h] / a[1][h].sum()
        wb = b[1][h] / b[1][h].sum()
        common, xa, xb = np.intersect1d(ia, ib, return_indices=True)
        jac.append(len(common) / (len(ia) + len(ib) - len(common)))
        wov.append(float(np.minimum(wa[xa], wb[xb]).sum()))
    return float(np.mean(jac)), float(np.mean(wov))


def summ(v):
    v = np.asarray(v, dtype=float)
    if not v.size:
        return {"n": 0}
    return {
        "n": int(v.size),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "p10": float(np.percentile(v, 10)),
        "p90": float(np.percentile(v, 90)),
    }


@torch.no_grad()
def reads_for(model, prompts, enc):
    mem = next(iter(model.memory_layers.values()))
    mem.set_read_logging(True)
    out = {}
    for rid, text in prompts.items():
        ids = enc.encode(text)[-model.config.block_size :]
        model(torch.tensor([ids]))
        r = mem.last_read()
        out[rid] = (
            r.indices[0, -1].numpy().copy(),
            r.weights[0, -1].float().numpy().copy(),
        )
    mem.set_read_logging(False)
    return out


def analyse(rows, reads):
    by_fact = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_fact[r["fact_id"]][r["role"]].append(r)
    res = {}
    # check 1
    pairs = defaultdict(lambda: {"jac": [], "wov": []})
    tests = [r for r in rows if r["role"] == "test"]
    for tier in ("frequent", "normal", "rare", "control"):
        t_tier = [r for r in tests if r["tier"] == tier]
        for r in t_tier:
            f = by_fact[r["fact_id"]]
            for role, name in (
                ("discovery", "test_vs_discovery"),
                ("paraphrase", "test_vs_paraphrase"),
            ):
                for o in f[role]:
                    j, w = overlap(reads[r["row_id"]], reads[o["row_id"]])
                    pairs[(tier, name)]["jac"].append(j)
                    pairs[(tier, name)]["wov"].append(w)
        rng = np.random.default_rng(0)
        for r in t_tier:
            same_attr = [
                o
                for o in t_tier
                if o["attribute"] == r["attribute"] and o["person"] != r["person"]
            ]
            same_pers = [
                o
                for o in t_tier
                if o["person"] == r["person"] and o["attribute"] != r["attribute"]
            ]
            for pool, name in (
                (same_attr, "test_vs_other_person_same_attr"),
                (same_pers, "test_vs_same_person_other_attr"),
            ):
                for o in rng.permutation(len(pool))[:4] if pool else []:
                    j, w = overlap(reads[r["row_id"]], reads[pool[o]["row_id"]])
                    pairs[(tier, name)]["jac"].append(j)
                    pairs[(tier, name)]["wov"].append(w)
    res["check1"] = {
        f"{t}/{n}": {k: summ(v) for k, v in d.items()} for (t, n), d in pairs.items()
    }

    # check 2: overlap with the same fact's training-style (discovery) reads vs outcome
    c2 = defaultdict(lambda: {"hit": [], "miss": []})
    c2o = defaultdict(
        lambda: {"hit": [], "miss": []}
    )  # control: other people's same attribute
    disc_by_attr = defaultdict(list)
    for r in rows:
        if r["role"] == "discovery":
            disc_by_attr[(r["tier"], r["attribute"])].append(r)
    rng2 = np.random.default_rng(1)
    for r in rows:
        if r["role"] not in ("test", "paraphrase"):
            continue
        refs = by_fact[r["fact_id"]]["discovery"]
        if not refs:
            continue
        j = float(
            np.mean([overlap(reads[r["row_id"]], reads[o["row_id"]])[0] for o in refs])
        )
        c2[f"{r['tier']}/{r['role']}"]["hit" if r["top1"] >= 1 else "miss"].append(j)
        others = [
            o
            for o in disc_by_attr[(r["tier"], r["attribute"])]
            if o["person"] != r["person"]
        ]
        if others:
            pick = [others[i] for i in rng2.permutation(len(others))[:4]]
            jo = float(
                np.mean(
                    [overlap(reads[r["row_id"]], reads[o["row_id"]])[0] for o in pick]
                )
            )
            c2o[f"{r['tier']}/{r['role']}"]["hit" if r["top1"] >= 1 else "miss"].append(
                jo
            )
    res["check2"] = {}
    for k, d in c2.items():
        hit, miss = summ(d["hit"]), summ(d["miss"])
        allv = d["hit"] + d["miss"]
        res["check2"][k] = {
            "hit": hit,
            "miss": miss,
            "control_other_person_hit": summ(c2o[k]["hit"]),
            "control_other_person_miss": summ(c2o[k]["miss"]),
        }
        if len(allv) >= 20 and d["hit"] and d["miss"]:
            # recall rate by overlap quartile
            q = np.percentile(allv, [25, 50, 75])
            lab = [1] * len(d["hit"]) + [0] * len(d["miss"])
            bins = np.digitize(allv, q)
            res["check2"][k]["recall_by_overlap_quartile"] = [
                (
                    float(np.mean([l for l, b in zip(lab, bins) if b == i]))
                    if any(b == i for b in bins)
                    else None
                )
                for i in range(4)
            ]
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="pkm-s0,pkm-s1,pkm-s2,pkm_doc-s0,pkm_doc-s1")
    ap.add_argument("--out", default="reports/fact_addressing_check.json")
    a = ap.parse_args(argv)
    import tiktoken

    enc = tiktoken.get_encoding("gpt2")
    facts = {}
    for line in open(ROOT / "data/v1/bios/facts.jsonl"):
        f = json.loads(line)
        facts[f["fact_id"]] = f
    out = {}
    for run in a.runs.split(","):
        rep = json.load(open(glob.glob(f"runs/final/cohort/{run}/step_*.json")[0]))
        rows = rep["metrics"]["Q2"]["result"]["rows"]
        prompts = {r["row_id"]: facts[r["row_id"]]["prompt"] for r in rows}
        model = load(CKPT[run])
        reads = reads_for(model, prompts, enc)
        out[run] = analyse(rows, reads)
        c1 = out[run]["check1"]
        print(
            run,
            {
                k: round(v["jac"]["mean"], 3)
                for k, v in c1.items()
                if k.startswith("frequent/")
            },
            flush=True,
        )
        for k in (
            "frequent/test",
            "frequent/paraphrase",
            "normal/test",
            "normal/paraphrase",
        ):
            d = out[run]["check2"].get(k, {})
            print(
                "   ",
                k,
                "hit",
                round(d["hit"].get("mean", float("nan")), 3),
                d["hit"]["n"],
                "miss",
                round(d["miss"].get("mean", float("nan")), 3),
                d["miss"]["n"],
                "quartiles",
                d.get("recall_by_overlap_quartile"),
                "| control other person: hit",
                round(d["control_other_person_hit"].get("mean", float("nan")), 3),
                "miss",
                round(d["control_other_person_miss"].get("mean", float("nan")), 3),
                flush=True,
            )
        Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
