"""The fixed evaluation sets: the same items for every run, every checkpoint.

    python -m memlayers.eval.eval_sets --version v1            # build + write the manifest
    python -m memlayers.eval.eval_sets --version v1 --check    # verify only

Two sets, both chosen from the DATA seed in configs/data/v1.yaml and never the
run seed:

  heldout_sample  200 documents per subject from the held-out test half, for
                  the 5 Pile training subjects and USPTO (ids only)
  fact_sample     the fact rows `data.q2_probe.select_eval_rows` picks: every
                  frequent-tier person and 300 random people from each other
                  tier and the controls, roles test and paraphrase (ids only)

They are written as JSON under `<data root>/eval_sets/` and their sha256s go
into the committed `data/manifests/eval_sets_<version>.json`. A run refuses to
start if the files on disk do not match that manifest. Training prompt 4 adds
a third set (`readlog_tokens`) to the same manifest; it is checked by the
read-log pass only, never at run start (`RUN_START_SETS` below).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "HELDOUT_PER_SUBJECT",
    "RUN_START_SETS",
    "build",
    "verify",
    "eval_sets_dir",
    "manifest_file",
    "load_heldout_sample",
    "load_fact_sample",
    "EvalSetMismatch",
]

HELDOUT_PER_SUBJECT = 200
HELDOUT_HALF = "test"
RUN_START_SETS = ("heldout_sample", "fact_sample")
# the read-log pass's tokens: checked by memlayers.readlog_pass, never at run
# start, so changing the read-log budget after the pilot never blocks training
READLOG_SET = "readlog_tokens"
READLOG_HALF = "label"
READLOG_TOKENS_PER_SUBJECT = 1_000_000
READLOG_BIO_FRACTION = 0.10


class EvalSetMismatch(RuntimeError):
    pass


def eval_sets_dir(dcfg) -> Path:
    return Path(dcfg.root) / "eval_sets"


def manifest_file(dcfg) -> Path:
    small = "_small" if getattr(dcfg, "small", False) else ""
    return Path(dcfg.manifest_dir) / f"eval_sets_{dcfg.version}{small}.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dump(obj: Any) -> bytes:
    # one canonical byte form, so two builds are byte-identical
    return (
        json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode()


# ------------------------------------------------------------------- selection
def select_heldout_sample(
    dcfg, per_subject: int = HELDOUT_PER_SUBJECT
) -> Dict[str, List[str]]:
    """{slug: [doc_id, ...]}: a keyed draw per subject, sorted by doc id."""
    from data import pack
    from data.common import keyed_rng

    index = pack.read_index(
        Path(dcfg.heldout_tokens_dir) / f"{HELDOUT_HALF}.idx.parquet"
    )
    by_subject: Dict[str, List[str]] = {}
    for doc_id, subject in zip(index["doc_id"], index["subject"]):
        by_subject.setdefault(subject, []).append(doc_id)
    out: Dict[str, List[str]] = {}
    for subject in dcfg.all_subjects:
        ids = sorted(by_subject.get(subject, []))
        if len(ids) > per_subject:
            ids = sorted(
                keyed_rng(dcfg.seed, "eval_heldout", subject).sample(ids, per_subject)
            )
        out[dcfg.slug(subject)] = ids
    return out


def select_readlog_heldout(dcfg, tokens_per_subject: int) -> Dict[str, List[str]]:
    """{slug: [doc_id, ...]} from the LABEL half, 5 training subjects only:
    whole documents in a keyed order until the subject reaches the budget
    (the document that crosses it is kept whole)."""
    from data import pack
    from data.common import keyed_rng

    index = pack.read_index(
        Path(dcfg.heldout_tokens_dir) / f"{READLOG_HALF}.idx.parquet"
    )
    by_subject: Dict[str, List[tuple]] = {}
    for doc_id, subject, length in zip(
        index["doc_id"], index["subject"], index["length"]
    ):
        by_subject.setdefault(subject, []).append((doc_id, int(length)))
    out: Dict[str, List[str]] = {}
    for subject in dcfg.train_subjects:
        docs = sorted(by_subject.get(subject, []))
        keyed_rng(dcfg.seed, "readlog_heldout", subject).shuffle(docs)
        take, total = [], 0
        for doc_id, length in docs:
            if total >= tokens_per_subject:
                break
            take.append(doc_id)
            total += length
        out[dcfg.slug(subject)] = take
    return out


def select_readlog_facts(dcfg, fraction: float = READLOG_BIO_FRACTION) -> List[str]:
    """Every test/paraphrase fact of the frequent tier, and of a keyed
    `fraction` of the people of each other tier (whole people, so a person's
    prompts are all in or all out)."""
    import math

    from data.common import keyed_rng, read_jsonl

    people: Dict[str, List[str]] = {}
    for p in read_jsonl(Path(dcfg.bios_dir) / "people.jsonl"):
        people.setdefault(p["tier"], []).append(p["person_id"])
    chosen = set()
    for tier, ids in sorted(people.items()):
        ids = sorted(ids)
        if tier == "frequent":
            chosen.update(ids)
        else:
            k = max(1, math.ceil(fraction * len(ids)))
            chosen.update(keyed_rng(dcfg.seed, "readlog_bio", tier).sample(ids, k))
    rows = [
        r
        for r in read_jsonl(Path(dcfg.bios_dir) / "facts.jsonl")
        if r["person_id"] in chosen and r["role"] in ("test", "paraphrase")
    ]
    rows.sort(key=lambda r: r["fact_id"])
    return [r["fact_id"] for r in rows]


def select_fact_sample(dcfg, per_tier: int = 300) -> List[str]:
    from data.q2_probe import select_eval_rows

    return [r["fact_id"] for r in select_eval_rows(dcfg, per_tier=per_tier)]


# ----------------------------------------------------------------------- build
def build(
    dcfg,
    write_manifest: bool = True,
    per_subject: int = HELDOUT_PER_SUBJECT,
    per_tier: int = 300,
    readlog_tokens_per_subject: int = READLOG_TOKENS_PER_SUBJECT,
    readlog_bio_fraction: float = READLOG_BIO_FRACTION,
) -> Dict[str, Any]:
    """`per_subject` / `per_tier` are for test fixtures only; v1 uses the
    defaults. The read-log budget is `eval.readlog.tokens_per_subject`: the
    pilot may change it, and that changes the readlog_tokens hash, by design."""
    out_dir = eval_sets_dir(dcfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    held = select_heldout_sample(dcfg, per_subject)
    facts = select_fact_sample(dcfg, per_tier)
    rl_docs = select_readlog_heldout(dcfg, readlog_tokens_per_subject)
    rl_facts = select_readlog_facts(dcfg, readlog_bio_fraction)
    files = {
        "heldout_sample": {
            "version": dcfg.version,
            "kind": "heldout_sample",
            "half": HELDOUT_HALF,
            "data_seed": dcfg.seed,
            "per_subject": per_subject,
            "doc_ids": held,
        },
        "fact_sample": {
            "version": dcfg.version,
            "kind": "fact_sample",
            "data_seed": dcfg.seed,
            "selection": f"data.q2_probe.select_eval_rows (per_tier={per_tier}, roles test+paraphrase)",
            "fact_ids": facts,
        },
        READLOG_SET: {
            "version": dcfg.version,
            "kind": READLOG_SET,
            "data_seed": dcfg.seed,
            "heldout_half": READLOG_HALF,
            "tokens_per_subject": int(readlog_tokens_per_subject),
            "bio_fraction": float(readlog_bio_fraction),
            "bio_selection": "every frequent-tier person; a keyed fraction of the "
            "people of each other tier; roles test+paraphrase; each prompt is run "
            "followed by its true value's tokens",
            "doc_ids": rl_docs,
            "fact_ids": rl_facts,
        },
    }
    entries = {}
    for name, obj in files.items():
        path = out_dir / f"{name}.json"
        path.write_bytes(_dump(obj))
        n = {
            "fact_sample": len(facts),
            "heldout_sample": sum(len(v) for v in held.values()),
            READLOG_SET: sum(len(v) for v in rl_docs.values()) + len(rl_facts),
        }[name]
        entries[name] = {
            "path": f"eval_sets/{name}.json",
            "sha256": _sha(path),
            "bytes": path.stat().st_size,
            "n_items": n,
        }
    man = {"version": dcfg.version, "data_seed": dcfg.seed, "sets": entries}
    if write_manifest:
        mf = manifest_file(dcfg)
        mf.parent.mkdir(parents=True, exist_ok=True)
        old = json.loads(mf.read_text()) if mf.exists() else {}
        # keep any set this build does not make
        merged = dict(old.get("sets", {}))
        merged.update(entries)
        man["sets"] = dict(sorted(merged.items()))
        mf.write_bytes(_dump(man))
    return man


def verify(dcfg, names=RUN_START_SETS) -> Dict[str, str]:
    """{set: sha256} if every named set matches the committed manifest; raises
    EvalSetMismatch otherwise."""
    mf = manifest_file(dcfg)
    if not mf.exists():
        raise EvalSetMismatch(
            f"no eval-set manifest {mf}. Build it with "
            f"`python -m memlayers.eval.eval_sets --version {dcfg.version}`."
        )
    sets = json.loads(mf.read_text())["sets"]
    out = {}
    for name in names:
        if name not in sets:
            raise EvalSetMismatch(f"{mf} has no entry for {name}")
        path = Path(dcfg.root) / sets[name]["path"]
        if not path.exists():
            raise EvalSetMismatch(
                f"{path} is missing. Build it with "
                f"`python -m memlayers.eval.eval_sets --version {dcfg.version}` "
                "(deterministic: it reproduces the committed hashes)."
            )
        got = _sha(path)
        if got != sets[name]["sha256"]:
            raise EvalSetMismatch(
                f"{path} has sha256 {got[:16]}, but {mf} commits "
                f"{sets[name]['sha256'][:16]}. Every run must be evaluated on "
                "the same items; rebuild the set, or if the change is intended, "
                "commit the new manifest."
            )
        out[name] = got
    return out


def load_heldout_sample(dcfg) -> Dict[str, List[str]]:
    return json.loads((eval_sets_dir(dcfg) / "heldout_sample.json").read_text())[
        "doc_ids"
    ]


def load_readlog_tokens(dcfg) -> Dict[str, Any]:
    return json.loads((eval_sets_dir(dcfg) / f"{READLOG_SET}.json").read_text())


def load_fact_sample(dcfg) -> List[str]:
    return json.loads((eval_sets_dir(dcfg) / "fact_sample.json").read_text())[
        "fact_ids"
    ]


def main(argv: Optional[List[str]] = None) -> int:

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--version", default="v1")
    ap.add_argument(
        "--data-config", default=None, help="default configs/data/<version>.yaml"
    )
    ap.add_argument("--check", action="store_true", help="verify only")
    ap.add_argument("--small", action="store_true", help="the 1%% build")
    ap.add_argument(
        "--data-root",
        default="data",
        help="where the bundle lives (data.root), e.g. a Google Drive folder",
    )
    ap.add_argument(
        "--readlog-tokens-per-subject",
        type=int,
        default=READLOG_TOKENS_PER_SUBJECT,
        help="eval.readlog.tokens_per_subject (changes the readlog_tokens hash)",
    )
    ap.add_argument(
        "--root", default=None, help="with --small: re-root it, e.g. data/v1_sample"
    )
    a = ap.parse_args(argv)
    from memlayers.train import load_bundle_config

    dcfg = load_bundle_config(
        {
            "data_config": a.data_config or f"configs/data/{a.version}.yaml",
            "small": a.small,
            "bundle": a.root,
            "root": a.data_root,
        }
    )
    if a.check:
        for k, v in verify(dcfg, RUN_START_SETS + (READLOG_SET,)).items():
            print(f"{k}: OK {v}")
        return 0
    man = build(dcfg, readlog_tokens_per_subject=a.readlog_tokens_per_subject)
    for k, v in man["sets"].items():
        print(f"{k}: {v['n_items']:,} items, {v['bytes']:,} B, sha256 {v['sha256']}")
    print(f"-> {manifest_file(dcfg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
