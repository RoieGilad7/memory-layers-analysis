"""Language modeling and fact recall with the selected memory layer suppressed."""

from collections import defaultdict
from statistics import fmean

from ..matching import gold_margin, top1_credit


def run(ctx):
    mask = range(ctx.model.memory.num_slots)
    quality = ctx.evaluator.documents("eval", mask=mask)[0]
    intact = ctx.baseline["documents"]["eval"]
    table = []
    for cohort, before, after in [
        ("All text", intact["overall"], quality["overall"]),
        *(
            (subject, intact["by_subject"][subject], after)
            for subject, after in sorted(quality["by_subject"].items())
        ),
    ]:
        table.append(
            [
                cohort,
                "NLL (nats/token)",
                before["nll"],
                after["nll"],
                after["nll"] - before["nll"],
            ]
        )
    base_rows = {r["row_id"]: r for r in ctx.baseline["facts"]["rows"]}
    groups = defaultdict(list)
    for fact in ctx.corpus.facts:
        if fact["role"] not in ("test", "paraphrase"):
            continue
        scores, _ = ctx.scorer.score(fact, mask=mask)
        answer = fact["answer"]
        row = base_rows[fact["row_id"]]
        groups[(fact["tier"], fact["role"])].append(
            (
                row["top1"],
                top1_credit(scores, answer),
                row["margin"],
                gold_margin(scores, answer),
            )
        )
    grouped = {}
    for (tier, role), rows in sorted(groups.items()):
        base_accuracy, off_accuracy, base_margin, off_margin = map(fmean, zip(*rows))
        cohort = f"{tier} / {role}"
        grouped[cohort] = dict(
            prompts=len(rows),
            intact_top1=base_accuracy,
            off_top1=off_accuracy,
            intact_margin_nats=base_margin,
            off_margin_nats=off_margin,
        )
        table.append(
            [
                cohort,
                "Top-1 accuracy",
                base_accuracy,
                off_accuracy,
                off_accuracy - base_accuracy,
            ]
        )
        table.append(
            [
                cohort,
                "Gold margin (nats)",
                base_margin,
                off_margin,
                off_margin - base_margin,
            ]
        )
    return dict(
        title="Whole-layer ablation",
        columns=["Cohort", "Measure", "Intact", "Layer off", "Change"],
        rows=table,
        result=dict(
            num_slots=ctx.model.memory.num_slots,
            intact_quality=intact,
            masked_quality=quality,
            fact_outcomes=grouped,
        ),
    )
