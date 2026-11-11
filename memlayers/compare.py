"""Many run dirs -> comparison tables and plots. Reads only files.

    python -m memlayers.compare runs/ --out reports/compare/
    python -m memlayers.compare runs/ --out reports/compare/ --runs pkm-s0 pkm-s1 dense-s0
    python -m memlayers.compare runs/ --out x/ --pkm smoke --twin smoke_randkey --dense smoke_dense

Writes, under --out:
    runs.csv                one row per run: identity, provenance, every final metric
    groups.csv              per (experiment, tag) x metric key: n_seeds, mean, std, min, max, range
    curves.csv              every during and final eval row of every run, stacked
    training_check.csv      each run's rules, plus pkm's cross-run rule: ppl <= dense's
    <comparison>.csv        every registered comparison (learned_vs_random_keys = X2)
    plot_heldout_loss.png   pile_avg held-out loss vs tokens
    plot_fact_recall.png    fact-recall top-1 per tier (test role) vs tokens, control dashed
    plot_slot_coverage.png  slot coverage vs tokens (memory runs)
    compare_meta.json       inputs, command line, runs used and skipped, warnings

A group is (experiment, tag): untagged runs are the main groups; a tagged run
(tag=pilot) is its own group and never mixes into them. Runs moved aside by
force=true (`*.old-<n>`) and dirs that are not run dirs are skipped; so are
runs not `done`, unless --include-unfinished. Two runs with the same
(experiment, seed, tag), or runs on different data or eval sets, are refused.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["RunRecord", "CompareError", "load_runs", "compare", "main"]

OLD_DIR = re.compile(r".*\.old-\d+$")


class CompareError(RuntimeError):
    pass


@dataclass
class RunRecord:
    run_dir: Path
    run_id: str
    experiment: str
    seed: int
    tag: str
    status: str
    meta: Dict[str, Any]
    config: Dict[str, Any]
    metrics: Dict[str, float]  # "<metric>/<key>" -> value
    metric_ids: Dict[str, str]
    evals: List[dict] = field(default_factory=list)
    training_check: Optional[dict] = None

    @property
    def device(self) -> str:
        return str(self.meta.get("device", ""))

    @property
    def precision(self) -> str:
        # the resolved precision (meta.json) over the requested one (config)
        return str(
            self.meta.get("precision")
            or (self.config.get("runtime") or {}).get("precision", "fp32")
        )

    @property
    def data_sha(self) -> Optional[str]:
        return (self.meta.get("data") or {}).get("data_sha256")

    @property
    def eval_sets(self) -> Dict[str, Optional[str]]:
        es = self.meta.get("eval_sets") or {}
        return {
            k: es.get(k) for k in ("heldout_sample", "fact_sample", "readlog_tokens")
        }


def _read_json(p: Path) -> Optional[dict]:
    return json.loads(p.read_text()) if p.exists() else None


def _load(run_dir: Path, stage: str) -> RunRecord:
    import yaml

    from .eval.writers import EvalsCSV

    meta = _read_json(run_dir / "meta.json") or {}
    status = (_read_json(run_dir / "status.json") or {}).get("state", "?")
    cfg = (
        yaml.safe_load((run_dir / "config.yaml").read_text())
        if (run_dir / "config.yaml").exists()
        else {}
    )
    evals = EvalsCSV(run_dir / "evals.csv").read()
    fm = _read_json(run_dir / "final_metrics.json") or {}
    if stage == "final":
        metrics = dict(fm.get("metrics") or {})
        ids = dict(fm.get("metric_ids") or {})
        tokens = fm.get("tokens_seen")
    else:  # the latest step's rows of that stage, e.g. posthoc
        rows = [r for r in evals if r["stage"] == stage]
        last = max((r["step"] for r in rows), default=None)
        rows = [r for r in rows if r["step"] == last]
        metrics = {f"{r['metric']}/{r['key']}": r["value"] for r in rows}
        ids = {r["metric"]: r["metric_id"] for r in rows}
        tokens = rows[0]["tokens_seen"] if rows else None
    if not ids:
        ids = {r["metric"]: r["metric_id"] for r in evals}
    meta = dict(meta)
    meta["_final_tokens"] = tokens
    return RunRecord(
        run_dir=run_dir,
        run_id=meta.get("run_id", cfg.get("run_id", run_dir.name)),
        experiment=meta.get("experiment", cfg.get("name", "?")),
        seed=int(meta.get("seed", cfg.get("seed", -1))),
        tag=str(meta.get("tag", cfg.get("tag", "")) or ""),
        status=status,
        meta=meta,
        config=cfg or {},
        metrics=metrics,
        metric_ids=ids,
        evals=[r for r in evals if r["stage"] in ("during", "final")],
        training_check=_read_json(run_dir / "training_check.json"),
    )


def find_run_dirs(roots: Sequence[Path]) -> Tuple[List[Path], List[Tuple[str, str]]]:
    found, skipped = [], []
    for root in roots:
        root = Path(root)
        cands = (
            [root]
            if (root / "status.json").exists()
            else sorted(root.iterdir()) if root.is_dir() else []
        )
        for d in cands:
            if not d.is_dir() or d.name.startswith("."):
                continue
            if OLD_DIR.match(d.name):
                skipped.append((str(d), "moved aside by force=true (*.old-<n>)"))
                continue
            if not (d / "status.json").exists() or not (d / "meta.json").exists():
                skipped.append((str(d), "not a run dir (no status.json / meta.json)"))
                continue
            found.append(d)
    return found, skipped


def load_runs(
    roots: Sequence[Path],
    runs: Optional[Sequence[str]] = None,
    include_unfinished: bool = False,
    stage: str = "final",
):
    """-> (records, skipped [(dir, reason)], warnings). Raises CompareError."""
    dirs, skipped = find_run_dirs(roots)
    warnings: List[str] = []
    recs: List[RunRecord] = []
    for d in dirs:
        r = _load(d, stage)
        if runs and r.run_id not in runs:
            continue
        if r.status != "done" and not include_unfinished:
            skipped.append((str(d), f"status {r.status} (pass --include-unfinished)"))
            continue
        recs.append(r)
    if runs:
        missing = sorted(set(runs) - {r.run_id for r in recs})
        if missing:
            warnings.append(f"--runs named runs not found or skipped: {missing}")
    if not recs:
        raise CompareError(f"no runs to compare under {[str(r) for r in roots]}")

    seen: Dict[tuple, RunRecord] = {}
    for r in recs:
        k = (r.experiment, r.seed, r.tag)
        if k in seen:
            raise CompareError(
                f"two runs share (experiment, seed, tag) = {k}: {seen[k].run_dir} and "
                f"{r.run_dir}. Pass --runs, or move one away."
            )
        seen[k] = r

    def refuse_mixed(what: str, value_of):
        by: Dict[Any, List[str]] = {}
        for r in recs:
            by.setdefault(value_of(r), []).append(r.run_id)
        if len(by) > 1:
            lines = "\n".join(
                f"  {str(v)[:16] if v else v}: {', '.join(sorted(ids))}"
                for v, ids in by.items()
            )
            raise CompareError(
                f"these runs used different {what}, so their numbers are not "
                f"comparable in one table:\n{lines}\nCompare them separately (--runs)."
            )

    refuse_mixed("data (data_sha256)", lambda r: r.data_sha)
    refuse_mixed("heldout_sample eval sets", lambda r: r.eval_sets["heldout_sample"])
    refuse_mixed("fact_sample eval sets", lambda r: r.eval_sets["fact_sample"])
    # read-log-based metrics: only runs that have a read log take part
    rl = [r for r in recs if (r.meta.get("eval_sets") or {}).get("readlog_tokens")]
    by_rl: Dict[str, List[str]] = {}
    for r in rl:
        by_rl.setdefault(r.meta["eval_sets"]["readlog_tokens"], []).append(r.run_id)
    if len(by_rl) > 1:
        lines = "\n".join(
            f"  {h[:16]}: {', '.join(sorted(ids))}" for h, ids in by_rl.items()
        )
        raise CompareError(
            "these runs' read logs were made on different readlog_tokens sets, so "
            f"read-log-based metrics are not comparable in one table:\n{lines}\n"
            "Re-run the read-log pass on one set (memlayers.readlog_pass ... force=true)."
        )

    for r in recs:
        if r.meta.get("device_changes"):
            ch = "; ".join(
                f"step {c['at_step']}: {c['from']} -> {c['to']}"
                for c in r.meta["device_changes"]
            )
            warnings.append(
                f"{r.run_id} changed device or precision on a resume ({ch})"
            )
    for exp in sorted({r.experiment for r in recs}):
        rs = [r for r in recs if r.experiment == exp]
        for what, get in (
            ("devices", lambda r: r.device),
            ("precisions", lambda r: r.precision),
        ):
            vals = sorted({get(r) for r in rs})
            if len(vals) > 1:
                warnings.append(
                    f"experiment {exp} mixes {what} {vals}: "
                    + ", ".join(f"{r.run_id}={get(r)}" for r in rs)
                )
    return sorted(recs, key=lambda r: (r.experiment, r.tag, r.seed)), skipped, warnings


# ---------------------------------------------------------------------- tables
def runs_table(recs):
    import pandas as pd

    keys = sorted({k for r in recs for k in r.metrics})
    rows = []
    for r in recs:
        row = {
            "run_id": r.run_id,
            "experiment": r.experiment,
            "seed": r.seed,
            "tag": r.tag,
            "status": r.status,
            "device": r.device,
            "precision": r.precision,
            "git_commit": (r.meta.get("git") or {}).get("commit"),
            "git_dirty": (r.meta.get("git") or {}).get("dirty"),
            "data_sha256": r.data_sha,
            "heldout_sample_sha256": r.eval_sets["heldout_sample"],
            "fact_sample_sha256": r.eval_sets["fact_sample"],
            "readlog_tokens_sha256": r.eval_sets["readlog_tokens"],
            "tokens_seen": r.meta.get("_final_tokens"),
            "gpu_name": r.meta.get("gpu_name"),
            "device_changed": bool(r.meta.get("device_changes")),
        }
        row.update({k: r.metrics.get(k) for k in keys})
        rows.append(row)
    return pd.DataFrame(rows)


def groups_table(recs):
    import pandas as pd

    long = [
        {
            "experiment": r.experiment,
            "tag": r.tag,
            "metric": k.split("/", 1)[0],
            "metric_id": r.metric_ids.get(k.split("/", 1)[0], ""),
            "key": k.split("/", 1)[1],
            "seed": r.seed,
            "value": v,
        }
        for r in recs
        for k, v in r.metrics.items()
    ]
    cols = [
        "experiment",
        "tag",
        "metric",
        "metric_id",
        "key",
        "n_seeds",
        "mean",
        "std",
        "min",
        "max",
        "range",
    ]
    if not long:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(long)
    g = df.groupby(["experiment", "tag", "metric", "metric_id", "key"], sort=True)[
        "value"
    ]
    out = g.agg(
        n_seeds="count", mean="mean", std="std", min="min", max="max"
    ).reset_index()
    out["range"] = out["max"] - out["min"]
    return out[cols]


def curves_table(recs):
    import pandas as pd

    rows = [
        {
            "run_id": r.run_id,
            "experiment": r.experiment,
            "seed": r.seed,
            "tag": r.tag,
            **e,
        }
        for r in recs
        for e in r.evals
    ]
    cols = [
        "run_id",
        "experiment",
        "seed",
        "tag",
        "step",
        "tokens_seen",
        "stage",
        "metric",
        "metric_id",
        "key",
        "value",
    ]
    return pd.DataFrame(rows, columns=cols)


PPL_KEY = "heldout_quality/ppl/pile_avg"


def dense_rule(pkm_rec, dense_recs) -> dict:
    """The methodology's cross-run check for pkm: final pile_avg perplexity at
    most the dense run's (same seed if there is one, else the dense mean)."""
    ppl = pkm_rec.metrics.get(PPL_KEY)
    out = {"rule": "ppl_at_most_dense", "gating": True, "pkm_ppl": ppl}
    if not dense_recs:
        return {**out, "pass": None, "detail": "no dense run"}
    same = [d for d in dense_recs if d.seed == pkm_rec.seed and PPL_KEY in d.metrics]
    pool = same or [d for d in dense_recs if PPL_KEY in d.metrics]
    if ppl is None or not pool:
        return {**out, "pass": None, "detail": "no pile_avg perplexity"}
    dppl = sum(d.metrics[PPL_KEY] for d in pool) / len(pool)
    return {
        **out,
        "dense_ppl": dppl,
        "dense_runs": ",".join(d.run_id for d in pool),
        "pass": bool(ppl <= dppl),
        "detail": f"pkm {ppl:.4f} vs dense {dppl:.4f}",
    }


