"""Bio generator: determinism, the QA split, rewordings, and the candidate sets."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import bio_generator as bg  # noqa: E402

N = 120
K = 4


@pytest.fixture(scope="module")
def people():
    return list(bg.generate(N, seed=0, rewordings=K, qa_split=True))


def _run(tmp_path, *extra, n=N, seed=0):
    out = tmp_path / "bios.jsonl"
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "bio_generator.py"),
         "--n", str(n), "--seed", str(seed), "--out", str(out), *extra],
        capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout + r.stderr
    return out


def test_same_seed_is_byte_identical(tmp_path):
    a = _run(tmp_path / "a", "--rewordings", "4", "--qa-split")
    b = _run(tmp_path / "b", "--rewordings", "4", "--qa-split")
    ha = hashlib.sha256(a.read_bytes()).hexdigest()
    hb = hashlib.sha256(b.read_bytes()).hexdigest()
    assert ha == hb, "same seed produced different bytes"
    # and the candidate sets too
    assert (hashlib.sha256((a.parent / "attribute_values.json").read_bytes()).hexdigest()
            == hashlib.sha256((b.parent / "attribute_values.json").read_bytes()).hexdigest())


def test_different_seed_differs(tmp_path):
    a = _run(tmp_path / "a", "--rewordings", "4", seed=0)
    b = _run(tmp_path / "b", "--rewordings", "4", seed=1)
    assert a.read_bytes() != b.read_bytes()


def test_names_are_unique(people):
    names = [p["name"] for p in people]
    assert len(set(names)) == len(names) == N


def test_qa_split_halves_share_no_person(people):
    train = {p["name"] for p in people if p["qa_split"] == "qa_train"}
    test = {p["name"] for p in people if p["qa_split"] == "qa_test"}
    assert train and test, "one half is empty"
    assert train.isdisjoint(test), "a person appears in both halves"
    assert len(train) + len(test) == N
    ids_train = {p["id"] for p in people if p["qa_split"] == "qa_train"}
    ids_test = {p["id"] for p in people if p["qa_split"] == "qa_test"}
    assert ids_train.isdisjoint(ids_test)
    # roughly balanced at the default fraction
    assert abs(len(train) - len(test)) <= 1


def test_qa_split_is_stable_across_rewording_count():
    """Changing --rewordings must not move people between halves."""
    a = {p["name"]: p["qa_split"]
         for p in bg.generate(N, seed=0, rewordings=1, qa_split=True)}
    b = {p["name"]: p["qa_split"]
         for p in bg.generate(N, seed=0, rewordings=7, qa_split=True)}
    assert a == b


def test_each_person_has_k_distinct_biographies(people):
    for p in people:
        bios = p["biographies"]
        assert len(bios) == K == p["n_rewordings"]
        assert [b["rewording_id"] for b in bios] == list(range(K))
        # every rewording states all five facts
        for b in bios:
            assert set(b["sentence_order"]) == set(bg.ATTRIBUTES)
            assert len(b["sentences"]) == len(bg.ATTRIBUTES)
        # the K versions must differ in wording or in order, not be copies
        signatures = {(tuple(b["sentence_order"]),
                       tuple(sorted(b["template_ids"].items()))) for b in bios}
        texts = {b["text"] for b in bios}
        assert len(signatures) > 1 or len(texts) > 1, \
            f"all {K} rewordings of {p['name']} are identical"


def test_rewordings_vary_overall(people):
    """Across the corpus, both template choice and sentence order should move."""
    orders, templates = set(), set()
    for p in people:
        for b in p["biographies"]:
            orders.add(tuple(b["sentence_order"]))
            templates.add(tuple(sorted(b["template_ids"].items())))
    assert len(orders) > 10
    assert len(templates) > 10


def test_every_fact_appears_in_every_biography(people):
    for p in people:
        for b in p["biographies"]:
            joined = b["text"]
            for attr, val in p["attributes"].items():
                assert val in joined, f"{attr}={val!r} missing from a rewording"


def test_qa_answers_match_attributes(people):
    for p in people:
        for qa in p["qa"]:
            assert qa["answer"] == p["attributes"][qa["attribute"]]
            assert p["name"] in qa["question"]
        assert {q["attribute"] for q in p["qa"]} == set(bg.ATTRIBUTES)


def test_attribute_values_json_covers_everything_in_the_output(tmp_path):
    out = _run(tmp_path, "--rewordings", "4", "--qa-split")
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    values = json.loads((out.parent / "attribute_values.json").read_text())

    assert set(values["attributes"]) == set(bg.ATTRIBUTES)
    assert values["n_people"] == len(rows)
    for attr, info in values["attributes"].items():
        candidates = set(info["values"])
        observed = {r["attributes"][attr] for r in rows}
        missing = observed - candidates
        assert not missing, f"{attr}: {len(missing)} observed values not listed"
        assert info["n_candidates"] == len(info["values"])
        assert info["n_observed"] == len(observed)
        assert len(candidates) >= len(observed)
        # the answers used for QA ranking must be in the candidate set too
        qa_answers = {q["answer"] for r in rows for q in r["qa"]
                      if q["attribute"] == attr}
        assert qa_answers <= candidates


def test_categorical_candidate_sets_are_the_full_pool(tmp_path):
    out = _run(tmp_path, "--rewordings", "2", n=30)
    values = json.loads((out.parent / "attribute_values.json").read_text())["attributes"]
    for attr, pool in (("birth_city", bg.CITIES), ("university", bg.UNIVERSITIES),
                       ("major", bg.MAJORS), ("employer", bg.EMPLOYERS)):
        assert set(values[attr]["values"]) == set(pool)
        # a 30-person sample cannot cover a 100+ value pool, so the pool must be bigger
        assert values[attr]["n_candidates"] > values[attr]["n_observed"]


def test_templates_meet_the_minimum_count():
    for attr in bg.ATTRIBUTES:
        assert len(bg.TEMPLATES[attr]) >= 5
        assert len(bg.QUESTIONS[attr]) >= 1


def test_rewordings_must_be_positive():
    with pytest.raises(ValueError):
        list(bg.generate(3, seed=0, rewordings=0))
