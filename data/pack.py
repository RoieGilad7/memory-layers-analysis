"""Stage 4 -- turn the cleaned Pile text and the biographies into token files.

    python -m data.pack --config configs/data/v1.yaml [--small]

Five steps, all deterministic from the one data seed:

  1. **Select.** Each subject contributes exactly `pack.train_tokens_per_subject`
     tokens, cut from prompt 1's 1.2x slack: whole documents in a seeded order
     until the next would pass the target, then a prefix of one more document
     to land on it exactly. So every subject is exactly 27,000,000 tokens, not
     "about".
  2. **Copy.** Each trained person gets its tier's copy count, cycling through
     its 4 rewordings as evenly as possible (30 -> 8, 8, 7, 7). Control people
     get none.
  3. **Interleave.** Six streams (5 subjects + biographies) are merged by
     deficit-greedy scheduling: always emit from the stream furthest below its
     share. That bounds the cumulative share error by one item length, so every
     1M-token window is within ~0.8 points of target. A seeded shuffle would be
     about 1.7 points noisy, which is too close to the 2-point limit.
  4. **Pack.** Concatenate with EOT between documents and cut into 512-token
     sequences. Pile documents may split across sequences; a biography copy
     never does -- when one would not fit in what is left of the current
     sequence, the remainder is filled with Pile text pulled forward from the
     stream (so no subject gains tokens) and the copy starts in the next
     sequence.
  5. **Held-out.** The same treatment for `heldout/<half>/`, without
     biographies, keeping each document's `ngram_overlap` in the index.

Outputs:

    tokens/train.bin            uint16, EOT-separated, 512-aligned
    tokens/train.idx.parquet    one row per document SEGMENT
    heldout/label.bin           uint16, the labeling half, all 6 subjects
    heldout/label.idx.parquet
    heldout/test.bin            the test half
    heldout/test.idx.parquet
    reports/pack_report.json
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from data.common import (record_timing, DataConfig, TOKEN_DTYPE, get_encoder,
                         keyed_rng, load_config, read_jsonl, write_json)

BIO_SUBJECT = "bio"

# Index columns. `doc_offset` is additive: a Pile document can reach the file in
# two pieces (a prefix pulled forward as filler, the rest at its own turn), and
# without the offset a consumer cannot tell which part of the document a
# segment is. The six columns the design fixes are all here unchanged.
INDEX_COLUMNS = ["doc_id", "subject", "start", "length", "doc_offset",
                 "person_id", "rewording_id"]


# ---------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------
@dataclass
class PileItem:
    doc_id: str
    subject: str
    take: int                 # tokens of this document that enter train.bin
    doc_tokens: int           # the document's full token count
    consumed: int = 0         # tokens already written (as filler or in turn)

    @property
    def remaining(self) -> int:
        return self.take - self.consumed


@dataclass
class BioItem:
    doc_id: str
    person_id: str
    rewording_id: int
    take: int


# ---------------------------------------------------------------------------
# 1. selection
# ---------------------------------------------------------------------------
def select_subject(cfg: DataConfig, subject: str
                   ) -> Tuple[List[PileItem], Dict[str, Any]]:
    """Exactly `pack.train_tokens_per_subject` tokens, in a seeded order."""
    slug = cfg.slug(subject)
    path = cfg.train_dir / f"{slug}.jsonl.gz"
    docs = [(r["doc_id"], int(r["n_tokens"])) for r in read_jsonl(path)]
    if not docs:
        raise RuntimeError(f"no training documents for {subject} at {path}")
    order = list(range(len(docs)))
    keyed_rng(cfg.seed, "select", subject).shuffle(order)

    target = cfg.pack_tokens_per_subject
    items: List[PileItem] = []
    acc = 0
    truncated: Optional[str] = None
    for i in order:
        if acc >= target:
            break
        doc_id, n = docs[i]
        take = min(n, target - acc)
        if take < n:
            truncated = doc_id
        items.append(PileItem(doc_id=doc_id, subject=subject, take=take,
                              doc_tokens=n))
        acc += take
    if acc != target:
        raise RuntimeError(
            f"{subject}: only {acc:,} tokens available but {target:,} needed. "
            "Prompt 1's slack was eaten -- re-run the pile stage or lower "
            "pack.train_tokens_per_subject.")
    report = {
        "documents_available": len(docs),
        "tokens_available": sum(n for _, n in docs),
        "documents_used": len(items),
        "tokens_used": acc,
        "target": target,
        "partial_document": truncated,
        "partial_document_tokens": items[-1].take if truncated else 0,
        "partial_document_full_tokens": items[-1].doc_tokens if truncated else 0,
    }
    return items, report


# ---------------------------------------------------------------------------
# 2. biography copies
# ---------------------------------------------------------------------------
def copies_per_rewording(n_copies: int, n_rewordings: int) -> List[int]:
    """Spread `n_copies` over the rewordings as evenly as possible.

    30 over 4 -> [8, 8, 7, 7]: the remainder goes to the lowest-numbered
    rewordings, so the split is a function of the two numbers alone.
    """
    base, rem = divmod(n_copies, n_rewordings)
    return [base + (1 if i < rem else 0) for i in range(n_rewordings)]


def build_bio_items(cfg: DataConfig) -> Tuple[List[BioItem], Dict[str, Any]]:
    """One item per biography copy, shuffled so one person's copies spread out."""
    people = list(read_jsonl(cfg.bios_dir / "people.jsonl"))
    lengths = _bio_token_lengths(cfg)
    items: List[BioItem] = []
    per_tier: Dict[str, Dict[str, int]] = {}
    for p in people:
        n = int(p["target_exposures"])
        tier = p["tier"]
        slot = per_tier.setdefault(tier, {"people": 0, "copies": 0, "tokens": 0})
        slot["people"] += 1
        if p["split"] != "train" or n == 0:
            continue
        for r, k in enumerate(copies_per_rewording(n, int(p["n_rewordings"]))):
            doc_id = f"bio-{p['person_id']}-{r}"
            take = lengths[doc_id]
            for _ in range(k):
                items.append(BioItem(doc_id=doc_id, person_id=p["person_id"],
                                     rewording_id=r, take=take))
            slot["copies"] += k
            slot["tokens"] += k * take
    keyed_rng(cfg.seed, "bio_order").shuffle(items)
    report = {
        "copies": len(items),
        "tokens": sum(i.take for i in items),
        "per_tier": per_tier,
        "distinct_biographies": len({i.doc_id for i in items}),
    }
    return items, report


