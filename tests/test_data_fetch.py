"""The bundle manifest and the fetch/verify path. No network."""
import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import fetch, manifest as manifest_mod
from data.common import DataConfig
from tests._data_fixtures import CONFIG


def make_cfg(root: Path, manifests: Path) -> DataConfig:
    raw = yaml.safe_load(CONFIG.read_text())
    r = str(root)
    raw["paths"] = {"root": r, "raw": f"{r}/raw", "work": f"{r}/_work",
                    "train": f"{r}/train", "heldout_pool": f"{r}/heldout_pool",
                    "heldout": f"{r}/heldout", "reports": f"{r}/reports"}
    raw["small"]["root"] = r
    raw["distribution"]["manifest_dir"] = str(manifests)
    return DataConfig(raw=raw)


@pytest.fixture
def bundle(tmp_path):
    """A miniature data/v1/ with a required file, an optional one and scratch."""
    root = tmp_path / "v1"
    (root / "tokens").mkdir(parents=True)
    (root / "tokens" / "train.bin").write_bytes(b"\x01\x02" * 100)
    (root / "tokens" / "train.idx.parquet").write_bytes(b"idx-bytes")
    (root / "raw" / "train").mkdir(parents=True)
    (root / "raw" / "train" / "pile_cc.jsonl.gz").write_bytes(b"raw-bytes" * 50)
    (root / "_work").mkdir()
    (root / "_work" / "scratch.tmp").write_bytes(b"scratch")
    (root / "reports").mkdir()
    (root / "reports" / "pack_report.json").write_text("{}")
    cfg = make_cfg(root, tmp_path / "manifests")
    man = manifest_mod.run(cfg)
    return cfg, man


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------
def test_manifest_lists_every_bundle_file_with_bytes_and_sha256(bundle):
    cfg, man = bundle
    paths = {f["path"] for f in man["files"]}
    assert paths == {"tokens/train.bin", "tokens/train.idx.parquet",
                     "raw/train/pile_cc.jsonl.gz", "reports/pack_report.json"}
    assert "_work/scratch.tmp" not in paths, "scratch must not enter the bundle"
    assert "manifest.json" not in paths, "the manifest cannot list itself"
    for f in man["files"]:
        assert f["bytes"] == (cfg.root / f["path"]).stat().st_size
        assert len(f["sha256"]) == 64
    assert man["n_files"] == 4


def test_manifest_records_provenance(bundle):
    cfg, man = bundle
    assert man["source"]["revision"] == cfg.revision
    assert man["config"]["fingerprint_pack"] == cfg.fingerprint("pack")
    assert man["config"]["fingerprint_pile"] == cfg.fingerprint("pile")
    assert man["config"]["seed"] == cfg.seed
    assert "commit" in man["git"]
    assert man["distribution"]["tag"] == cfg.hf_tag


def test_manifest_separates_optional_bytes(bundle):
    cfg, man = bundle
    raw = next(f for f in man["files"] if f["path"].startswith("raw/"))
    assert raw["optional"] is True
    assert all(f["optional"] is False for f in man["files"]
               if not f["path"].startswith("raw/"))
    b = man["bytes"]
    assert b["required"] + b["optional"] == b["total"]
    assert b["optional"] == raw["bytes"]


def test_a_committed_copy_is_written(bundle):
    cfg, man = bundle
    committed = cfg.manifest_dir / f"{cfg.version}.json"
    assert committed.exists()
    assert json.loads(committed.read_text())["files"] == man["files"]


# --------------------------------------------------------------------------
# verify
# --------------------------------------------------------------------------
def test_verify_only_passes_on_a_good_bundle(bundle):
    cfg, man = bundle
    r = fetch.verify(man, cfg.root, with_raw=False,
                     optional_prefixes=tuple(cfg.optional_prefixes),
                     progress=False)
    assert r["passed"] and r["ok"] == 3 and r["skipped"] == 1
    r2 = fetch.verify(man, cfg.root, with_raw=True,
                      optional_prefixes=tuple(cfg.optional_prefixes),
                      progress=False)
    assert r2["passed"] and r2["ok"] == 4 and r2["skipped"] == 0


def test_one_flipped_byte_fails_verification(bundle):
    cfg, man = bundle
    path = cfg.root / "tokens" / "train.bin"
    data = bytearray(path.read_bytes())
    data[17] ^= 0x01                       # same length, one bit different
    path.write_bytes(bytes(data))

    r = fetch.verify(man, cfg.root, with_raw=False,
                     optional_prefixes=tuple(cfg.optional_prefixes),
                     progress=False)
    assert not r["passed"]
    assert [b["reason"] for b in r["bad"]] == ["sha256"]
    assert r["bad"][0]["path"] == "tokens/train.bin"

    with pytest.raises(RuntimeError, match="failed verification"):
        fetch.require_verified(cfg, cfg.version)


def test_a_truncated_file_is_caught_by_size(bundle):
    cfg, man = bundle
    (cfg.root / "tokens" / "train.bin").write_bytes(b"\x01\x02" * 50)
    r = fetch.verify(man, cfg.root, optional_prefixes=("raw/",), progress=False)
    assert not r["passed"] and r["bad"][0]["reason"] == "size"


def test_a_missing_file_is_reported(bundle):
    cfg, man = bundle
    (cfg.root / "tokens" / "train.idx.parquet").unlink()
    r = fetch.verify(man, cfg.root, optional_prefixes=("raw/",), progress=False)
    assert not r["passed"] and r["missing"] == ["tokens/train.idx.parquet"]


def test_require_verified_returns_the_manifest_hash(bundle):
    cfg, man = bundle
    r = fetch.require_verified(cfg, cfg.version)
    assert r["passed"] and r["version"] == cfg.version
    assert r["manifest_sha256"] == manifest_mod.sha256_file(
        cfg.manifest_dir / f"{cfg.version}.json")


def test_a_missing_manifest_says_how_to_make_one(tmp_path):
    cfg = make_cfg(tmp_path / "v1", tmp_path / "nowhere")
    with pytest.raises(SystemExit, match="data.manifest"):
        fetch.load_manifest(cfg, "v1")


# --------------------------------------------------------------------------
# download refuses while the repo is a placeholder
# --------------------------------------------------------------------------
def test_download_refuses_the_placeholder_repo_but_names_the_way_out(bundle):
    cfg, man = bundle
    assert fetch.PLACEHOLDER in cfg.hf_repo, \
        "the config should still carry the placeholder until the freeze"
    with pytest.raises(SystemExit, match="placeholder"):
        fetch.download(cfg, man, with_raw=False)


def test_verify_only_cli_passes_and_then_fails_without_the_network(bundle, monkeypatch):
    cfg, man = bundle
    monkeypatch.setattr(fetch, "load_config", lambda *a, **k: cfg)
    monkeypatch.setattr(fetch, "download",
                        lambda *a, **k: pytest.fail("no network"))
    assert fetch.main(["--version", cfg.version, "--verify-only"]) == 0
    data = bytearray((cfg.root / "tokens" / "train.bin").read_bytes())
    data[3] ^= 0xFF
    (cfg.root / "tokens" / "train.bin").write_bytes(bytes(data))
    assert fetch.main(["--version", cfg.version, "--verify-only"]) == 1