def training_check_table(recs, roles):
    import pandas as pd

    rows = []
    for r in recs:
        tc = r.training_check or {}
        for name, rule in (tc.get("rules") or {}).items():
            numbers = {k: v for k, v in rule.items() if k not in ("gating", "pass")}
            rows.append(
                {
                    "run_id": r.run_id,
                    "experiment": r.experiment,
                    "seed": r.seed,
                    "tag": r.tag,
                    "rule": name,
                    "gating": rule.get("gating"),
                    "pass": rule.get("pass"),
                    "run_verdict": tc.get("verdict"),
                    "detail": json.dumps(numbers, default=str, sort_keys=True),
                }
            )
    dense = [r for r in recs if r.experiment == roles["dense"] and not r.tag]
    for r in recs:
        if r.experiment != roles["pkm"] or r.tag:
            continue  # the twin's quality vs dense is a result, not a health check
        d = dense_rule(r, dense)
        rows.append(
            {
                "run_id": r.run_id,
                "experiment": r.experiment,
                "seed": r.seed,
                "tag": r.tag,
                "rule": d["rule"],
                "gating": True,
                "pass": d["pass"],
                "run_verdict": (r.training_check or {}).get("verdict"),
                "detail": (
                    d["detail"]
                    if d["pass"] is None
                    else json.dumps(
                        {k: d[k] for k in ("pkm_ppl", "dense_ppl", "dense_runs")},
                        sort_keys=True,
                    )
                ),
            }
        )
    cols = [
        "run_id",
        "experiment",
        "seed",
        "tag",
        "rule",
        "gating",
        "pass",
        "run_verdict",
        "detail",
    ]
    return pd.DataFrame(rows, columns=cols)


