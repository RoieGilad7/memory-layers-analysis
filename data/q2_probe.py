"""Fact-recall scorer -- **a data check, not the metric**.

The metrics owner owns the real fact-recall evaluation. This exists only to
answer one question about the *data*: are the biography facts learnable at all
at this exposure budget? If they are not, no amount of memory-layer analysis
downstream will find anything, and the data has to change before training
starts. Nothing here should be imported by the analysis code; when the real
scorer lands, delete this.

Method, from the fixed design: for each `facts.jsonl` row, feed `prompt` and
rank every candidate value of that attribute by its first GPT-2 token. Dates
cannot be ranked on one token -- 200 dates share twelve month tokens (prompt
2 §6) -- so a date is ranked on the sum of its first two tokens'
log-probabilities, which is the exact joint `log p(month) + log p(day | month)`
because `(month, day)` pairs are unique.

    from data.q2_probe import ProbeSet
    probe = ProbeSet.build(cfg, rows)         # tokenizes the prompts once
    result = probe.score(model, device)       # top-1, rank, margin per row

Costing note: a date row needs one forward per distinct month token, but they
all share the prompt, so the twelve go out as a single batch and give both
`log p(month | prompt)` and `log p(day | prompt, month)` in one pass.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch

from data.common import DataConfig, get_encoder, read_jsonl

__all__ = ["ProbeSet", "ProbeRow", "summarize"]


@dataclass
class ProbeRow:
    fact_id: str
    person_id: str
    split: str
    tier: str
    attribute: str
    role: str
    true_value: str
    prompt_ids: List[int]
    true_index: int          # index of the true value in the candidate list


@dataclass
class Candidates:
    """Scoring keys for one attribute's value list."""
    attribute: str
    values: List[str]
    first: np.ndarray                      # first token id per value
    second: Optional[np.ndarray] = None    # second token id, two-token mode
    two_token: bool = False
    # two-token mode: the distinct first tokens, and each value's slot in them
    first_unique: Optional[np.ndarray] = None
    first_slot: Optional[np.ndarray] = None

    @property
    def n(self) -> int:
        return len(self.values)


def build_candidates(cfg: DataConfig, enc) -> Dict[str, Candidates]:
    data = json.loads((cfg.bios_dir / "attribute_values.json").read_text())
    out: Dict[str, Candidates] = {}
    for attr, values in data["values"].items():
        two = attr in cfg.bio_first_two_tokens_unique
        ids = [enc.encode_ordinary(" " + v) for v in values]
        first = np.array([t[0] for t in ids], dtype=np.int64)
        c = Candidates(attribute=attr, values=list(values), first=first,
                       two_token=two)
        if two:
            second = np.array([t[1] if len(t) > 1 else t[0] for t in ids],
                              dtype=np.int64)
            uniq = np.unique(first)
            slot = np.searchsorted(uniq, first)
            pairs = list(zip(first.tolist(), second.tolist()))
            if len(set(pairs)) != len(pairs):
                raise ValueError(
                    f"{attr}: first two tokens are not unique, so a date cannot "
                    "be identified from them")
            c.second, c.first_unique, c.first_slot = second, uniq, slot
        elif len(set(first.tolist())) != len(first):
            raise ValueError(
                f"{attr}: first tokens are not unique; ranking on them would be "
                "ambiguous. Add it to bios.values.first_two_tokens_unique.")
        out[attr] = c
    return out


