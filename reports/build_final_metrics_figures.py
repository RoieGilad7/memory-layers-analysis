"""Figures and summary tables for the final Phase 1 metric report.

Reads the per-checkpoint JSON reports written by metrics.py and writes PNG
figures plus a JSON digest of every number the report quotes.

    python reports/build_final_metrics_figures.py runs/final/cohort reports/final_metrics runs/final/hf_meta
"""

import glob
import json
import sys
from pathlib import Path
from statistics import fmean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

LEARNED = ["pkm-s0", "pkm-s1", "pkm-s2"]
TWIN = "pkm_randkey-s0"
SUBJECTS = ["FreeLaw", "Github", "Pile-CC", "PubMed Central", "Wikipedia (en)"]
BLUE, ORANGE = "#2a78d6", "#eb6834"  # learned keys, frozen random keys
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SEED_MARKERS = {"pkm-s0": "o", "pkm-s1": "s", "pkm-s2": "D"}
JITTER = {"pkm-s0": -0.12, "pkm-s1": 0.0, "pkm-s2": 0.12}  # keep near-equal seeds visible

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "font.size": 9,
        "legend.frameon": False,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def load(root):
    out = {}
    for run in LEARNED + [TWIN]:
        paths = glob.glob(str(Path(root) / run / "step_*.json"))
        if paths:
            out[run] = json.loads(Path(paths[0]).read_text())
    return out


def m(report, name):
    return report["metrics"][name]["result"]


def digest(reports):
    d = {}
    for run, r in reports.items():
        q1 = m(r, "Q1")
        q2 = m(r, "Q2")["by_tier_role"]
        u1, u4, c6 = m(r, "U1"), m(r, "U4"), m(r, "C6")
        v2 = r["metrics"]["V2"]["rows"]
        e1 = m(r, "E1")
        e2 = m(r, "E2")
        cum = e2["cumulative"]
        wl = r["metrics"]["Whole layer off"]["rows"]
        d[run] = dict(
            parity=r["parity"],
            q1_nll=q1["overall"]["nll"],
            q1_by_subject={s: q1["by_subject"][s]["nll"] for s in SUBJECTS},
            q2_top1={
                k: q2[k]["top1"]
                for k in q2
                if k.endswith("/test") or k.endswith("/paraphrase")
            },
            q2_rank={k: q2[k]["rank"] for k in q2 if k.endswith("/paraphrase")},
            u1=dict(
                coverage=u1["coverage"],
                top1_coverage=u1["top1_coverage"],
                kl_bits=u1["kl_to_uniform_bits"],
            ),
            u4=dict(
                excess_bits=u4["excess_bits"],
                mi_bits=u4["conditional_mi_bits"],
                shuffle_bits=u4["shuffled_mean_bits"],
                p=u4["shuffle_p"],
            ),
            v2={row[0]: dict(top1=row[1], top2=row[2], paired_excess=row[6]) for row in v2},
            c6=dict(
                active=c6.get("effective_rank"),
                top512=c6.get("effective_rank_fixed_rows"),
            ),
            e1_mean={k: v["mean_specificity_excess_nll"] for k, v in e1["by_lesion_size"].items()},
            e1_matched={k: v["matched_subjects"] for k, v in e1["by_lesion_size"].items()},
            e1_by_subject={
                row[0]: (row[4] if row[5] == "matched" else None)
                for row in r["metrics"]["E1"]["rows"]
            },
            e2=dict(
                cohort=len(cum["facts"]),
                matched=cum["matched_facts"],
                status_counts=cum["status_counts"],
                core_fraction=cum["mean_matched_core_fraction"],
                erasure_rate=cum["mean_matched_erasure_rate"],
                single_slot_status=e2["single_slot"].get("status"),
            ),
            whole_off={row[0]: row[4] for row in wl if row[1].startswith("NLL")},
            whole_off_recall={
                row[0]: (row[2], row[3]) for row in wl if row[1] == "Top-1 accuracy"
            },
        )
        if run == TWIN and r["metrics"]["X2"].get("result"):
            d["x2"] = r["metrics"]["X2"]["result"]
    return d