def _bio_token_lengths(cfg: DataConfig) -> Dict[str, int]:
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    out: Dict[str, int] = {}
    for rec in read_jsonl(cfg.bios_dir / "bios_train.jsonl"):
        out[rec["doc_id"]] = len(enc.encode_ordinary(rec["text"]))
    return out


# ---------------------------------------------------------------------------
# 3. interleave
# ---------------------------------------------------------------------------
def interleave(streams: Dict[str, Sequence[Any]]) -> List[Tuple[str, int]]:
    """Merge streams so every prefix is close to each stream's token share.

    Deficit-greedy: emit from whichever stream is furthest below
    `share * tokens_placed_so_far`. After an emit that stream is below target by
    at most the item it just placed, so the cumulative error never exceeds one
    item length and any window's share error never exceeds two of them. Returns
    (stream key, index within the stream) pairs.
    """
    keys = sorted(streams)
    totals = {k: sum(getattr(i, "take") for i in streams[k]) for k in keys}
    grand = sum(totals.values())
    if grand == 0:
        return []
    share = {k: totals[k] / grand for k in keys}
    pos = {k: 0 for k in keys}
    placed = {k: 0 for k in keys}
    out: List[Tuple[str, int]] = []
    total_placed = 0
    live = [k for k in keys if streams[k]]
    while live:
        best, best_deficit = None, None
        for k in live:
            deficit = share[k] * total_placed - placed[k]
            if best_deficit is None or deficit > best_deficit:
                best, best_deficit = k, deficit
        i = pos[best]
        item = streams[best][i]
        out.append((best, i))
        placed[best] += item.take
        total_placed += item.take
        pos[best] = i + 1
        if pos[best] >= len(streams[best]):
            live = [k for k in live if k != best]
    return out


