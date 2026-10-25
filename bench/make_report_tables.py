"""Emit the markdown tables for reports/step1_demo_report.md from bench/results/*.json.

Keeps the report's numbers traceable: every figure in it comes from a result file
written by bench/benchmark.py, not retyped by hand.

    python bench/make_report_tables.py > /tmp/tables.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "bench" / "results"
sys.path.insert(0, str(ROOT))

TIER_TOKENS = {"t1": 150e6, "t2": 500e6}
RUNS_PER_TIER = 12
ORDER = ["t1_dense", "t1_pkm", "t1_pkm_frozen", "t1_peer",
         "t2_dense", "t2_pkm", "t2_pkm_262k", "t2_peer"]


def load(stem, mode, tag=""):
    f = RESULTS / f"{stem}__{mode}{('__' + tag) if tag else ''}.json"
    return json.loads(f.read_text()) if f.exists() else None


def fmt(x, nd=2, dash="--"):
    return dash if x is None else f"{x:,.{nd}f}"


def main() -> int:
    print("### Table A -- parameter counts, micro-batch, speed and memory\n")
    print("| config | embedding | backbone | memory (keys+values) | total | micro-batch "
          "| ms/step mean | ms/step p90 | tokens/sec | peak mem |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for stem in ORDER:
        s = load(stem, "speed")
        if not s:
            continue
        pc = s["param_counts"]
        mem_kv = pc["memory_keys"] + pc["memory_values"]
        print(f"| `{s['name']}` | {pc['embedding']/1e6:.2f}M | {pc['backbone']/1e6:.2f}M "
              f"| {mem_kv/1e6:.2f}M | {pc['total']/1e6:.2f}M | {s['micro_batch_size']} "
              f"| {s['ms_per_step_mean']:.0f} | {s['ms_per_step_p90']:.0f} "
              f"| {s['tokens_per_s_from_mean_time']:,.0f} | {s['peak_mem_GB']:.1f} GB |")

    print("\n### Table B -- read-logging cost\n")
    print("| config | ms/step off | ms/step on | slowdown | read-log size | "
          "GB per 1M tokens | reads/token |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for stem in ORDER:
        base, rl = load(stem, "speed"), load(stem, "speed", "readlog")
        if not (base and rl):
            continue
        slow = rl["ms_per_step_mean"] / base["ms_per_step_mean"]
        info = rl.get("readlog", {})
        ml = next(iter(rl.get("memory_layers", {}).values()), {})
        print(f"| `{rl['name']}` | {base['ms_per_step_mean']:.0f} "
              f"| {rl['ms_per_step_mean']:.0f} | {slow:.2f}x "
              f"| {fmt(info.get('bytes_per_token'), 0)} B/token "
              f"| {fmt(info.get('GB_per_million_tokens'), 3)} GB "
              f"| {ml.get('reads_per_token', '--')} |")

    print("\n### Table C -- learning check on fake data (b)\n")
    print("| config | steps | tokens | loss start | loss end (mean last 25) | "
          "random-token level | task floor | below random? | slots read | "
          "KL(usage \\|\\| uniform) | normalized KL |")
    print("|---|---:|---:|---:|---:|---:|---:|:--:|---:|---:|---:|")
    for stem in ORDER:
        d = load(stem, "learn")
        if not d:
            continue
        su = next(iter((d.get("slot_usage") or {}).values()), {})
        print(f"| `{d['name']}` | {d['steps']} | {d['tokens_seen']/1e6:.1f}M "
              f"| {d['loss_first']:.3f} | {d['loss_final_mean_last25']:.3f} "
              f"| {d['random_token_level_nats']:.3f} | {d['task_loss_floor_nats']:.3f} "
              f"| {'yes' if d['clearly_below_random'] else 'NO'} "
              f"| {100*su.get('fraction_used', 0):.1f}% "
              f"| {fmt(su.get('kl_from_uniform'), 3)} nats "
              f"| {fmt(su.get('normalized_kl'), 3)} |")

    print("\n### Table D -- extrapolated wall-clock per run and per tier\n")
    print(f"Hours = training tokens / measured tokens-per-sec. Tier 1 = 150M tokens, "
          f"tier 2 = 0.5B tokens, {RUNS_PER_TIER} runs per tier.\n")
    print("| config | tokens/sec (Mac) | hours/run (Mac) | hours for 12 runs (Mac) | "
          "tokens/sec (T4) | hours/run (T4) | hours for 12 runs (T4) |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for stem in ORDER:
        s = load(stem, "speed")
        if not s:
            continue
        tier = "t1" if stem.startswith("t1") else "t2"
        tok = TIER_TOKENS[tier]
        tps = s["tokens_per_s_from_mean_time"]
        h = tok / tps / 3600
        print(f"| `{s['name']}` | {tps:,.0f} | {h:.2f} | {h*RUNS_PER_TIER:.1f} "
              f"| _TBD_ | _TBD_ | _TBD_ |")

    print("\n### Table E -- micro-batch probe\n")
    print("| config | 4 | 8 | 16 | 32 | largest | peak mem at largest |")
    print("|---|:--:|:--:|:--:|:--:|---:|---:|")
    for stem in ORDER:
        p = load(stem, "probe")
        if not p:
            continue
        by = {a["micro_batch_size"]: a for a in p["attempts"]}
        cells = []
        for mb in (4, 8, 16, 32):
            a = by.get(mb)
            cells.append("--" if a is None else ("ok" if a.get("ok") else "OOM"))
        oks = [a for a in p["attempts"] if a.get("ok")]
        peak = oks[-1]["peak_mem_bytes"] / 1e9 if oks else None
        print(f"| `{Path(p['config']).stem}` | " + " | ".join(cells) +
              f" | {p['largest_micro_batch']} | {fmt(peak, 1)} GB |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