def save(fig, out, name):
    fig.savefig(out / name)
    plt.close(fig)


def seed_points(ax, x, values, label_once):
    for run, v in values.items():
        if v is None:
            continue
        ax.scatter(
            [x], [v], marker=SEED_MARKERS[run], s=40, color=BLUE,
            edgecolor=SURFACE, linewidth=1.5, zorder=3,
            label=run if label_once else None,
        )


def fig_q2(d, out):
    tiers = ["frequent", "normal", "rare", "control"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, role in zip(axes, ["test", "paraphrase"]):
        for i, t in enumerate(tiers):
            key = f"{t}/{role}"
            vals = {r: d[r]["q2_top1"][key] for r in LEARNED if r in d}
            mean = fmean(vals.values())
            ax.bar(i - 0.2, mean, 0.36, color=BLUE, label="Learned keys (mean of 3 seeds)" if i == 0 else None)
            ax.vlines(i - 0.2, min(vals.values()), max(vals.values()), color=INK, lw=1.5)
            if TWIN in d:
                ax.bar(i + 0.2, d[TWIN]["q2_top1"][key], 0.36, color=ORANGE, label="Random-key twin" if i == 0 else None)
        ax.set_xticks(range(len(tiers)), tiers)
        ax.set_title(f"Q2 top-1 recall, {role} wordings")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("Top-1 accuracy (slice)")
    axes[0].legend(loc="upper right")
    fig.text(0.01, -0.04, "Black whisker: range over learned seeds s0/s1/s2.", color=INK2)
    save(fig, out, "q2_recall.png")


def fig_core_scalars(d, out):
    """U4 excess, V2 top-1 share and E1 headline: learned seeds vs twin, with the X2 range."""
    items = [
        ("U4 within-token excess (bits)", lambda r: d[r]["u4"]["excess_bits"]),
        ("V2 top-1 share, subject text", lambda r: d[r]["v2"]["Subject text"]["top1"]),
        ("V2 top-1 share, fact probes", lambda r: d[r]["v2"]["Fact probes"]["top1"]),
        ("E1 mean excess, m=64 (nats)", lambda r: d[r]["e1_mean"]["64"]),
    ]
    fig, axes = plt.subplots(1, len(items), figsize=(11, 3))
    for ax, (title, get) in zip(axes, items):
        vals = {r: get(r) for r in LEARNED if r in d}
        ax.axhspan(min(vals.values()), max(vals.values()), color=BLUE, alpha=0.12, lw=0)
        seed_points(ax, 0, vals, ax is axes[0])
        if TWIN in d:
            ax.scatter([1], [get(TWIN)], marker="^", s=55, color=ORANGE, edgecolor=SURFACE, linewidth=1.5, zorder=3, label="randkey-s0" if ax is axes[0] else None)
        ax.set_xticks([0, 1], ["learned", "random keys"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_title(title, fontsize=9.5)
    axes[0].legend(loc="lower left", fontsize=7.5)
    fig.text(0.01, -0.05, "Shaded band: full range over the 3 learned seeds (the X2 equivalence range).", color=INK2)
    fig.tight_layout()
    save(fig, out, "core_learned_vs_twin.png")


def fig_e1(d, out):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    ax = axes[0]
    sizes = ["16", "64", "256"]
    for run in LEARNED:
        if run in d:
            ax.plot(range(3), [d[run]["e1_mean"][s] for s in sizes], color=BLUE, lw=2, marker=SEED_MARKERS[run], ms=6, label=run)
    if TWIN in d:
        ax.plot(range(3), [d[TWIN]["e1_mean"][s] for s in sizes], color=ORANGE, lw=2, marker="^", ms=7, label="randkey-s0")
    ax.set_xticks(range(3), [f"m={s}" for s in sizes])
    ax.set_ylabel("Mean target − other ΔNLL, excess over control (nats)")
    ax.set_title("E1 by lesion size")
    ax.legend(fontsize=7.5)
    ax = axes[1]
    width = 0.2
    for j, run in enumerate(LEARNED + [TWIN]):
        if run not in d:
            continue
        vals = [d[run]["e1_by_subject"].get(s) for s in SUBJECTS]
        xs = [i + (j - 1.5) * width for i in range(len(SUBJECTS))]
        color = ORANGE if run == TWIN else BLUE
        alpha = 1.0 if run in (TWIN, "pkm-s0") else (0.7 if run == "pkm-s1" else 0.45)
        ax.bar([x for x, v in zip(xs, vals) if v is not None], [v for v in vals if v is not None], width * 0.9, color=color, alpha=alpha, label=run)
        for x, v in zip(xs, vals):
            if v is None:
                ax.text(x, 0.0005, "×", ha="center", color=INK2, fontsize=9)
    ax.set_xticks(range(len(SUBJECTS)), [s.replace(" (en)", "").replace(" Central", "") for s in SUBJECTS])
    ax.set_title("E1 per subject, m=64 (× = no matched controls)")
    ax.legend(fontsize=7.5)
    fig.tight_layout()
    save(fig, out, "e1.png")


def fig_e2(d, out):
    order = ["matched", "no_matched_controls", "prefix_limit_reached", "threshold_not_reached", "at_chance_on_test", "unlearned_discovery"]
    shades = {"matched": BLUE, "no_matched_controls": "#86b6ef", "prefix_limit_reached": "#c3c2b7", "at_chance_on_test": "#e4e3df", "unlearned_discovery": "#f0efec"}
    runs = [r for r in LEARNED + [TWIN] if r in d]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    for i, run in enumerate(runs):
        left = 0
        counts = d[run]["e2"]["status_counts"]
        for s in order:
            n = counts.get(s, 0)
            if not n:
                continue
            ax.barh(i, n, left=left, color=shades.get(s, "#e4e3df"), edgecolor=SURFACE, linewidth=2, label=s.replace("_", " ") if i == 0 or s not in [h.get_label() for h in ax.patches] else None)
            if n >= 12:
                ax.text(left + n / 2, i, str(n), ha="center", va="center", color=INK if s != "matched" else SURFACE, fontsize=8)
            left += n
    ax.set_yticks(range(len(runs)), runs)
    ax.invert_yaxis()
    ax.set_xlabel(f"Facts in the shared E2 cohort (n = {d[runs[0]]['e2']['cohort']})")
    ax.set_title("E2 cumulative lesion outcome per fact (prefix limit 16 slots)")
    handles, labels = ax.get_legend_handles_labels()
    seen = {}
    for h, l in zip(handles, labels):
        seen.setdefault(l, h)
    ax.legend(seen.values(), seen.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=3, fontsize=7.5)
    save(fig, out, "e2_status.png")


def fig_whole_off(d, out):
    fig, ax = plt.subplots(figsize=(7, 3))
    cohorts = ["All text"] + SUBJECTS
    width = 0.2
    for j, run in enumerate(LEARNED + [TWIN]):
        if run not in d:
            continue
        color = ORANGE if run == TWIN else BLUE
        alpha = 1.0 if run in (TWIN, "pkm-s0") else (0.7 if run == "pkm-s1" else 0.45)
        ax.bar([i + (j - 1.5) * width for i in range(len(cohorts))], [d[run]["whole_off"][c] for c in cohorts], width * 0.9, color=color, alpha=alpha, label=run)
    ax.set_xticks(range(len(cohorts)), [c.replace(" (en)", "").replace(" Central", "") for c in cohorts])
    ax.set_ylabel("NLL increase (nats/token)")
    ax.set_title("Whole memory layer off: loss increase by subject")
    ax.set_ylim(0, 1.35)
    ax.legend(fontsize=7.5, ncol=4, loc="upper right")
    save(fig, out, "whole_layer_off.png")


def fig_official(meta_root, out):
    """Q1 and Q2 as logged by the training runs (whole test half, every fact)."""
    runs = LEARNED + [TWIN, "dense-s0"]
    off = {}
    for r in runs:
        path = Path(meta_root) / r / "final_metrics.json"
        if path.exists():
            off[r] = json.loads(path.read_text())["metrics"]
    colors = {r: BLUE for r in LEARNED} | {TWIN: ORANGE, "dense-s0": "#1baf7a"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    ax = axes[0]
    subj = ["pile_avg", "freelaw", "github", "pile_cc", "pubmed_central", "wikipedia_en"]
    width = 0.16
    for j, r in enumerate([r for r in runs if r in off]):
        alpha = 1.0 if r in (TWIN, "dense-s0", "pkm-s0") else (0.7 if r == "pkm-s1" else 0.45)
        base = [off["pkm-s0"][f"heldout_quality/loss/{s}"] for s in subj]
        ax.bar([i + (j - 2) * width for i in range(len(subj))],
               [off[r][f"heldout_quality/loss/{s}"] - b for s, b in zip(subj, base)],
               width * 0.9, color=colors[r], alpha=alpha, label=r)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(len(subj)), ["Pile avg", "FreeLaw", "Github", "Pile-CC", "PubMed", "Wikipedia"])
    ax.set_ylabel("Held-out loss minus pkm-s0 (nats)")
    ax.set_title("Q1 (official): held-out loss relative to pkm-s0")
    ax.set_ylim(top=0.1)
    ax.legend(fontsize=7, ncol=3, loc="upper left")
    ax = axes[1]
    tiers = ["frequent", "normal", "rare", "control"]
    for j, r in enumerate([r for r in runs if r in off]):
        alpha = 1.0 if r in (TWIN, "dense-s0", "pkm-s0") else (0.7 if r == "pkm-s1" else 0.45)
        ax.bar([i + (j - 2) * width for i in range(len(tiers))],
               [off[r][f"fact_recall/top1/{t}/test"] for t in tiers],
               width * 0.9, color=colors[r], alpha=alpha, label=r)
    ax.set_xticks(range(len(tiers)), tiers)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Top-1 accuracy, test wordings")
    ax.set_title("Q2 (official): fact recall by exposure tier")
    fig.tight_layout()
    save(fig, out, "official_q1_q2.png")
    return off


def fig_x2(d, out):
    x2 = d.get("x2")
    if not x2:
        return
    rows = [(k, v) for k, v in x2["metrics"].items()]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    labels, ratios = [], []
    for k, v in rows:
        labels.append(k)
        if v["within_margin"] is None:
            ratios.append(None)
        else:
            ratios.append(v["learned_minus_twin"] / v["margin"])
    y = range(len(labels))
    ax.axvspan(-1, 1, color=BLUE, alpha=0.12, lw=0)
    for i, r in zip(y, ratios):
        if r is None:
            ax.text(0, i, "no margin: matched set differs across seeds", ha="center", va="center", color=INK2, fontsize=7.5)
        else:
            ax.barh(i, r, 0.55, color=ORANGE if abs(r) > 1 else "#86b6ef")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(list(y), labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("(learned mean − twin) / margin   (shaded: within the 3-seed range)")
    ax.set_title("X2: learned keys vs random-key twin, gap in units of the seed range")
    save(fig, out, "x2_gaps.png")


def main(root, out, meta_root=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    reports = load(root)
    d = digest(reports)
    (out / "digest.json").write_text(json.dumps(d, indent=1, default=str))
    fig_q2(d, out)
    fig_core_scalars(d, out)
    fig_e1(d, out)
    fig_e2(d, out)
    fig_whole_off(d, out)
    fig_x2(d, out)
    if meta_root:
        fig_official(meta_root, out)
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
