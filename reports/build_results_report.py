"""Results-only Phase 1 metrics report: one self-contained HTML page with figures.

    python reports/build_results_report.py runs/final reports/final_metrics_results.html
    python reports/build_results_report.py runs/final reports/final_metrics_analysis.html --analysis
    (the PDF is the --analysis page printed with headless Chrome)

Reads the final per-checkpoint reports (runs/final/cohort/<run>, runs/final/dense-s0),
the training runs' own metrics (runs/final/hf_meta/<run>) and the X2 margins.
Figures are written next to the HTML under final_metrics/results/ and embedded.
"""

import base64
import glob
import html
import io
import json
import sys
from pathlib import Path
from statistics import fmean

sys.path.insert(0, str(Path(__file__).parent))
import build_final_metrics_figures as base  # noqa: E402  (style, loaders, digest)

plt = base.plt
RUNS = ["pkm-s0", "pkm-s1", "pkm-s2", "pkm_randkey-s0", "dense-s0"]
PKM = RUNS[:4]
LEARNED = RUNS[:3]
NAME = {
    "pkm-s0": "PKM, learned keys, seed 0",
    "pkm-s1": "PKM, learned keys, seed 1",
    "pkm-s2": "PKM, learned keys, seed 2",
    "pkm_randkey-s0": "PKM, frozen random keys, seed 0",
    "dense-s0": "Dense, no memory layer",
}
SHORT = {"pkm-s0": "Learned s0", "pkm-s1": "Learned s1", "pkm-s2": "Learned s2",
         "pkm_randkey-s0": "Random keys", "dense-s0": "Dense"}
# Fixed categorical order (validated: CVD and normal-vision separation pass).
COLOR = {"pkm-s0": "#2a78d6", "pkm-s1": "#1baf7a", "pkm-s2": "#e87ba4",
         "pkm_randkey-s0": "#eb6834", "dense-s0": "#eda100"}
MARK = {"pkm-s0": "o", "pkm-s1": "s", "pkm-s2": "D", "pkm_randkey-s0": "^", "dense-s0": "v"}
SUBJECTS = base.SUBJECTS
SUBJ_KEY = {"FreeLaw": "freelaw", "Github": "github", "Pile-CC": "pile_cc",
            "PubMed Central": "pubmed_central", "Wikipedia (en)": "wikipedia_en"}
SHORT_SUBJ = {"FreeLaw": "FreeLaw", "Github": "Github", "Pile-CC": "Pile-CC",
              "PubMed Central": "PubMed", "Wikipedia (en)": "Wikipedia"}
GREEN_BG, RED_BG = "#d9f2d9", "#f8d7d7"


def png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def legend_below(ax, runs, ncol=None):
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="s", ls="", ms=9, color=COLOR[r], label=NAME[r]) for r in runs]
    ax.figure.legend(handles=handles, loc="lower center", ncol=ncol or len(runs),
                     bbox_to_anchor=(0.5, -0.02), fontsize=8, frameon=False)


def grouped_bars(ax, groups, runs, value, width=None, label_fmt=None):
    width = width or 0.8 / len(runs)
    for j, r in enumerate(runs):
        xs = [i + (j - (len(runs) - 1) / 2) * width for i in range(len(groups))]
        vals = [value(r, g) for g in groups]
        ax.bar([x for x, v in zip(xs, vals) if v is not None], [v for v in vals if v is not None],
               width * 0.88, color=COLOR[r])
        for x, v in zip(xs, vals):
            if v is None:
                ax.text(x, 0, "n/a", ha="center", va="bottom", fontsize=6.5, color=base.INK2, rotation=90)
            elif label_fmt:
                ax.text(x, v, label_fmt(v), ha="center", va="bottom", fontsize=6, color=base.INK2, rotation=90)
    ax.set_xticks(range(len(groups)))


def dots(ax, x, runs, value, spread=0.12):
    for j, r in enumerate(runs):
        v = value(r)
        if v is None:
            continue
        ax.scatter([x + (j - (len(runs) - 1) / 2) * spread], [v], s=55, marker=MARK[r],
                   color=COLOR[r], edgecolor=base.SURFACE, linewidth=1.2, zorder=3)


