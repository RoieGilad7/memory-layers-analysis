"""What a metric sees: `EvalContext`, and the resources it loads lazily.

A context is built for one evaluation point (one step, one stage). Resources
that do not change between points -- the held-out documents, the tokenized
fact prompts -- live in `EvalResources`, built once per run and shared by every
context, so the second eval of a run costs no loading at all.

The held-out pass is shared too: `ctx.heldout_pass()` runs ONE forward over the
held-out text, capturing the memory reads on the way, and caches the result on
the context. `heldout_quality` and `slot_usage` both read it, so slot usage
costs no extra forward.
"""

from __future__ import annotations

import contextlib
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn.functional as F

__all__ = [
    "EvalContext",
    "EvalResources",
    "HeldoutDoc",
    "HeldoutPass",
    "preserved_state",
    "accumulate_reads",
    "new_usage",
]


@dataclass(frozen=True)
class HeldoutDoc:
    doc_id: str
    start: int
    length: int


@dataclass
class HeldoutPass:
    """Sums from one forward over a held-out set, per subject slug.

    `sums[slug] = {loss_sum, tokens, correct, docs}`; `sample_sums` the same
    restricted to the documents of the fixed sample (a full pass covers them
    too, so a final full-set number can be put on the same curve as the
    during-training sample numbers). `usage[layer] = {counts, weights, best}`
    as int64 / float64 / int64 tensors over the layer's slots, or {} for a
    model without memory.
    """

    sample: bool
    sums: Dict[str, Dict[str, float]]
    sample_sums: Dict[str, Dict[str, float]]
    usage: Dict[int, Dict[str, torch.Tensor]]
    n_slots: Dict[int, int]
    seconds: float = 0.0


