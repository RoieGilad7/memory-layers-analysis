"""A miniature, manifest-verified v1 bundle for the evaluation tests.

Built from slices of the committed data/v1_sample/ (real held-out text, real
biographies), so it needs no network beyond tiktoken's cached GPT-2 vocabulary
and nothing from the 1.1 GB bundle:

    tokens/train.bin       random GPT-2 ids, cut in 128-token sequences
    heldout/test.bin/.idx  the 3 shortest test-half documents of each subject
    bios/                  people.jsonl, facts.jsonl, attribute_values.json
    eval_sets/             heldout_sample (2 docs/subject), fact_sample (2 people/tier)
    <tmp>/manifests/       v1.json (bundle) and eval_sets_v1.json
"""

import shutil
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "v1_sample"
BLOCK = 128


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
        "data.root=null",
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

    src = np.memmap(SAMPLE / "heldout" / "test.bin", dtype=np.uint16, mode="r")
    idx = pack.read_index(SAMPLE / "heldout" / "test.idx.parquet")
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
    np.concatenate(chunks).astype(np.uint16).tofile(root / "heldout" / "test.bin")
    pack.write_index(
        rows, root / "heldout" / "test.idx.parquet", extra_columns=("ngram_overlap",)
    )
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
    eval_sets.build(dcfg, per_subject=2, per_tier=2)
    return cfg_path, dcfg