# ----------------------------------------------------------------------- plots
def _curve(r, keyf):
    pts = {}
    for e in r.evals:
        v = keyf(e)
        if v is not None:
            pts[e["step"]] = (e["tokens_seen"], v)
    return [pts[s] for s in sorted(pts)]


def _plot(recs, path: Path, title: str, ylabel: str, panels):
    """panels: [(panel title, keyf, control keyf or None)]."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    exps = sorted({r.experiment + (f" [{r.tag}]" if r.tag else "") for r in recs})
    colors = {e: plt.cm.tab10(i % 10) for i, e in enumerate(exps)}
    fig, axes = plt.subplots(
        1, len(panels), figsize=(5.2 * len(panels), 3.8), squeeze=False
    )
    drew = False
    for ax, (ptitle, keyf, ctrlf) in zip(axes[0], panels):
        for exp in exps:
            rs = [
                r
                for r in recs
                if r.experiment + (f" [{r.tag}]" if r.tag else "") == exp
            ]
            curves = []
            for r in rs:
                c = _curve(r, keyf)
                if c:
                    ax.plot(
                        [x for x, _ in c],
                        [y for _, y in c],
                        color=colors[exp],
                        lw=1.2,
                        alpha=0.9,
                        label=f"{exp} s{r.seed}" if len(rs) > 1 else exp,
                        marker="o",
                        ms=2.5,
                    )
                    curves.append(c)
                    drew = True
            if len(curves) >= 2 and len({len(c) for c in curves}) == 1:
                xs = [x for x, _ in curves[0]]
                lo = [min(c[i][1] for c in curves) for i in range(len(curves[0]))]
                hi = [max(c[i][1] for c in curves) for i in range(len(curves[0]))]
                ax.fill_between(xs, lo, hi, color=colors[exp], alpha=0.15, lw=0)
        if ctrlf is not None:
            ctrl: Dict[int, List[tuple]] = {}
            for r in recs:
                for x, y in _curve(r, ctrlf):
                    ctrl.setdefault(x, []).append(y)
            if ctrl:
                xs = sorted(ctrl)
                ax.plot(
                    xs,
                    [sum(ctrl[x]) / len(ctrl[x]) for x in xs],
                    "k--",
                    lw=1,
                    label="control (mean)",
                )
        ax.set_title(ptitle, fontsize=10)
        ax.set_xlabel("tokens seen")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        axes[0][-1].legend(handles, labels, fontsize=7, loc="best")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return drew


def _ev(metric, key, stages=("during", "final")):
    def f(e):
        if e["metric"] == metric and e["key"] == key and e["stage"] in stages:
            return e["value"]
        return None

    return f


def _pile_loss(e):
    # the fixed sample's documents at every point (loss/pile_avg_sample at final)
    if e["metric"] != "heldout_quality":
        return None
    if e["stage"] == "during" and e["key"] == "loss/pile_avg":
        return e["value"]
    if e["stage"] == "final" and e["key"] == "loss/pile_avg_sample":
        return e["value"]
    return None


def plots(recs, out: Path) -> Dict[str, str]:
    written = {}
    p = out / "plot_heldout_loss.png"
    _plot(
        recs,
        p,
        "Held-out loss, 5 training subjects (token-weighted; fixed sample)",
        "loss",
        [("pile_avg", _pile_loss, None)],
    )
    written["heldout_loss"] = p.name
    p = out / "plot_fact_recall.png"
    _plot(
        recs,
        p,
        "Fact recall top-1, test prompts (final point: all facts)",
        "top-1",
        [
            (
                t,
                _ev("fact_recall", f"top1/{t}/test"),
                _ev("fact_recall", "top1/control/test"),
            )
            for t in ("frequent", "normal", "rare")
        ],
    )
    written["fact_recall"] = p.name
    layers = sorted(
        {
            e["key"].split("/", 1)[1]
            for r in recs
            for e in r.evals
            if e["metric"] == "slot_usage" and e["key"].startswith("coverage/")
        }
    )
    if layers:
        p = out / "plot_slot_coverage.png"
        mem = [r for r in recs if any(e["metric"] == "slot_usage" for e in r.evals)]
        _plot(
            mem,
            p,
            "Memory slot coverage on held-out text",
            "coverage",
            [(L, _ev("slot_usage", f"coverage/{L}"), None) for L in layers],
        )
        written["slot_coverage"] = p.name
    return written


# --------------------------------------------------------------------- driver
def compare(
    roots: Sequence[Path],
    out: Path,
    runs: Optional[Sequence[str]] = None,
    stage: str = "final",
    include_unfinished: bool = False,
    roles: Optional[Dict[str, str]] = None,
    argv: Optional[List[str]] = None,
) -> Dict[str, Any]:
    from .eval import comparisons as _builtin  # noqa: F401  (registers X2)
    from .eval.registry import comparisons

    roles = {"pkm": "pkm", "twin": "pkm_randkey", "dense": "dense", **(roles or {})}
    recs, skipped, warnings = load_runs(roots, runs, include_unfinished, stage)
    for w in warnings:
        print(f"[compare] WARNING: {w}", file=sys.stderr)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, df in (
        ("runs", runs_table(recs)),
        ("groups", groups_table(recs)),
        ("curves", curves_table(recs)),
        ("training_check", training_check_table(recs, roles)),
    ):
        df.to_csv(out / f"{name}.csv", index=False)
        written[name] = f"{name}.csv"
    for name, spec in comparisons().items():
        spec.fn(recs, roles).to_csv(out / f"{name}.csv", index=False)
        written[name] = f"{name}.csv"
    written.update(plots(recs, out))
    meta = {
        "command": " ".join(["python -m memlayers.compare", *(argv or [])]),
        "inputs": [str(r) for r in roots],
        "stage": stage,
        "roles": roles,
        "runs": [str(r.run_dir) for r in recs],
        "skipped": [{"dir": d, "reason": why} for d, why in skipped],
        "warnings": warnings,
        "files": written,
    }
    (out / "compare_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(
        f"[compare] {len(recs)} runs -> {out}/ ({', '.join(sorted(written.values()))})"
    )
    for d, why in skipped:
        print(f"[compare] skipped {d}: {why}")
    return meta


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("roots", nargs="+", help="run dirs, or dirs holding run dirs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", nargs="*", default=None, help="only these run ids")
    ap.add_argument(
        "--stage", default="final", help="final (final_metrics.json) or posthoc"
    )
    ap.add_argument("--include-unfinished", action="store_true")
    ap.add_argument("--pkm", default="pkm", help="the main experiment's name")
    ap.add_argument("--twin", default="pkm_randkey", help="the random-key twin's name")
    ap.add_argument("--dense", default="dense", help="the dense baseline's name")
    a = ap.parse_args(argv)
    try:
        compare(
            [Path(r) for r in a.roots],
            Path(a.out),
            a.runs,
            a.stage,
            a.include_unfinished,
            {"pkm": a.pkm, "twin": a.twin, "dense": a.dense},
            argv,
        )
    except CompareError as e:
        print(f"[compare] REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