def window_shares(order: Sequence[Tuple[str, int]], streams: Dict[str, Sequence[Any]],
                  window: int, stride: Optional[int] = None
                  ) -> Dict[str, Dict[str, float]]:
    """Worst share deviation per stream over every `window` of tokens.

    Windows overlap (stride = window/4 by default) so the check is stricter than
    testing a partition: a deviation that straddles two tiles of a partition
    would otherwise be averaged away.
    """
    keys = sorted(streams)
    lengths = np.array([streams[k][i].take for k, i in order], dtype=np.int64)
    which = np.array([keys.index(k) for k, _ in order], dtype=np.int64)
    ends = np.cumsum(lengths)
    total = int(ends[-1])
    cum = np.zeros((len(keys), len(order) + 1), dtype=np.int64)
    for j, w in enumerate(which):
        cum[:, j + 1] = cum[:, j]
        cum[w, j + 1] += lengths[j]
    target = {k: float(cum[i, -1]) / total for i, k in enumerate(keys)}

    out = {k: {"target_share": target[k], "worst_share": target[k],
               "worst_deviation_points": 0.0, "worst_window_start": 0,
               "n_windows": 0} for k in keys}
    step = stride or max(1, window // 4)
    starts = np.arange(0, max(total - window + 1, 1), step)
    if total < window:
        starts = np.array([0])
    for a in starts:
        b = min(a + window, total)
        ja = int(np.searchsorted(ends, a, side="left"))
        jb = int(np.searchsorted(ends, b, side="left"))
        span = float(ends[jb - 1] - (ends[ja - 1] if ja > 0 else 0)) if jb > ja else 0.0
        if span <= 0:
            continue
        for i, k in enumerate(keys):
            got = float(cum[i, jb] - cum[i, ja])
            dev = abs(got / span - target[k]) * 100.0
            out[k]["n_windows"] += 1
            if dev > out[k]["worst_deviation_points"]:
                out[k]["worst_deviation_points"] = dev
                out[k]["worst_share"] = got / span
                out[k]["worst_window_start"] = int(a)
    for k in keys:
        out[k]["target_share"] = round(out[k]["target_share"], 6)
        out[k]["worst_share"] = round(out[k]["worst_share"], 6)
        out[k]["worst_deviation_points"] = round(out[k]["worst_deviation_points"], 4)
    return out


# ---------------------------------------------------------------------------
# 4. packing
# ---------------------------------------------------------------------------
class Writer:
    """Token-stream writer that keeps biography copies inside one sequence.

    Documents are separated by a single EOT. `place_pile` may split a document
    across sequence boundaries freely; `place_bio` never does -- it first fills
    the rest of the current sequence from `filler`, which pulls Pile tokens
    forward out of the stream rather than adding any, so no subject's total
    changes.
    """

    def __init__(self, block_size: int, eot: int, filler=None):
        self.block = block_size
        self.eot = eot
        self.filler = filler
        self.buf: List[np.ndarray] = []
        self.n = 0
        self.need_sep = False
        self.rows: List[Dict[str, Any]] = []
        self.pad_tokens = 0
        self.filler_tokens = 0
        self.moved_biographies = 0

    # -- primitives --------------------------------------------------------
    def _emit(self, arr: np.ndarray) -> None:
        self.buf.append(arr)
        self.n += int(arr.size)

    def _sep(self) -> None:
        if self.need_sep:
            self._emit(np.array([self.eot], dtype=TOKEN_DTYPE))
            self.need_sep = False

    def _row(self, doc_id: str, subject: str, start: int, length: int,
             doc_offset: int, person_id: Optional[str], rewording_id: int) -> None:
        self.rows.append({
            "doc_id": doc_id, "subject": subject, "start": start,
            "length": length, "doc_offset": doc_offset,
            "person_id": person_id, "rewording_id": rewording_id})

    def write_segment(self, tokens: np.ndarray, doc_id: str, subject: str,
                      doc_offset: int, person_id: Optional[str] = None,
                      rewording_id: int = -1) -> None:
        self._sep()
        self._row(doc_id, subject, self.n, int(tokens.size), doc_offset,
                  person_id, rewording_id)
        self._emit(tokens)
        self.need_sep = True

    # -- biography placement ----------------------------------------------
    def _fits(self, length: int) -> bool:
        start = self.n + (1 if self.need_sep else 0)
        return start // self.block == (start + length - 1) // self.block

    def fill_to(self, target: int) -> None:
        """Write exactly `target - n` tokens of Pile text (or EOT padding)."""
        while self.n < target:
            if self.need_sep:
                self._emit(np.array([self.eot], dtype=TOKEN_DTYPE))
                self.need_sep = False
                continue
            chunk = self.filler(target - self.n) if self.filler else None
            if chunk is None:
                # no Pile text left: pad with EOT rather than split a biography
                k = target - self.n
                self._emit(np.full(k, self.eot, dtype=TOKEN_DTYPE))
                self.pad_tokens += k
                self.need_sep = False
                return
            tokens, doc_id, subject, doc_offset = chunk
            self._row(doc_id, subject, self.n, int(tokens.size), doc_offset,
                      None, -1)
            self._emit(tokens)
            self.filler_tokens += int(tokens.size)
            self.need_sep = True

    def place_bio(self, tokens: np.ndarray, doc_id: str, person_id: str,
                  rewording_id: int) -> None:
        length = int(tokens.size)
        if length >= self.block:
            raise ValueError(
                f"{doc_id}: {length} tokens cannot fit in a {self.block}-token "
                "sequence without splitting")
        if not self._fits(length):
            self.fill_to(((self.n // self.block) + 1) * self.block)
            self.moved_biographies += 1
        self.write_segment(tokens, doc_id, BIO_SUBJECT, 0, person_id,
                           rewording_id)

    # -- finish ------------------------------------------------------------
    def finish(self, align: bool = True) -> np.ndarray:
        """Concatenate. With `align`, pad the tail to a whole sequence."""
        if align and self.n % self.block:
            k = self.block - (self.n % self.block)
            self._emit(np.full(k, self.eot, dtype=TOKEN_DTYPE))
            self.pad_tokens += k
        return (np.concatenate(self.buf) if self.buf
                else np.zeros(0, dtype=TOKEN_DTYPE))


def pack_train(cfg: DataConfig, tokens: Dict[str, np.ndarray],
               pile_streams: Dict[str, List[PileItem]],
               bio_items: List[BioItem], bio_tokens: Dict[str, np.ndarray]
               ) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
    streams: Dict[str, Sequence[Any]] = dict(pile_streams)
    streams[BIO_SUBJECT] = bio_items
    order = interleave(streams)
    windows = window_shares(order, streams, cfg.window_tokens)

    # filler pulls the earliest Pile item that still has tokens, at or after
    # the current position -- which is what "fill the remainder with Pile text"
    # means: tokens are brought forward, never invented
    pile_order = [(k, i) for k, i in order if k != BIO_SUBJECT]
    filler_ptr = [0]

    def filler(n: int):
        while filler_ptr[0] < len(pile_order):
            k, i = pile_order[filler_ptr[0]]
            item = pile_streams[k][i]
            if item.remaining <= 0:
                filler_ptr[0] += 1
                continue
            take = min(n, item.remaining)
            off = item.consumed
            arr = tokens[item.doc_id][off:off + take]
            item.consumed += take
            return arr, item.doc_id, item.subject, off
        return None

    w = Writer(cfg.block_size, cfg.eot_token, filler)
    for k, i in order:
        if k == BIO_SUBJECT:
            item = bio_items[i]
            w.place_bio(bio_tokens[item.doc_id], item.doc_id, item.person_id,
                        item.rewording_id)
        else:
            item = pile_streams[k][i]
            if item.remaining <= 0:
                continue                      # already written as filler
            off = item.consumed
            arr = tokens[item.doc_id][off:off + item.remaining]
            item.consumed = item.take
            w.write_segment(arr, item.doc_id, item.subject, off)
    arr = w.finish(align=True)
    stats = {
        "items": len(order),
        "sequences": arr.size // cfg.block_size,
        "tokens": int(arr.size),
        "eot_pad_tokens": w.pad_tokens,
        "filler_tokens": w.filler_tokens,
        "biographies_moved_to_next_sequence": w.moved_biographies,
        "window_shares": windows,
        "window_tokens": cfg.window_tokens,
        "window_tolerance_points": cfg.window_tolerance_points,
    }
    return arr, w.rows, stats


# ---------------------------------------------------------------------------
# 5. held-out
# ---------------------------------------------------------------------------
def pack_heldout(cfg: DataConfig, half: str
                 ) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
    """One .bin per half, all six subjects, no biographies."""
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    w = Writer(cfg.block_size, cfg.eot_token, filler=None)
    overlaps: List[Optional[float]] = []
    per_subject: Dict[str, Dict[str, Any]] = {}
    for subject in cfg.all_subjects:
        slug = cfg.slug(subject)
        path = cfg.heldout_dir / half / f"{slug}.jsonl.gz"
        docs = sorted(read_jsonl(path), key=lambda r: (r["source"], r["line"]))
        n_tok = 0
        texts = [r["text"] for r in docs]
        encoded = enc.encode_ordinary_batch(texts, num_threads=8) if texts else []
        for rec, toks in zip(docs, encoded):
            if len(toks) > cfg.max_tokens:
                raise AssertionError(
                    f"{rec['doc_id']}: {len(toks)} tokens exceeds the "
                    f"{cfg.max_tokens}-token cap")
            w.write_segment(np.asarray(toks, dtype=TOKEN_DTYPE), rec["doc_id"],
                            subject, 0)
            overlaps.append(rec.get("ngram_overlap"))
            n_tok += len(toks)
        per_subject[subject] = {"documents": len(docs), "tokens": n_tok}
    arr = w.finish(align=False)
    for row, ov in zip(w.rows, overlaps):
        row["ngram_overlap"] = ov
    stats = {"half": half, "tokens": int(arr.size), "documents": len(w.rows),
             "per_subject": per_subject}
    return arr, w.rows, stats


# ---------------------------------------------------------------------------
# index IO
# ---------------------------------------------------------------------------
def write_index(rows: Sequence[Dict[str, Any]], path: Path,
                extra_columns: Sequence[str] = ()) -> Path:
    """Write the segment index. Parquet, byte-stable for a given pyarrow."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    cols = list(INDEX_COLUMNS) + list(extra_columns)
    arrays = {
        "doc_id": pa.array([r["doc_id"] for r in rows], pa.string()),
        "subject": pa.array([r["subject"] for r in rows],
                            pa.string()).dictionary_encode(),
        "start": pa.array([r["start"] for r in rows], pa.int64()),
        "length": pa.array([r["length"] for r in rows], pa.int64()),
        "doc_offset": pa.array([r["doc_offset"] for r in rows], pa.int64()),
        "person_id": pa.array([r["person_id"] for r in rows], pa.string()),
        "rewording_id": pa.array([r["rewording_id"] for r in rows], pa.int32()),
    }
    for c in extra_columns:
        arrays[c] = pa.array([r.get(c) for r in rows], pa.float64())
    table = pa.table({c: arrays[c] for c in cols})
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")
    return path


def read_index(path: Path) -> Dict[str, Any]:
    """The index as a dict of numpy/object arrays -- no pandas needed."""
    import pyarrow.parquet as pq
    t = pq.read_table(path)
    out: Dict[str, Any] = {}
    for name in t.column_names:
        col = t.column(name)
        if str(col.type).startswith("dictionary"):
            col = col.cast("string")
        out[name] = col.to_pylist() if col.type == "string" else col.to_numpy(
            zero_copy_only=False)
    return out


def write_bin(arr: np.ndarray, path: Path) -> Path:
    if arr.dtype != TOKEN_DTYPE:
        raise TypeError(f"{path}: dtype {arr.dtype}, expected {TOKEN_DTYPE}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(arr.tobytes(order="C"))
    return path



# ---------------------------------------------------------------------------
# tokenizing the selected documents
# ---------------------------------------------------------------------------
def tokenize_selected(cfg: DataConfig, enc, subject: str,
                      wanted: Dict[str, int]) -> Dict[str, np.ndarray]:
    """Tokenize only the documents selection kept. Asserts the recorded counts."""
    slug = cfg.slug(subject)
    out: Dict[str, np.ndarray] = {}
    batch: List[Tuple[str, str, int]] = []

    def flush() -> None:
        if not batch:
            return
        for (doc_id, _t, n_rec), toks in zip(
                batch, enc.encode_ordinary_batch([t for _, t, _ in batch],
                                                 num_threads=8)):
            if len(toks) != n_rec:
                raise AssertionError(
                    f"{doc_id}: n_tokens says {n_rec} but the text encodes to "
                    f"{len(toks)}. The cleaned text and its recorded count have "
                    "drifted apart -- re-run the dedup stage.")
            out[doc_id] = np.asarray(toks, dtype=TOKEN_DTYPE)
        batch.clear()

    for rec in read_jsonl(cfg.train_dir / f"{slug}.jsonl.gz"):
        if rec["doc_id"] in wanted:
            batch.append((rec["doc_id"], rec["text"], int(rec["n_tokens"])))
            if len(batch) >= 256:
                flush()
    flush()
    missing = set(wanted) - set(out)
    if missing:
        raise RuntimeError(f"{subject}: {len(missing)} selected documents not found")
    return out


def bio_token_arrays(cfg: DataConfig, enc, wanted: Iterable[str]
                     ) -> Dict[str, np.ndarray]:
    want = set(wanted)
    out: Dict[str, np.ndarray] = {}
    recs = [r for r in read_jsonl(cfg.bios_dir / "bios_train.jsonl")
            if r["doc_id"] in want]
    for rec, toks in zip(recs, enc.encode_ordinary_batch(
            [r["text"] for r in recs], num_threads=8)):
        out[rec["doc_id"]] = np.asarray(toks, dtype=TOKEN_DTYPE)
    return out


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def run(cfg: DataConfig) -> Dict[str, Any]:
    t0 = time.time()
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    print(f"[pack] root={cfg.root}  small={cfg.small}  "
          f"fingerprint={cfg.fingerprint('pack')[:16]}", flush=True)

    # 1. select
    pile_streams: Dict[str, List[PileItem]] = {}
    select_reports: Dict[str, Any] = {}
    for subject in cfg.train_subjects:
        items, rep = select_subject(cfg, subject)
        pile_streams[subject] = items
        select_reports[subject] = rep
        print(f"[pack] select {subject:20s} {rep['documents_used']:>7,} docs "
              f"of {rep['documents_available']:>7,} -> {rep['tokens_used']:,} "
              f"tokens (1 partial: {rep['partial_document']})", flush=True)

    # 2. biography copies
    bio_items, bio_report = build_bio_items(cfg)
    print(f"[pack] bios {bio_report['copies']:,} copies of "
          f"{bio_report['distinct_biographies']:,} biographies = "
          f"{bio_report['tokens']:,} tokens", flush=True)

    # tokenize
    tokens: Dict[str, np.ndarray] = {}
    for subject, items in pile_streams.items():
        tokens.update(tokenize_selected(
            cfg, enc, subject, {i.doc_id: i.take for i in items}))
    bio_tokens = bio_token_arrays(cfg, enc, {i.doc_id for i in bio_items})
    print(f"[pack] tokenized {len(tokens):,} Pile documents and "
          f"{len(bio_tokens):,} biographies ({time.time() - t0:.0f}s)", flush=True)

    # 3+4. interleave and pack
    arr, rows, stats = pack_train(cfg, tokens, pile_streams, bio_items, bio_tokens)
    write_bin(arr, cfg.tokens_dir / "train.bin")
    write_index(rows, cfg.tokens_dir / "train.idx.parquet")
    worst = max(v["worst_deviation_points"] for v in stats["window_shares"].values())
    print(f"[pack] train.bin {stats['tokens']:,} tokens = "
          f"{stats['sequences']:,} sequences, {len(rows):,} index rows, "
          f"{stats['filler_tokens']:,} filler tokens, "
          f"{stats['biographies_moved_to_next_sequence']:,} biographies moved, "
          f"worst window deviation {worst:.3f} pts", flush=True)

    # 5. held-out
    heldout_stats = {}
    for half in cfg.pack_halves:
        h_arr, h_rows, h_stats = pack_heldout(cfg, half)
        write_bin(h_arr, cfg.heldout_tokens_dir / f"{half}.bin")
        write_index(h_rows, cfg.heldout_tokens_dir / f"{half}.idx.parquet",
                    extra_columns=["ngram_overlap"])
        heldout_stats[half] = h_stats
        print(f"[pack] heldout/{half}.bin {h_stats['tokens']:,} tokens, "
              f"{h_stats['documents']:,} documents", flush=True)

    per_subject = {}
    idx_subjects = np.array([r["subject"] for r in rows])
    idx_lengths = np.array([r["length"] for r in rows], dtype=np.int64)
    for subject in cfg.train_subjects + [BIO_SUBJECT]:
        m = idx_subjects == subject
        per_subject[subject] = {
            "segments": int(m.sum()),
            "tokens": int(idx_lengths[m].sum()),
        }
    report = {
        "stage": "pack",
        "config_fingerprint": cfg.fingerprint("pack"),
        "small": cfg.small,
        "seed": cfg.seed,
        "block_size": cfg.block_size,
        "eot_token": cfg.eot_token,
        "select": select_reports,
        "biographies": bio_report,
        "train": {**stats, "per_subject": per_subject,
                  "index_rows": len(rows)},
        "heldout": heldout_stats,
    }
    record_timing(cfg, "pack", time.time() - t0)
    write_json(cfg.reports_dir / "pack_report.json", report)
    return report


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    r = run(cfg)
    print("\n[pack] done")
    for s, v in r["train"]["per_subject"].items():
        print(f"   {s:20s} {v['tokens']:>12,} tokens in {v['segments']:>7,} segments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
