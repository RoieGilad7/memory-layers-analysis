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
from typing import Any, Dict, Iterator, List, Optional, Tuple

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
            return "no read log: run the read-log pass first (training prompt 4)"
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
        self._pass: Dict[bool, HeldoutPass] = {}
        self._init_model = None

    # -- inputs --------------------------------------------------------------
    def why_missing(self, what: str) -> Optional[str]:
        if what == "model":
            return None
        return self.resources.why_missing(what)

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

    def readlog(self, *args, **kwargs):
        raise RuntimeError(
            "ctx.readlog(): there is no read log for this run yet. Run the "
            "read-log pass first (it arrives in training prompt 4)."
        )

    # -- slot masking --------------------------------------------------------
    @contextlib.contextmanager
    def masked_slots(self, spec: Dict[int, Any]) -> Iterator[None]:
        """Switch slots off: they contribute zero and no other slot takes their
        place (renormalize=False). The mask is always cleared on exit."""
        mems = self.memory_layers
        prev = {i: (m.slot_mask, m.renormalize_after_mask) for i, m in mems.items()}
        try:
            self.model.set_mask_slots(spec, renormalize=False)
            yield
        finally:
            for i, m in mems.items():
                m.slot_mask, m.renormalize_after_mask = prev[i]
            self._pass.clear()  # a pass under a mask is not the model's pass

    # -- the shared held-out pass ---------------------------------------------
    @torch.no_grad()
    def heldout_pass(self, sample: Optional[bool] = None) -> HeldoutPass:
        sample = self.sample if sample is None else bool(sample)
        if sample in self._pass:
            return self._pass[sample]
        import time

        from data.loader import iter_document_windows

        t0 = time.perf_counter()
        docs = self.heldout("test", sample)
        tokens = self.resources.tokens("test")
        in_sample = None
        if not sample:
            in_sample = {
                s: {d.doc_id for d in v} for s, v in self.heldout("test", True).items()
            }
        mems = self.memory_layers
        prev_logging = {i: m.read_logging for i, m in mems.items()}
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
                if not sample:
                    sample_sums[slug] = sacc
        finally:
            for i, m in mems.items():
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
        self._pass[sample] = res
        return res
