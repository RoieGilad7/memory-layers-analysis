"""Cleaning + exact dedup + the 50% 13-gram rule, on synthetic fixtures."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import dedup
from data.common import get_encoder, ngram_hashes, overlap_rate, read_jsonl
from tests._data_fixtures import LICENSE, body, build_corpus, make_cfg, write_raw


@pytest.fixture
def built(tmp_path):
    cfg = make_cfg(tmp_path / "out")
    planted = build_corpus(cfg)
    log = dedup.run(cfg)
    return cfg, planted, log


def _docs(path):
    return list(read_jsonl(path))


# ------------------------------------------------------------- exact dedup
def test_exact_duplicate_within_a_split_is_dropped(built):
    cfg, _, log = built
    c = log["per_subject"]["train"]["Pile-CC"]
    assert c["dropped_exact_dup_same_split"] == 1
    ids = [d["doc_id"] for d in _docs(cfg.train_dir / "pile_cc.jsonl.gz")]
    assert len(ids) == len(set(ids))
    # the first copy (line 20) survives, the later one (line 999) does not
    assert "pile_cc-train00-20" in ids
    assert "pile_cc-train00-999" not in ids


def test_exact_duplicate_across_splits_is_dropped(built):
    cfg, planted, log = built
    assert log["per_subject"]["heldout"]["Pile-CC"]["dropped_exact_dup_cross_split"] == 1
    pool_ids = [d["doc_id"] for d in _docs(cfg.heldout_pool_dir / "pile_cc.jsonl.gz")]
    assert "pile_cc-val-0" not in pool_ids          # the verbatim copy
    train_hashes = {d["sha256"] for d in _docs(cfg.train_dir / "pile_cc.jsonl.gz")}
    pool_hashes = {d["sha256"] for d in _docs(cfg.heldout_pool_dir / "pile_cc.jsonl.gz")}
    assert not (train_hashes & pool_hashes)


def test_empty_and_short_documents_are_dropped_with_their_reason(built):
    _, _, log = built
    c = log["per_subject"]["heldout"]["Pile-CC"]
    assert c["dropped_empty"] == 1
    assert c["dropped_under_min_tokens"] == 1


# --------------------------------------------------------- the 13-gram rule
def test_ngram_rule_drops_a_copy_but_keeps_a_shared_license_header(built):
    cfg, _, log = built
    pool = _docs(cfg.heldout_pool_dir / "pile_cc.jsonl.gz")
    ids = {d["doc_id"] for d in pool}
    # doc 1 is a training document plus a short tail: >50% of its 13-grams
    # are in the training set, so it must be gone
    assert "pile_cc-val-1" not in ids
    assert log["ngram_overlap"]["Pile-CC"]["docs_dropped"] == 1
    # doc 2 shares only the license header, so it must survive
    assert "pile_cc-val-2" in ids
    kept = next(d for d in pool if d["doc_id"] == "pile_cc-val-2")
    assert 0.0 < kept["ngram_overlap"] <= cfg.ngram_drop_threshold


def test_ngram_rule_threshold_is_what_decides(tmp_path):
    """A document whose overlap sits either side of 0.50 flips the decision."""
    enc = get_encoder("gpt2", 50257)
    shared = body("sh", 600, 1)
    fresh = body("fr", 600, 2)
    tr = ngram_hashes(enc.encode_ordinary(shared), 13)
    index = np.unique(tr)
    mostly_copied = f"{shared} {body('tail', 40, 3)}"
    half_and_half = f"{shared} {fresh}"
    r_copy = overlap_rate(ngram_hashes(enc.encode_ordinary(mostly_copied), 13), index)
    r_half = overlap_rate(ngram_hashes(enc.encode_ordinary(half_and_half), 13), index)
    assert r_copy[0] / r_copy[1] > 0.5
    assert r_half[0] / r_half[1] < 0.5


def test_aggregate_overlap_rate_is_reported_per_subject(built):
    _, _, log = built
    for subject in ("Pile-CC", "Github", "USPTO Backgrounds"):
        o = log["ngram_overlap"][subject]
        assert 0.0 <= o["aggregate_overlap_rate"] <= 1.0
        assert o["heldout_ngrams_total"] > 0
    # USPTO has no training text at all, so it cannot be contaminated
    assert log["ngram_overlap"]["USPTO Backgrounds"]["aggregate_overlap_rate"] == 0.0
    assert log["ngram_overlap"]["USPTO Backgrounds"]["docs_dropped"] == 0


def test_ngram_hashes_are_stable_and_not_process_seeded():
    h1 = ngram_hashes(list(range(50)), 13)
    h2 = ngram_hashes(np.arange(50), 13)
    assert np.array_equal(h1, h2)
    assert h1.dtype == np.uint64 and h1.size == 38
    # a single changed token changes only the n-grams covering it
    changed = list(range(50))
    changed[25] = 999
    h3 = ngram_hashes(changed, 13)
    assert (h1 != h3).sum() == 13


# ------------------------------------------------------------- the 4096 cap
def test_cap_is_applied_to_every_stored_document(tmp_path):
    cfg = make_cfg(tmp_path / "out", **{"document.max_tokens": 64,
                                        "document.min_tokens": 20})
    enc = get_encoder("gpt2", 50257)
    write_raw(cfg, "train", "Pile-CC", [(0, f"{LICENSE} {body('tr', 600, 0)}")])
    write_raw(cfg, "train", "Github", [(0, f"{LICENSE} {body('gh', 600, 0)}")])
    for subject in ("Pile-CC", "Github", "USPTO Backgrounds"):
        write_raw(cfg, "heldout", subject,
                  [(i, f"{LICENSE} {body('ho', 600, i)}") for i in range(4)])
    dedup.run(cfg)
    files = list(cfg.train_dir.glob("*.jsonl.gz")) + \
        list(cfg.heldout_pool_dir.glob("*.jsonl.gz"))
    assert files
    n = 0
    for f in files:
        for rec in read_jsonl(f):
            assert rec["n_tokens"] <= 64
            assert len(enc.encode_ordinary(rec["text"])) <= 64
            assert rec["truncated"] is True
            n += 1
    assert n > 0


def test_a_huge_document_is_cleaned_and_capped_like_a_small_one(tmp_path):
    """The prefix shortcut in clean_record must not change the result."""
    cfg = make_cfg(tmp_path / "out", **{"document.max_tokens": 64,
                                        "document.min_tokens": 20})
    from data.common import CHARS_PER_TOKEN_BOUND, clean_text
    from data.dedup import clean_record
    limit = 64 * CHARS_PER_TOKEN_BOUND
    for raw in (
            "head  line\n" + "a   b\t c  " * (limit // 4),     # far past 2*limit
            "head  line\n" + " " * (5 * limit) + "tail words here " * 50,
    ):                                                          # mostly blank
        rec = {"doc_id": "x-y-0", "subject": "Pile-CC", "split": "train",
               "source": "train/00.jsonl.zst", "line": 0, "text": raw}
        got, reason = clean_record(get_encoder("gpt2", 50257), rec, cfg)
        assert reason is None
        # identical to cleaning the whole document and then capping
        full = clean_text(raw, cfg.unicode_form, cfg.max_consecutive_newlines)
        assert full.startswith(got["text"][:200])
        assert got["n_tokens"] <= 64


# ---------------------------------------------------- the biography exemption
def test_near_duplicate_biographies_pass_through_dedup_untouched(tmp_path):
    """The 13-gram rule must never be able to touch biography text.

    Four rewordings of one person restate the same five facts, so their 13-gram
    overlap with each other is enormous by construction. If the rule applied,
    it would delete the held-out biographies it exists to protect.
    """
    cfg = make_cfg(tmp_path / "out", **{
        "subjects": {"train": ["Pile-CC", "bio"], "heldout_only": [],
                     "slugs": {"Pile-CC": "pile_cc", "bio": "bio"}},
        "dedup.ngram_exempt_subjects": ["bio"],
    })
    assert cfg.ngram_rule_applies("Pile-CC") and not cfg.ngram_rule_applies("bio")

    # one person, five facts, four near-identical rewordings -- and the held-out
    # copies are verbatim restatements of the training ones
    facts = "born on March 4, 1987 in Austin, Texas, studied Economics at " \
            "Rice University, and works at Acme Metals"
    rewordings = [
        f"Ada Lovelace was {facts}. " + body("pad", 300, i) for i in range(4)]
    write_raw(cfg, "train", "bio", list(enumerate(rewordings)))
    write_raw(cfg, "heldout", "bio",
              [(10 + i, t.replace("Ada Lovelace", "Ada Lovelace")) for i, t in
               enumerate(r + " " + body("extra", 60, i) for i, r in
                         enumerate(rewordings))])
    # a Pile subject in the same build, to prove the rule still runs elsewhere
    shared = body("sh", 600, 1)
    write_raw(cfg, "train", "Pile-CC", [(0, f"{LICENSE} {shared}")])
    write_raw(cfg, "heldout", "Pile-CC",
              [(0, f"{LICENSE} {shared} tail"),
               (1, f"{LICENSE} {body('fresh', 600, 9)}")])

    log = dedup.run(cfg)

    bio = log["ngram_overlap"]["bio"]
    assert bio["exempt"] is True
    assert bio["docs_dropped"] == 0
    assert bio["aggregate_overlap_rate"] is None    # not "0.0" -- never measured
    assert log["per_subject"]["heldout"]["bio"]["dropped_ngram_overlap"] == 0

    pool = _docs(cfg.heldout_pool_dir / "bio.jsonl.gz")
    assert len(pool) == 4
    for rec in pool:
        assert rec["ngram_rule"] == "exempt"
        assert "ngram_overlap" not in rec

    # the same build still drops a near-duplicate Pile document
    assert log["ngram_overlap"]["Pile-CC"]["exempt"] is False
    assert log["ngram_overlap"]["Pile-CC"]["docs_dropped"] == 1
    assert log["ngram_exempt_subjects"] == ["bio"]


def test_the_exemption_is_what_saves_the_biographies(tmp_path):
    """With the exemption removed, the same input loses most of the held-out set.

    This is the test that gives the exemption its reason to exist: it shows the
    rule really would fire on biographies.
    """
    def build(exempt):
        cfg = make_cfg(tmp_path / f"out{int(exempt)}", **{
            "subjects": {"train": ["bio"], "heldout_only": [],
                         "slugs": {"bio": "bio"}},
            "dedup.ngram_exempt_subjects": ["bio"] if exempt else [],
        })
        facts = "born on March 4, 1987 in Austin, Texas, studied Economics at " \
                "Rice University, and works at Acme Metals"
        rew = [f"Ada Lovelace was {facts}. " + body("pad", 300, i) for i in range(4)]
        write_raw(cfg, "train", "bio", list(enumerate(rew)))
        write_raw(cfg, "heldout", "bio", [(10 + i, t) for i, t in enumerate(
            r + " " + body("extra", 60, i) for i, r in enumerate(rew))])
        log = dedup.run(cfg)
        return log["ngram_overlap"]["bio"]["docs_dropped"], \
            len(_docs(cfg.heldout_pool_dir / "bio.jsonl.gz"))

    dropped_exempt, kept_exempt = build(True)
    dropped_plain, kept_plain = build(False)
    assert (dropped_exempt, kept_exempt) == (0, 4)
    assert dropped_plain > 0, "the rule should fire on biographies without the exemption"
    assert kept_plain < kept_exempt
