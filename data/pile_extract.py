"""Stage 1 -- stream the pinned Pile revision and archive the raw JSONL we keep.

Streams `train/00.jsonl.zst` (training text) and `val.jsonl.zst` (held-out text)
straight over HTTP from one pinned commit, decompressing with `zstandard`, and
writes one gzipped JSONL file per (split, subject) under `<root>/raw/`. That
archive is the frozen bundle's input: a rebuild never needs the Pile again.

Budget: a subject stops being collected once it reaches `target + slack`
cleaned, 4096-capped tokens. Cleaning and the cap are recomputed here only to
make the budget accurate -- the archive holds the untouched source text.

Resumable. Records go to per-block part files; the state file is written at
block boundaries only, so an interrupted run restarts from the last boundary
(it re-streams the skipped prefix of the current file, which is the price of a
single-frame zstd stream having no random access).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import zstandard as zstd
from huggingface_hub import hf_hub_url

from data.common import (record_timing, CHARS_PER_TOKEN_BOUND, DataConfig, clean_text, merge_gz,
                         dumps_record, free_disk_gb, get_encoder, load_config,
                         open_write, write_json)

# State checkpoint granularity. Overridable so the resume path can be exercised
# against a real stream without reading 100,000 lines first.
BLOCK_LINES = int(os.environ.get("DATA_BLOCK_LINES", 100_000))
TOKENIZE_BATCH = 128           # docs per tiktoken batch call
STREAM_RETRIES = 4
MIN_FREE_DISK_GB = 20.0


class _CountingReader(io.RawIOBase):
    """Wraps a raw HTTP stream and counts the compressed bytes pulled."""

    def __init__(self, raw):
        self._raw = raw
        self.n_bytes = 0

    def readable(self) -> bool:
        return True

    def readinto(self, b) -> int:
        chunk = self._raw.read(len(b))
        if not chunk:
            return 0
        b[:len(chunk)] = chunk
        self.n_bytes += len(chunk)
        return len(chunk)


def _open_stream(cfg: DataConfig, filename: str) -> Tuple[Any, _CountingReader, Any]:
    url = hf_hub_url(cfg.dataset, filename, repo_type=cfg.repo_type,
                     revision=cfg.revision)
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    counter = _CountingReader(resp.raw)
    dctx = zstd.ZstdDecompressor(max_window_size=2 ** 31)
    reader = dctx.stream_reader(counter)
    text = io.TextIOWrapper(io.BufferedReader(reader, buffer_size=1 << 22),
                            encoding="utf-8")
    return resp, counter, text


# --------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------
def _empty_subject_stats() -> Dict[str, int]:
    return {"docs": 0, "tokens": 0, "docs_under_min": 0, "docs_truncated": 0,
            "raw_chars": 0}


def _empty_split_state(cfg: DataConfig, split: str) -> Dict[str, Any]:
    return {
        "done": False,
        "files_done": [],
        "current_file": None,
        "block": 0,
        "lines_read": 0,
        "bytes_downloaded": 0,
        "subjects": {s: _empty_subject_stats() for s in cfg.subjects_for(split)},
    }


def _load_state(cfg: DataConfig, path: Path) -> Dict[str, Any]:
    if path.exists():
        state = json.loads(path.read_text())
        if state.get("config_fingerprint") == cfg.fingerprint("pile"):
            return state
        print(f"[extract] state fingerprint mismatch -> starting over ({path})")
    return {
        "config_fingerprint": cfg.fingerprint("pile"),
        "revision": cfg.revision,
        "dataset": cfg.dataset,
        "splits": {s: _empty_split_state(cfg, s) for s in ("train", "heldout")},
    }


def _part_path(cfg: DataConfig, split: str, subject: str, tag: str,
               block: int) -> Path:
    return (cfg.raw_dir / "_parts" / split / cfg.slug(subject)
            / f"{tag}-{block:06d}.jsonl.gz")


def _part_key(path: Path) -> Tuple[str, int]:
    """("train00", 12) from "train00-000012.jsonl.gz"."""
    tag, _, block = path.name.split(".", 1)[0].rpartition("-")
    return tag, int(block)


def _drop_parts_from(cfg: DataConfig, split: str, tag: str, block: int) -> int:
    """Remove part files for this file at or after `block` (incomplete work)."""
    n = 0
    base = cfg.raw_dir / "_parts" / split
    if not base.exists():
        return 0
    for p in sorted(base.glob(f"*/{tag}-*.jsonl.gz")):
        if _part_key(p)[1] >= block:
            p.unlink()
            n += 1
    return n


# --------------------------------------------------------------------------
# one file
# --------------------------------------------------------------------------
def _stream_file(cfg: DataConfig, split: str, filename: str,
                 st: Dict[str, Any], state_path: Path, state: Dict[str, Any],
                 enc) -> bool:
    """Collect from one source file. Returns True if every subject is full."""
    tag = cfg.source_tag(filename)
    wanted = set(cfg.subjects_for(split))
    targets = {s: cfg.target_tokens(split, s) for s in wanted}
    stats = st["subjects"]

    def hungry(subject: str) -> bool:
        return stats[subject]["tokens"] < targets[subject]

    def all_full() -> bool:
        return all(not hungry(s) for s in wanted)

    resume_line = st["block"] * BLOCK_LINES if st["current_file"] == filename else 0
    if resume_line:
        dropped = _drop_parts_from(cfg, split, tag, st["block"])
        print(f"[extract] {split}/{filename}: resuming at line {resume_line:,} "
              f"(dropped {dropped} partial part files)", flush=True)
    else:
        _drop_parts_from(cfg, split, tag, 0)
        st["block"] = 0
        st["lines_read"] = 0
    st["current_file"] = filename

    bytes_at_start = st["bytes_downloaded"]
    handles: Dict[str, Any] = {}
    # (subject, line, raw text) -- every document of a wanted subject goes in,
    # full or not, so that the archive does not depend on TOKENIZE_BATCH
    buf: List[Tuple[str, int, str]] = []
    char_limit = cfg.max_tokens * CHARS_PER_TOKEN_BOUND
    t0 = time.time()
    attempt = 0
    line_no = resume_line
    block = st["block"]

    def close_handles() -> None:
        for fh in handles.values():
            fh.close()
        handles.clear()

    def flush_buffer() -> None:
        """Clean, tokenize and archive one batch, strictly in line order.

        Every decision -- is the subject still hungry, is the document archived,
        does it count toward the budget -- is made here, in line order, against
        counts that are live as of that line. That is what makes the archive a
        pure function of the stream: it does not depend on TOKENIZE_BATCH, on
        BLOCK_LINES, or on where a run was interrupted and resumed.
        """
        if not buf:
            return
        cleaned_all = [clean_text(raw, cfg.unicode_form,
                                  cfg.max_consecutive_newlines)[:char_limit]
                       for _, _, raw in buf]
        counts = enc.encode_ordinary_batch(cleaned_all, num_threads=8)
        for (subject, line, raw), cleaned, toks in zip(buf, cleaned_all, counts):
            if not hungry(subject):
                continue
            s = stats[subject]
            if not cleaned:
                s["docs_under_min"] += 1
                continue
            # `cleaned` is a char prefix long enough to hold max_tokens tokens,
            # so this count is exact below the cap and saturates above it.
            truncated = len(toks) > cfg.max_tokens
            n_tok = min(len(toks), cfg.max_tokens)
            key = cfg.slug(subject)
            if key not in handles:
                handles[key] = open_write(
                    _part_path(cfg, split, subject, tag, block), append=True)
            handles[key].write(dumps_record({
                "doc_id": cfg.doc_id(subject, filename, line),
                "subject": subject,
                "split": split,
                "source": filename,
                "line": line,
                "text": raw,
            }))
            s["raw_chars"] += len(raw)
            if n_tok < cfg.min_tokens:
                s["docs_under_min"] += 1
            else:
                s["docs"] += 1
                s["tokens"] += n_tok
                s["docs_truncated"] += int(truncated)
        buf.clear()

    def checkpoint(new_block: int) -> None:
        flush_buffer()
        close_handles()
        st["block"] = new_block
        st["lines_read"] = line_no
        write_json(state_path, state)

    while True:
        try:
            resp, counter, stream = _open_stream(cfg, filename)
            break
        except Exception as exc:                                # pragma: no cover
            attempt += 1
            if attempt > STREAM_RETRIES:
                raise
            print(f"[extract] open failed ({exc!r}), retry {attempt}", flush=True)
            time.sleep(5 * attempt)

    try:
        for idx, line in enumerate(stream):
            if idx < resume_line:
                continue
            line_no = idx
            if idx and idx % BLOCK_LINES == 0:
                checkpoint(idx // BLOCK_LINES)
                block = st["block"]
                st["bytes_downloaded"] = bytes_at_start + counter.n_bytes
                done = sum(v["tokens"] for v in stats.values())
                print(f"[extract] {split}/{tag} line {idx:,} "
                      f"({counter.n_bytes / 1e9:.2f} GB) tokens={done:,} "
                      f"{time.time() - t0:.0f}s "
                      + " ".join(f"{cfg.slug(s)}={stats[s]['tokens'] / 1e6:.1f}M"
                                 for s in cfg.subjects_for(split)), flush=True)
                # A checkpoint flushes the buffer, so the last subject can fill
                # here rather than on a buffer-full flush. Without this check the
                # buffer would never fill again (no subject is hungry, so nothing
                # is appended) and the loop would read the shard to EOF.
                if all_full():
                    break
                if free_disk_gb() < MIN_FREE_DISK_GB:
                    raise RuntimeError(
                        f"free disk {free_disk_gb():.1f} GB < {MIN_FREE_DISK_GB} GB "
                        "-- stopping (re-run to resume)")
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:                        # pragma: no cover
                continue
            subject = rec.get("meta", {}).get("pile_set_name")
            if subject not in wanted:
                continue
            buf.append((subject, idx, rec.get("text") or ""))
            if len(buf) >= TOKENIZE_BATCH:
                flush_buffer()
                if all_full():
                    break
    finally:
        flush_buffer()
        close_handles()
        st["lines_read"] = line_no + 1
        st["bytes_downloaded"] = bytes_at_start + counter.n_bytes
        try:
            stream.close()
            resp.close()
        except Exception:                                       # pragma: no cover
            pass
        write_json(state_path, state)

    full = all_full()
    print(f"[extract] {split}/{tag} finished at line {line_no:,}: "
          f"all_subjects_full={full}, {time.time() - t0:.0f}s, "
          f"{counter.n_bytes / 1e9:.2f} GB downloaded", flush=True)
    return full


# --------------------------------------------------------------------------
# finalize
# --------------------------------------------------------------------------
def _finalize_split(cfg: DataConfig, split: str, st: Dict[str, Any]) -> None:
    """Concatenate part files into one gzip per subject, in (file, block) order."""
    order = {t: i for i, t in enumerate(
        [cfg.source_tag(f) for f in st["files_done"]])}
    for subject in cfg.subjects_for(split):
        pdir = cfg.raw_dir / "_parts" / split / cfg.slug(subject)
        parts = sorted(pdir.glob("*.jsonl.gz"),
                       key=lambda p: (order.get(_part_key(p)[0], 99),
                                      _part_key(p)[1]))
        out = cfg.raw_dir / split / f"{cfg.slug(subject)}.jsonl.gz"
        merge_gz(parts, out)
        for p in parts:
            p.unlink()
        if pdir.exists() and not any(pdir.iterdir()):
            pdir.rmdir()


def run(cfg: DataConfig, splits: Tuple[str, ...] = ("train", "heldout")) -> Dict[str, Any]:
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    state_path = cfg.raw_dir / "extract_state.json"
    state = _load_state(cfg, state_path)
    t_start = time.time()

    for split in splits:
        st = state["splits"][split]
        if st["done"]:
            print(f"[extract] {split}: already done, skipping", flush=True)
            continue
        files = (cfg.train_files + cfg.train_fallback_files if split == "train"
                 else cfg.heldout_files + cfg.heldout_fallback_files)
        primary = set(cfg.train_files if split == "train" else cfg.heldout_files)
        for filename in files:
            if filename in st["files_done"]:
                continue
            if filename not in primary:
                short = [s for s in cfg.subjects_for(split)
                         if st["subjects"][s]["tokens"] < cfg.target_tokens(split, s)]
                if not short:
                    break
                print(f"[extract] {split}: short on {short} -> fallback {filename}",
                      flush=True)
            full = False
            for attempt in range(STREAM_RETRIES + 1):
                try:
                    full = _stream_file(cfg, split, filename, st, state_path,
                                        state, enc)
                    break
                except KeyboardInterrupt:
                    raise
                except Exception as exc:                        # pragma: no cover
                    if attempt == STREAM_RETRIES or "free disk" in str(exc):
                        raise
                    print(f"[extract] {split}/{filename} failed mid-stream "
                          f"({exc!r}); retry {attempt + 1} from the last "
                          f"checkpoint", flush=True)
                    time.sleep(5 * (attempt + 1))
            st["files_done"].append(filename)
            st["current_file"] = None
            st["block"] = 0
            write_json(state_path, state)
            if full:
                break
        st["done"] = True
        _finalize_split(cfg, split, st)
        write_json(state_path, state)

    manifest = {
        "stage": "pile_extract",
        "config_fingerprint": cfg.fingerprint("pile"),
        "small": cfg.small,
        "dataset": cfg.dataset,
        "revision": cfg.revision,
        "tokenizer": cfg.tokenizer_name,
        "max_tokens": cfg.max_tokens,
        "min_tokens": cfg.min_tokens,
        "splits": {},
    }
    for split in ("train", "heldout"):
        st = state["splits"][split]
        manifest["splits"][split] = {
            "files_used": st["files_done"],
            "fallback_files_used": [
                f for f in st["files_done"]
                if f not in (cfg.train_files if split == "train" else cfg.heldout_files)],
            "lines_read": st["lines_read"],
            "bytes_downloaded": st["bytes_downloaded"],
            "target_tokens_per_subject": {
                s: cfg.target_tokens(split, s) for s in cfg.subjects_for(split)},
            "subjects": st["subjects"],
            "short_subjects": [
                s for s in cfg.subjects_for(split)
                if st["subjects"][s]["tokens"] < cfg.target_tokens(split, s)],
        }
    record_timing(cfg, "extract", time.time() - t_start)
    write_json(cfg.reports_dir / "extract_manifest.json", manifest)
    return manifest


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    ap.add_argument("--split", choices=["train", "heldout", "both"], default="both")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    splits = ("train", "heldout") if args.split == "both" else (args.split,)
    m = run(cfg, splits)
    for split, d in m["splits"].items():
        print(f"\n[extract] {split}: files={d['files_used']} "
              f"lines={d['lines_read']:,} "
              f"download={d['bytes_downloaded'] / 1e9:.2f} GB")
        for s, v in d["subjects"].items():
            print(f"   {s:20s} docs={v['docs']:>8,} tokens={v['tokens']:>12,} "
                  f"under_min={v['docs_under_min']:>6,} trunc={v['docs_truncated']:>7,}")
        if d["short_subjects"]:
            print(f"   SHORT: {d['short_subjects']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
