"""Model reads and token-weighted document scoring."""

from collections import Counter
import math
import torch
import torch.nn.functional as F


def padded(sequences, device, fill=0):
    batch = torch.full(
        (len(sequences), max(map(len, sequences))), fill, dtype=torch.long
    )
    for i, seq in enumerate(sequences):
        batch[i, : len(seq)] = torch.tensor(seq)
    return batch.to(device)


def batch_xy(docs, device):
    return (
        padded([d["tokens"][:-1] for d in docs], device),
        padded([d["tokens"][1:] for d in docs], device, fill=-100),
    )


class Evaluator:
    def __init__(self, model, corpus, batch_size, *, log_heads=False):
        self.model, self.corpus, self.batch_size = model, corpus, batch_size
        self.device = next(model.parameters()).device
        self.log_heads = log_heads

    def record(self, doc, pos, seq, trace, cohort, batch_idx):
        ids, weights, vectors = (part[batch_idx, pos] for part in trace)
        head_reads = {}
        if hasattr(self.model, "physical_read"):
            if self.log_heads:
                k = self.model.memory.module.topk
                head_reads = dict(
                    layer=self.model.layer_index,
                    head_ids=ids.reshape(-1, k).tolist(),
                    head_weights=weights.reshape(-1, k).tolist(),
                )
            ids, weights, vectors = self.model.physical_read(ids, weights, vectors)
        return dict(
            doc_id=doc["doc_id"],
            subject=doc.get("subject", "bio"),
            token=seq[pos],
            position=pos,
            cohort=cohort,
            ids=ids.tolist(),
            weights=weights.tolist(),
            vectors=vectors.clone(),
            **head_reads,
            snippet=" ".join(
                self.corpus.vocab[t] for t in seq[max(0, pos - 4) : pos + 1]
            ),
        )

    @torch.no_grad()
    def documents(self, split, mask=(), collect=False):
        self.model.eval()
        docs = self.corpus.docs[split]
        reads, sums, correct, counts = [], Counter(), Counter(), Counter()
        for start in range(0, len(docs), self.batch_size):
            group = docs[start : start + self.batch_size]
            x, y = batch_xy(group, self.device)
            logits, trace = self.model(x, mask=mask, trace=collect)
            nll = F.cross_entropy(logits.transpose(1, 2), y, reduction="none").cpu()
            hits = (logits.argmax(-1) == y).cpu()
            if trace is not None:
                trace = tuple(t.detach().cpu() for t in trace)
            for i, doc in enumerate(group):
                subject, seq = doc["subject"], doc["tokens"]
                count = len(seq) - 1
                counts[subject] += count
                sums[subject] += nll[i, :count].double().sum().item()
                correct[subject] += int(hits[i, :count].sum())
                if trace is not None:
                    reads.extend(
                        self.record(doc, p, seq, trace, "text", i) for p in range(count)
                    )

        def quality(total, nll, hits):
            mean = nll / total
            return dict(
                tokens=total, nll=mean, ppl=math.exp(mean), accuracy=hits / total
            )

        return (
            dict(
                overall=quality(
                    sum(counts.values()), sum(sums.values()), sum(correct.values())
                ),
                by_subject={s: quality(counts[s], sums[s], correct[s]) for s in counts},
            ),
            reads,
        )
