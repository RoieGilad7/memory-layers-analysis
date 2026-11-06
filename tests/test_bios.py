"""The biography generator. No network: the Pile name check runs against a
tiny synthetic corpus written into tmp_path.
"""

import gzip
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import data.bios_data as bd
from data import bios
from data.common import DataConfig, dumps_record, get_encoder, open_write, read_jsonl

CONFIG = Path(__file__).resolve().parent.parent / "configs" / "data" / "v1.yaml"
ATTRS = bd.ATTRIBUTES


# --------------------------------------------------------------------------
# chi-square, without pulling in scipy for one test
# --------------------------------------------------------------------------
def _gser(a, x, itmax=500, eps=3e-12):
    ap, total, delta = a, 1.0 / a, 1.0 / a
    for _ in range(itmax):
        ap += 1
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * eps:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a, x, itmax=500, eps=3e-12):
    tiny = 1e-300
    b, c, d = x + 1.0 - a, 1.0 / tiny, 1.0 / (x + 1.0 - a)
    h = d
    for i in range(1, itmax):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chisquare_p(counts):
    """p-value of Pearson's chi-square against a uniform expectation."""
    n, k = sum(counts), len(counts)
    expected = n / k
    stat = sum((c - expected) ** 2 / expected for c in counts)
    df = k - 1
    a, x = df / 2.0, stat / 2.0
    if x <= 0:
        return 1.0
    return 1.0 - _gser(a, x) if x < a + 1.0 else _gcf(a, x)