class EvalResources:
    """Per-run, lazily loaded, cached: held-out documents, fact probes, init weights."""

    def __init__(self, data_cfg: Any, data_source: str, run_dir: Optional[Path] = None):
        self.data_source = data_source
        self.dcfg = data_cfg  # a data.common.DataConfig, or None for fake data
        self.run_dir = Path(run_dir) if run_dir else None
        self._tokens: Dict[str, np.ndarray] = {}
        self._heldout: Dict[Tuple[str, bool], Dict[str, List[HeldoutDoc]]] = {}
        self._probe: Dict[bool, Any] = {}
        self._init_state: Optional[dict] = None

    @classmethod
    def from_config(cls, data: Any, run_dir: Optional[Path] = None) -> "EvalResources":
        source = data["source"] if isinstance(data, dict) else data.source
        if source != "real":
            return cls(None, source, run_dir)
        from memlayers.train import load_bundle_config

        return cls(load_bundle_config(data), source, run_dir)

    # -- availability --------------------------------------------------------
    def why_missing(self, what: str) -> Optional[str]:
        if what in ("heldout", "fact_probe") and self.dcfg is None:
            return f"data.source={self.data_source} has no held-out text or fact probes"
        if what == "heldout":
            p = Path(self.dcfg.heldout_tokens_dir) / "test.bin"
            if not p.exists():
                return f"held-out tokens {p} not found"
        if what == "fact_probe":
            p = Path(self.dcfg.bios_dir) / "facts.jsonl"
            if not p.exists():
                return f"fact rows {p} not found"
        if what == "init_model":
            if (
                self.run_dir is None
                or not (self.run_dir / "checkpoints/step_000000.pt").exists()
            ):
                return "no checkpoints/step_000000.pt in the run dir"
        if what == "readlog":
            return "no read log: run the read-log pass first (memlayers.readlog_pass)"
        return None

    # -- held-out ------------------------------------------------------------
    def tokens(self, half: str) -> np.ndarray:
        if half not in self._tokens:
            self._tokens[half] = np.memmap(
                Path(self.dcfg.heldout_tokens_dir) / f"{half}.bin",
                dtype=np.uint16,
                mode="r",
            )
        return self._tokens[half]

    def heldout(
        self, half: str = "test", sample: bool = True
    ) -> Dict[str, List[HeldoutDoc]]:
        """{slug: [HeldoutDoc, ...]} for the 6 subjects, in index order."""
        key = (half, bool(sample))
        if key not in self._heldout:
            from data import pack

            from .eval_sets import load_heldout_sample

            index = pack.read_index(
                Path(self.dcfg.heldout_tokens_dir) / f"{half}.idx.parquet"
            )
            want = None
            if sample:
                if half != "test":
                    raise ValueError(
                        "the fixed held-out sample is drawn from the test half"
                    )
                want = {
                    s: set(ids) for s, ids in load_heldout_sample(self.dcfg).items()
                }
            out: Dict[str, List[HeldoutDoc]] = {
                self.dcfg.slug(s): [] for s in self.dcfg.all_subjects
            }
            for doc_id, subj, start, length in zip(
                index["doc_id"], index["subject"], index["start"], index["length"]
            ):
                slug = self.dcfg.slug(subj)
                if want is not None and doc_id not in want.get(slug, ()):
                    continue
                out[slug].append(HeldoutDoc(doc_id, int(start), int(length)))
            self._heldout[key] = out
        return self._heldout[key]

    def train_slugs(self) -> List[str]:
        return [self.dcfg.slug(s) for s in self.dcfg.train_subjects]

    # -- facts ---------------------------------------------------------------
    def fact_probe(self, sample: bool = True):
        key = bool(sample)
        if key not in self._probe:
            from data.common import read_jsonl
            from data.q2_probe import ProbeSet

            from .eval_sets import load_fact_sample

            rows = [
                r
                for r in read_jsonl(Path(self.dcfg.bios_dir) / "facts.jsonl")
                if r["role"] in ("test", "paraphrase")
            ]
            if sample:
                order = {fid: i for i, fid in enumerate(load_fact_sample(self.dcfg))}
                rows = sorted(
                    (r for r in rows if r["fact_id"] in order),
                    key=lambda r: order[r["fact_id"]],
                )
                if len(rows) != len(order):
                    raise RuntimeError(
                        f"fact_sample names {len(order)} facts, facts.jsonl has {len(rows)} of them"
                    )
            else:
                rows.sort(
                    key=lambda r: (
                        r["person_id"],
                        r["role"],
                        r["attribute"],
                        (
                            r.get("rewording_id")
                            if r.get("rewording_id") is not None
                            else -1
                        ),
                        r["template_id"],
                    )
                )
            self._probe[key] = ProbeSet.build(self.dcfg, rows)
        return self._probe[key]

    def init_state(self) -> dict:
        if self._init_state is None:
            ck = torch.load(
                self.run_dir / "checkpoints/step_000000.pt",
                map_location="cpu",
                weights_only=False,
            )
            self._init_state = ck["model"]
        return self._init_state


def new_usage(n_slots: Dict[int, int]) -> Dict[int, Dict[str, torch.Tensor]]:
    return {
        i: {
            "counts": torch.zeros(n, dtype=torch.long),
            "weights": torch.zeros(n, dtype=torch.float64),
            "best": torch.zeros(n, dtype=torch.long),
        }
        for i, n in n_slots.items()
    }


@torch.no_grad()
def accumulate_reads(usage, reads) -> None:
    """Add one forward's reads ({layer: MemoryRead}, [..., heads, topk]) to
    `usage`: read counts, summed gate weights, and how often each slot was the
    highest-weight slot of a read (one head's top-k for one token)."""
    for i, r in reads.items():
        if i not in usage:
            continue
        u = usage[i]
        n = u["counts"].numel()
        idx = r.indices.reshape(-1).to("cpu", torch.long)
        w = r.weights.reshape(-1).to("cpu", torch.float64)
        u["counts"] += torch.bincount(idx, minlength=n)
        u["weights"] += torch.bincount(idx, weights=w, minlength=n)
        k = r.indices.shape[-1]
        ri = r.indices.reshape(-1, k).to("cpu", torch.long)
        rw = r.weights.reshape(-1, k).to("cpu", torch.float32)
        top = ri.gather(1, rw.argmax(-1, keepdim=True)).reshape(-1)
        u["best"] += torch.bincount(top, minlength=n)