class ProbeSet:
    """Prompts tokenized once, scored against a model many times."""

    def __init__(self, rows: List[ProbeRow], candidates: Dict[str, Candidates]):
        self.rows = rows
        self.candidates = candidates

    # -- construction ------------------------------------------------------
    @classmethod
    def build(cls, cfg: DataConfig, rows: Iterable[Dict[str, Any]],
              enc=None) -> "ProbeSet":
        enc = enc or get_encoder(cfg.tokenizer_name, cfg.vocab_size)
        cand = build_candidates(cfg, enc)
        index_of = {a: {v: i for i, v in enumerate(c.values)}
                    for a, c in cand.items()}
        out: List[ProbeRow] = []
        raw = list(rows)
        prompts = enc.encode_ordinary_batch([r["prompt"] for r in raw],
                                            num_threads=8)
        for r, ids in zip(raw, prompts):
            attr = r["attribute"]
            ti = index_of[attr].get(r["true_value"])
            if ti is None:
                raise ValueError(
                    f"{r['fact_id']}: true value {r['true_value']!r} is not in "
                    f"the {attr} list")
            out.append(ProbeRow(
                fact_id=r["fact_id"], person_id=r["person_id"], split=r["split"],
                tier=r["tier"], attribute=attr, role=r["role"],
                true_value=r["true_value"], prompt_ids=list(ids), true_index=ti))
        return cls(out, cand)

    def __len__(self) -> int:
        return len(self.rows)

    # -- scoring -----------------------------------------------------------
    @torch.no_grad()
    def score(self, model, device, batch_tokens: int = 16384,
              block_size: int = 512, progress: bool = False) -> Dict[str, Any]:
        """Rank the true value among its attribute's candidates, per row.

        Rows are batched by EXACT prompt length. The model returns only the
        final position's logits when it is called without targets, so a padded
        batch would read the wrong position; equal lengths make the final
        position the right one for every row, and waste no padding either.
        """
        model.eval()
        n = len(self.rows)
        rank = np.zeros(n, dtype=np.int32)
        top1 = np.zeros(n, dtype=bool)
        margin = np.zeros(n, dtype=np.float32)

        buckets: Dict[Tuple[bool, int], List[int]] = defaultdict(list)
        for i, r in enumerate(self.rows):
            two = self.candidates[r.attribute].two_token
            buckets[(two, len(r.prompt_ids))].append(i)

        done = 0
        for (two, length), idx in sorted(buckets.items()):
            # a date row costs one forward for the month plus twelve for the
            # days, so its batch is that much smaller
            mult = 1
            if two:
                mult = 1 + max(
                    len(self.candidates[self.rows[i].attribute].first_unique)
                    for i in idx)
            per_batch = max(1, batch_tokens // max(1, length * mult))
            for a in range(0, len(idx), per_batch):
                chunk = idx[a:a + per_batch]
                if two:
                    self._score_two(chunk, model, device, rank, top1, margin,
                                    block_size)
                else:
                    self._score_one(chunk, model, device, rank, top1, margin,
                                    block_size)
                done += len(chunk)
                if progress and done % 5000 < per_batch:
                    print(f"[probe] {done}/{n}", flush=True)
        return self._summary(rank, top1, margin)

    def _last_logprobs(self, seqs: List[List[int]], model, device,
                       block_size: int) -> torch.Tensor:
        """Log-probabilities at the final position. All `seqs` are equal length."""
        if len(seqs[0]) > block_size:
            raise ValueError(f"prompt of {len(seqs[0])} tokens exceeds "
                             f"block_size {block_size}")
        x = torch.tensor(seqs, dtype=torch.long, device=device)
        logits, _ = model(x)                       # (B, 1, V) -- no targets
        return torch.log_softmax(logits[:, -1, :].float(), dim=-1)

    def _score_one(self, chunk, model, device, rank, top1, margin, block_size):
        lp = self._last_logprobs([self.rows[i].prompt_ids for i in chunk],
                                 model, device, block_size)
        attr = self.rows[chunk[0]].attribute
        c = self.candidates[attr]
        if any(self.rows[i].attribute != attr for i in chunk):
            # mixed attributes in one length bucket: gather per row
            for j, i in enumerate(chunk):
                cc = self.candidates[self.rows[i].attribute]
                tok = torch.as_tensor(cc.first, device=device)
                scores = lp[j].index_select(0, tok).cpu().numpy()
                self._record(i, scores, self.rows[i].true_index, rank, top1,
                             margin)
            return
        tok = torch.as_tensor(c.first, device=device)
        scores = lp.index_select(1, tok).cpu().numpy()      # (B, n_candidates)
        for j, i in enumerate(chunk):
            self._record(i, scores[j], self.rows[i].true_index, rank, top1,
                         margin)

    def _score_two(self, chunk, model, device, rank, top1, margin, block_size):
        """Dates: log p(month | prompt) + log p(day | prompt, month).

        Exact, because (month, day) pairs are unique across the 200 dates. Two
        forwards: the prompts for the month distribution, then every prompt with
        each of the twelve month tokens appended for the day distributions.
        """
        c = self.candidates[self.rows[chunk[0]].attribute]
        months = c.first_unique
        k, m = len(chunk), len(months)
        prompts = [self.rows[i].prompt_ids for i in chunk]

        lp_month = self._last_logprobs(prompts, model, device, block_size)
        first = torch.as_tensor(c.first, device=device)
        month_scores = lp_month.index_select(1, first)              # (k, n_cand)

        seqs = [p + [int(mo)] for p in prompts for mo in months]
        lp_day = self._last_logprobs(seqs, model, device, block_size)
        slot = torch.as_tensor(c.first_slot, device=device)         # (n_cand,)
        second = torch.as_tensor(c.second, device=device)           # (n_cand,)
        lp_day = lp_day.view(k, m, -1)
        day_scores = lp_day[:, slot, second]                        # (k, n_cand)

        scores = (month_scores + day_scores).cpu().numpy()
        for j, i in enumerate(chunk):
            self._record(i, scores[j], self.rows[i].true_index, rank, top1,
                         margin)

    @staticmethod
    def _record(i, scores, true_index, rank, top1, margin):
        true_score = scores[true_index]
        rank[i] = int((scores > true_score).sum()) + 1
        top1[i] = bool(rank[i] == 1)
        wrong = np.delete(scores, true_index)
        margin[i] = float(true_score - wrong.max()) if wrong.size else 0.0

    def _summary(self, rank, top1, margin) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "n": len(self.rows),
            "overall": _agg(rank, top1, margin,
                            [self.candidates[r.attribute].n for r in self.rows]),
            "by_tier_role": {},
            "by_attribute": {},
            "by_tier_role_attribute": {},
        }
        groups: Dict[Tuple, List[int]] = defaultdict(list)
        for i, r in enumerate(self.rows):
            groups[("tier_role", r.tier, r.role)].append(i)
            groups[("attribute", r.attribute)].append(i)
            groups[("full", r.tier, r.role, r.attribute)].append(i)
        for key, idx in groups.items():
            sizes = [self.candidates[self.rows[i].attribute].n for i in idx]
            agg = _agg(rank[idx], top1[idx], margin[idx], sizes)
            if key[0] == "tier_role":
                out["by_tier_role"][f"{key[1]}/{key[2]}"] = agg
            elif key[0] == "attribute":
                out["by_attribute"][key[1]] = agg
            else:
                out["by_tier_role_attribute"][f"{key[1]}/{key[2]}/{key[3]}"] = agg
        out["_rank"] = rank
        out["_top1"] = top1
        return out


