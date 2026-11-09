"""The metric test kit: a tiny trained PKM run with read logs, in a temp dir.

    from memlayers.eval.testkit import metric_kit   # a pytest fixture (session scope)

    def test_my_metric(metric_kit):
        with temporary_metric("my_metric", metric_id="ZZ1", inputs=("model", "readlog")) as fn:
            out = metric_kit.run_metric(my_metric)          # -> dict[str, float]
            assert 0 <= out["share/heldout"] <= 1

What it builds (once per test session, a few seconds on CPU), from slices of
the committed data/v1_sample/ -- real Pile text and real biographies, no network
beyond tiktoken's cached GPT-2 vocabulary:

    bundle   tokens/train.bin (random ids, 128-token sequences); heldout/test and
             heldout/label (the 3 shortest documents of each subject); bios/
    eval sets  heldout_sample (2 docs/subject), fact_sample (2 people/tier),
             readlog_tokens (label docs up to 200 tokens/subject + facts)
    run      a tiny PKM (d64, 3 layers, PKM 16x16 at layer 1, vocab 50257, block
             128) trained 10 steps with evals at 0 and 10
    readlogs step 0 and step 10 (final)

`MetricKit.context(step)` gives an EvalContext on that run; `run_metric(fn)`
calls a metric the way the framework does and checks the contract.
"""

import contextlib
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE = ROOT / "data" / "v1_sample"
BLOCK = 128
READLOG_BUDGET = 200  # held-out tokens per training subject in the kit's read log


# overrides that point a run at the mini bundle with a CPU-sized model
def run_overrides(
    data_config, out_root, steps=10, eval_steps="[0,5,10]", experiment="smoke"
):
    model = {"smoke_dense": "tiny_dense"}.get(experiment, "tiny_pkm")
    extra = ["model.memory.freeze_keys=true"] if experiment == "smoke_randkey" else []
    return [
        f"experiment={experiment}",
        "data=v1",
        "data.small=false",
        "data.bundle=null",
        f"data.data_config={data_config}",
        f"model={model}",
        *extra,
        "model.vocab_size=50257",
        f"model.block_size={BLOCK}",
        "train.micro_batch_size=2",
        f"train.steps={steps}",
        "train.ckpt_every=0",
        "runtime=cpu",
        "eval=standard",
        f"eval.steps={eval_steps}",
        "eval.heldout_batch=4",
        f"eval.readlog.tokens_per_subject={READLOG_BUDGET}",
        f"out_root={out_root}",
    ]


def make_mini_bundle(base: Path):
    from data import manifest as manifest_mod
    from data import pack
    from data.common import DataConfig, load_config

    from memlayers.eval import eval_sets

    root = base / "v1"
    for d in ("tokens", "heldout", "bios"):
        (root / d).mkdir(parents=True)

    rng = np.random.default_rng(0)
    rng.integers(0, 50257, size=BLOCK * 64 + 1, dtype=np.uint16).tofile(
        root / "tokens" / "train.bin"
    )

    for half in ("test", "label"):
        _slice_half(root, half)
    for f in ("people.jsonl", "facts.jsonl", "attribute_values.json"):
        shutil.copy(SAMPLE / "bios" / f, root / "bios" / f)

    raw = yaml.safe_load((ROOT / "configs" / "data" / "v1.yaml").read_text())
    r = str(root)
    raw["paths"] = {
        "root": r,
        "raw": f"{r}/raw",
        "work": f"{r}/_work",
        "train": f"{r}/train",
        "heldout_pool": f"{r}/heldout_pool",
        "heldout": f"{r}/heldout",
        "reports": f"{r}/reports",
    }
    raw["small"]["root"] = r
    raw["distribution"]["manifest_dir"] = str(base / "manifests")
    raw["pack"]["block_size"] = BLOCK
    cfg_path = base / "data_config.yaml"
    cfg_path.write_text(yaml.safe_dump(raw))
    manifest_mod.run(DataConfig(raw=raw))
    dcfg = load_config(cfg_path)
    eval_sets.build(
        dcfg, per_subject=2, per_tier=2, readlog_tokens_per_subject=READLOG_BUDGET
    )
    return cfg_path, dcfg