@contextlib.contextmanager
def preserved_state(model, device) -> Iterator[None]:
    """Everything an evaluation could disturb, saved and put back.

    RNG states (torch CPU, CUDA, MPS, numpy's global, Python's), the model's
    train/eval mode, each memory layer's read-logging switch and slot mask.
    The data loader is never touched by evaluation at all.
    """
    from memlayers.devices import get_rng_states, set_rng_states

    rng = get_rng_states(device)
    np_state = np.random.get_state()
    py_state = random.getstate()
    was_training = model.training
    mems = getattr(model, "memory_layers", {}) or {}
    flags = {
        i: (m.read_logging, m.slot_mask, m.renormalize_after_mask)
        for i, m in mems.items()
    }
    try:
        yield
    finally:
        for i, m in mems.items():
            logging_on, mask, renorm = flags[i]
            m.set_read_logging(logging_on)
            m.slot_mask = mask
            m.renormalize_after_mask = renorm
        model.train(was_training)
        set_rng_states(rng, device)
        np.random.set_state(np_state)
        random.setstate(py_state)


class EvalContext:
    """One evaluation point.

    model: in eval mode, under torch.no_grad (the framework's job), on `device`.
    """

    def __init__(
        self,
        model,
        config: Dict[str, Any],
        run_dir: Optional[Path],
        step: int,
        tokens_seen: int,
        stage: str,
        resources: EvalResources,
        seed: int = 0,
        sample: Optional[bool] = None,
        heldout_batch: int = 8,
        fact_batch_tokens: int = 16384,
    ):
        self.model = model
        self.config = config
        self.run_dir = Path(run_dir) if run_dir else None
        self.step = int(step)
        self.tokens_seen = int(tokens_seen)
        self.stage = stage
        self.resources = resources
        self.seed = int(seed)
        # during -> the fixed samples; final and posthoc -> the full sets
        self.sample = (stage == "during") if sample is None else bool(sample)
        self.heldout_batch = int(heldout_batch)
        self.fact_batch_tokens = int(fact_batch_tokens)
        self.device = next(model.parameters()).device
        self.generator = torch.Generator().manual_seed(self.seed)
        self.np_rng = np.random.default_rng(self.seed)
        self.metric: Optional[str] = None  # set by the framework per metric
        self._pass: Dict[tuple, HeldoutPass] = {}
        self._init_model = None
        self._readlogs: Dict[int, Any] = {}
        self._snap: Dict[tuple, torch.Tensor] = {}

    # -- inputs --------------------------------------------------------------
    def why_missing(self, what: str) -> Optional[str]:
        if what == "model":
            return None
        if what == "readlog":
            return self._readlog_missing(self.step)
        return self.resources.why_missing(what)

    def _readlog_dir(self, step: int) -> Optional[Path]:
        if self.run_dir is None:
            return None
        return self.run_dir / "readlogs" / f"step_{int(step):06d}"

    def _readlog_missing(self, step: int) -> Optional[str]:
        d = self._readlog_dir(step)
        if d is None or not (d / "manifest.json").exists():
            where = self.run_dir or "<run_dir>"
            return (
                f"no read log for step {step}: run the read-log pass first: "
                f"python -m memlayers.readlog_pass run_dir={where} step={step}"
            )
        return None

    @property
    def memory_layers(self) -> Dict[int, Any]:
        return getattr(self.model, "memory_layers", {}) or {}

    @property
    def block_size(self) -> int:
        return int(self.model.config.block_size)

    @property
    def artifact_dir(self) -> Path:
        if self.run_dir is None or self.metric is None:
            raise RuntimeError("artifact_dir needs a run dir and a current metric")
        d = self.run_dir / "analysis" / self.metric
        d.mkdir(parents=True, exist_ok=True)
        return d

    def heldout(self, half: str = "test", sample: Optional[bool] = None):
        return self.resources.heldout(half, self.sample if sample is None else sample)

    def fact_probe(self, sample: Optional[bool] = None):
        return self.resources.fact_probe(self.sample if sample is None else sample)

    def init_model(self):
        """The run's step-0 weights in a second model, eval mode, same device."""
        if self._init_model is None:
            import copy

            m = copy.deepcopy(self.model)
            m.load_state_dict(self.resources.init_state())
            m.eval()
            self._init_model = m
        return self._init_model

    def readlog(self, step: Optional[int] = None):
        """The read log (memlayers.readlog.ReadLog) of this context's checkpoint
        step, or of `step`. RuntimeError, naming the command, if there is none."""
        from memlayers.readlog import ReadLog

        step = self.step if step is None else int(step)
        if step not in self._readlogs:
            why = self._readlog_missing(step)
            if why:
                raise RuntimeError(f"ctx.readlog(): {why}")
            self._readlogs[step] = ReadLog.open(self._readlog_dir(step))
        return self._readlogs[step]

    # -- shared helpers for the analysis metrics -------------------------------
    def _memory(self, layer: int):
        mems = self.memory_layers
        if layer not in mems:
            raise KeyError(
                f"layer {layer} is not a memory layer; memory layers {sorted(mems)}"
            )
        return mems[layer]

    def value_table(self, layer: int) -> torch.Tensor:
        """[n_slots, d]: what each slot writes into the residual stream (PKM:
        the value table; PEER: the up-projection embedding). A detached fp32
        CPU copy, so a metric cannot change the model through it."""
        key = ("values", int(layer))
        if key not in self._snap:
            m = self._memory(layer)
            w = (
                m.pkm.values.weight
                if m.kind == "pkm"
                else m.peer.weight_up_embed.weight
            )
            self._snap[key] = w.detach().to("cpu", torch.float32).clone()
        return self._snap[key]

    def unembedding(self) -> torch.Tensor:
        """[vocab, d]: the output head (tied to the token embedding), detached
        fp32 CPU copy, for the logit lens. The final LayerNorm is
        `ctx.model.transformer.ln_f` if a metric wants to apply it first."""
        key = ("unembed",)
        if key not in self._snap:
            self._snap[key] = (
                self.model.lm_head.weight.detach().to("cpu", torch.float32).clone()
            )
        return self._snap[key]

    def used_slots(self, layer: int, step: Optional[int] = None) -> np.ndarray:
        """Slots read at least once in the read log, ascending."""
        return np.flatnonzero(self.readlog(step).slot_counts(layer) > 0)

    def slot_bins(self, layer: int, n_bins: int = 10, step: Optional[int] = None):
        """-> (used slots, read-count bin, value-norm bin), deciles by default:
        each used slot's rank among used slots, cut into `n_bins` equal parts."""
        counts = self.readlog(step).slot_counts(layer)
        used = np.flatnonzero(counts > 0)
        norms = self.value_table(layer)[torch.as_tensor(used)].norm(dim=1).numpy()

        def rank_bins(v):
            order = np.argsort(v, kind="stable")
            ranks = np.empty(len(v), dtype=np.int64)
            ranks[order] = np.arange(len(v))
            return (ranks * n_bins) // max(1, len(v))

        return used, rank_bins(counts[used]), rank_bins(norms)

    def matched_random_slots(
        self, layer: int, slots, n: int, rng: np.random.Generator, n_bins: int = 10
    ) -> np.ndarray:
        """`n` random used slots matched to `slots` in read count and value norm.

        Every used slot gets a (count decile, norm decile) cell; the draw takes
        from each cell in the proportion `slots` occupy it (largest-remainder
        rounding), never returns a slot of `slots`, and raises ValueError naming
        the cell when it has too few candidates. Deterministic for a given rng.
        """
        slots = np.unique(np.asarray(slots, dtype=np.int64))
        used, cb, nb = self.slot_bins(layer, n_bins)
        pos = {int(s_): i for i, s_ in enumerate(used)}
        missing = [int(s_) for s_ in slots if int(s_) not in pos]
        if missing:
            raise ValueError(
                f"slots {missing[:10]} are never read in the read log; cannot bin them"
            )
        cells: Dict[tuple, int] = {}
        for s_ in slots:
            i = pos[int(s_)]
            cells[(int(cb[i]), int(nb[i]))] = cells.get((int(cb[i]), int(nb[i])), 0) + 1
        keys = sorted(cells)
        exact = {k: n * cells[k] / len(slots) for k in keys}
        quota = {k: int(np.floor(exact[k])) for k in keys}
        rest = n - sum(quota.values())
        for k in sorted(keys, key=lambda k: (-(exact[k] - quota[k]), k))[:rest]:
            quota[k] += 1
        taken = set(int(x) for x in slots)
        out = []
        for k in keys:
            if quota[k] == 0:
                continue
            cand = np.array(
                [
                    int(used[i])
                    for i in np.flatnonzero((cb == k[0]) & (nb == k[1]))
                    if int(used[i]) not in taken
                ],
                dtype=np.int64,
            )
            if len(cand) < quota[k]:
                raise ValueError(
                    f"cell (read-count bin {k[0]}, value-norm bin {k[1]}) of layer {layer} has "
                    f"{len(cand)} candidate slots outside the input, {quota[k]} needed"
                )
            out.append(rng.choice(cand, size=quota[k], replace=False))
        return np.sort(np.concatenate(out)) if out else np.empty(0, dtype=np.int64)

    @torch.no_grad()
    def loss_with_masked_slots(
        self,
        layer: int,
        slots,
        half: str = "test",
        subjects: Optional[Sequence[str]] = None,
        sample: bool = True,
    ) -> Dict[str, float]:
        """{subject slug: held-out loss} with `slots` of `layer` switched off,
        plus `pile_avg` (token-weighted over the training subjects included).
        Default: the fixed 200-doc/subject sample. `sample=False` is the whole
        half (~15M tokens for test) -- slow; removal tests call this many times.
        An empty `slots` gives exactly heldout_quality's losses."""
        with self.masked_slots({layer: list(np.asarray(slots, dtype=np.int64))}):
            p = self.heldout_pass(
                sample=sample, half=half, subjects=subjects, capture_reads=False
            )
        out = {
            s_: v["loss_sum"] / v["tokens"] for s_, v in p.sums.items() if v["tokens"]
        }
        train = [
            s_
            for s_ in self.resources.train_slugs()
            if s_ in p.sums and p.sums[s_]["tokens"]
        ]
        if train:
            out["pile_avg"] = sum(p.sums[s_]["loss_sum"] for s_ in train) / sum(
                p.sums[s_]["tokens"] for s_ in train
            )
        return out

    @torch.no_grad()
    def fact_recall_with_masked_slots(self, layer: int, slots, rows):
        """Per-row fact recall with `slots` of `layer` switched off: a DataFrame
        with fact_id, tier, role, attribute, top1, rank, margin. `rows` are fact
        rows (facts.jsonl dicts) or fact ids. Scored by the same
        ProbeSet.score that fact_recall uses."""
        import pandas as pd

        from data.common import read_jsonl
        from data.q2_probe import ProbeSet

        rows = list(rows)
        if rows and isinstance(rows[0], str):
            want = {r: i for i, r in enumerate(rows)}
            found = [
                r
                for r in read_jsonl(Path(self.resources.dcfg.bios_dir) / "facts.jsonl")
                if r["fact_id"] in want
            ]
            rows = sorted(found, key=lambda r: want[r["fact_id"]])
        probe = ProbeSet.build(self.resources.dcfg, rows)
        with self.masked_slots({layer: list(np.asarray(slots, dtype=np.int64))}):
            res = probe.score(
                self.model,
                self.device,
                batch_tokens=self.fact_batch_tokens,
                block_size=self.block_size,
            )
        return pd.DataFrame(
            {
                "fact_id": [r.fact_id for r in probe.rows],
                "tier": [r.tier for r in probe.rows],
                "role": [r.role for r in probe.rows],
                "attribute": [r.attribute for r in probe.rows],
                "top1": res["_top1"],
                "rank": res["_rank"],
                "margin": res["_margin"],
            }
        )

    # -- slot masking --------------------------------------------------------
    @contextlib.contextmanager
    def masked_slots(self, spec: Dict[int, Any]) -> Iterator[None]:
        """Switch slots off: they contribute zero and no other slot takes their
        place (renormalize=False). The mask is always cleared on exit."""
        mems = self.memory_layers
        prev = {i: (m.slot_mask, m.renormalize_after_mask) for i, m in mems.items()}
        self._pass.clear()  # a cached unmasked pass must not answer a masked query
        try:
            self.model.set_mask_slots(spec, renormalize=False)
            yield
        finally:
            for i, m in mems.items():
                m.slot_mask, m.renormalize_after_mask = prev[i]
            self._pass.clear()  # a pass under a mask is not the model's pass

    # -- the shared held-out pass ---------------------------------------------
    @torch.no_grad()
    def heldout_pass(
        self,
        sample: Optional[bool] = None,
        half: str = "test",
        subjects: Optional[Sequence[str]] = None,
        capture_reads: bool = True,
    ) -> HeldoutPass:
        """One forward over held-out documents, cached on the context.

        `sample`: the fixed 200-doc/subject sample (test half only) or the whole
        half. `subjects`: slugs to restrict to. `capture_reads=False` skips the
        slot-usage bookkeeping (the masked-loss helper does not need it).
        """
        sample = self.sample if sample is None else bool(sample)
        if half != "test":
            sample = False  # the fixed sample is drawn from the test half
        key = (
            sample,
            half,
            tuple(sorted(subjects)) if subjects else None,
            bool(capture_reads),
        )
        if key in self._pass:
            return self._pass[key]
        import time

        from data.loader import iter_document_windows

        t0 = time.perf_counter()
        docs = self.heldout(half, sample)
        if subjects:
            unknown = sorted(set(subjects) - set(docs))
            if unknown:
                raise KeyError(f"unknown subject slugs {unknown}; have {sorted(docs)}")
            docs = {s_: v for s_, v in docs.items() if s_ in set(subjects)}
        tokens = self.resources.tokens(half)
        in_sample = None
        if not sample and half == "test":
            in_sample = {
                s: {d.doc_id for d in v} for s, v in self.heldout("test", True).items()
            }
        mems = self.memory_layers if capture_reads else {}
        all_mems = self.memory_layers
        prev_logging = {i: m.read_logging for i, m in all_mems.items()}
        usage = new_usage({i: m.n_slots for i, m in mems.items()})
        self.model.eval()
        for m in mems.values():
            m.set_read_logging(True)
        sums: Dict[str, Dict[str, float]] = {}
        sample_sums: Dict[str, Dict[str, float]] = {}
        try:
            for slug, dl in docs.items():
                acc = {"loss_sum": 0.0, "tokens": 0, "correct": 0, "docs": len(dl)}
                sacc = {"loss_sum": 0.0, "tokens": 0, "correct": 0, "docs": 0}
                buckets: Dict[int, List[Tuple[np.ndarray, np.ndarray, bool]]] = {}
                for d in dl:
                    flag = in_sample is not None and d.doc_id in in_sample.get(slug, ())
                    sacc["docs"] += int(flag)
                    for x, y in iter_document_windows(
                        tokens, d.start, d.length, self.block_size
                    ):
                        buckets.setdefault(len(x), []).append((x, y, flag))
                for length in sorted(buckets):
                    wins = buckets[length]
                    for a in range(0, len(wins), self.heldout_batch):
                        chunk = wins[a : a + self.heldout_batch]
                        x = torch.from_numpy(np.stack([c[0] for c in chunk])).to(
                            self.device
                        )
                        y = torch.from_numpy(np.stack([c[1] for c in chunk])).to(
                            self.device
                        )
                        logits, _ = self.model(x, y)
                        lf = logits.float()
                        nll = F.cross_entropy(
                            lf.reshape(-1, lf.size(-1)), y.reshape(-1), reduction="none"
                        ).view(y.shape)
                        row_loss = nll.cpu().double().sum(1)
                        row_ok = (lf.argmax(-1) == y).sum(1).cpu()
                        for j, c in enumerate(chunk):
                            for tgt, use in ((acc, True), (sacc, c[2])):
                                if use:
                                    tgt["loss_sum"] += float(row_loss[j])
                                    tgt["tokens"] += int(length)
                                    tgt["correct"] += int(row_ok[j])
                        if mems:
                            accumulate_reads(usage, self.model.read_logs())
                sums[slug] = acc
                if in_sample is not None:
                    sample_sums[slug] = sacc
        finally:
            for i, m in all_mems.items():
                m.set_read_logging(prev_logging[i])
        if sample:
            sample_sums = sums
        res = HeldoutPass(
            sample=sample,
            sums=sums,
            sample_sums=sample_sums,
            usage=usage,
            n_slots={i: m.n_slots for i, m in mems.items()},
            seconds=time.perf_counter() - t0,
        )
        self._pass[key] = res
        return res
