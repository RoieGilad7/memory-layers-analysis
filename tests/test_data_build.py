"""The build is reproducible: same config + same input -> byte-identical output."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import build, dedup, split
from data.common import load_config, read_jsonl
from tests._data_fixtures import CONFIG, build_corpus, make_cfg

ROOT = Path(__file__).resolve().parent.parent


def _digest_tree(root: Path) -> dict:
    """sha256 of every output file, keyed by path relative to the root.

    JSON reports are excluded: they carry wall-clock timings on purpose.
    """
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix != ".json":
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _run(root: Path) -> dict:
    cfg = make_cfg(root)
    build_corpus(cfg, n_heldout=20)
    dedup.run(cfg)
    split.run(cfg)
    return _digest_tree(cfg.root)


def test_same_config_gives_byte_identical_output(tmp_path):
    a = _run(tmp_path / "a")
    b = _run(tmp_path / "b")
    assert a == b
    assert len(a) >= 6                      # train + pool + both halves


def test_gzip_outputs_carry_no_timestamp(tmp_path):
    """mtime must be zeroed, or two runs minutes apart differ byte for byte."""
    cfg = make_cfg(tmp_path / "out")
    build_corpus(cfg)
    dedup.run(cfg)
    for p in cfg.train_dir.glob("*.jsonl.gz"):
        header = p.read_bytes()[:8]
        assert header[4:8] == b"\x00\x00\x00\x00", f"{p} has a gzip mtime"


def test_records_are_sorted_key_json(tmp_path):
    cfg = make_cfg(tmp_path / "out")
    build_corpus(cfg)
    dedup.run(cfg)
    import gzip
    with gzip.open(cfg.train_dir / "pile_cc.jsonl.gz", "rt", encoding="utf-8") as fh:
        line = fh.readline().strip()
    obj = json.loads(line)
    assert list(obj) == sorted(obj)
    assert set(obj) == {"doc_id", "subject", "split", "source", "line",
                        "n_tokens", "truncated", "sha256", "text"}


def test_manifest_records_the_pinned_revision_and_fingerprint(tmp_path):
    cfg = make_cfg(tmp_path / "out")
    build_corpus(cfg)
    dedup.run(cfg)
    rep = split.run(cfg)
    log = json.loads((cfg.reports_dir / "dedup_log.json").read_text())
    assert log["config_fingerprint"] == cfg.fingerprint() == rep["config_fingerprint"]
    assert cfg.revision == "3be90335b66f24456a5d6659d9c8d208c0357119"


def test_cli_is_wired_up():
    out = subprocess.run([sys.executable, "-m", "data.build", "--help"],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0
    assert "--stage" in out.stdout and "--small" in out.stdout
    assert "pile" in out.stdout


def test_real_config_loads_and_is_self_consistent():
    cfg = load_config(CONFIG)
    assert cfg.train_tokens_per_subject * len(cfg.train_subjects) == \
        int(cfg.total_train_tokens * (1 - cfg.bio_share))
    assert cfg.heldout_tokens_per_half * len(cfg.heldout_halves) == \
        cfg.heldout_tokens_per_subject
    assert set(cfg.source_tags) >= set(cfg.train_files + cfg.heldout_files)
    assert "train/00.jsonl.zst" not in cfg.train_fallback_files
    assert "train/00.jsonl.zst" not in cfg.heldout_fallback_files
