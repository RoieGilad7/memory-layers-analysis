"""Small, reproducible evaluation slices of Roie's published data-v1 bundle."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random

import numpy as np


DATA_SHA256 = "bb1bfd407af2c44e86d020df1c075f8764c5bf6979be2835684f6f0453086fd6"
HF_REVISION = "db21410b27824fd321b5e6ad4577d5e7fad65021"
BLOCK_SIZE = 512
ROLES = ("discovery", "test", "paraphrase")
REQUIRED = (
    "tokens/train.bin",
    "tokens/train.idx.parquet",
    "heldout/label.bin",
    "heldout/label.idx.parquet",
    "heldout/test.bin",
    "heldout/test.idx.parquet",
    "bios/attribute_values.json",
    "bios/people.jsonl",
    "bios/facts.jsonl",
)


@dataclass
class V1Slice:
    docs: dict
    facts: list
    vocab: list
    fingerprint: str
    fixture: bool
    context: int
    root: Path
    train_sha256: str
    selection: dict
    people: dict
    value_lists: dict


def _verified_files(root):
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        # The tagged data.fetch command uses the code repository's manifest.
        manifest_path = root.parent / "manifests" / "v1.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"No data-v1 manifest at {root}/manifest.json or {manifest_path}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["files"]
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    if (
        hashlib.sha256(canonical).hexdigest() != DATA_SHA256
        or manifest.get("data_sha256") != DATA_SHA256
    ):
        raise ValueError(
            "Expected the frozen data-v1 manifest; its file list or data_sha256 differs"
        )
    by_path = {e["path"]: e for e in entries}
    verified = {}
    for name in REQUIRED:
        e, path = by_path[name], root / name
        if path.stat().st_size != e["bytes"]:
            raise ValueError(f"data-v1 size mismatch for {name}")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != e["sha256"]:
            raise ValueError(f"data-v1 SHA-256 mismatch for {name}")
        verified[name] = digest
    return verified


def _rows(path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def _sample(ids, count, seed, *parts):
    ids = sorted(ids)
    if count > len(ids):
        raise ValueError(
            f"Requested {count} items from {'/'.join(parts)}, which has {len(ids)}"
        )
    if count == len(ids):
        return ids
    # The first two keys for the person sample match data.q2_probe.select_eval_rows.
    key = ":".join([str(seed), *parts]).encode()
    key_seed = int.from_bytes(hashlib.blake2b(key, digest_size=8).digest(), "big")
    return sorted(random.Random(key_seed).sample(ids, count))


def _heldout_docs(root, docs_per_subject, doc_tokens, seed):
    import pyarrow.parquet as pq

    docs = {}
    for split, half in (("discovery", "label"), ("eval", "test")):
        stem = root / "heldout" / half
        index = pq.read_table(
            stem.with_suffix(".idx.parquet"),
            columns=["doc_id", "subject", "start", "length", "doc_offset"],
        )
        by_id = {row["doc_id"]: row for row in index.to_pylist()}
        by_subject = defaultdict(list)
        for identifier, row in by_id.items():
            by_subject[row["subject"]].append(identifier)
        tokens = np.memmap(stem.with_suffix(".bin"), dtype="<u2", mode="r")
        group = []
        for subject, ids in sorted(by_subject.items()):
            for identifier in _sample(
                ids, docs_per_subject, seed, "documents", half, subject
            ):
                row = by_id[identifier]
                start, length = row["start"], row["length"]
                if (
                    row["doc_offset"] != 0
                    or length < 2
                    or start < 0
                    or start + length > len(tokens)
                ):
                    raise ValueError(
                        f"Invalid data-v1 held-out segment for {identifier}"
                    )
                window = tokens[start : start + min(length, doc_tokens + 1)].tolist()
                group.append(
                    dict(
                        doc_id=identifier,
                        subject=subject,
                        split=split,
                        tokens=window,
                        source_half=half,
                        start=start,
                        source_length=length,
                    )
                )
        docs[split] = group
    return docs


def _facts(root, chosen_ids, people, values, enc):
    candidates = {
        attr: [
            enc.encode_ordinary(" " + v)[: 2 if attr == "birth_date" else 1]
            for v in pool
        ]
        for attr, pool in values.items()
    }
    answer_indexes = {
        a: {v: i for i, v in enumerate(pool)} for a, pool in values.items()
    }
    for attr, keys in candidates.items():
        if len({tuple(key) for key in keys}) != len(keys):
            raise ValueError(f"Non-unique candidate scoring keys for {attr}")
    facts = []
    by_context = defaultdict(list)
    for row in _rows(root / "bios/facts.jsonl"):
        pid, attr = row["person_id"], row["attribute"]
        if pid not in chosen_ids:
            continue
        person = people[pid]
        gold = person["facts"][attr]
        if (gold, person["tier"], person["split"]) != (
            row["true_value"],
            row["tier"],
            row["split"],
        ):
            raise ValueError(f"Inconsistent data-v1 person join at {row['fact_id']}")
        role, prompt = row["role"], row["prompt"]
        if role not in ROLES:
            raise ValueError(f"Unknown fact role {role}")
        ids = enc.encode_ordinary(prompt)
        value_ids = row["value_token_ids"]
        if enc.encode_ordinary(prompt + row["continuation"]) != ids + value_ids:
            raise ValueError(f"Unexpected GPT-2 answer boundary in {row['fact_id']}")
        answer = answer_indexes[attr][gold]
        key = candidates[attr][answer]
        if key != value_ids[: len(key)]:
            raise ValueError(f"Incorrect candidate key at {row['fact_id']}")
        f = dict(
            row_id=row["fact_id"],
            fact_id=f"{pid}-{attr}",
            person=pid,
            attribute=attr,
            doc_id=row["doc_id"] or row["fact_id"],
            source_split=row["split"],
            tier=row["tier"],
            role=role,
            split="discovery" if role == "discovery" else "eval",
            rewording_id=row["rewording_id"],
            template_id=row["template_id"],
            prompt=ids,
            prompt_text=prompt,
            true_value=gold,
            candidates=candidates[attr],
            answer=answer,
        )
        facts.append(f)
        if role != "paraphrase":
            by_context[pid, f["rewording_id"]].append(f)
    # Paraphrase templates replace the target sentence of training rewording zero.
    position = {}
    for (pid, wording), group in by_context.items():
        for i, f in enumerate(sorted(group, key=lambda x: len(x["prompt_text"]))):
            position[pid, wording, f["attribute"]] = i
    for f in facts:
        wording = f["rewording_id"] if f["role"] != "paraphrase" else 0
        f["preceding_fact_count"] = position[f["person"], wording, f["attribute"]]
    return facts


def load_v1_slice(
    root, *, seed=17, people_per_tier=1, docs_per_subject=1, doc_tokens=64
):
    """Read selected docs and facts only; fingerprint identifies the entire verified release."""
    import tiktoken

    if any(
        type(v) is not int or v < 1
        for v in (people_per_tier, docs_per_subject, doc_tokens)
    ):
        raise ValueError(
            "people_per_tier, docs_per_subject and doc_tokens must be positive integers"
        )
    if doc_tokens > BLOCK_SIZE:
        raise ValueError(
            f"Document prefix exceeds the {BLOCK_SIZE}-token native context"
        )
    root = Path(root).resolve()
    verified = _verified_files(root)
    enc = tiktoken.get_encoding("gpt2")
    vocab = [enc.decode([i]) for i in range(enc.n_vocab)]
    if len(vocab) != 50257:
        raise ValueError("data-v1 requires the GPT-2 vocabulary with 50,257 tokens")
    people = {p["person_id"]: p for p in _rows(root / "bios/people.jsonl")}
    by_tier = defaultdict(list)
    for pid, p in people.items():
        by_tier[p["tier"]].append(pid)
    chosen = {
        tier: _sample(ids, people_per_tier, seed, "q2_eval", tier)
        for tier, ids in sorted(by_tier.items())
    }
    values = json.loads(
        (root / "bios/attribute_values.json").read_text(encoding="utf-8")
    )["values"]
    facts = _facts(
        root, {pid for ids in chosen.values() for pid in ids}, people, values, enc
    )
    docs = _heldout_docs(root, docs_per_subject, doc_tokens, seed)
    context = max(
        max(len(d["tokens"]) - 1 for group in docs.values() for d in group),
        max(len(f["prompt"]) + len(f["candidates"][0]) - 1 for f in facts),
    )
    selection = dict(
        release="data-v1",
        hf_revision=HF_REVISION,
        seed=seed,
        people_per_tier=people_per_tier,
        docs_per_subject=docs_per_subject,
        max_document_targets=doc_tokens,
        people_by_tier=chosen,
        document_windows={
            split: [
                {k: v for k, v in d.items() if k != "tokens"}
                | {"scored_tokens": len(d["tokens"]) - 1}
                for d in group
            ]
            for split, group in docs.items()
        },
        fact_rows_by_role=dict(Counter(f["role"] for f in facts)),
        policy="Sample people per tier and whole documents per subject by keyed seed; "
        "use the first in-document targets and all 8 prompt rows per selected fact.",
        verified_file_sha256=verified,
    )
    return V1Slice(
        docs=docs,
        facts=facts,
        vocab=vocab,
        fingerprint=DATA_SHA256,
        fixture=False,
        context=context,
        root=root,
        train_sha256=verified["tokens/train.bin"],
        selection=selection,
        people=people,
        value_lists=values,
    )
