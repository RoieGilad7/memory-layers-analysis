"""The validator's own logic, on fixtures. The real run is `python -m data.validate`."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import validate
from data.hand_samples import _near_duplicate_pairs
from data.q2_probe import ProbeSet, ProbeRow, Candidates, score_random


def test_subsequence_counter():
    arr = np.array([1, 2, 3, 1, 2, 3, 4, 1, 2], dtype=np.uint16)
    assert validate._count_subsequence(arr, np.array([1, 2, 3], dtype=np.uint16)) == 2
    assert validate._count_subsequence(arr, np.array([1, 2], dtype=np.uint16)) == 3
    assert validate._count_subsequence(arr, np.array([9], dtype=np.uint16)) == 0
    assert validate._count_subsequence(arr, np.array([], dtype=np.uint16)) == 0
    # a pattern longer than the array
    assert (
        validate._count_subsequence(
            np.array([1], dtype=np.uint16), np.array([1, 2], dtype=np.uint16)
        )
        == 0
    )


def test_chisquare_matches_a_known_case():
    assert validate._chisquare_p([100] * 50) > 0.99
    assert validate._chisquare_p([100] * 49 + [400]) < 0.01
    assert validate._chisquare_p([10, 10]) == pytest.approx(1.0)


def test_tiling_detector_catches_each_way_a_file_can_be_wrong():
    block = 8
    # a clean little file: two documents separated by one EOT
    tokens = np.array([5, 6, 7, validate.EOT, 8, 9, 10, 11], dtype=np.uint16)
    idx = {"start": [0, 4], "length": [3, 4], "subject": ["a", "a"]}
    ok, detail, nums = validate._tiling(tokens, idx, 50257, "t")
    assert ok, detail
    assert nums["covered"] == 7 and nums["eot_gap_tokens"] == 1

    # an uncovered token that is not EOT
    bad = tokens.copy()
    bad[3] = 42
    ok, detail, _ = validate._tiling(bad, idx, 50257, "t")
    assert not ok and "non-EOT tokens outside documents" in detail

    # an EOT inside a document
    bad = tokens.copy()
    bad[1] = validate.EOT
    ok, detail, _ = validate._tiling(bad, idx, 50257, "t")
    assert not ok and "EOT tokens inside documents" in detail

    # overlapping segments
    ok, detail, _ = validate._tiling(
        tokens, {"start": [0, 2], "length": [4, 4], "subject": ["a", "a"]}, 50257, "t"
    )
    assert not ok and "overlap" in detail

    # an id outside the vocabulary
    ok, detail, _ = validate._tiling(tokens, idx, 8, "t")
    assert not ok and "max id" in detail


def test_overlap_ceilings_match_what_the_report_measured():
    """The ceilings exist because Github and FreeLaw are self-overlapping."""
    assert validate.OVERLAP_CEILING["Github"] == 0.25
    assert validate.OVERLAP_CEILING["FreeLaw"] == 0.15
    assert validate.OVERLAP_CEILING_DEFAULT == 0.05
    for s in ("Pile-CC", "PubMed Central", "Wikipedia (en)"):
        assert validate.OVERLAP_CEILING.get(s, validate.OVERLAP_CEILING_DEFAULT) == 0.05


def test_near_duplicate_net_uses_per_attribute_generic_words():
    """A global suffix list made "Systems Engineering" nest in every other one."""
    majors = [
        "Systems Engineering",
        "Aerospace Engineering",
        "Computer Science",
        "Computer Engineering",
        "Chemistry",
        "Biochemistry",
    ]
    pairs = _near_duplicate_pairs(majors, "major")
    why = {(min(p["a"], p["b"]), max(p["a"], p["b"])) for p in pairs}
    assert ("Biochemistry", "Chemistry") in why  # a real containment
    assert ("Aerospace Engineering", "Systems Engineering") not in why
    assert ("Computer Engineering", "Computer Science") not in {
        (p["a"], p["b"]) for p in pairs if "nest" in p["why"]
    }
    # universities DO strip the academic suffix, so these are the same entity
    unis = ["Boston College", "Boston University"]
    assert _near_duplicate_pairs(unis, "university")


def test_the_first_word_rule_is_off_for_dates():
    dates = ["April 2, 1956", "April 3, 1997", "May 5, 1960"]
    assert _near_duplicate_pairs(dates, "birth_date", skip_first_word=True) == []
    assert _near_duplicate_pairs(dates, "birth_date", skip_first_word=False)


def test_random_scorer_sits_in_the_middle_of_the_list():
    """The A15 floor, on a synthetic candidate list."""
    cand = {
        "x": Candidates(
            attribute="x",
            values=[f"v{i}" for i in range(200)],
            first=np.arange(200, dtype=np.int64),
        )
    }
    rows = [
        ProbeRow(
            fact_id=f"f{i}",
            person_id="p",
            split="train",
            tier="rare",
            attribute="x",
            role="test",
            true_value=f"v{i % 200}",
            prompt_ids=[1, 2, 3],
            true_index=i % 200,
        )
        for i in range(4000)
    ]
    res = score_random(ProbeSet(rows, cand), seed=0)
    assert 0.45 < res["overall"]["mean_rank_fraction"] < 0.55
    assert res["overall"]["top1"] < 0.02