def test_chisquare_helper_is_sane():
    """A uniform sample passes, a skewed one does not -- the test's own test."""
    assert chisquare_p([100] * 50) > 0.99
    assert chisquare_p([100] * 49 + [400]) < 0.01


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------
def make_cfg(
    root: Path, seed=None, n_train=200, n_control=50, candidates=400, **over
) -> DataConfig:
    """The real v1 config with fewer people, so a test build is a few seconds.

    Value lists, templates and rewordings are left at full size -- they are what
    most of these tests are about.
    """
    raw = yaml.safe_load(CONFIG.read_text())
    r = str(root)
    raw["paths"] = {
        "root": r,
        "raw": f"{r}/raw",
        "work": f"{r}/_work",
        "train": f"{r}/train",
        "heldout_pool": f"{r}/heldout_pool",
        "heldout": f"{r}/heldout",
        "reports": f"{r}/reports",
    }
    raw["small"]["root"] = r
    if seed is not None:
        raw["seed"] = seed
    pe = raw["bios"]["people"]
    pe["n_train"] = n_train
    pe["n_control"] = n_control
    pe["name_candidates_per_gender"] = candidates
    # keep the tiers even (so they can be gender-balanced) and summing to
    # n_train, which DataConfig checks
    scale = n_train / 2000
    sized = [max(2, int(t["n_people"] * scale) // 2 * 2) for t in pe["tiers"]]
    sized[0] += n_train - sum(sized)
    assert sized[0] > 0 and sized[0] % 2 == 0, sized
    for t, n in zip(pe["tiers"], sized):
        t["n_people"] = n
    for k, v in over.items():
        section, _, field = k.partition(".")
        raw[section][field] = v
    return DataConfig(raw=raw)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root = tmp_path_factory.mktemp("bios")
    cfg = make_cfg(root)
    manifest = bios.run(cfg, name_check=False)
    return cfg, manifest


def _people(cfg):
    return list(read_jsonl(cfg.bios_dir / "people.jsonl"))


def _bios(cfg):
    return list(read_jsonl(cfg.bios_dir / "bios_train.jsonl")) + list(
        read_jsonl(cfg.bios_dir / "bios_control.jsonl")
    )


def _facts(cfg):
    return list(read_jsonl(cfg.bios_dir / "facts.jsonl"))


# --------------------------------------------------------------------------
# determinism
# --------------------------------------------------------------------------
def _digest(root: Path):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def test_same_seed_is_byte_identical_and_a_new_seed_is_not(tmp_path):
    a = make_cfg(tmp_path / "a")
    b = make_cfg(tmp_path / "b")
    c = make_cfg(tmp_path / "c", seed=999)
    for cfg in (a, b, c):
        bios.run(cfg, name_check=False)
    da, db, dc = _digest(a.bios_dir), _digest(b.bios_dir), _digest(c.bios_dir)
    assert da == db
    assert set(da) == set(dc)
    # templates.json is seed-independent by construction; everything else moves
    moved = {k for k in da if da[k] != dc[k]}
    assert {
        "people.jsonl",
        "facts.jsonl",
        "bios_train.jsonl",
        "bios_control.jsonl",
    } <= moved


# --------------------------------------------------------------------------
# people
# --------------------------------------------------------------------------
def test_people_counts_names_genders_and_tiers(built):
    cfg, m = built
    people = _people(cfg)
    assert len(people) == cfg.bio_n_train + cfg.bio_n_control
    assert Counter(p["split"] for p in people) == {
        "train": cfg.bio_n_train,
        "control": cfg.bio_n_control,
    }

    names = [p["name"] for p in people]
    assert len(set(names)) == len(names)
    assert len({p["person_id"] for p in people}) == len(people)

    g = Counter(p["gender"] for p in people)
    assert set(g) == {"female", "male"}
    assert abs(g["female"] - g["male"]) / len(people) < 0.05

    tiers = Counter(p["tier"] for p in people)
    for t in cfg.bio_tiers:
        assert tiers[t["name"]] == t["n_people"], t["name"]
    assert tiers[cfg.bio_control_tier] == cfg.bio_n_control

    # exactly, not approximately, balanced inside every tier
    per = Counter((p["tier"], p["gender"]) for p in people)
    for t in list(cfg.bio_tiers) + [
        {"name": cfg.bio_control_tier, "n_people": cfg.bio_n_control}
    ]:
        assert (
            per[(t["name"], "female")] == per[(t["name"], "male")] == t["n_people"] // 2
        ), t["name"]


def test_exposure_targets_follow_the_tier(built):
    cfg, _ = built
    want = {t["name"]: t["exposures"] for t in cfg.bio_tiers}
    want[cfg.bio_control_tier] = 0
    for p in _people(cfg):
        assert p["target_exposures"] == want[p["tier"]]
        assert p["n_rewordings"] == cfg.bio_n_rewordings


def test_control_people_appear_only_in_the_control_file(built):
    cfg, _ = built
    control = {p["person_id"] for p in _people(cfg) if p["split"] == "control"}
    train_ids = {r["person_id"] for r in read_jsonl(cfg.bios_dir / "bios_train.jsonl")}
    ctrl_ids = {r["person_id"] for r in read_jsonl(cfg.bios_dir / "bios_control.jsonl")}
    assert control and not (control & train_ids)
    assert ctrl_ids == control


# --------------------------------------------------------------------------
# values
# --------------------------------------------------------------------------
def test_every_fact_value_is_in_attribute_values(built):
    cfg, _ = built
    lists = json.loads((cfg.bios_dir / "attribute_values.json").read_text())["values"]
    sets = {a: set(v) for a, v in lists.items()}
    assert set(sets) == set(ATTRS)
    for p in _people(cfg):
        for attr, val in p["facts"].items():
            assert val in sets[attr], (attr, val)


def test_first_tokens_are_unique_within_each_list(built):
    cfg, _ = built
    enc = get_encoder("gpt2", 50257)
    data = json.loads((cfg.bios_dir / "attribute_values.json").read_text())
    for attr, vals in data["values"].items():
        n = 2 if attr in cfg.bio_first_two_tokens_unique else 1
        prefixes = [tuple(enc.encode_ordinary(" " + v)[:n]) for v in vals]
        assert len(set(prefixes)) == len(vals), f"{attr}: first {n} token(s) not unique"
        assert data["tokens"][attr][
            "first_two_tokens_unique" if n == 2 else "first_token_unique"
        ]


@pytest.fixture(scope="module")
def full_people(tmp_path_factory):
    """The real 2,500-person draw, without rendering or writing anything.

    Uniformity has to be tested at full size: the module fixture has 250 people
    against 300 universities, under one expected count per value, where Pearson's
    chi-square does not apply.
    """
    cfg = make_cfg(
        tmp_path_factory.mktemp("full"), n_train=2000, n_control=500, candidates=1500
    )
    enc = get_encoder("gpt2", 50257)
    values, _ = bios.build_value_lists(cfg, enc)
    candidates = bios.build_name_candidates(cfg)
    people, _stats = bios.build_people(cfg, values, candidates, [])
    return cfg, values, people


def test_value_frequencies_are_uniform(full_people):
    """Facts must be uniformly random, or "it could only have stored it" fails."""
    cfg, values, people = full_people
    assert len(people) == 2500
    for attr in ATTRS:
        counts = Counter(p["facts"][attr] for p in people)
        full = [counts.get(v, 0) for v in values[attr]]
        assert sum(full) == len(people)
        expected = len(people) / len(values[attr])
        assert expected >= 5, f"{attr}: expected count {expected:.1f} too low"
        p = chisquare_p(full)
        assert p > 0.01, f"{attr}: chi-square p={p:.4g} -- not uniform"


def test_value_lists_are_the_configured_size(full_people):
    cfg, values, _ = full_people
    for attr in ATTRS:
        assert len(values[attr]) == cfg.bio_value_targets[attr], attr


# --------------------------------------------------------------------------
# rewordings
# --------------------------------------------------------------------------
def test_every_rewording_carries_all_five_values_verbatim(built):
    cfg, _ = built
    facts = {p["person_id"]: p["facts"] for p in _people(cfg)}
    seen = Counter()
    for rec in _bios(cfg):
        text = rec["text"]
        for attr, val in facts[rec["person_id"]].items():
            assert text.count(val) >= 1, (rec["doc_id"], attr, val)
        seen[rec["person_id"]] += 1
    assert set(seen.values()) == {cfg.bio_n_rewordings}


def test_rewording_doc_ids_follow_the_interface(built):
    cfg, _ = built
    for rec in _bios(cfg):
        assert rec["doc_id"] == f"bio-{rec['person_id']}-{rec['rewording_id']}"
        assert 0 <= rec["rewording_id"] < cfg.bio_n_rewordings


def test_held_out_template_wording_never_enters_training_text(built):
    cfg, _ = built
    train_text = "\n".join(
        r["text"] for r in read_jsonl(cfg.bios_dir / "bios_train.jsonl")
    )
    control_text = "\n".join(
        r["text"] for r in read_jsonl(cfg.bios_dir / "bios_control.jsonl")
    )
    for marker in bd.HELDOUT_MARKERS:
        assert marker not in train_text, marker
        assert marker not in control_text, marker
    # and no rendered held-out sentence appears either
    for attr in ATTRS:
        for t in bd.HELDOUT_TEMPLATES[attr]:
            head = t.split("{v}")[0]
            for ph in ("{Subj}", "{Poss}", "{poss}", "{obj}"):
                head = head.replace(ph, "")
            frag = head.strip()[-25:]
            assert frag and frag not in train_text, t


def test_pronouns_match_the_gender_field(built):
    cfg, _ = built
    gender = {p["person_id"]: p["gender"] for p in _people(cfg)}
    female = {" She ", " she ", " Her ", " her ", "She ", "Her "}
    male = {" He ", " he ", " His ", " his ", " him ", "He ", "His "}
    saw_pronoun = 0
    for rec in _bios(cfg):
        text = " " + rec["text"] + " "
        g = gender[rec["person_id"]]
        wrong = male if g == "female" else female
        for token in wrong:
            assert token not in text, (rec["doc_id"], g, token)
        right = female if g == "female" else male
        saw_pronoun += any(t in text for t in right)
    assert saw_pronoun > 0


def test_first_sentence_names_the_person_and_later_ones_mix(built):
    """The first sentence must NAME the person -- not necessarily open with it.

    Templates like "Illness interrupted a whole year of {poss} studies at ..."
    name the person mid-sentence, which is the point of having them.
    """
    cfg, _ = built
    names = {p["person_id"]: p["name"] for p in _people(cfg)}
    for rec in _bios(cfg):
        name = names[rec["person_id"]]
        first, _, later = rec["text"].partition(". ")
        assert name in first, rec["text"][:90]
        # a mix: the name again somewhere later, and at least one pronoun
        has_name = name in later
        has_pron = re.search(r"\b(she|he|her|his|him)\b", later, re.I) is not None
        assert has_name and has_pron, rec["text"]


# --------------------------------------------------------------------------
# prompts
# --------------------------------------------------------------------------
def test_facts_rows_cover_every_person_attribute_and_role(built):
    cfg, m = built
    people = _people(cfg)
    rows = _facts(cfg)
    expected = (
        len(people) * len(ATTRS) * (cfg.bio_n_rewordings + cfg.bio_n_heldout_templates)
    )
    assert len(rows) == expected == m["facts"]["rows"]
    assert len({r["fact_id"] for r in rows}) == len(rows)
    by_role = Counter(r["role"] for r in rows)
    assert by_role["discovery"] == len(people) * len(ATTRS) * len(
        cfg.bio_discovery_rewordings
    )
    assert by_role["test"] == len(people) * len(ATTRS) * len(cfg.bio_test_rewordings)
    assert (
        by_role[cfg.bio_heldout_role]
        == len(people) * len(ATTRS) * cfg.bio_n_heldout_templates
    )


def test_training_prompts_are_exact_prefixes_of_their_biography(built):
    cfg, _ = built
    text_of = {r["doc_id"]: r["text"] for r in _bios(cfg)}
    checked = 0
    for row in _facts(cfg):
        if row["held_out_template"]:
            continue
        bio = text_of[row["doc_id"]]
        full = row["prompt"] + row["continuation"]
        assert bio.startswith(full), row["fact_id"]
        assert row["continuation"] == " " + row["true_value"]
        assert not row["prompt"].endswith(" ")
        # the value does not leak into the prompt
        assert row["true_value"] not in row["prompt"], row["fact_id"]
        # ...and the value really does start where the prompt stops
        assert bio[len(row["prompt"]) + 1 :].startswith(row["true_value"])
        checked += 1
    assert checked == len(_people(cfg)) * len(ATTRS) * cfg.bio_n_rewordings


def test_held_out_prompts_stop_before_the_value_too(built):
    cfg, _ = built
    people = {p["person_id"]: p for p in _people(cfg)}
    n = 0
    for row in _facts(cfg):
        if not row["held_out_template"]:
            continue
        assert row["rewording_id"] is None and row["doc_id"] is None
        assert row["role"] == cfg.bio_heldout_role
        assert row["continuation"] == " " + row["true_value"]
        assert not row["prompt"].endswith(" ")
        assert row["true_value"] not in row["prompt"], row["fact_id"]
        # the prompt is a prefix of the regenerated held-out biography
        person = people[row["person_id"]]
        plan = bios.person_plan(cfg, person)[cfg.bio_heldout_context_rewording]
        text, _spans = bios.build_biography(
            cfg, person, plan, heldout=(row["attribute"], row["template_id"])
        )
        assert text.startswith(row["prompt"] + row["continuation"]), row["fact_id"]
        n += 1
    assert n > 0


def test_row_value_tier_and_split_match_people_jsonl(built):
    cfg, _ = built
    by_id = {p["person_id"]: p for p in _people(cfg)}
    for row in _facts(cfg):
        p = by_id[row["person_id"]]
        assert row["true_value"] == p["facts"][row["attribute"]]
        assert row["tier"] == p["tier"]
        assert row["split"] == p["split"]


def test_value_token_ids_tokenize_the_continuation(built):
    cfg, _ = built
    enc = get_encoder("gpt2", 50257)
    for row in _facts(cfg)[:500]:
        assert row["value_token_ids"] == enc.encode_ordinary(row["continuation"])


# --------------------------------------------------------------------------
# the Pile name check
# --------------------------------------------------------------------------
def test_a_name_present_in_the_corpus_is_rejected(tmp_path):
    """One generated name planted in a fixture corpus must not reach people.jsonl."""
    cfg = make_cfg(tmp_path / "out", n_train=20, n_control=10, candidates=40)
    candidates = bios.build_name_candidates(cfg)
    # the first candidate of each gender would otherwise certainly be chosen
    planted = [
        candidates[0]["name"],
        next(c["name"] for c in candidates if c["gender"] == "male"),
    ]
    corpus = cfg.root / "train" / "pile_cc.jsonl.gz"
    with open_write(corpus) as fh:
        fh.write(
            dumps_record(
                {
                    "doc_id": "pile_cc-train00-0",
                    "subject": "Pile-CC",
                    "split": "train",
                    "source": "train/00.jsonl.zst",
                    "line": 0,
                    "text": f"A news item mentioning {planted[0]} and also {planted[1]} "
                    "in passing, plus Some Other Person who is not ours.",
                }
            )
        )

    found = bios.scan_corpus_for_names([corpus], [c["name"] for c in candidates])
    assert set(planted) <= set(found["names_found"])
    assert found["n_names_found"] == len(set(planted))

    bios.run(cfg, name_check=True)
    names = {p["name"] for p in _people(cfg)}
    for name in planted:
        assert name not in names, name
    check = json.loads((cfg.bios_dir / "name_check.json").read_text())
    assert check["skipped"] is False
    assert set(planted) <= set(check["names_found"])


def test_name_check_is_case_sensitive_and_needs_a_single_space(tmp_path):
    cfg = make_cfg(tmp_path / "out", n_train=20, n_control=10, candidates=40)
    cand = bios.build_name_candidates(cfg)[0]["name"]
    first, last = cand.split(" ")
    corpus = cfg.root / "train" / "pile_cc.jsonl.gz"
    with open_write(corpus) as fh:
        fh.write(
            dumps_record(
                {
                    "doc_id": "d",
                    "subject": "Pile-CC",
                    "split": "train",
                    "source": "s",
                    "line": 0,
                    "text": f"{first.upper()} {last.upper()} and "
                    f"{first}\n{last} and {first}  {last}",
                }
            )
        )
    found = bios.scan_corpus_for_names([corpus], [cand])
    assert found["names_found"] == []


def test_build_fails_loudly_when_the_corpus_is_missing(tmp_path):
    cfg = make_cfg(tmp_path / "out", n_train=20, n_control=10, candidates=40)
    with pytest.raises(RuntimeError, match="name check found no corpus"):
        bios.run(cfg, name_check=True)


def test_not_enough_surviving_names_is_an_error_not_a_short_set(tmp_path):
    cfg = make_cfg(tmp_path / "out", n_train=40, n_control=20, candidates=20)
    with pytest.raises(RuntimeError, match="not enough surviving names"):
        bios.run(cfg, name_check=False)


# --------------------------------------------------------------------------
# templates and manifest
# --------------------------------------------------------------------------
def test_templates_json_marks_held_out_templates(built):
    cfg, _ = built
    data = json.loads((cfg.bios_dir / "templates.json").read_text())
    for attr in ATTRS:
        rows = data["templates"][attr]
        train = [r for r in rows if not r["held_out_template"]]
        held = [r for r in rows if r["held_out_template"]]
        assert len(train) == cfg.bio_n_templates
        assert len(held) == cfg.bio_n_heldout_templates
        assert {r["text"] for r in train} == set(bd.TRAIN_TEMPLATES[attr])
        assert {r["text"] for r in held} == set(bd.HELDOUT_TEMPLATES[attr])
        # the invariant that makes a paraphrase a real paraphrase
        ctx = {r["pre_value_context"] for r in train}
        assert not ctx & {r["pre_value_context"] for r in held}


def test_template_pools_are_the_configured_size():
    import data.bios_data as d

    for attr in ATTRS:
        assert len(d.TRAIN_TEMPLATES[attr]) == 20
        assert len(d.HELDOUT_TEMPLATES[attr]) == 4


def test_a_persons_four_rewordings_use_four_different_templates(built):
    cfg, _ = built
    for p in _people(cfg)[:50]:
        plans = bios.person_plan(cfg, p)
        for attr in ATTRS:
            ids = [pl["template_ids"][attr] for pl in plans]
            assert len(set(ids)) == len(ids), (p["person_id"], attr)


# --------------------------------------------------------------------------
# answer leaks (data prompt 5)
# --------------------------------------------------------------------------
def test_a_name_that_collides_with_a_value_is_rejected(tmp_path):
    """ "Peter Ferrari" cannot exist while "Ferrari" is an employer.

    This is the defect A13 caught in prompt 4: the person's own surname was
    their employer, so every employer prompt for them contained the answer.
    """
    cfg = make_cfg(tmp_path / "out")
    enc = get_encoder("gpt2", 50257)
    values = {
        "employer": ["Ferrari", "Nokia"],
        "birth_city": ["Charlotte, North Carolina", "Lyon, France"],
        "birth_date": ["March 4, 1987"],
        "major": ["Physics"],
        "university": ["Keio University"],
    }

    # (a) the name word is a whole word of the value
    assert bios.name_word_collides(enc, cfg, "Ferrari", values)[:2] == (
        "employer",
        "Ferrari",
    )
    assert bios.name_word_collides(enc, cfg, "Charlotte", values)[2] == "word"
    # (b) the name word's token is the value's ranking key
    hit = bios.name_word_collides(enc, cfg, "Keiko", values)
    assert hit is not None and hit[1] == "Keio University" and hit[2] == "token"
    # a name that collides with nothing survives
    assert bios.name_word_collides(enc, cfg, "Vadnais", values) is None

    # and the filter rejects the candidate, not just the word
    cands = [
        {
            "gender": "female",
            "first": "Peter",
            "last": "Ferrari",
            "name": "Peter Ferrari",
        },
        {
            "gender": "male",
            "first": "Dmitri",
            "last": "Vadnais",
            "name": "Dmitri Vadnais",
        },
    ]
    rejected, stats = bios.names_colliding_with_values(cfg, enc, cands, values)
    assert rejected == ["Peter Ferrari"]
    assert stats["by_gender"] == {"female": 1, "male": 0}


def test_a_colliding_name_never_reaches_people_jsonl(tmp_path):
    cfg = make_cfg(tmp_path / "out", n_train=20, n_control=10, candidates=120)
    enc = get_encoder("gpt2", 50257)
    values, _ = bios.build_value_lists(cfg, enc)
    candidates = bios.build_name_candidates(cfg)
    colliding, _ = bios.names_colliding_with_values(cfg, enc, candidates, values)
    assert colliding, "the filter should reject something from a real pool"
    people, stats = bios.build_people(cfg, values, candidates, [], colliding, enc)
    names = {p["name"] for p in people}
    assert not (names & set(colliding))
    assert stats["names_rejected_by_value_collision"] > 0
    # no surviving name word is a word of any value
    allwords = {
        w
        for vs in values.values()
        for v in vs
        for w in v.lower().replace(",", " ").split()
    }
    for p in people:
        assert p["first_name"].lower() not in allwords, p["name"]
        assert p["last_name"].lower() not in allwords, p["name"]


def test_values_that_leak_each_other_are_redrawn(tmp_path):
    """ "Columbus, Ohio" + "Ohio State University" hands the probe its answer."""
    cfg = make_cfg(tmp_path / "out")
    enc = get_encoder("gpt2", 50257)
    values = {
        "birth_date": ["March 4, 1987", "July 9, 1960"],
        "birth_city": ["Columbus, Ohio", "Lyon, France"],
        "university": ["Ohio State University", "Vassar College"],
        "major": ["Physics"],
        "employer": ["Nokia"],
    }
    facts = {
        "birth_date": "March 4, 1987",
        "birth_city": "Columbus, Ohio",
        "university": "Ohio State University",
        "major": "Physics",
        "employer": "Nokia",
    }
    fixed, changes = bios.resolve_fact_collisions(
        cfg, enc, "p000001", dict(facts), values
    )
    assert changes, "the Ohio collision should have been caught"
    # birth_city comes before university in the attribute order, so the LATER
    # one is the one that moves
    assert fixed["birth_city"] == "Columbus, Ohio"
    assert fixed["university"] == "Vassar College"
    assert changes[0]["attribute"] == "university"
    assert changes[0]["clashed_with"] == {"birth_city": "Columbus, Ohio"}

    # and nothing is redrawn when there is no collision
    clean = {
        "birth_date": "July 9, 1960",
        "birth_city": "Lyon, France",
        "university": "Vassar College",
        "major": "Physics",
        "employer": "Nokia",
    }
    fixed2, changes2 = bios.resolve_fact_collisions(
        cfg, enc, "p000002", dict(clean), values
    )
    assert fixed2 == clean and changes2 == []


def test_the_redraw_is_keyed_so_only_the_affected_person_moves(tmp_path):
    """A redraw must be a function of (seed, person, attribute, attempt)."""
    cfg = make_cfg(tmp_path / "out")
    enc = get_encoder("gpt2", 50257)
    values = {
        "birth_date": ["March 4, 1987"],
        "birth_city": ["Columbus, Ohio"],
        "university": ["Ohio State University", "Vassar College", "Reed College"],
        "major": ["Physics"],
        "employer": ["Nokia"],
    }
    facts = {
        "birth_date": "March 4, 1987",
        "birth_city": "Columbus, Ohio",
        "university": "Ohio State University",
        "major": "Physics",
        "employer": "Nokia",
    }
    a, _ = bios.resolve_fact_collisions(cfg, enc, "p000001", dict(facts), values)
    b, _ = bios.resolve_fact_collisions(cfg, enc, "p000001", dict(facts), values)
    c, _ = bios.resolve_fact_collisions(cfg, enc, "p000999", dict(facts), values)
    assert a == b  # same person, same answer
    assert a["university"] != "Ohio State University"
    assert c["university"] != "Ohio State University"


def test_raising_the_candidate_pool_only_appends(tmp_path):
    """More candidates must not rename the people already chosen."""
    import copy

    small = make_cfg(tmp_path / "a", candidates=300)
    big = copy.deepcopy(small.raw)
    big["bios"]["people"]["name_candidates_per_gender"] = 900
    big = DataConfig(raw=big)
    a = bios.build_name_candidates(small)
    b = bios.build_name_candidates(big)
    for g in small.bio_genders:
        ga = [c["name"] for c in a if c["gender"] == g]
        gb = [c["name"] for c in b if c["gender"] == g]
        assert len(gb) > len(ga)
        assert gb[: len(ga)] == ga, g


def test_the_real_build_has_no_answer_leaks(tmp_path):
    """End to end on a small build: the three A13 criteria, all zero."""
    cfg = make_cfg(tmp_path / "out", n_train=40, n_control=20, candidates=400)
    enc = get_encoder("gpt2", 50257)
    bios.run(cfg, name_check=False)
    people = {p["person_id"]: p for p in read_jsonl(cfg.bios_dir / "people.jsonl")}
    rows = list(read_jsonl(cfg.bios_dir / "facts.jsonl"))
    assert rows
    for r in rows:
        p = people[r["person_id"]]
        key = set(bios.ranking_key(enc, cfg, r["attribute"], r["true_value"]))
        assert r["true_value"] not in r["prompt"], r["fact_id"]
        assert not (key & set(enc.encode_ordinary(" " + p["name"]))), r["fact_id"]
        assert not (key & set(enc.encode_ordinary(p["name"]))), r["fact_id"]
        for a, v in p["facts"].items():
            if a != r["attribute"]:
                assert not (
                    key & bios.value_token_set(enc, v)
                ), f"{r['fact_id']} leaks via {a}={v!r}"


# --------------------------------------------------------------------------
# the relation rule and the two grammar guards (data prompt 6)
# --------------------------------------------------------------------------
def test_relations_name_every_attribute():
    assert set(bd.RELATIONS) == set(ATTRS)
    for attr, relation in bd.RELATIONS.items():
        assert "{v}" in relation, attr


@pytest.mark.parametrize(
    "bad",
    [
        "Question: what did {obj} study? Answer: {v}.",  # the real bug
        "Question: when was {obj} born? Answer: {v}.",
        "Question: where does {obj} work? Answer: {v}.",
        "Everyone knows where {obj} is from, namely {v}.",
    ],
)
def test_obj_where_the_subject_belongs_is_rejected(monkeypatch, bad):
    """`{obj}` renders "her"/"him", so "what did him study?" is a grammar bug.

    The guard has to fire wherever the template sits, so this patches one into
    the held-out pool and calls the checker that runs at import.
    """
    held = {a: list(v) for a, v in bd.HELDOUT_TEMPLATES.items()}
    held["major"] = [bad] + held["major"][1:]
    monkeypatch.setattr(bd, "HELDOUT_TEMPLATES", held)
    with pytest.raises(AssertionError, match=r"\{obj\} stands where the subject"):
        bd.check_templates()


def test_the_shipped_templates_have_no_obj_as_subject():
    guard = re.compile(r"\b(when|where|what|did|does|do|was|is)\s+\{obj\}")
    for attr in ATTRS:
        for t in bd.TRAIN_TEMPLATES[attr] + bd.HELDOUT_TEMPLATES[attr]:
            assert not guard.search(t), t


def test_every_template_renders_for_both_genders_by_name_and_pronoun():
    """All 120 templates x {female, male} x {name, pronoun}: nothing left over."""
    n = 0
    for attr in ATTRS:
        for t in bd.TRAIN_TEMPLATES[attr] + bd.HELDOUT_TEMPLATES[attr]:
            for gender in ("female", "male"):
                for use_name in (True, False):
                    text, at = bios.render(
                        t, "Ada Lovelace", gender, use_name, "A VALUE"
                    )
                    assert "{" not in text and "}" not in text, (t, text)
                    assert text[at:].startswith("A VALUE"), (t, text)
                    assert text[at - 1] == " ", (t, text)
                    assert text[0].isupper(), (t, text)
                    n += 1
    assert n == 120 * 4


def test_a_template_that_leaves_a_placeholder_behind_is_rejected(monkeypatch):
    """A brace that survives rendering would reach the biography text verbatim."""
    train = {a: list(v) for a, v in bd.TRAIN_TEMPLATES.items()}
    train["major"] = ["{Subj} graduated, major {{tbd}}, in {v}.", *train["major"][1:]]
    monkeypatch.setattr(bd, "TRAIN_TEMPLATES", train)
    with pytest.raises(AssertionError, match="left a placeholder unrendered"):
        bd.check_templates()


def test_an_unknown_placeholder_is_rejected(monkeypatch):
    train = {a: list(v) for a, v in bd.TRAIN_TEMPLATES.items()}
    train["major"] = ["{Subj} majored, like {sibling}, in {v}.", *train["major"][1:]]
    monkeypatch.setattr(bd, "TRAIN_TEMPLATES", train)
    with pytest.raises(KeyError):
        bd.check_templates()


def test_pre_value_wording_is_distinct_inside_each_attribute():
    for attr in ATTRS:
        ctx = [bd.pre_value_context(t) for t in bd.TRAIN_TEMPLATES[attr]]
        assert len(set(ctx)) == len(ctx), attr


def test_two_training_templates_with_the_same_pre_value_wording_are_rejected(
    monkeypatch,
):
    train = {a: list(v) for a, v in bd.TRAIN_TEMPLATES.items()}
    first = train["employer"][0]
    tail = " ".join(first.split("{v}")[0].split()[-3:])
    train["employer"] = [
        first,
        f"{{Subj}} works, as it happens, {tail} {{v}}.",
        *train["employer"][2:],
    ]
    monkeypatch.setattr(bd, "TRAIN_TEMPLATES", train)
    with pytest.raises(AssertionError, match="pre-value wording"):
        bd.check_templates()