def main(root, dest, analysis=False):
    root, dest = Path(root), Path(dest)
    reports = base.load(root / "cohort")
    d = base.digest(reports)
    dense = json.loads(Path(glob.glob(str(root / "dense-s0" / "step_*.json"))[0]).read_text())
    off = {r: json.loads((root / "hf_meta" / r / "final_metrics.json").read_text())["metrics"] for r in RUNS}
    chk = {r: json.loads((root / "hf_meta" / r / "training_check.json").read_text()) for r in RUNS}
    x2 = d["x2"]["metrics"]
    figs = {}

    # Q1: all five models, one panel per subject (each panel has its own y-range).
    groups = ["pile_avg"] + [SUBJ_KEY[s] for s in SUBJECTS]
    titles = ["Average (5 subjects)"] + [SHORT_SUBJ[s] for s in SUBJECTS]
    fig, axes = plt.subplots(1, 6, figsize=(12, 3.4))
    for ax, g, t in zip(axes, groups, titles):
        for j, r in enumerate(RUNS):
            v = off[r][f"heldout_quality/loss/{g}"]
            ax.bar(j, v, 0.8, color=COLOR[r])
        vals = [off[r][f"heldout_quality/loss/{g}"] for r in RUNS]
        lo, hi = min(vals), max(vals)
        ax.set_ylim(lo - (hi - lo) * 1.2, hi + (hi - lo) * 0.4)
        ax.set_xticks([])
        ax.set_title(t, fontsize=9.5)
    axes[0].set_ylabel("Held-out loss (nats/token)\nlower is better")
    fig.suptitle("Q1: next-token loss on held-out text (y-axis zoomed per panel)", fontsize=11, fontweight="bold", y=1.02)
    legend_below(axes[0], RUNS, ncol=3)
    fig.subplots_adjust(bottom=0.28, wspace=0.55)
    figs["q1"] = png(fig)

    # Q2: one chart, all five models, by exposure tier and wording.
    combos = [("frequent", "test"), ("normal", "test"), ("rare", "test"), ("control", "test"),
              ("frequent", "paraphrase"), ("normal", "paraphrase")]
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    grouped_bars(ax, combos, RUNS, lambda r, c: off[r].get(f"fact_recall/top1/{c[0]}/{c[1]}"))
    ax.set_xticklabels([f"{t}\n{'training wording' if w == 'test' else 'new wording'}" for t, w in combos])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Top-1 accuracy\n(true value ranked first)")
    ax.set_title("Q2: fact recall by how often the person was seen in training")
    legend_below(ax, RUNS, ncol=3)
    fig.subplots_adjust(bottom=0.32)
    figs["q2"] = png(fig)

    # Main memory metrics, PKM runs: one panel per metric (different units), same colors.
    items = [
        ("U4 excess (bits)", lambda r: d[r]["u4"]["excess_bits"]),
        ("E1 at m = 64 (nats)", lambda r: d[r]["e1_mean"]["64"]),
        ("V2 largest-value share, text", lambda r: d[r]["v2"]["Subject text"]["top1"]),
        ("V2 largest-value share, facts", lambda r: d[r]["v2"]["Fact probes"]["top1"]),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.4))
    for ax, (title, get) in zip(axes, items):
        vals = [get(r) for r in LEARNED]
        ax.axhspan(min(vals), max(vals), color="#2a78d6", alpha=0.10, lw=0)
        dots(ax, 0, PKM, get, spread=0.18)
        ax.set_xticks([])
        ax.set_xlim(-0.6, 0.6)
        ax.set_title(title, fontsize=9.5)
        ax.margins(y=0.25)
    legend_below(axes[0], PKM, ncol=4)
    fig.text(0.5, 0.15, "Shaded band: lowest to highest of the three learned-key seeds", ha="center", color=base.INK2, fontsize=8)
    fig.subplots_adjust(bottom=0.3, wspace=0.5)
    figs["core"] = png(fig)

    # E1: two clear panels.
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1, 1.6]})
    ax = axes[0]
    sizes = ["16", "64", "256"]
    for r in PKM:
        ax.plot(range(3), [d[r]["e1_mean"][s] for s in sizes], color=COLOR[r], lw=2, marker=MARK[r], ms=6)
    ax.set_xticks(range(3), ["16 slots", "64 slots", "256 slots"])
    ax.set_xlabel("Number of the subject's top slots switched off")
    ax.set_ylabel("Extra loss on the subject vs others,\nbeyond matched random slots (nats)")
    ax.set_title("E1: average over subjects", fontsize=10)
    ax = axes[1]
    grouped_bars(ax, SUBJECTS, PKM, lambda r, s: d[r]["e1_by_subject"].get(s))
    ax.set_xticklabels([SHORT_SUBJ[s] for s in SUBJECTS])
    ax.set_title("E1 per subject, 64 slots off\n(n/a = no matched random slots found)", fontsize=10)
    ax.set_ylabel("nats")
    legend_below(axes[0], PKM, ncol=4)
    fig.subplots_adjust(bottom=0.3, wspace=0.3)
    figs["e1"] = png(fig)

    # E2 outcome per fact.
    order = [("matched", "Fact erased; random-slot control done", "#2a78d6"),
             ("no_matched_controls", "Fact erased; no random-slot control found", "#86b6ef"),
             ("prefix_limit_reached", "Fact not erased by its top 16 slots", "#c3c2b7")]
    fig, ax = plt.subplots(figsize=(8.5, 2.9))
    for i, r in enumerate(PKM):
        left, counts = 0, d[r]["e2"]["status_counts"]
        for key, label, color in order:
            n = counts.get(key, 0)
            ax.barh(i, n, left=left, color=color, edgecolor=base.SURFACE, linewidth=2, label=label if i == 0 else None)
            ax.text(left + n / 2, i, str(n), ha="center", va="center", fontsize=8,
                    color=base.SURFACE if key == "matched" else base.INK)
            left += n
    ax.set_yticks(range(len(PKM)), [NAME[r] for r in PKM])
    ax.invert_yaxis()
    ax.set_xlabel("Facts (339 facts known by all four PKM models)")
    ax.set_title("E2: switching off the slots a fact reads, up to 16 slots")
    ax.legend(loc="upper center", bbox_to_anchor=(0.4, -0.3), ncol=2, fontsize=7.5)
    figs["e2"] = png(fig)

    # V2 and U4 shares as grouped bars (PKM only).
    fig, ax = plt.subplots(figsize=(8, 3.4))
    v2groups = [("Subject text", "top1"), ("Subject text", "top2"), ("Fact probes", "top1"), ("Fact probes", "top2")]
    grouped_bars(ax, v2groups, PKM, lambda r, g: d[r]["v2"][g[0]][g[1]])
    ax.set_xticklabels(["largest value\n(held-out text)", "two largest\n(held-out text)",
                        "largest value\n(fact prompts)", "two largest\n(fact prompts)"])
    ax.set_ylabel("Share of the read's output")
    ax.set_title("V2: how much of a memory read comes from its largest values")
    legend_below(ax, PKM, ncol=2)
    fig.subplots_adjust(bottom=0.33)
    figs["v2"] = png(fig)

    # Whole layer off.
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    cohorts = ["All text"] + SUBJECTS
    grouped_bars(ax, cohorts, PKM, lambda r, c: d[r]["whole_off"][c])
    ax.set_xticklabels(["All"] + [SHORT_SUBJ[s] for s in SUBJECTS])
    ax.set_ylabel("Loss increase (nats per token)")
    ax.set_title("Whole memory layer switched off: loss increase")
    legend_below(ax, PKM, ncol=2)
    fig.subplots_adjust(bottom=0.33)
    figs["off"] = png(fig)

    # X2: learned range vs twin, one small panel per metric.
    paths = [p for p, v in x2.items() if v["margin"] is not None]
    nice = {
        "Q1.overall.ppl": "Q1 perplexity (slice)", "U4.excess_bits": "U4 excess (bits)",
        "V2.text.top1_share": "V2 largest value, text", "V2.text.top2_share": "V2 two largest, text",
        "V2.text.cosine_excess": "V2 alignment, text", "V2.fact.top1_share": "V2 largest value, facts",
        "V2.fact.top2_share": "V2 two largest, facts", "V2.fact.cosine_excess": "V2 alignment, facts",
        "E1.mean_specificity_excess_nll": "E1 at 64 slots (nats)", "E2.mean_matched_core_fraction": "E2 core fraction",
    }
    fig, axes = plt.subplots(2, 4, figsize=(11, 5))
    for ax, p in zip(axes.flat, paths):
        v = x2[p]
        mean, margin, twin = v["learned_mean"], v["margin"], v["twin_value"]
        ax.axhspan(mean - margin, mean + margin, color=GREEN_BG, lw=0)
        ax.axhline(mean, color="#2a78d6", lw=1.5)
        for j, r in enumerate(LEARNED):
            ax.scatter([-0.15 + j * 0.15], [v["learned_values"][j]], marker=MARK[r], color=COLOR[r], s=40, zorder=3)
        ax.scatter([0.6], [twin], marker="^", s=70, color=COLOR["pkm_randkey-s0"], zorder=3)
        ax.set_xlim(-0.5, 1.0)
        ax.set_xticks([0, 0.6], ["learned", "random"])
        ax.set_title(nice[p] + ("  (inside)" if v["within_margin"] else "  (outside)"), fontsize=8.5)
        ax.margins(y=0.2)
    legend_below(axes[1, 0], PKM, ncol=4)
    fig.text(0.5, 0.045, "Blue line: learned-key mean.  Green band: mean ± the learned seeds' full range (the X2 margin).", ha="center", color=base.INK2, fontsize=8)
    fig.subplots_adjust(bottom=0.16, hspace=0.45, wspace=0.4)
    figs["x2"] = png(fig)

    # ---------- HTML ----------
    def num(v, f="{:.3f}"):
        return "—" if v is None else f.format(v)

    def table(head, rows, cls=None):
        h = "".join(f"<th>{html.escape(x)}</th>" for x in head)
        body = ""
        for r in rows:
            cells = ""
            for c in r:
                if isinstance(c, tuple):  # (text, background)
                    cells += f'<td style="background:{c[1]}">{c[0]}</td>'
                else:
                    cells += f"<td>{c}</td>"
            body += f"<tr>{cells}</tr>"
        return f"<table><tr>{h}</tr>{body}</table>"

    def img(key):
        return f'<img src="data:image/png;base64,{figs[key]}">'

    def learned_col(f, fmt="{:.4f}"):
        vals = [f(r) for r in LEARNED]
        vals = [v for v in vals if v is not None]
        return f"{fmt.format(fmean(vals))} [{fmt.format(min(vals))}, {fmt.format(max(vals))}]"

    H = []
    H.append("<h1>Phase 1 metric results</h1>")
    H.append("<p>Final checkpoints (training step 9,156, about 150M training tokens each). Results only; each section says what the metric measures. Raw values: <code>final_metrics_raw_results.csv</code>.</p>")
    H.append("<h2>The five models</h2>")
    H.append(table(["Model", "What it is"], [
        [NAME["pkm-s0"] + ", seed 1, seed 2", "The main model: a 6-layer GPT with a product-key memory (PKM) layer at layer 3. Each token's query is matched against learned <b>keys</b>; the best-matching slots are read and their <b>values</b> are added to the token's representation. Keys, queries and values all train. Three training seeds."],
        [NAME["pkm_randkey-s0"], "Same as the main model, but the keys are frozen at their random starting values. Queries and values still train, so the model can still use the memory but cannot move the keys."],
        [NAME["dense-s0"], "Same network with an ordinary feed-forward layer at layer 3 instead of the memory, sized for the same compute per token."],
    ]))
    H.append("<h2>Where the numbers come from</h2>")
    H.append("<ul>"
             "<li><b>Held-out text.</b> For each of the five Pile subjects (FreeLaw, Github, Pile-CC, PubMed Central, Wikipedia), a set of documents was kept out of training entirely. It is split into two halves: a <i>discovery</i> half, used only to choose slots (U4 ranking for E1), and a <i>test</i> half, used to score (Q1, E1). A test never reuses text that chose its slots.</li>"
             "<li><b>Biographies.</b> Made-up people with five facts each (birth date, birth city, university, major, employer). People are in four exposure tiers by how often their biography appeared in training: <i>frequent</i> (~300 copies), <i>normal</i> (~100), <i>rare</i> (~30), <i>control</i> (never). Each fact has 8 prompts: 2 discovery and 2 test prompts in training wordings, and 4 paraphrase prompts in wordings never used in training.</li>"
             "<li><b>Official</b> numbers (Q1, Q2) are each training run's own final evaluation: the whole test half (about 2.5M tokens per subject) and every person.</li>"
             "<li><b>Slice</b> numbers (everything else) come from <code>metrics.py</code> on a fixed sample, the same for every model: 64 test-half documents per subject, first 256 tokens of each (about 72k tokens in all); 80 frequent people and 10 per other tier (all 8 prompts of every fact). The slice is smaller because the removal tests (E1, E2) rerun the model many times.</li>"
             "<li><b>\"Learned seeds: mean [min, max]\"</b> column = the average of the three learned-key models (seeds 0, 1, 2), with the lowest and highest of the three in brackets.</li></ul>")

    H.append("<h2>Training check</h2>")
    H.append("<p>Each run's own check before analysis, from its training log. Cell = the measured value; green = within the required limit, red = outside it, grey = not evaluated.</p>")
    def cell(k, rule):
        if k == "finite":
            return "no NaN/inf" if rule["first_bad_train_step"] is None and not rule["bad_eval"] else f"bad at step {rule['first_bad_train_step']}"
        if k == "no_divergence":
            return f"{rule['worst_ratio_to_running_min']:.3f}× at step {rule['at_step']:,}"
        if k == "learned":
            return f"{rule['init_loss']:.2f} → {rule['final_loss']:.2f} (−{rule['drop']:.1%})"
        if k == "not_rising":
            return f"{rule['excess']:.3f} above its minimum"
        if k == "coverage":
            return ", ".join(f"{v:.0%}" for v in rule["coverage"].values())
        if k == "fact_learning":
            return f"{rule['frequent_test_top1']:.3f} vs {rule['control_test_top1']:.4f} ({rule['ratio']:.0f}×)"
        if k == "flattening":
            return f"{rule['last_interval_relative_drop']:.1%} drop over steps {rule['last_interval'][0]:,}–{rule['last_interval'][1]:,}"
        return ""
    checks = [
        ("finite", "Losses finite"),
        ("no_divergence", "Worst training-loss spike ÷ running minimum (limit 1.5)"),
        ("learned", "Loss at start → end of training (needs ≥ 40% drop)"),
        ("not_rising", "Final held-out loss above its lowest value (limit 0.005)"),
        ("coverage", "Memory slots used (needs ≥ 80%)"),
        ("fact_learning", "Fact recall, frequent vs control (needs ≥ 2×)"),
        ("flattening", "Held-out loss drop in the last stretch (informational)"),
    ]
    rows = []
    for k, label in checks:
        row = [label]
        for r in RUNS:
            rule = chk[r]["rules"].get(k)
            if rule is None or "why" in rule:
                row.append(((rule or {}).get("why", "not applicable"), "#f0efec"))
                continue
            bg = "#f0efec" if rule.get("pass") is None else (GREEN_BG if rule["pass"] else RED_BG)
            row.append((cell(k, rule), bg))
        rows.append(row)
    H.append(table(["Check"] + [SHORT[r] for r in RUNS], rows))

    H.append("<h2>Q1: next-token quality on held-out text</h2>")
    H.append("<p><b>What it measures.</b> How well each model predicts the next token in text it never trained on: the average loss (negative log-probability of the true next token, in nats; lower is better), per subject and averaged. Perplexity is e<sup>loss</sup>. Official numbers: whole test half, ~2.5M tokens per subject.</p>")
    H.append(img("q1"))
    rows = []
    for g, label in [("pile_avg", "Average (5 subjects)")] + [(SUBJ_KEY[s], s) for s in SUBJECTS]:
        rows.append([label] + [f"{off[r][f'heldout_quality/loss/{g}']:.3f}" for r in RUNS])
    rows.append(["Average perplexity"] + [f"{off[r]['heldout_quality/ppl/pile_avg']:.2f}" for r in RUNS])
    rows.append(["Average next-token top-1 accuracy"] + [f"{off[r]['heldout_quality/top1/pile_avg']:.4f}" for r in RUNS])
    rows.append(["USPTO loss (subject never in training)"] + [f"{off[r]['heldout_quality/loss/uspto_backgrounds']:.3f}" for r in RUNS])
    H.append(table(["Official held-out loss"] + [SHORT[r] for r in RUNS], rows))

    H.append("<h2>Q2: fact recall</h2>")
    H.append("<p><b>What it measures.</b> The model gets a biography sentence cut just before a fact (\"… was born in\") and scores every possible value of that attribute (100–300 candidates: 200 birth dates, 200 cities, 300 universities, 100 majors, 250 employers). <b>Top-1 accuracy</b>: how often the true value scores highest. <b>Mean rank</b>: the true value's average position in that ranked list (1 = top; about half the list size = no knowledge). Training wording = the 2 test prompts; new wording = the 4 paraphrase prompts.</p>")
    H.append(img("q2"))
    rows = []
    for t in ["frequent", "normal", "rare", "control"]:
        for w in ["test", "paraphrase"]:
            rows.append([f"{t}, {'training wording' if w == 'test' else 'new wording'}"] +
                        [f"{off[r][f'fact_recall/top1/{t}/{w}']:.3f} (rank {off[r][f'fact_recall/rank/{t}/{w}']:.1f})" for r in RUNS])
    H.append(table(["Official top-1 (mean rank)"] + [SHORT[r] for r in RUNS], rows))

    H.append("<h2>U1: how many memory slots are used (diagnostic)</h2>")
    H.append("<p><b>What it measures.</b> The memory has 65,536 slots; each token reads 128 of them (32 per head, 4 heads). On the slice text: the share of slots read at least once, the share that is ever a token's single highest-weighted slot, and the KL divergence of the read distribution from perfectly even use (0 = even).</p>")
    H.append(table(["", *[SHORT[r] for r in PKM]], [
        ["Slots read at least once"] + [f"{d[r]['u1']['coverage']:.2%}" for r in PKM],
        ["Slots ever ranked first"] + [f"{d[r]['u1']['top1_coverage']:.1%}" for r in PKM],
        ["KL to even use (bits)"] + [f"{d[r]['u1']['kl_bits']:.3f}" for r in PKM],
    ]))

    H.append("<h2>U4: do slots specialize by subject?</h2>")
    H.append("<p><b>What it measures.</b> Whether knowing <i>which slot was read</i> tells you <i>which subject the text is from</i>, beyond what the token itself already tells you. Many words are typical of one subject (e.g. <code>def</code> in Github), so a slot that simply serves that word would look subject-specific. U4 removes that by comparing reads <b>of the same token</b> across subjects.</p>")
    H.append("<p><b>Example.</b> Take the token <code> court</code>. Suppose it appears in FreeLaw and in Wikipedia text. If in FreeLaw documents it mostly reads slots {12, 870, 4031} and in Wikipedia documents mostly {55, 902, 7718}, then the slot reveals the subject even though the token is the same: high U4. If it reads the same slots wherever it appears, U4 is zero for that token. U4 averages this over all tokens, as the mutual information between slot and subject given the token (bits).</p>")
    H.append("<p><b>Shuffle baseline.</b> Even with no specialization the estimate is above zero by chance. So the subject labels are shuffled between whole documents 99 times and U4 recomputed each time. <b>Excess</b> = real value − shuffle average. p = share of shuffles at least as high as the real value (0.01 = none of 99).</p>")
    H.append("<p>Rows of the table:</p><ul>"
             "<li><b>U4, real</b>: the slot–subject mutual information given the token, measured with the true subject labels.</li>"
             "<li><b>U4, shuffled average</b>: the same quantity after randomly reassigning subject labels between whole documents, averaged over 99 shuffles. This is what chance alone gives.</li>"
             "<li><b>Excess</b>: real − shuffled average. The part of U4 that is due to actual subject specialization.</li>"
             "<li><b>p</b>: share of the 99 shuffles that reached the real value or higher (plus one, divided by 100). 0.01 means no shuffle reached it.</li></ul>")
    H.append(table(["", *[SHORT[r] for r in PKM], "Learned seeds: mean [min, max]"], [
        ["U4, real (bits)"] + [f"{d[r]['u4']['mi_bits']:.3f}" for r in PKM] + [learned_col(lambda r: d[r]["u4"]["mi_bits"], "{:.3f}")],
        ["U4, shuffled average (bits)"] + [f"{d[r]['u4']['shuffle_bits']:.3f}" for r in PKM] + [learned_col(lambda r: d[r]["u4"]["shuffle_bits"], "{:.3f}")],
        ["<b>Excess (bits)</b>"] + [f"{d[r]['u4']['excess_bits']:.4f}" for r in PKM] + [learned_col(lambda r: d[r]["u4"]["excess_bits"])],
        ["p (99 shuffles)"] + [f"{d[r]['u4']['p']:.2f}" for r in PKM] + [""],
    ]))
    H.append(img("core"))

    e1x = reports["pkm-s0"]["metrics"]["E1"]["result"]["subjects"]["FreeLaw"]
    others = [v for s, v in e1x["delta_nll_by_subject"].items() if s != "FreeLaw"]
    H.append("<h2>E1: switching off a subject's slots</h2>")
    H.append("<p><b>What it measures.</b> Whether a subject's own slots matter more to that subject than to the others. For each subject: take its m most subject-specific slots (ranked on the discovery half), switch them off (value set to zero), and measure on the test half how much the loss rises on <i>that</i> subject minus how much it rises on the <i>other</i> subjects. Then do the same with m random slots chosen to match the real ones in how often they are read and how large their output is. Reported: real − random. Above zero = the subject depends on its own slots more than chance.</p>")
    H.append(f"<p><b>Example (learned s0, FreeLaw, m = 64).</b> Switching off FreeLaw's top 64 slots raised FreeLaw's loss by {e1x['delta_nll_by_subject']['FreeLaw']:.4f} nats/token and the other subjects' by {fmean(others):+.4f} on average, a gap of {e1x['target_minus_other_nll']:.4f}. Three matched random sets of 64 slots gave an average gap of {e1x['target_minus_other_nll'] - e1x['specificity_excess_nll']:.4f}. Result: {e1x['specificity_excess_nll']:.4f} nats.</p>")
    H.append("<p>Run at m = 16, 64 (main) and 256 slots. \"n/a\" = no set of random slots matched that subject's slots closely enough, so that subject has no result for that model and is left out of its average.</p>")
    H.append(img("e1"))
    H.append(table(["Average over subjects (nats)", *[SHORT[r] for r in PKM], "Learned seeds: mean [min, max]"], [
        [f"{m} slots"] + [f"{d[r]['e1_mean'][m]:.4f}" for r in PKM] + [learned_col(lambda r, m=m: d[r]["e1_mean"][m])] for m in ["16", "64", "256"]
    ] + [["Subjects with a result (64 slots)"] + [str(d[r]["e1_matched"]["64"]) for r in PKM] + [""]]))
    H.append(table(["Per subject, 64 slots (nats)", *[SHORT[r] for r in PKM]], [
        [s] + [num(d[r]["e1_by_subject"].get(s), "{:.4f}").replace("—", "n/a") for r in PKM] for s in SUBJECTS
    ]))
    H.append("<p>Sampling note: in the sample-size pilot, redrawing the documents moved the 64-slot value by about 1/2.3 of the smallest seed value, so part of the spread between seeds is sampling noise.</p>")

    H.append("<h2>E2: are single facts stored in a few slots?</h2>")
    H.append("<p><b>What it measures.</b> For each fact, the slots its prompts read are switched off one at a time, most-used first, until the model's recall of that fact on the test prompts drops to chance, up to 16 slots. If that happens, those slots are the fact's <b>core set</b>; <b>core fraction</b> = core set size ÷ slots the fact reads. As a check, the same number of random slots from the fact's own reads (matched for read count and output size) are switched off instead; <b>control erasure rate</b> = how often that also erases the fact. Run on the 339 facts that all four PKM models recall, so every model is tested on the same facts.</p>")
    H.append("<p>Each of the 339 facts ends in one of three outcomes (bars and first three table rows):</p><ul>"
             "<li><b>Fact erased, control done</b>: switching off some of the fact's slots (16 or fewer) made the model lose the fact, and we could also find a matching set of random slots (same number, similar read counts and output sizes, taken from the fact's own reads) to switch off for comparison. Only these facts get a core fraction and a control erasure rate.</li>"
             "<li><b>Fact erased, no control found</b>: the fact was lost within 16 slots, but no matching random set could be found (the core slots were unusually busy or large compared with the fact's other slots), so there is no comparison for it.</li>"
             "<li><b>Not erased within 16 slots</b>: the 16 most-used slots were switched off and the model still recalled the fact above chance. The search stops at 16, so these facts' core sets, if any, are larger than 16 slots.</li>"
             "<li><b>Core fraction</b>: for facts in the first group, the number of slots that erased the fact ÷ the number of slots the fact reads, averaged.</li>"
             "<li><b>Control erasure rate</b>: for the same facts, how often switching off the matched random slots also erased the fact.</li></ul>")
    H.append(img("e2"))
    H.append(table(["", *[SHORT[r] for r in PKM], "Learned seeds: mean [min, max]"], [
        ["Fact erased, control done"] + [str(d[r]["e2"]["matched"]) for r in PKM] + [learned_col(lambda r: d[r]["e2"]["matched"], "{:.0f}")],
        ["Fact erased, no control found"] + [str(d[r]["e2"]["status_counts"].get("no_matched_controls", 0)) for r in PKM] + [learned_col(lambda r: d[r]["e2"]["status_counts"].get("no_matched_controls", 0), "{:.0f}")],
        ["Not erased within 16 slots"] + [str(d[r]["e2"]["status_counts"].get("prefix_limit_reached", 0)) for r in PKM] + [learned_col(lambda r: d[r]["e2"]["status_counts"].get("prefix_limit_reached", 0), "{:.0f}")],
        ["Core fraction (erased facts with control)"] + [f"{d[r]['e2']['core_fraction']:.3f}" for r in PKM] + [learned_col(lambda r: d[r]["e2"]["core_fraction"], "{:.3f}")],
        ["Control erasure rate"] + [f"{d[r]['e2']['erasure_rate']:.3f}" for r in PKM] + [learned_col(lambda r: d[r]["e2"]["erasure_rate"], "{:.3f}")],
    ]))
    H.append("<p>Sampling note: in the pilot, E2's sampling spread was larger than a third of its seed spread (about 1.6×).</p>")

    H.append("<h2>V2: is a read dominated by one value?</h2>")
    H.append("<p><b>What it measures.</b> A memory read adds up 128 weighted values. V2 asks how much of that sum comes from the largest single value (and the two largest), as a share of the output, on held-out text and on fact prompts. It also measures whether values read together point in similar directions: mean cosine between co-read values minus that of random pairs with the same sizes (<b>alignment</b>; 0 = no more aligned than chance).</p>")
    H.append(img("v2"))
    H.append(table(["", *[SHORT[r] for r in PKM], "Learned seeds: mean [min, max]"], [
        [lab] + [f"{d[r]['v2'][c][k]:.4f}" for r in PKM] + [learned_col(lambda r, c=c, k=k: d[r]["v2"][c][k])]
        for lab, c, k in [("Largest value share, text", "Subject text", "top1"), ("Two largest share, text", "Subject text", "top2"),
                          ("Alignment, text", "Subject text", "paired_excess"), ("Largest value share, facts", "Fact probes", "top1"),
                          ("Two largest share, facts", "Fact probes", "top2"), ("Alignment, facts", "Fact probes", "paired_excess")]
    ]))

    H.append("<h2>X2: learned keys vs frozen random keys</h2>")
    H.append("<p><b>What it measures.</b> Whether learning the keys changes the main results. We have three learned-key seeds but only one random-key model, so the comparison uses the seeds' own variation as the yardstick: for each metric, the <b>margin</b> is the full range of the three learned seeds (highest − lowest), fixed before the random-key model was scored. If the random-key value is within one margin of the learned mean, it counts as <b>inside</b> (no difference larger than seed-to-seed variation); otherwise <b>outside</b>.</p>")
    H.append(f"<p><b>Example (U4 excess).</b> Learned seeds 0.1689, 0.1835, 0.1651: mean {x2['U4.excess_bits']['learned_mean']:.4f}, margin {x2['U4.excess_bits']['margin']:.4f}. Random keys {x2['U4.excess_bits']['twin_value']:.4f}, which is {x2['U4.excess_bits']['learned_minus_twin']:.4f} below the mean, more than one margin, so: outside.</p>")
    H.append("<p>E1 and E2 have no margin: each seed's E1 average is over a different set of subjects (s1 lacks FreeLaw, s2 lacks Github), and each seed's E2 average is over a different set of erased facts, so the seeds' values are not directly comparable.</p>")
    H.append(img("x2"))
    rows = []
    for p, v in x2.items():
        if v["margin"] is None:
            rows.append([nice[p], "—", num(v["twin_value"], "{:.4f}"), "—", ("no margin", "#f0efec")])
        else:
            rows.append([nice[p], f"{v['learned_mean']:.4f}", f"{v['twin_value']:.4f}", f"{v['margin']:.4f}",
                         ("inside" if v["within_margin"] else "outside", GREEN_BG if v["within_margin"] else RED_BG)])
    H.append(table(["Metric", "Learned mean", "Random keys", "Margin", "Random keys vs learned"], rows))

    H.append("<h2>Diagnostics</h2>")
    H.append("<p><b>C6, effective rank of the stored values.</b> How many independent directions the memory's values span (out of 384 possible), from the spread of their singular values. Compared with the dense model's feed-forward output matrix at the same number of rows (896).</p>")
    c6 = reports["pkm-s0"]["metrics"]["C6"]["result"]
    pass1 = json.loads(Path(glob.glob(str(root / "pkm-s0" / "step_*.json"))[0]).read_text())["metrics"]["C6"]["result"]
    H.append(table(["", *[SHORT[r] for r in PKM]], [
        ["All read slots"] + [f"{d[r]['c6']['active']:.1f}" for r in PKM],
        ["512 most-read slots"] + [f"{d[r]['c6']['top512']:.1f}" for r in PKM],
    ]))
    H.append(f"<p>At 896 rows: learned s0 values {pass1['memory_rank_at_comparable_rows']:.1f}, dense feed-forward matrix {pass1['dense_rank_at_comparable_rows']:.1f}.</p>")
    H.append("<p><b>C4, what the busiest slots write.</b> For learned s0's six most-read slots, the tokens each value pushes up most when passed through the output layer:</p>")
    H.append(table(["Slot", "Reads", "Tokens pushed up most"], [
        [str(r[0]), f"{r[1]:,}", html.escape(r[2])] for r in reports["pkm-s0"]["metrics"]["C4"]["rows"]
    ]))
    H.append("<p><b>Whole memory layer off.</b> How it is done: in the trained model, every one of the 65,536 memory slots is switched off at once, the same way single slots are switched off in E1 and E2 (the slot's value is set to zero after the key search, so each read returns zero). The memory layer then adds nothing to a token's representation; every other layer is unchanged and nothing is retrained. The slice text (Q1) and the test and new-wording fact prompts (Q2) are run again and compared with the intact model on the same inputs. Change = switched-off minus intact.</p>")
    H.append(img("off"))
    H.append(table(["", *[SHORT[r] for r in PKM]], [
        ["Loss increase, all text (nats)"] + [f"{d[r]['whole_off']['All text']:.3f}" for r in PKM],
        ["Frequent, training wording: top-1 before → after"] + [f"{d[r]['whole_off_recall']['frequent / test'][0]:.3f} → {d[r]['whole_off_recall']['frequent / test'][1]:.3f}" for r in PKM],
    ]))
    res = {r: {row[0]: row[1] for row in (dense if r == "dense-s0" else reports[r])["metrics"]["Resources"]["rows"]} for r in ["pkm-s0", "dense-s0"]}
    H.append("<p><b>Resources</b> (batch-one prefill on an Apple-silicon GPU; indicative only).</p>")
    H.append(table(["", SHORT["pkm-s0"], SHORT["dense-s0"]], [
        ["Checkpoint size (MiB)", f"{res['pkm-s0']['Checkpoint']:.1f}", f"{res['dense-s0']['Checkpoint']:.1f}"],
        ["Memory parameters (MiB)", f"{res['pkm-s0']['Memory parameters']:.1f}", "0"],
        ["Prefill latency (ms)", f"{res['pkm-s0']['Prefill latency']:.2f}", f"{res['dense-s0']['Prefill latency']:.2f}"],
        ["Prefill throughput (tokens/s)", f"{res['pkm-s0']['Prefill throughput']:,.0f}", f"{res['dense-s0']['Prefill throughput']:,.0f}"],
    ]))

    if analysis:
        import results_analysis as A
        out, current = [], None

        def block(key):
            paras = A.SECTIONS.get(key)
            if not paras:
                return ""
            body = "".join(p if p.startswith("<ul>") else f"<p>{p}</p>" for p in paras)
            return f'<div class="analysis"><h3>Analysis</h3>{body}</div>'

        for part in H:
            if part.startswith("<h2>"):
                if current:
                    out.append(block(current))
                title = part[4:]
                current = next((k for k in A.SECTIONS if title.startswith(k)), None)
            out.append(part)
        if current:
            out.append(block(current))
        for title, paras in A.OVERALL:
            out.append(f'<h2>{title}</h2><div class="analysis">' + "".join(p if p.startswith("<ul>") else f"<p>{p}</p>" for p in paras) + "</div>")
        H = out
        H[0] = "<h1>Phase 1 metric results, with analysis</h1>"
        H[1] = H[1].replace("Results only; each section says what the metric measures.", "Each section says what the metric measures, gives the results, and ends with an analysis (blue box). The overall view is at the end.")

    css = ("body{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:1050px;margin:2em auto;padding:0 1em;"
           "color:#0b0b0b;background:#fcfcfb;line-height:1.5}table{border-collapse:collapse;margin:1em 0;font-size:13px}"
           "td,th{border:1px solid #e4e3df;padding:4px 8px;text-align:left;vertical-align:top}th{background:#f0efec}"
           "img{max-width:100%;margin:1em 0}code{background:#f0efec;padding:1px 4px;border-radius:3px;font-size:12px}"
           "h1{font-size:24px}h2{margin-top:1.8em;border-bottom:1px solid #e4e3df}"
           ".analysis{background:#eef4fc;border-left:4px solid #2a78d6;padding:0.4em 1em;margin:1em 0}"
           ".analysis h3{margin:0.4em 0;font-size:15px;color:#1c5cab}"
           "*{-webkit-print-color-adjust:exact;print-color-adjust:exact}@media print{body{max-width:none;margin:0;background:#fff}h2{break-after:avoid}img,table,.analysis{break-inside:avoid}}")
    dest.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Phase 1 metric results</title>'
                    f"<style>{css}</style></head><body>" + "\n".join(H) + "</body></html>")
    print(dest)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "--analysis")
