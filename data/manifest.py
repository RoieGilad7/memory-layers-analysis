"""The bundle manifest -- what `data/v1/` contains and what it should hash to.

    python -m data.manifest --config configs/data/v1.yaml

Writes `data/v1/manifest.json` (every file: path, bytes, sha256, plus the
counts) and a copy to `data/manifests/v1.json`, which IS committed to git while
`data/v1/` is not. That committed copy is what `data.fetch` verifies a download
against, and what a reviewer can read without the 2 GB bundle.

The manifest is the one place that answers "is this the right data?": the
config fingerprint, the pinned Pile revision, the git commit, and a hash per
file. `data.fetch --verify-only` and `memlayers.train` with `data: real` both
refuse to proceed on any mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from data.common import ROOT, DataConfig, load_config, write_json

CHUNK = 1 << 20
# Written by this module, so it cannot be inside its own file list.
MANIFEST_NAME = "manifest.json"
# Working files that are not part of the bundle.
EXCLUDE_DIRS = {"_work", "_parts"}
EXCLUDE_NAMES = {".DS_Store", MANIFEST_NAME}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def git_commit() -> Dict[str, Any]:
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:                                      # pragma: no cover
            return ""
    return {"commit": run("rev-parse", "HEAD"),
            "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def iter_bundle_files(root: Path) -> List[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in EXCLUDE_NAMES:
            continue
        if set(p.relative_to(root).parts) & EXCLUDE_DIRS:
            continue
        out.append(p)
    return out


def _load(path: Path) -> Optional[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else None


def build(cfg: DataConfig) -> Dict[str, Any]:
    t0 = time.time()
    root = cfg.root
    files: List[Dict[str, Any]] = []
    by_prefix: Dict[str, Dict[str, int]] = {}
    for p in iter_bundle_files(root):
        rel = p.relative_to(root).as_posix()
        size = p.stat().st_size
        files.append({"path": rel, "bytes": size, "sha256": sha256_file(p),
                      "optional": any(rel.startswith(pre)
                                      for pre in cfg.optional_prefixes)})
        top = rel.split("/")[0]
        slot = by_prefix.setdefault(top, {"files": 0, "bytes": 0})
        slot["files"] += 1
        slot["bytes"] += size

    pile = _load(cfg.reports_dir / "pile_manifest.json")
    bios = _load(cfg.bios_dir / "manifest.json")
    packr = _load(cfg.reports_dir / "pack_report.json")

    counts: Dict[str, Any] = {"train": {}, "heldout": {}, "biographies": {}}
    if packr:
        counts["train"] = {
            "tokens": packr["train"]["tokens"],
            "sequences": packr["train"]["sequences"],
            "block_size": packr["block_size"],
            "index_rows": packr["train"]["index_rows"],
            "per_subject": packr["train"]["per_subject"],
            "eot_pad_tokens": packr["train"]["eot_pad_tokens"],
            "filler_tokens": packr["train"]["filler_tokens"],
        }
        counts["heldout"] = {
            h: {"tokens": v["tokens"], "documents": v["documents"],
                "per_subject": v["per_subject"]}
            for h, v in packr["heldout"].items()}
        counts["biographies"] = {
            "copies": packr["biographies"]["copies"],
            "tokens": packr["biographies"]["tokens"],
            "distinct_biographies": packr["biographies"]["distinct_biographies"],
            "per_tier": packr["biographies"]["per_tier"],
        }
    if bios:
        counts["biographies"]["people"] = bios["people"]["by_split"]
        counts["biographies"]["by_tier"] = bios["people"]["by_tier"]
        counts["biographies"]["facts_rows"] = bios["facts"]["rows"]
    if pile:
        counts["pile_documents"] = {
            s: {"train_documents": v["train"]["docs"],
                "train_tokens_available": v["train"]["tokens"],
                "heldout_pool_documents": v["heldout"]["pool_docs"]}
            for s, v in pile["subjects"].items()}

    total = sum(f["bytes"] for f in files)
    optional = sum(f["bytes"] for f in files if f["optional"])
    manifest = {
        "version": cfg.version,
        "small": cfg.small,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": {
            "path": "configs/data/v1.yaml",
            "fingerprint_pile": cfg.fingerprint("pile"),
            "fingerprint_bios": cfg.fingerprint("bios"),
            "fingerprint_pack": cfg.fingerprint("pack"),
            "fingerprint_all": cfg.fingerprint(),
            "seed": cfg.seed,
        },
        "source": {"dataset": cfg.dataset, "revision": cfg.revision,
                   "tokenizer": cfg.tokenizer_name,
                   "vocab_size": cfg.vocab_size},
        "git": git_commit(),
        "distribution": {"hf_repo": cfg.hf_repo, "repo_type": cfg.hf_repo_type,
                         "tag": cfg.hf_tag,
                         "optional_prefixes": cfg.optional_prefixes},
        "counts": counts,
        "bytes": {"total": total, "optional": optional,
                  "required": total - optional, "by_prefix": by_prefix},
        "n_files": len(files),
        "files": files,
        "seconds": round(time.time() - t0, 1),
    }
    return manifest


def run(cfg: DataConfig) -> Dict[str, Any]:
    manifest = build(cfg)
    write_json(cfg.manifest_path, manifest)
    committed = cfg.manifest_dir / f"{cfg.version}.json"
    if cfg.small:
        committed = cfg.manifest_dir / f"{cfg.version}_small.json"
    write_json(committed, manifest)
    b = manifest["bytes"]
    print(f"[manifest] {manifest['n_files']} files, "
          f"{b['total'] / 1e6:,.1f} MB total "
          f"({b['required'] / 1e6:,.1f} MB without raw/)")
    for pre, v in sorted(manifest["bytes"]["by_prefix"].items()):
        print(f"   {pre + '/':20s} {v['files']:>4} files  {v['bytes'] / 1e6:>9,.1f} MB")
    print(f"[manifest] {cfg.manifest_path}")
    print(f"[manifest] {committed}  (committed to git)")
    return manifest


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args(argv)
    run(load_config(args.config, small=args.small))
    return 0


if __name__ == "__main__":
    sys.exit(main())
