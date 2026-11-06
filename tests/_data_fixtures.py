"""Tiny synthetic raw JSONL fixtures for the data tests. No network anywhere."""
import random
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.common import DataConfig, dumps_record, open_write

CONFIG = Path(__file__).resolve().parent.parent / "configs" / "data" / "v1.yaml"

LICENSE = (
    "Copyright 2019 the authors. Licensed under the Apache License, Version 2.0 "
    "(the License); you may not use this file except in compliance with the "
    "License. You may obtain a copy of the License at the address below. Unless "
    "required by applicable law or agreed to in writing, software distributed "
    "under the License is distributed on an AS IS BASIS, without warranties."
)


def body(tag: str, n_words: int = 600, seed: int = 0) -> str:
    """A long, unique word sequence -- no 13-gram of it appears anywhere else."""
    rng = random.Random(f"{tag}:{seed}")
    return " ".join(f"{tag}{rng.randrange(10 ** 6)}" for _ in range(n_words))


def make_cfg(root: Path, **overrides) -> DataConfig:
    """Real v1 config, pointed at `root`, shrunk to two training subjects."""
    raw = yaml.safe_load(CONFIG.read_text())
    r = str(root)
    raw["paths"] = {"root": r, "raw": f"{r}/raw", "work": f"{r}/_work",
                    "train": f"{r}/train", "heldout_pool": f"{r}/heldout_pool",
                    "heldout": f"{r}/heldout", "reports": f"{r}/reports"}
    raw["small"]["root"] = r
    raw["subjects"]["train"] = ["Pile-CC", "Github"]
    raw["subjects"]["heldout_only"] = ["USPTO Backgrounds"]
    raw["document"]["min_tokens"] = 20
    raw["targets"]["heldout_tokens_per_subject"] = 20000
    raw["targets"]["heldout_tokens_per_half"] = 4000
    raw["targets"]["heldout_min_docs_per_half"] = 3
    for key, val in overrides.items():
        section, _, field = key.partition(".")
        if field:
            raw[section][field] = val
        else:
            raw[section] = val
    return DataConfig(raw=raw)


def write_raw(cfg: DataConfig, split: str, subject: str, docs) -> Path:
    """docs: iterable of (line_number, text). Writes the raw archive file."""
    path = cfg.raw_dir / split / f"{cfg.slug(subject)}.jsonl.gz"
    src = cfg.train_files[0] if split == "train" else cfg.heldout_files[0]
    with open_write(path) as fh:
        for line, text in docs:
            fh.write(dumps_record({
                "doc_id": cfg.doc_id(subject, src, line),
                "subject": subject, "split": split, "source": src,
                "line": line, "text": text,
            }))
    return path


def build_corpus(cfg: DataConfig, n_train: int = 6, n_heldout: int = 12) -> dict:
    """A small corpus with every dedup case planted in it.

    Returns the pieces the tests assert on.
    """
    train_texts = {i: f"{LICENSE} {body('tr', seed=i)}" for i in range(n_train)}
    # Pile-CC train: doc 2 is written twice -> one exact duplicate
    train_docs = [(i * 10, t) for i, t in train_texts.items()]
    train_docs.append((999, train_texts[2]))
    write_raw(cfg, "train", "Pile-CC", train_docs)
    write_raw(cfg, "train", "Github",
              [(i * 10, f"def f{i}():\n    return {body('gh', 200, i)}")
               for i in range(3)])

    held = []
    # 0: a verbatim copy of a training document -> exact dup across splits
    held.append((0, train_texts[0]))
    # 1: the same training document with a short tail -> >50% 13-gram overlap
    held.append((1, train_texts[1] + " and one more trailing sentence here."))
    # 2: shares only the license header -> must survive
    held.append((2, f"{LICENSE} {body('ho', seed=100)}"))
    # 3: too short -> dropped
    held.append((3, "tiny"))
    # 4: whitespace only -> dropped as empty
    held.append((4, "   \n\n  "))
    # the rest are clean, independent documents
    held += [(i, f"{LICENSE} {body('ho', seed=i)}") for i in range(5, n_heldout)]
    write_raw(cfg, "heldout", "Pile-CC", held)
    write_raw(cfg, "heldout", "Github",
              [(i, f"class C{i}:\n    pass\n{body('ghh', 200, i)}")
               for i in range(n_heldout)])
    write_raw(cfg, "heldout", "USPTO Backgrounds",
              [(i, f"A background of the invention. {body('us', 300, i)}")
               for i in range(n_heldout)])
    return {"train_texts": train_texts, "heldout": held}