def _slice_half(root: Path, half: str) -> None:
    """The 3 shortest documents of each subject of one held-out half."""
    from data import pack

    src = np.memmap(SAMPLE / "heldout" / f"{half}.bin", dtype=np.uint16, mode="r")
    idx = pack.read_index(SAMPLE / "heldout" / f"{half}.idx.parquet")
    by_subject = {}
    for i, s in enumerate(idx["subject"]):
        by_subject.setdefault(s, []).append(i)
    rows, chunks, pos = [], [], 0
    for subject in sorted(by_subject):
        pick = sorted(
            by_subject[subject], key=lambda i: (int(idx["length"][i]), idx["doc_id"][i])
        )[:3]
        for i in sorted(pick):
            a, n = int(idx["start"][i]), int(idx["length"][i])
            chunks.append(np.asarray(src[a : a + n]))
            rows.append(
                dict(
                    doc_id=idx["doc_id"][i],
                    subject=subject,
                    start=pos,
                    length=n,
                    doc_offset=0,
                    person_id=None,
                    rewording_id=-1,
                    ngram_overlap=0.0,
                )
            )
            pos += n
    np.concatenate(chunks).astype(np.uint16).tofile(root / "heldout" / f"{half}.bin")
    pack.write_index(
        rows, root / "heldout" / f"{half}.idx.parquet", extra_columns=("ngram_overlap",)
    )


# ------------------------------------------------------------------------ kit
class MetricKit:
    """A finished tiny PKM run with read logs at step 0 and its final step."""

    def __init__(self, base: Path):
        from memlayers.config import compose
        from memlayers.readlog_pass import readlog_pass
        from memlayers.run import launch

        self.base = Path(base)
        self.data_config, self.dcfg = make_mini_bundle(self.base / "bundle")
        self.overrides = run_overrides(
            self.data_config, self.base / "runs", steps=10, eval_steps="[0,10]"
        )
        self.run_dir = launch(compose(self.overrides))
        readlog_pass(self.run_dir, ["init", "final"], device="cpu")
        self.final_step = 10

    def context(self, step="final", stage: str = "posthoc", sample: bool = True):
        """An EvalContext on the kit run's checkpoint at `step` (final | init | int)."""
        from omegaconf import OmegaConf

        from memlayers.eval.context import EvalContext, EvalResources
        from memlayers.evaluate import _model_for, find_checkpoints, load_run_config

        cfg = load_run_config(self.run_dir)
        ((_, path),) = find_checkpoints(self.run_dir, str(step))
        import torch

        model, ck_step, tokens = _model_for(cfg, path, torch.device("cpu"))
        return EvalContext(
            model=model,
            config=OmegaConf.to_container(cfg, resolve=True),
            run_dir=self.run_dir,
            step=ck_step,
            tokens_seen=tokens,
            stage=stage,
            resources=EvalResources.from_config(cfg.data, self.run_dir),
            seed=int(cfg.eval.seed),
            sample=sample,
            heldout_batch=4,
        )

    def run_metric(
        self, fn: Callable, stage: str = "posthoc", step="final", sample: bool = True
    ) -> Dict[str, float]:
        """Call a metric as the framework does, and check the contract: a flat
        dict of float values under slash-path keys, the model left unchanged."""
        import torch

        ctx = self.context(step, stage, sample)
        ctx.metric = getattr(fn, "__name__", "metric")
        before = {k: v.clone() for k, v in ctx.model.state_dict().items()}
        ctx.model.eval()
        with torch.no_grad():
            out = fn(ctx)
        after = ctx.model.state_dict()
        changed = [k for k in before if not torch.equal(before[k], after[k])]
        assert not changed, f"the metric changed the model: {changed[:5]}"
        assert all(
            m.slot_mask is None for m in ctx.memory_layers.values()
        ), "a slot mask was left on"
        assert isinstance(out, dict), "a metric returns dict[str, float]"
        for k, v in out.items():
            assert (
                isinstance(k, str) and "/" in k
            ), f"key {k!r} must be <quantity>/<subset>"
            float(v)
        return {k: float(v) for k, v in out.items()}


@contextlib.contextmanager
def temporary_metric(name: str, **kwargs):
    """Register a metric for the duration of a test only:

    with temporary_metric("example_read_share", metric_id="EX1",
                          inputs=("model", "readlog"), needs_memory=True) as reg:
        reg(fn)
    """
    from memlayers.eval.registry import _unregister, register_metric

    deco = register_metric(name, **kwargs)
    try:
        yield deco
    finally:
        _unregister(name)


try:  # the fixture, for any test module that imports it (or via conftest)
    import pytest

    @pytest.fixture(scope="session")
    def metric_kit(tmp_path_factory):
        return MetricKit(tmp_path_factory.mktemp("metric_kit"))

except ImportError:  # pragma: no cover - pytest is in requirements.txt
    pass
