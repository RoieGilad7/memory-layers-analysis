"""Fetch and verify the frozen data bundle.

    python -m data.fetch --version v1                 # download + verify
    python -m data.fetch --version v1 --with-raw      # include raw/ (398 MB more)
    python -m data.fetch --version v1 --verify-only    # offline: verify only

The authority is `data/manifests/<version>.json`, which is committed to git
while `data/v1/` is not. Every file is checked against its recorded sha256, so
a truncated download, a wrong tag or an edited file is caught before training
reads a single token. `--verify-only` touches the network never, which is what
`memlayers.train` calls with `data: real` before step 0.

`raw/` -- prompt 1's archived source text -- is skipped by default: a rebuild
needs it, training does not.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from data.common import ROOT, DataConfig, load_config
from data.manifest import sha256_file

PLACEHOLDER = "<owner>"


def _rel(path: Path) -> str:
    """Repo-relative when it can be, absolute otherwise (tests use tmp dirs)."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------
def manifest_path(cfg: DataConfig, version: str) -> Path:
    """Where the committed manifest for this build lives.

    `data.manifest` writes `<version>_small.json` for a `--small` build, so the
    verifier has to look in the same place or it checks a 1% bundle against the
    full one.
    """
    name = f"{version}_small.json" if cfg.small else f"{version}.json"
    return cfg.manifest_dir / name


def load_manifest(cfg: DataConfig, version: str) -> Dict[str, Any]:
    path = manifest_path(cfg, version)
    if not path.exists():
        raise SystemExit(
            f"no committed manifest at {_rel(path)}. Build one with "
            "`python -m data.manifest --config configs/data/v1.yaml`.")
    return json.loads(path.read_text())


def verify(manifest: Dict[str, Any], root: Path, with_raw: bool = False,
           optional_prefixes: Tuple[str, ...] = ("raw/",),
           progress: bool = True) -> Dict[str, Any]:
    """Check every file's size and sha256 against the manifest."""
    ok: List[str] = []
    bad: List[Dict[str, Any]] = []
    missing: List[str] = []
    skipped: List[str] = []
    t0 = time.time()
    total = len(manifest["files"])
    for i, entry in enumerate(manifest["files"], 1):
        rel = entry["path"]
        optional = entry.get("optional") or any(
            rel.startswith(p) for p in optional_prefixes)
        if optional and not with_raw:
            skipped.append(rel)
            continue
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        size = path.stat().st_size
        if size != entry["bytes"]:
            bad.append({"path": rel, "reason": "size",
                        "expected": entry["bytes"], "got": size})
            continue
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            bad.append({"path": rel, "reason": "sha256",
                        "expected": entry["sha256"], "got": digest})
            continue
        ok.append(rel)
        if progress and i % 10 == 0:
            print(f"[fetch] verified {i}/{total}", flush=True)
    return {"ok": len(ok), "bad": bad, "missing": missing,
            "skipped": len(skipped), "checked": len(ok) + len(bad) + len(missing),
            "passed": not bad and not missing,
            "seconds": round(time.time() - t0, 1)}


def require_verified(cfg: DataConfig, version: str, with_raw: bool = False,
                     progress: bool = False) -> Dict[str, Any]:
    """Verify or raise. This is what a training run calls before step 0."""
    manifest = load_manifest(cfg, version)
    result = verify(manifest, cfg.root, with_raw=with_raw,
                    optional_prefixes=tuple(cfg.optional_prefixes),
                    progress=progress)
    if not result["passed"]:
        lines = [f"data bundle {version} failed verification against "
                 f"{_rel(manifest_path(cfg, version))}:"]
        for b in result["bad"][:10]:
            lines.append(f"  {b['path']}: {b['reason']} mismatch "
                         f"(expected {str(b['expected'])[:16]}, "
                         f"got {str(b['got'])[:16]})")
        for m in result["missing"][:10]:
            lines.append(f"  {m}: missing")
        extra = len(result["bad"]) + len(result["missing"]) - 20
        if extra > 0:
            lines.append(f"  ... and {extra} more")
        lines.append("Re-fetch with `python -m data.fetch --version "
                     f"{version}` or rebuild with `python -m data.pack`.")
        raise RuntimeError("\n".join(lines))
    return {"version": version, "manifest_sha256": manifest_sha256(cfg, version),
            **result}


