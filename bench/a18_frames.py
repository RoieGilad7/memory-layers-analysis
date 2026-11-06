"""A18, split by held-out frame -- which paraphrase wording recovers the fact?

    python bench/a18_frames.py

Re-scores the A18 run's saved checkpoint (`runs/learnability_t1_pkm/ckpt.pt`)
over the same 36,000 prompts and reports top-1 and mean rank **per held-out
template**, which the run's own JSON aggregates away. The four frames are
structurally different questions -- a question/answer pair, the attribute
topicalized, the person predicated as being on record, a profile line with a
colon -- so "a new wording barely recovers the fact" is worth seeing per frame
rather than only in aggregate.

Writes `bench/results/learnability_t1_pkm_frames.json`. Leaves the run's own
JSON alone: the overall numbers it prints are a check that this scoring
reproduces the run exactly.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data.bios_data as bd                                     # noqa: E402
from data.common import load_config as load_data_config         # noqa: E402
from data.q2_probe import ProbeSet, select_eval_rows, summarize  # noqa: E402
from memlayers.train import Trainer, load_config               # noqa: E402

# Which structural frame each held-out template id is, for the report.
FRAME_NAMES = {0: "question", 1: "topic", 2: "record", 3: "profile line"}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="memlayers/configs/t1_pkm.yaml")
    ap.add_argument("--data-config", default="configs/data/v1.yaml")
    ap.add_argument("--run-dir", default="runs/learnability_t1_pkm")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="bench/results/learnability_t1_pkm_frames.json")
    args = ap.parse_args(argv)

    data_cfg = load_data_config(args.data_config)
    cfg = load_config(ROOT / args.config, [
        "data.source=real", "data.version=v1",
        f"data.data_config={args.data_config}", f"data.seed={args.seed}",
        f"train.seed={args.seed}", f"runtime.out_dir={args.run_dir}"])
    trainer = Trainer(cfg)
    ck = Path(args.run_dir) / "ckpt.pt"
    print(f"[frames] loading {ck}", flush=True)
    trainer.load_checkpoint(ck)

    rows = select_eval_rows(data_cfg)
    probe = ProbeSet.build(data_cfg, rows)
    print(f"[frames] scoring {len(probe):,} prompts at step {trainer.step:,}",
          flush=True)
    t0 = time.time()
    result = summarize(probe.score(trainer.model, trainer.device,
                                   block_size=cfg.model.get("block_size", 512)))
    print(f"[frames] scored in {time.time() - t0:.0f}s", flush=True)

    out: Dict[str, Any] = {
        "source_run": "bench/results/learnability_t1_pkm.json",
        "checkpoint": str(ck),
        "step": trainer.step,
        "data_sha256": trainer.data_provenance.get("data_sha256"),
        "frame_names": {str(k): v for k, v in FRAME_NAMES.items()},
        "heldout_templates": {attr: bd.HELDOUT_TEMPLATES[attr]
                              for attr in data_cfg.bio_attributes},
        "by_tier_role": result["by_tier_role"],
        "by_role_template": result["by_role_template"],
        "by_tier_role_template": result["by_tier_role_template"],
    }
    Path(args.out).write_text(json.dumps(out, indent=2))

    print("\n=== paraphrase, per held-out frame (all tiers pooled)")
    for tid, name in FRAME_NAMES.items():
        a = result["by_role_template"].get(f"paraphrase/t{tid}")
        if a:
            print(f"   t{tid} {name:13s} top-1 {a['top1']:.3%}  "
                  f"mean rank {a['mean_rank']:.2f}  n={a['n']:,}")
    print("\n=== paraphrase, per frame, per tier")
    for tier in ("frequent", "normal", "rare", "control"):
        parts = []
        for tid, name in FRAME_NAMES.items():
            a = result["by_tier_role_template"].get(f"{tier}/paraphrase/t{tid}")
            if a:
                parts.append(f"{name}={a['top1']:.3%}/{a['mean_rank']:.1f}")
        print(f"   {tier:9s} " + "  ".join(parts))
    print("\n=== check: these should match the run's own numbers")
    for tier in ("frequent", "normal", "rare", "control"):
        for role in ("test", "paraphrase"):
            a = result["by_tier_role"][f"{tier}/{role}"]
            print(f"   {tier:9s} {role:11s} top-1 {a['top1']:.3%}  "
                  f"mean rank {a['mean_rank']:.2f}")
    print(f"\n   -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
