"""Score released data-v1 windows and check the adapter against native GPT inference."""

from __future__ import annotations

from collections import defaultdict

import torch

from . import q1, q2
from .q2 import fact_metrics
from .evaluation import Evaluator


# Independent forwards can select different floating-point kernels for final-only
# vs all-position logits. Report actual errors as well as testing tolerances.
ATOL = 5e-5
RTOL = 2e-5


class V1Scorer:
    """A small, fixed slice evaluated with one frozen native checkpoint."""

    def __init__(self, model, corpus, device):
        self.model = model.eval()
        self.corpus = corpus
        self.device = torch.device(device)
        self.evaluator = Evaluator(model, corpus, 1)
        self._intact = {}

    def _matrix(self, sequences):
        return torch.tensor(sequences, dtype=torch.long, device=self.device)

    @torch.inference_mode()
    def score(self, fact, mask=(), collect=False):
        """Teacher-force every candidate, tracing only the true continuation's read sites."""
        row_id = fact["row_id"]
        if not mask and not collect and row_id in self._intact:
            original, cached = self._intact[row_id]
            if fact is original:
                return list(cached), []

        candidates = fact["candidates"]
        width = len(candidates[0])
        if width not in (1, 2) or any(len(c) != width for c in candidates):
            raise ValueError(
                f"{row_id}: expected one-token candidates or month/day pairs"
            )
        prompt = fact["prompt"]
        start = len(prompt) - 1
        # All candidates sharing the same prefix have identical model input.
        # A 200-date list needs only the distinct month contexts.
        indices_by_prefix = defaultdict(list)
        for i, key in enumerate(candidates):
            indices_by_prefix[tuple(key[:-1])].append(i)
        scores = [0.0] * len(candidates)
        prefixes = list(indices_by_prefix)
        # Limit all-position vocabulary logits even when the user requests long inputs.
        batch_size = min(
            4, max(1, 2_000_000 // ((len(prompt) + width - 1) * len(self.corpus.vocab)))
        )
        for offset in range(0, len(prefixes), batch_size):
            group = prefixes[offset : offset + batch_size]
            contexts = [prompt + list(p) for p in group]
            logits, _ = self.model(self._matrix(contexts), mask=mask)
            logp = logits[:, start:, :].float().log_softmax(-1)
            for j, prefix in enumerate(group):
                index = indices_by_prefix[prefix]
                keys = self._matrix([candidates[i] for i in index])
                positions = torch.arange(width, device=self.device)
                joint = logp[j][positions, keys].sum(-1).tolist()
                for i, value in zip(index, joint, strict=True):
                    scores[i] = value

        reads = []
        if collect:
            gold_seq = prompt + candidates[fact["answer"]]
            _, trace = self.model(self._matrix([gold_seq[:-1]]), mask=mask, trace=True)
            if trace is None:
                raise ValueError("A memory layer is required to collect fact reads")
            doc = {"doc_id": row_id, "subject": "bio"}
            for pos in range(start, start + width):
                read = self.evaluator.record(doc, pos, gold_seq, trace, "fact", 0)
                read["vectors"] = read["vectors"].detach().cpu()
                reads.append(read)
        return scores, reads

    def _native_scores(self, fact):
        """Independent reference using Roie's native last-logit next-token interface."""
        keys = fact["candidates"]
        prompt = fact["prompt"]
        logits, _ = self.model.gpt(self._matrix([prompt]))
        first = torch.log_softmax(logits[0, -1].float(), dim=0)
        if len(keys[0]) == 1:
            return first[[c[0] for c in keys]].tolist()

        # Native inference never sees tokens after the prediction it is checking.
        # Score each month once and preserve the released candidate ordering.
        months = sorted(set(c[0] for c in keys))
        day_by_month = {}
        for i in range(0, len(months), 4):
            group = months[i : i + 4]
            logits, _ = self.model.gpt(self._matrix([prompt + [m] for m in group]))
            days = logits[:, -1].float().log_softmax(-1)
            day_by_month.update(zip(group, days.unbind(), strict=True))
        second = torch.stack([day_by_month[m][d] for m, d in keys])
        return (first[[c[0] for c in keys]] + second).tolist()

    @torch.inference_mode()
    def check_baselines(self):
        """Compare every selected candidate score and document loss on identical inputs."""
        self._intact.clear()
        parity = {
            "atol": ATOL,
            "rtol": RTOL,
            "candidate_scores_checked": 0,
            "max_candidate_abs_error": 0.0,
            "candidate_score_failures": 0,
            "native_rank_mismatches": 0,
            "documents_checked": 0,
            "max_doc_nll_abs_error": 0.0,
            "doc_nll_mismatches": 0,
            "doc_prediction_mismatches": 0,
        }
        documents = q1.check_documents(self, parity, ATOL, RTOL)
        facts, intact = q2.check_facts(self, parity, ATOL, RTOL)
        passed = (
            parity["documents_checked"] > 0
            and parity["candidate_scores_checked"] > 0
            and all(
                parity[k] == 0
                for k in (
                    "candidate_score_failures",
                    "native_rank_mismatches",
                    "doc_nll_mismatches",
                    "doc_prediction_mismatches",
                )
            )
        )
        if passed:
            self._intact = intact
        return {
            "passed": passed,
            "parity": parity,
            "documents": documents,
            "facts": facts,
        }