def manifest_sha256(cfg: DataConfig, version: str) -> str:
    """Hash of the committed manifest file itself -- recorded in checkpoints."""
    return sha256_file(manifest_path(cfg, version))


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------
def download(cfg: DataConfig, manifest: Dict[str, Any], with_raw: bool,
             force: bool = False) -> Dict[str, Any]:
    from huggingface_hub import hf_hub_download

    repo = manifest.get("distribution", {}).get("hf_repo", cfg.hf_repo)
    tag = manifest.get("distribution", {}).get("tag", cfg.hf_tag)
    repo_type = manifest.get("distribution", {}).get("repo_type", cfg.hf_repo_type)
    if PLACEHOLDER in repo:
        raise SystemExit(
            f"distribution.hf_repo is still the placeholder {repo!r}. The bundle "
            "has not been published yet -- the owner fills this in at the freeze "
            "(prompt 4). Until then build locally:\n"
            "  python -m data.build --config configs/data/v1.yaml --stage pile\n"
            "  python -m data.bios  --config configs/data/v1.yaml\n"
            "  python -m data.pack  --config configs/data/v1.yaml\n"
            "or verify an existing build with --verify-only.")

    got, skipped = [], []
    t0 = time.time()
    for entry in manifest["files"]:
        rel = entry["path"]
        optional = entry.get("optional") or any(
            rel.startswith(p) for p in cfg.optional_prefixes)
        if optional and not with_raw:
            skipped.append(rel)
            continue
        dest = cfg.root / rel
        if dest.exists() and not force and dest.stat().st_size == entry["bytes"] \
                and sha256_file(dest) == entry["sha256"]:
            got.append(rel)
            continue
        print(f"[fetch] {rel} ({entry['bytes'] / 1e6:.1f} MB)", flush=True)
        src = hf_hub_download(repo, rel, repo_type=repo_type, revision=tag)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(Path(src).read_bytes())
        got.append(rel)
    return {"downloaded": len(got), "skipped": len(skipped),
            "repo": repo, "tag": tag, "seconds": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--config", default="configs/data/v1.yaml")
    ap.add_argument("--small", action="store_true")
    ap.add_argument("--with-raw", action="store_true",
                    help="also fetch raw/, the archived source text")
    ap.add_argument("--verify-only", action="store_true",
                    help="no network: check what is on disk against the manifest")
    ap.add_argument("--force", action="store_true",
                    help="re-download even files that already verify")
    args = ap.parse_args(argv)

    cfg = load_config(args.config, small=args.small)
    manifest = load_manifest(cfg, args.version)
    print(f"[fetch] manifest {args.version}: {manifest['n_files']} files, "
          f"{manifest['bytes']['total'] / 1e6:,.1f} MB "
          f"({manifest['bytes']['required'] / 1e6:,.1f} MB without raw/)")
    print(f"[fetch] config fingerprint (pack) "
          f"{manifest['config']['fingerprint_pack'][:16]}, Pile revision "
          f"{manifest['source']['revision'][:12]}, git "
          f"{manifest['git']['commit'][:12]}")

    if not args.verify_only:
        d = download(cfg, manifest, with_raw=args.with_raw, force=args.force)
        print(f"[fetch] {d['downloaded']} files from {d['repo']}@{d['tag']}, "
              f"{d['skipped']} skipped, {d['seconds']}s")

    r = verify(manifest, cfg.root, with_raw=args.with_raw,
               optional_prefixes=tuple(cfg.optional_prefixes))
    print(f"[fetch] verified {r['ok']}/{r['checked']} files in {r['seconds']}s "
          f"({r['skipped']} skipped as optional)")
    if r["passed"]:
        print("[fetch] OK")
        return 0
    for b in r["bad"]:
        print(f"[fetch] MISMATCH {b['path']}: {b['reason']} "
              f"expected {str(b['expected'])[:20]} got {str(b['got'])[:20]}")
    for m in r["missing"]:
        print(f"[fetch] MISSING  {m}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
