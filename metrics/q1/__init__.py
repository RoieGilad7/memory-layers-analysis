"""Q1: next-token loss, perplexity and accuracy by subject."""

import math
from collections import defaultdict


def check_documents(scorer, parity, atol, rtol):
    documents = {}
    for split, docs in scorer.corpus.docs.items():
        if split not in ("discovery", "eval"):
            continue
        totals = defaultdict(lambda: [0, 0.0, 0])
        per_doc = []
        for doc in docs:
            seq = doc["tokens"]
            x, y = scorer._matrix([seq[:-1]]), scorer._matrix([seq[1:]])
            logits, _ = scorer.model(x)
            token_lp = logits[0].float().log_softmax(-1)
            loss_sum = float(-token_lp.gather(1, y.T).double().sum())
            pred = logits.argmax(-1)
            hits = int((pred == y).sum())
            del logits, token_lp
            native_logits, loss = scorer.model.gpt(x, targets=y)
            changed = int((native_logits.argmax(-1) != pred).sum())
            del native_logits
            n = y.numel()
            mean_nll = loss_sum / n
            native_nll = float(loss)
            if not all(map(math.isfinite, (native_nll, mean_nll))):
                raise ValueError(f"Non-finite NLL in {doc['doc_id']}")
            error = abs(mean_nll - native_nll)
            parity["documents_checked"] += 1
            parity["max_doc_nll_abs_error"] = max(
                parity["max_doc_nll_abs_error"], error
            )
            parity["doc_prediction_mismatches"] += changed
            parity["doc_nll_mismatches"] += int(error > atol + rtol * abs(native_nll))
            per_doc.append(
                {
                    "doc_id": doc["doc_id"],
                    "subject": doc["subject"],
                    "tokens": n,
                    "nll": mean_nll,
                    "native_nll": native_nll,
                    "prediction_mismatches": changed,
                }
            )
            for key in (doc["subject"], "overall"):
                acc = totals[key]
                acc[0] += n
                acc[1] += loss_sum
                acc[2] += hits
        quality = {
            s: {"tokens": n, "nll": v / n, "ppl": math.exp(v / n), "accuracy": h / n}
            for s, (n, v, h) in totals.items()
        }
        documents[split] = {
            "overall": quality.pop("overall", None),
            "by_subject": quality,
            "rows": per_doc,
        }

    return documents


def run(ctx):
    quality = ctx.baseline["documents"]["eval"]
    rows = [
        [name, r["tokens"], r["nll"], r["ppl"], r["accuracy"]]
        for name, r in [("All", quality["overall"]), *quality["by_subject"].items()]
    ]
    return dict(
        title="Next-token prediction",
        columns=["Subject", "Tokens", "NLL (nats)", "Perplexity", "Accuracy"],
        rows=rows,
        result=quality,
    )