def _agg(rank, top1, margin, sizes) -> Dict[str, Any]:
    rank = np.asarray(rank, dtype=np.float64)
    sizes = np.asarray(sizes, dtype=np.float64)
    if rank.size == 0:
        return {"n": 0}
    return {
        "n": int(rank.size),
        "top1": round(float(np.mean(top1)), 6),
        "mean_rank": round(float(rank.mean()), 3),
        "median_rank": float(np.median(rank)),
        "mean_rank_fraction": round(float((rank / sizes).mean()), 6),
        "mean_margin": round(float(np.mean(margin)), 4),
        "candidates_mean": round(float(sizes.mean()), 1),
    }


def score_random(probe: ProbeSet, seed: int = 0) -> Dict[str, Any]:
    """What a scorer that knows nothing produces: mean rank at the middle."""
    rng = np.random.default_rng(seed)
    n = len(probe.rows)
    rank = np.zeros(n, dtype=np.int32)
    top1 = np.zeros(n, dtype=bool)
    margin = np.zeros(n, dtype=np.float32)
    for i, row in enumerate(probe.rows):
        c = probe.candidates[row.attribute]
        scores = rng.standard_normal(c.n)
        ProbeSet._record(i, scores, row.true_index, rank, top1, margin)
    return probe._summary(rank, top1, margin)


def select_eval_rows(cfg: DataConfig, per_tier: int = 300,
                     roles: Sequence[str] = ("test", "paraphrase"),
                     seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """All frequent-tier people plus `per_tier` random each of the others.

    Deterministic from the data seed, so the same people are evaluated at every
    checkpoint and across runs.
    """
    from data.common import keyed_rng
    seed = cfg.seed if seed is None else seed
    people = list(read_jsonl(cfg.bios_dir / "people.jsonl"))
    by_tier: Dict[str, List[str]] = defaultdict(list)
    for p in people:
        by_tier[p["tier"]].append(p["person_id"])
    chosen: Dict[str, str] = {}
    for tier, ids in sorted(by_tier.items()):
        ids = sorted(ids)
        if tier == "frequent" or len(ids) <= per_tier:
            take = ids
        else:
            take = keyed_rng(seed, "q2_eval", tier).sample(ids, per_tier)
        for pid in take:
            chosen[pid] = tier
    want_roles = set(roles)
    rows = [r for r in read_jsonl(cfg.bios_dir / "facts.jsonl")
            if r["person_id"] in chosen and r["role"] in want_roles]
    rows.sort(key=lambda r: (r["person_id"], r["role"], r["attribute"],
                             r.get("rewording_id") if r.get("rewording_id")
                             is not None else -1, r["template_id"]))
    return rows


def summarize(result: Dict[str, Any]) -> Dict[str, Any]:
    """The JSON-safe part of a result (drops the per-row arrays)."""
    return {k: v for k, v in result.items() if not k.startswith("_")}
