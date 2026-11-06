"""Run every packing invariant against the REAL build, not a test fixture.

    python bench/check_pack_invariants.py

tests/test_data_pack.py proves the same properties on a miniature synthetic
build in about a second. This re-proves them on the 150M-token article: exact
per-subject budgets, uint16 and the vocab bound, no biography across a 512
boundary, the index tiling the file with EOT in every gap, 1M-token window
shares, per-person copy counts, 1,000 segments decoded back to their source,
and the two held-out files. Exits non-zero on the first failure.
"""
import json, sys
from collections import Counter, defaultdict
sys.path.insert(0, ".")
import numpy as np
from data import pack
from data.common import load_config, get_encoder, read_jsonl
from data.pack import BIO_SUBJECT

cfg = load_config("configs/data/v1.yaml")
rep = json.load(open(cfg.reports_dir / "pack_report.json"))
tok = np.memmap(cfg.tokens_dir / "train.bin", dtype=np.uint16, mode="r")
idx = pack.read_index(cfg.tokens_dir / "train.idx.parquet")
block, eot = cfg.block_size, cfg.eot_token
print(f"train.bin {tok.size:,} tokens, {tok.size//block:,} sequences, "
      f"{len(idx['start']):,} index rows")

# 1. exact token budget per subject
by_subject = Counter()
for s, n in zip(idx["subject"], idx["length"]):
    by_subject[s] += int(n)
for subj in cfg.train_subjects:
    assert by_subject[subj] == cfg.pack_tokens_per_subject, (subj, by_subject[subj])
print("OK  every subject is exactly", f"{cfg.pack_tokens_per_subject:,}", "tokens")
print("    bio tokens:", f"{by_subject[BIO_SUBJECT]:,}")

# 2. dtype / vocab
assert tok.dtype == np.uint16 and int(tok.max()) < cfg.vocab_size
assert tok.size % block == 0
print("OK  dtype uint16, max id", int(tok.max()), "<", cfg.vocab_size)

# 3. no biography crosses a boundary
starts = np.asarray(idx["start"], np.int64); lens = np.asarray(idx["length"], np.int64)
subj = np.asarray(idx["subject"], dtype=object)
m = subj == BIO_SUBJECT
cross = ((starts[m] // block) != ((starts[m] + lens[m] - 1) // block)).sum()
assert cross == 0, cross
print("OK  0 of", f"{int(m.sum()):,}", "biography copies cross a 512 boundary")
pm = ~m
pcross = int(((starts[pm] // block) != ((starts[pm] + lens[pm] - 1) // block)).sum())
print("    Pile segments that do cross (allowed):", f"{pcross:,}")

# 4. tiling: uncovered tokens are exactly the EOTs
assert (np.diff(starts) > 0).all()
assert (starts[1:] >= (starts[:-1] + lens[:-1])).all()
covered = np.zeros(tok.size, dtype=bool)
for s, e in zip(starts, starts + lens):
    covered[s:e] = True
arr = np.asarray(tok)
assert (arr[covered] != eot).all(), "a document token equals EOT"
assert (arr[~covered] == eot).all(), "an uncovered token is not EOT"
assert int(lens.sum()) == int(covered.sum())
print("OK  index tiles the file; all", f"{int((~covered).sum()):,}",
      "uncovered tokens are EOT")

# 5. window shares
w = rep["train"]["window_shares"]
worst = max(v["worst_deviation_points"] for v in w.values())
for k, v in sorted(w.items()):
    print(f"    {k:20s} target {v['target_share']*100:6.3f}%  worst "
          f"{v['worst_share']*100:6.3f}%  dev {v['worst_deviation_points']:.3f} pts"
          f"  ({v['n_windows']} windows)")
assert worst <= cfg.window_tolerance_points, worst
print("OK  worst window deviation", f"{worst:.3f}", "pts <=",
      cfg.window_tolerance_points)

# 6. biography copy counts per person and per rewording
people = {p["person_id"]: p for p in read_jsonl(cfg.bios_dir / "people.jsonl")}
seen = defaultdict(Counter)
for s, pid, rw in zip(idx["subject"], idx["person_id"], idx["rewording_id"]):
    if s == BIO_SUBJECT:
        seen[pid][int(rw)] += 1
bad = 0
for pid, p in people.items():
    want = int(p["target_exposures"])
    if p["split"] != "train":
        if pid in seen: bad += 1
        continue
    counts = [seen[pid][r] for r in range(p["n_rewordings"])]
    if counts != pack.copies_per_rewording(want, p["n_rewordings"]): bad += 1
assert bad == 0, bad
print("OK  every person's copies match the tier and the 4-rewording spread")

# 7. decode 1,000 random segments
enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
src = {}
for s_ in cfg.train_subjects:
    for r in read_jsonl(cfg.train_dir / f"{cfg.slug(s_)}.jsonl.gz"):
        src[r["doc_id"]] = r["text"]
for r in read_jsonl(cfg.bios_dir / "bios_train.jsonl"):
    src[r["doc_id"]] = r["text"]
rng = np.random.default_rng(0)
sample = rng.choice(len(starts), size=1000, replace=False)
whole = 0
for j in sample:
    d = idx["doc_id"][j]; st = int(starts[j]); ln = int(lens[j]); off = int(idx["doc_offset"][j])
    want_ids = np.asarray(enc.encode_ordinary(src[d]), dtype=np.uint16)
    assert np.array_equal(arr[st:st+ln], want_ids[off:off+ln]), d
    if off == 0 and ln == want_ids.size:
        assert enc.decode(arr[st:st+ln].tolist()) == src[d], d
        whole += 1
print("OK  1,000 random segments decode to the source exactly "
      f"({whole} of them whole documents)")

# 8. held-out
for half in cfg.pack_halves:
    h = np.memmap(cfg.heldout_tokens_dir / f"{half}.bin", dtype=np.uint16, mode="r")
    hi = pack.read_index(cfg.heldout_tokens_dir / f"{half}.idx.parquet")
    hs = np.asarray(hi["start"], np.int64); hl = np.asarray(hi["length"], np.int64)
    cov = np.zeros(h.size, dtype=bool)
    for s, e in zip(hs, hs + hl): cov[s:e] = True
    ha = np.asarray(h)
    assert (ha[cov] != eot).all() and (ha[~cov] == eot).all()
    assert int(hl.max()) <= cfg.max_tokens
    assert set(hi["subject"]) == set(cfg.all_subjects)
    assert BIO_SUBJECT not in set(hi["subject"])
    print(f"OK  heldout/{half}.bin {h.size:,} tokens, {len(hs):,} docs, "
          f"max doc {int(hl.max()):,} <= {cfg.max_tokens}, "
          f"{len(set(hi['subject']))} subjects, no biographies")
print("\nALL REAL-BUILD INVARIANTS PASS")
