"""C4. Static value vectors projected onto the language model's output vocabulary."""

import torch
from ..u1 import selection_counts, text_reads


def _inspect(reads, counts, table, unembedding):
    # Limit the lens to the most often read rows so a million-slot table does
    # not require a slots-by-vocabulary matrix. Snippets use held-out inputs.
    slots = [
        s for s, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:6]
    ]
    snippets = {s: [] for s in slots}
    for read in reads:
        for slot, weight in zip(read["ids"], read["weights"]):
            if slot in snippets:
                best = snippets[slot]
                best.append(
                    dict(
                        weight=float(weight),
                        doc_id=read["doc_id"],
                        snippet=read["snippet"],
                    )
                )
                best.sort(key=lambda row: -row["weight"])
                del best[3:]
    if not slots:
        return []
    projection = (
        table[slots].detach().to(device=unembedding.device, dtype=torch.float32)
    )
    logits = projection @ unembedding.detach().float().T
    tokens = logits.topk(min(5, logits.shape[1]), dim=1).indices.cpu().tolist()
    return [
        dict(
            slot=slot,
            selections=counts[slot],
            promoted_token_ids=tokens[i],
            strongest_snippets=snippets[slot],
        )
        for i, slot in enumerate(slots)
    ]


def run(ctx):
    reads = list(text_reads(ctx.eval_reads))
    table = ctx.model.memory.value_table()
    result = _inspect(reads, selection_counts(reads), table, ctx.model.head.weight)
    rows = []
    for r in result:
        r["promoted_tokens"] = [ctx.corpus.vocab[t] for t in r["promoted_token_ids"]]
        snippet = (
            r["strongest_snippets"][0]["snippet"] if r["strongest_snippets"] else ""
        )
        rows.append(
            [
                r["slot"],
                r["selections"],
                " · ".join(repr(t) for t in r["promoted_tokens"]),
                snippet,
            ]
        )
    return dict(
        title="Static value projection",
        result=result,
        columns=["Slot", "Reads", "Highest-scoring tokens", "Highest-weight context"],
        rows=rows,
    )
