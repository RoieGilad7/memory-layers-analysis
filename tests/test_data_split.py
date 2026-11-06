"""Held-out label/test halves: disjoint, deterministic, trimmed, counted."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import dedup, split
from data.common import heldout_half, read_jsonl
from tests._data_fixtures import LICENSE, body, build_corpus, make_cfg, write_raw


@pytest.fixture
def built(tmp_path):
    cfg = make_cfg(tmp_path / "out")
    build_corpus(cfg, n_heldout=40)
    dedup.run(cfg)
    rep = split.run(cfg)
    return cfg, rep


def _ids(cfg, half, subject):
    path = cfg.heldout_dir / half / f"{cfg.slug(subject)}.jsonl.gz"
    return [d["doc_id"] for d in read_jsonl(path)]


def test_halves_are_disjoint_by_whole_document(built):
    cfg, rep = built
    for subject in cfg.all_subjects:
        label, test = set(_ids(cfg, "label", subject)), set(_ids(cfg, "test", subject))
        assert label and test
        assert not (label & test)
        assert rep["per_subject"][subject]["halves_disjoint"] is True


def test_half_assignment_is_a_seeded_hash_of_the_doc_id(built):
    cfg, _ = built
    for subject in cfg.all_subjects:
        for half in cfg.heldout_halves:
            for doc_id in _ids(cfg, half, subject):
                assert heldout_half(doc_id, cfg.seed, cfg.heldout_halves) == half


def test_a_different_seed_moves_documents(built):
    cfg, _ = built
    ids = _ids(cfg, "label", "USPTO Backgrounds") + _ids(cfg, "test", "USPTO Backgrounds")
    a = [heldout_half(i, cfg.seed, cfg.heldout_halves) for i in ids]
    b = [heldout_half(i, cfg.seed + 1, cfg.heldout_halves) for i in ids]
    assert a != b


def test_each_half_is_trimmed_to_the_token_budget(built):
    cfg, rep = built
    for subject in cfg.all_subjects:
        for half in cfg.heldout_halves:
            st = rep["per_subject"][subject]["halves"][half]
            if st["tokens_available"] >= cfg.heldout_tokens_per_half:
                # the budget is reached, and overshot by at most one document
                assert st["tokens"] >= cfg.heldout_tokens_per_half
                assert st["tokens"] < cfg.heldout_tokens_per_half + cfg.max_tokens
                assert st["below_target_tokens"] is False


def test_documents_written_match_the_reported_counts(built):
    cfg, rep = built
    for subject in cfg.all_subjects:
        for half in cfg.heldout_halves:
            recs = list(read_jsonl(cfg.heldout_dir / half /
                                   f"{cfg.slug(subject)}.jsonl.gz"))
            st = rep["per_subject"][subject]["halves"][half]
            assert len(recs) == st["docs"]
            assert sum(r["n_tokens"] for r in recs) == st["tokens"]
            assert all(r["half"] == half for r in recs)
            assert all(r["subject"] == subject for r in recs)


def test_a_subject_below_the_document_minimum_is_reported_not_crashed(tmp_path):
    cfg = make_cfg(tmp_path / "out",
                   **{"targets.heldout_min_docs_per_half": 500})
    build_corpus(cfg, n_heldout=12)
    dedup.run(cfg)
    rep = split.run(cfg)
    assert rep["subjects_below_min_docs"]
    for entry in rep["subjects_below_min_docs"]:
        assert "/" in entry                      # "<subject>/<half>"
    assert rep["min_docs_per_half"] == 500


def test_halves_split_is_stable_when_documents_are_reordered(tmp_path):
    """Order in the raw file must not change which half a document lands in."""
    docs = [(i, f"{LICENSE} {body('ho', 300, i)}") for i in range(20)]
    seen = []
    for order in (docs, list(reversed(docs))):
        cfg = make_cfg(tmp_path / f"out{len(seen)}")
        write_raw(cfg, "train", "Pile-CC", [(0, body("tr", 600, 0))])
        write_raw(cfg, "train", "Github", [(0, body("gh", 600, 0))])
        for subject in cfg.all_subjects:
            write_raw(cfg, "heldout", subject, order)
        dedup.run(cfg)
        split.run(cfg)
        seen.append({h: sorted(_ids(cfg, h, "USPTO Backgrounds"))
                     for h in cfg.heldout_halves})
    assert seen[0] == seen[1]
