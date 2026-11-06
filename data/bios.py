"""Biography generator -- data prompt 2. Replaces the old tools/bio_generator.py.

Makes up 2,500 people whose five facts (birth date, birth city, university,
major, employer) are drawn uniformly at random from fixed value lists. Because
the facts are random, a model can only answer a question about one by having
*stored* it, and we know every right answer -- which is the whole point: the
memory-layer analysis needs facts whose ground truth is certain and whose
surface form it controls.

    python -m data.bios --config configs/data/v1.yaml
    python -m data.bios --config configs/data/v1.yaml --small
    python -m data.bios --config configs/data/v1.yaml --skip-name-check

Everything is a pure function of `seed` in the config: same config, byte-
identical output. Each person's draws come from an RNG seeded with
(seed, person index), so a person's facts do not depend on how many people were
generated before them.

Outputs, in `<root>/bios/`:

    people.jsonl          one row per person: name, gender, tier, exposures, facts
    bios_train.jsonl      4 rewordings x 2,000 trained people
    bios_control.jsonl    4 rewordings x 500 control people (never trained on)
    facts.jsonl           one row per (person, attribute, rewording) plus one per
                          (person, attribute, held-out template)
    attribute_values.json the realised value lists and what was dropped
    templates.json        every template, held-out ones flagged
    name_check.json       which candidate names the Pile contains

Prompt 3 places the exposure copies, tokenizes and packs. This prompt only
records the targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from data import bios_data as bd
from data.common import (
    record_timing,
    ROOT,
    DataConfig,
    clean_text,
    dumps_record,
    get_encoder,
    keyed_rng,
    load_config,
    open_write,
    read_jsonl,
    write_json,
)

# A full name is two capitalized words with exactly one space between them, so
# this is all the corpus scan has to look for.
_CAP_WORD = re.compile(r"[A-Z][A-Za-z]+")

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
DAYS_IN_MONTH = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Words carrying no identity, for the near-duplicate test -- per attribute,
# because they differ completely. "College"/"University" say nothing about which
# school, so "Boston College" and "Boston University" are the same entity for
# our purposes. But in a list of majors every word counts: strip "Science" and
# "Computer Science" collapses into "Computer Engineering", which are different
# degrees. So majors, cities and dates strip nothing and are compared on
# containment alone.
_GENERIC_BY_ATTR: Dict[str, frozenset] = {
    "university": frozenset(
        {
            "university",
            "college",
            "institute",
            "school",
            "of",
            "the",
            "and",
            "for",
            "state",
            "technology",
            "polytechnic",
            "technological",
            "national",
            "military",
            "universiteit",
        }
    ),
    "employer": frozenset(
        {
            "group",
            "holdings",
            "company",
            "corporation",
            "inc",
            "plc",
            "ag",
            "sa",
            "nv",
            "ltd",
            "limited",
            "co",
            "the",
            "and",
            "of",
            "international",
            "technology",
            "technologies",
        }
    ),
    "major": frozenset(),
    "birth_city": frozenset(),
    "birth_date": frozenset(),
}


# ---------------------------------------------------------------------------
# determinism helpers
# ---------------------------------------------------------------------------
def _rng(seed: int, *parts: Any) -> random.Random:
    """An RNG keyed by the data seed and a label. Order-independent by design."""
    return keyed_rng(seed, *parts)


# ---------------------------------------------------------------------------
# value lists
# ---------------------------------------------------------------------------
def _significant_words(value: str, attribute: str) -> frozenset:
    generic = _GENERIC_BY_ATTR.get(attribute, frozenset())
    words = re.findall(r"[a-z0-9]+", value.lower())
    keep = [w for w in words if w not in generic]
    return frozenset(keep or words)


def _near_duplicate_of(
    value: str, attribute: str, kept: Dict[frozenset, str]
) -> Optional[str]:
    """A value is a near-duplicate when its identity words nest in another's.

    Catches "Boston College" vs "Boston University" and "Michigan State
    University" vs "Michigan", which are the same entity for our purposes and
    would make a fact ambiguous.
    """
    sig = _significant_words(value, attribute)
    for other_sig, other in kept.items():
        if sig <= other_sig or other_sig <= sig:
            return other
    return None


def build_date_values(cfg: DataConfig, n: int) -> List[str]:
    """`n` dates like "March 4, 1987", each with a unique (month, day) pair.

    Unique month-day pairs are what make a date identifiable from its first two
    GPT-2 tokens. The first token alone cannot do it -- see `first_token_report`.
    """
    lo, hi = cfg.bio_year_range
    pairs = [(m, d) for m in range(12) for d in range(1, DAYS_IN_MONTH[m] + 1)]
    if n > len(pairs):
        raise ValueError(
            f"cannot build {n} dates with unique month-day pairs "
            f"(only {len(pairs)} exist)"
        )
    rng = _rng(cfg.seed, "dates")
    chosen = rng.sample(pairs, n)
    chosen.sort()
    out = []
    for m, d in chosen:
        year = rng.randrange(lo, hi + 1)
        out.append(f"{MONTHS[m]} {d}, {year}")
    return out


def filter_values(
    enc,
    candidates: Sequence[str],
    target: int,
    mode: str,
    rng: random.Random,
    attribute: str = "major",
) -> Tuple[List[str], Dict[str, Any]]:
    """Drop near-duplicates, then first-token clashes, then trim to `target`.

    `mode` is "first_token" or "first_two_tokens" -- which prefix has to be
    unique inside the list. Returns the list and a report of what went.
    """
    n_prefix = 2 if mode == "first_two_tokens" else 1
    kept_sig: Dict[frozenset, str] = {}
    near_drops: List[Dict[str, str]] = []
    stage1: List[str] = []
    for v in candidates:
        other = _near_duplicate_of(v, attribute, kept_sig)
        if other is not None:
            near_drops.append({"dropped": v, "near_duplicate_of": other})
            continue
        kept_sig[_significant_words(v, attribute)] = v
        stage1.append(v)

    seen: Dict[Tuple[int, ...], str] = {}
    token_drops: List[Dict[str, str]] = []
    stage2: List[str] = []
    for v in stage1:
        prefix = tuple(enc.encode_ordinary(" " + v)[:n_prefix])
        if prefix in seen:
            token_drops.append(
                {
                    "dropped": v,
                    "clashes_with": seen[prefix],
                    "on": enc.decode(list(prefix)),
                }
            )
            continue
        seen[prefix] = v
        stage2.append(v)

    trimmed = sorted(rng.sample(stage2, target)) if len(stage2) > target else stage2
    report = {
        "candidates": len(candidates),
        "after_near_duplicate_drop": len(stage1),
        "after_prefix_drop": len(stage2),
        "target": target,
        "final": len(trimmed),
        "uniqueness": mode,
        "dropped_near_duplicate": len(near_drops),
        "dropped_prefix_clash": len(token_drops),
        "dropped_over_target": max(0, len(stage2) - target),
        "near_duplicate_examples": near_drops[:20],
        "prefix_clash_examples": token_drops[:20],
    }
    return trimmed, report


def build_value_lists(
    cfg: DataConfig, enc
) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    sources = {
        "birth_city": bd.CITY_CANDIDATES,
        "university": bd.UNIVERSITY_CANDIDATES,
        "major": bd.MAJOR_CANDIDATES,
        "employer": bd.EMPLOYER_CANDIDATES,
    }
    values: Dict[str, List[str]] = {}
    reports: Dict[str, Any] = {}
    for attr in cfg.bio_attributes:
        target = cfg.bio_value_targets[attr]
        mode = (
            "first_two_tokens"
            if attr in cfg.bio_first_two_tokens_unique
            else "first_token"
        )
        if attr == "birth_date":
            dates = build_date_values(cfg, target)
            vals, rep = filter_values(
                enc, dates, target, mode, _rng(cfg.seed, "trim", attr), attr
            )
        else:
            vals, rep = filter_values(
                enc, sources[attr], target, mode, _rng(cfg.seed, "trim", attr), attr
            )
        if not vals:
            raise RuntimeError(f"{attr}: no values survived filtering")
        values[attr] = vals
        reports[attr] = rep
    return values, reports


def first_token_report(enc, values: Dict[str, List[str]]) -> Dict[str, Any]:
    """Per attribute: are first tokens unique, and if not how far from it."""
    out = {}
    for attr, vals in values.items():
        firsts = [enc.encode_ordinary(" " + v)[0] for v in vals]
        pairs = [tuple(enc.encode_ordinary(" " + v)[:2]) for v in vals]
        out[attr] = {
            "n_values": len(vals),
            "distinct_first_tokens": len(set(firsts)),
            "first_token_unique": len(set(firsts)) == len(vals),
            "distinct_first_two_tokens": len(set(pairs)),
            "first_two_tokens_unique": len(set(pairs)) == len(vals),
            "value_tokens_mean": round(
                sum(len(enc.encode_ordinary(" " + v)) for v in vals) / len(vals), 2
            ),
        }
    return out


# ---------------------------------------------------------------------------
# names
# ---------------------------------------------------------------------------
def ranking_key(enc, cfg: DataConfig, attribute: str, value: str) -> Tuple[int, ...]:
    """The tokens a fact-recall probe ranks this value on.

    One token for most attributes; two for `birth_date`, where 200 dates share
    twelve month tokens so a date is only identified by (month, day). Anything
    that puts these tokens in front of the model for free is an answer leak.
    """
    ids = enc.encode_ordinary(" " + value)
    n = 2 if attribute in cfg.bio_first_two_tokens_unique else 1
    return tuple(ids[:n])


def value_token_set(enc, value: str) -> frozenset:
    return frozenset(enc.encode_ordinary(" " + value))


def _value_words(value: str) -> frozenset:
    return frozenset(w.lower() for w in re.findall(r"[A-Za-z0-9]+", value))


def name_word_collides(
    enc, cfg: DataConfig, word: str, values: Dict[str, List[str]]
) -> Optional[Tuple[str, str, str]]:
    """Does this name word hand a probe one of its answers for free?

    Two ways, both global across every list -- a surname that primes *another*
    person's city is as bad as one that primes its owner's employer, because
    the model sees every biography:

      (a) the word, lowercased, is a whole word of the value;
      (b) the GPT-2 token of " word" or of "word" is the value's ranking key
          (for a date, either of its first two tokens).

    Returns (attribute, value, reason) for the first hit, or None.
    """
    low = word.lower()
    toks = {enc.encode_ordinary(" " + word)[0], enc.encode_ordinary(word)[0]}
    for attribute, vals in values.items():
        for value in vals:
            if low in _value_words(value):
                return attribute, value, "word"
            if toks & set(ranking_key(enc, cfg, attribute, value)):
                return attribute, value, "token"
    return None


def names_colliding_with_values(
    cfg: DataConfig,
    enc,
    candidates: Sequence[Dict[str, str]],
    values: Dict[str, List[str]],
) -> Tuple[List[str], Dict[str, Any]]:
    """Candidate names rejected because a name word collides with a value.

    Rejected in the same place the Pile name check rejects -- before people are
    assigned -- so this only shifts which name a person gets. Person ids, tiers,
    facts and templates are all keyed by person id and do not move.
    """
    cache: Dict[str, Optional[Tuple[str, str, str]]] = {}

    def hit(word: str):
        if word not in cache:
            cache[word] = name_word_collides(enc, cfg, word, values)
        return cache[word]

    rejected: List[str] = []
    by_gender: Dict[str, int] = {g: 0 for g in cfg.bio_genders}
    by_reason: Dict[str, int] = {"word": 0, "token": 0}
    by_attribute: Dict[str, int] = {}
    examples: List[Dict[str, str]] = []
    for cand in candidates:
        for part in ("first", "last"):
            h = hit(cand[part])
            if h is None:
                continue
            attribute, value, reason = h
            rejected.append(cand["name"])
            by_gender[cand["gender"]] += 1
            by_reason[reason] += 1
            by_attribute[attribute] = by_attribute.get(attribute, 0) + 1
            if len(examples) < 25:
                examples.append(
                    {
                        "name": cand["name"],
                        "word": cand[part],
                        "attribute": attribute,
                        "value": value,
                        "reason": reason,
                    }
                )
            break
    stats = {
        "candidates": len(candidates),
        "rejected": len(rejected),
        "by_gender": by_gender,
        "by_reason": by_reason,
        "by_attribute": dict(sorted(by_attribute.items())),
        "distinct_words_tested": len(cache),
        "examples": examples,
    }
    return rejected, stats


def resolve_fact_collisions(
    cfg: DataConfig,
    enc,
    pid: str,
    facts: Dict[str, str],
    values: Dict[str, List[str]],
    max_attempts: int = 200,
) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """Redraw a person's later facts until no value leaks another's answer.

    Every rewording puts all five values in one paragraph in a random order, so
    if one value's ranking key sits inside another value's tokens -- "Columbus,
    Ohio" and "Ohio State University" -- the prompt for whichever comes second
    hands the probe its answer. Checked in both directions for that reason.

    Only the colliding attribute is redrawn, from an RNG keyed by
    (seed, "facts", person id, attribute, attempt), so one person's collision
    cannot disturb anybody else's facts.
    """
    attributes = list(cfg.bio_attributes)
    keys = {a: ranking_key(enc, cfg, a, facts[a]) for a in attributes}
    toks = {a: value_token_set(enc, facts[a]) for a in attributes}
    changes: List[Dict[str, Any]] = []

    for i, attr in enumerate(attributes):
        earlier = attributes[:i]
        attempt = 0
        while True:
            clash = next(
                (
                    (e, facts[e])
                    for e in earlier
                    if (set(keys[attr]) & toks[e]) or (set(keys[e]) & toks[attr])
                ),
                None,
            )
            if clash is None:
                break
            attempt += 1
            if attempt > max_attempts:
                raise RuntimeError(
                    f"{pid}/{attr}: could not redraw clear of {clash} in "
                    f"{max_attempts} attempts"
                )
            old = facts[attr]
            facts[attr] = keyed_rng(cfg.seed, "facts", pid, attr, attempt).choice(
                values[attr]
            )
            keys[attr] = ranking_key(enc, cfg, attr, facts[attr])
            toks[attr] = value_token_set(enc, facts[attr])
            changes.append(
                {
                    "person_id": pid,
                    "attribute": attr,
                    "attempt": attempt,
                    "was": old,
                    "now": facts[attr],
                    "clashed_with": {clash[0]: clash[1]},
                }
            )
    return facts, changes


def build_name_candidates(cfg: DataConfig) -> List[Dict[str, str]]:
    """Candidate people in draw order: gender, first, last, full name.

    Generated before the Pile check and longer than needed, so the first
    survivors in this order become the people and a rejection just shifts the
    cut-off instead of changing anybody's facts.
    """
    out: List[Dict[str, str]] = []
    for gender in cfg.bio_genders:
        pool = bd.FEMALE_FIRST if gender == "female" else bd.MALE_FIRST
        rng = _rng(cfg.seed, "names", gender)
        seen = set()
        want = cfg.bio_name_candidates_per_gender
        guard = 0
        while len(seen) < want:
            guard += 1
            if guard > 400 * want + 10_000:
                raise RuntimeError(f"could not draw {want} unique {gender} names")
            first, last = rng.choice(pool), rng.choice(bd.LAST)
            name = f"{first} {last}"
            if name in seen:
                continue
            seen.add(name)
            out.append({"gender": gender, "first": first, "last": last, "name": name})
    return out


def scan_corpus_for_names(
    paths: Iterable[Path], names: Iterable[str], case_sensitive: bool = True
) -> Dict[str, Any]:
    """Which of `names` occur verbatim in the cleaned Pile text.

    One pass. Candidate names are two capitalized words with a single space, so
    it is enough to find every capitalized word, pair up the ones that are
    adjacent with exactly one space between them, and look each pair up. That is
    one cheap regex over the corpus instead of thousands of substring searches.
    """
    wanted = set(names) if case_sensitive else {n.lower() for n in names}
    hits: Dict[str, int] = {}
    files, docs, chars = [], 0, 0
    for path in paths:
        if not Path(path).exists():
            continue
        # repo-relative, so a committed manifest carries no home directory
        try:
            files.append(str(Path(path).resolve().relative_to(ROOT)))
        except ValueError:
            files.append(str(path))
        for rec in read_jsonl(Path(path)):
            text = rec.get("text") or ""
            docs += 1
            chars += len(text)
            spans = [(m.start(), m.end()) for m in _CAP_WORD.finditer(text)]
            for (s0, e0), (s1, e1) in zip(spans, spans[1:]):
                if s1 != e0 + 1 or text[e0] != " ":
                    continue
                pair = text[s0:e1]
                key = pair if case_sensitive else pair.lower()
                if key in wanted:
                    hits[pair if case_sensitive else key] = (
                        hits.get(pair if case_sensitive else key, 0) + 1
                    )
    return {
        "files": files,
        "documents_scanned": docs,
        "characters_scanned": chars,
        "candidates_tested": len(wanted),
        "case_sensitive": case_sensitive,
        "names_found": sorted(hits),
        "n_names_found": len(hits),
        "occurrences": {k: hits[k] for k in sorted(hits)},
    }


def corpus_paths(cfg: DataConfig) -> List[Path]:
    out: List[Path] = []
    for sub in cfg.bio_name_check_dirs:
        d = cfg.root / sub
        if d.exists():
            out.extend(sorted(d.glob("*.jsonl.gz")))
    return out


# ---------------------------------------------------------------------------
# people
# ---------------------------------------------------------------------------
def build_people(
    cfg: DataConfig,
    values: Dict[str, List[str]],
    candidates: Sequence[Dict[str, str]],
    banned: Sequence[str],
    value_colliding: Sequence[str] = (),
    enc=None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """2,000 trained + 500 control people, gender-balanced inside every tier.

    Tiers are assigned by filling a deterministic plan -- (tier, gender) slots in
    config order -- and then shuffling the plan with the data seed, which gives a
    random assignment that is still *exactly* balanced rather than balanced on
    average.
    """
    banned_set = set(banned)
    collide_set = set(value_colliding)
    enc = enc or get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    n_total = cfg.bio_n_train + cfg.bio_n_control
    per_gender = n_total // len(cfg.bio_genders)
    if n_total % len(cfg.bio_genders):
        raise ValueError("bios.people counts must divide by the number of genders")

    # pick names: first survivors in draw order, per gender
    chosen: Dict[str, List[Dict[str, str]]] = {g: [] for g in cfg.bio_genders}
    rejected: List[str] = []
    rejected_collision: List[str] = []
    for cand in candidates:
        g = cand["gender"]
        if len(chosen[g]) >= per_gender:
            continue
        if cand["name"] in banned_set:
            rejected.append(cand["name"])
            continue
        if cand["name"] in collide_set:
            rejected_collision.append(cand["name"])
            continue
        chosen[g].append(cand)
    short = {g: per_gender - len(v) for g, v in chosen.items() if len(v) < per_gender}
    if short:
        raise RuntimeError(
            f"not enough surviving names: {short}. Raise "
            "bios.people.name_candidates_per_gender."
        )

    # the exactly-balanced (split, tier) plan, per gender
    plan: Dict[str, List[Tuple[str, str, int]]] = {}
    for g in cfg.bio_genders:
        slots: List[Tuple[str, str, int]] = []
        for tier in cfg.bio_tiers:
            n = tier["n_people"] // len(cfg.bio_genders)
            slots += [("train", tier["name"], tier["exposures"])] * n
        slots += [("control", cfg.bio_control_tier, 0)] * (
            cfg.bio_n_control // len(cfg.bio_genders)
        )
        if len(slots) != per_gender:
            raise ValueError(
                f"{g}: plan has {len(slots)} slots but {per_gender} names; "
                "every tier's n_people must divide by the number of genders"
            )
        _rng(cfg.seed, "tierplan", g).shuffle(slots)
        plan[g] = slots

    # interleave the genders so person ids are not blocked by gender
    people: List[Dict[str, Any]] = []
    fact_redraws: List[Dict[str, Any]] = []
    order: List[Tuple[str, int]] = [
        (g, i) for i in range(per_gender) for g in cfg.bio_genders
    ]
    for idx, (g, i) in enumerate(order):
        cand = chosen[g][i]
        split, tier, exposures = plan[g][i]
        pid = f"p{idx:06d}"
        prng = _rng(cfg.seed, "facts", pid)
        facts = {attr: prng.choice(values[attr]) for attr in cfg.bio_attributes}
        facts, changes = resolve_fact_collisions(cfg, enc, pid, facts, values)
        fact_redraws.extend(changes)
        people.append(
            {
                "person_id": pid,
                "name": cand["name"],
                "first_name": cand["first"],
                "last_name": cand["last"],
                "gender": g,
                "split": split,
                "tier": tier,
                "target_exposures": exposures,
                "n_rewordings": cfg.bio_n_rewordings,
                "facts": facts,
            }
        )

    stats = {
        "n_people": len(people),
        "names_rejected_by_pile_check": len(rejected),
        "names_rejected_by_value_collision": len(rejected_collision),
        "fact_redraws": len(fact_redraws),
        "people_with_a_redrawn_fact": len({c["person_id"] for c in fact_redraws}),
        "fact_redraw_examples": fact_redraws[:20],
        "rejected_names": sorted(rejected),
        "candidates_per_gender": cfg.bio_name_candidates_per_gender,
        "by_split": _count(people, "split"),
        "by_gender": _count(people, "gender"),
        "by_tier": _count(people, "tier"),
        "by_tier_gender": {f"{p['tier']}/{p['gender']}": 0 for p in people},
    }
    for p in people:
        stats["by_tier_gender"][f"{p['tier']}/{p['gender']}"] += 1
    return people, stats


def _count(rows: Sequence[Dict[str, Any]], field: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in rows:
        out[r[field]] = out.get(r[field], 0) + 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
PRONOUNS = {
    "female": {
        "Subj": "She",
        "subj": "she",
        "Poss": "Her",
        "poss": "her",
        "obj": "her",
    },
    "male": {"Subj": "He", "subj": "he", "Poss": "His", "poss": "his", "obj": "him"},
}


def mention(name: str, gender: str, use_name: bool) -> Dict[str, str]:
    """The person-placeholder fills for one sentence."""
    if use_name:
        return {
            "Subj": name,
            "subj": name,
            "Poss": f"{name}'s",
            "poss": f"{name}'s",
            "obj": name,
        }
    return dict(PRONOUNS[gender])


def render(
    template: str, name: str, gender: str, use_name: bool, value: str
) -> Tuple[str, int]:
    """Render one sentence. Returns (text, index where the value starts).

    The index is taken from the template, not searched for in the output, so a
    value that happens to repeat a word of the frame cannot throw it off.
    """
    fills = mention(name, gender, use_name)
    head = template.split("{v}")[0].format(**fills)
    tail = template.split("{v}")[1].format(**fills)
    return head + value + tail, len(head)


def mention_pattern(cfg: DataConfig, rng: random.Random, n: int) -> List[bool]:
    """Which sentences name the person. Sentence 0 always does; the rest mix.

    Resampled until both forms appear among the later sentences, so no
    biography is all-name or all-pronoun after the first line.
    """
    if n <= 2:
        return [True] + [False] * (n - 1)
    for _ in range(50):
        rest = [rng.random() < 0.5 for _ in range(n - 1)]
        if any(rest) and not all(rest):
            return [True] + rest
    return [True] + [i % 2 == 0 for i in range(n - 1)]


def person_plan(cfg: DataConfig, person: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The 4 training rewordings of one person, as orderings + template picks.

    Templates are drawn WITHOUT replacement across a person's rewordings, so the
    four copies of a fact are worded four different ways -- that is what makes
    "did it store the fact or the sentence" answerable.
    """
    pid = person["person_id"]
    n_rw = cfg.bio_n_rewordings
    picks: Dict[str, List[int]] = {}
    for attr in cfg.bio_attributes:
        pool = range(len(bd.TRAIN_TEMPLATES[attr]))
        picks[attr] = _rng(cfg.seed, "tmpl", pid, attr).sample(list(pool), n_rw)
    plans = []
    for r in range(n_rw):
        rng = _rng(cfg.seed, "rw", pid, r)
        order = list(cfg.bio_attributes)
        rng.shuffle(order)
        plans.append(
            {
                "rewording_id": r,
                "order": order,
                "template_ids": {a: picks[a][r] for a in cfg.bio_attributes},
                "use_name": mention_pattern(cfg, rng, len(order)),
            }
        )
    return plans


def build_biography(
    cfg: DataConfig,
    person: Dict[str, Any],
    plan: Dict[str, Any],
    heldout: Optional[Tuple[str, int]] = None,
) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    """Render one biography. Returns (text, {attribute: {offset, template_id,...}}).

    `heldout=(attribute, index)` swaps that one attribute's sentence for a
    held-out template and leaves the other four sentences exactly as the
    training rewording had them, so only the structure of one sentence is new.
    """
    name, gender = person["name"], person["gender"]
    parts: List[str] = []
    spans: Dict[str, Dict[str, Any]] = {}
    pos = 0
    for i, attr in enumerate(plan["order"]):
        use_name = plan["use_name"][i]
        if heldout is not None and heldout[0] == attr:
            template = bd.HELDOUT_TEMPLATES[attr][heldout[1]]
            tid, is_held = heldout[1], True
        else:
            tid = plan["template_ids"][attr]
            template = bd.TRAIN_TEMPLATES[attr][tid]
            is_held = False
        if i == 0:
            use_name = True  # the first sentence names them
        value = person["facts"][attr]
        text, at = render(template, name, gender, use_name, value)
        spans[attr] = {
            "offset": pos + at,
            "template_id": tid,
            "held_out_template": is_held,
            "sentence_index": i,
            "used_name": use_name,
            "value": value,
        }
        parts.append(text)
        pos += len(text) + 1  # sentences joined by one space
    return " ".join(parts), spans


# ---------------------------------------------------------------------------
# facts
# ---------------------------------------------------------------------------
def _role(cfg: DataConfig, rewording_id: int) -> str:
    if rewording_id in cfg.bio_discovery_rewordings:
        return "discovery"
    if rewording_id in cfg.bio_test_rewordings:
        return "test"
    raise ValueError(f"rewording {rewording_id} has no role in the config")


def fact_rows(
    cfg: DataConfig, person: Dict[str, Any], enc, value_tokens: Dict[str, List[int]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """All fact rows for one person, plus that person's biography rows.

    A row's `prompt` is the biography text up to the value, with the space
    before the value NOT included: the value's first GPT-2 token carries that
    space (" March", not "March"), so a prompt ending in a space would feed the
    model token 220 and make the expected continuation unreachable. `prompt +
    continuation` is exactly the biography prefix; `continuation` is what the
    model has to produce and `value_token_ids` is its tokenization.
    """
    plans = person_plan(cfg, person)
    rows: List[Dict[str, Any]] = []
    bios: List[Dict[str, Any]] = []
    pid = person["person_id"]

    for plan in plans:
        text, spans = build_biography(cfg, person, plan)
        r = plan["rewording_id"]
        doc_id = f"bio-{pid}-{r}"
        bios.append(
            {
                "person_id": pid,
                "rewording_id": r,
                "doc_id": doc_id,
                "split": person["split"],
                "text": text,
            }
        )
        for attr in cfg.bio_attributes:
            sp = spans[attr]
            rows.append(
                _row(
                    cfg, person, attr, sp, text, r, _role(cfg, r), doc_id, value_tokens
                )
            )

    ctx = plans[cfg.bio_heldout_context_rewording]
    for h in range(cfg.bio_n_heldout_templates):
        for attr in cfg.bio_attributes:
            text, spans = build_biography(cfg, person, ctx, heldout=(attr, h))
            rows.append(
                _row(
                    cfg,
                    person,
                    attr,
                    spans[attr],
                    text,
                    None,
                    cfg.bio_heldout_role,
                    None,
                    value_tokens,
                )
            )
    return rows, bios


def _row(
    cfg: DataConfig,
    person: Dict[str, Any],
    attr: str,
    span: Dict[str, Any],
    text: str,
    rewording_id: Optional[int],
    role: str,
    doc_id: Optional[str],
    value_tokens: Dict[str, List[int]],
) -> Dict[str, Any]:
    value = span["value"]
    start = span["offset"]
    if start == 0 or text[start - 1] != " ":
        raise AssertionError(f"value must be preceded by one space: {text!r}")
    tag = f"r{rewording_id}" if rewording_id is not None else f"h{span['template_id']}"
    return {
        "fact_id": f"{person['person_id']}-{attr}-{tag}",
        "person_id": person["person_id"],
        "split": person["split"],
        "tier": person["tier"],
        "attribute": attr,
        "template_id": span["template_id"],
        "rewording_id": rewording_id,
        "held_out_template": span["held_out_template"],
        "role": role,
        "prompt": text[: start - 1],
        "continuation": " " + value,
        "true_value": value,
        "value_token_ids": value_tokens[value],
        "doc_id": doc_id,
    }


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def run(cfg: DataConfig, name_check: bool = True) -> Dict[str, Any]:
    t0 = time.time()
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    out_dir = cfg.bios_dir
    print(
        f"[bios] root={out_dir}  small={cfg.small}  "
        f"fingerprint={cfg.fingerprint('bios')[:16]}",
        flush=True,
    )

    values, value_reports = build_value_lists(cfg, enc)
    tok_report = first_token_report(enc, values)
    for attr in cfg.bio_attributes:
        r = value_reports[attr]
        print(
            f"[bios] values {attr:12s} {r['candidates']:>4d} cand -> "
            f"{r['after_near_duplicate_drop']:>4d} after near-dup -> "
            f"{r['after_prefix_drop']:>4d} after {r['uniqueness']} -> "
            f"{r['final']:>4d} final",
            flush=True,
        )

    candidates = build_name_candidates(cfg)
    if name_check and cfg.bio_name_check:
        paths = corpus_paths(cfg)
        if not paths:
            raise RuntimeError(
                f"the Pile name check found no corpus under {cfg.root} "
                f"({cfg.bio_name_check_dirs}). Build the pile stage first, or "
                "pass --skip-name-check and accept unchecked names."
            )
        print(
            f"[bios] name check: scanning {len(paths)} files for "
            f"{len(candidates):,} candidate names",
            flush=True,
        )
        check = scan_corpus_for_names(
            paths,
            [c["name"] for c in candidates],
            case_sensitive=cfg.bio_name_check_case_sensitive,
        )
        check["skipped"] = False
    else:
        check = {
            "skipped": True,
            "reason": "name check disabled",
            "names_found": [],
            "n_names_found": 0,
            "candidates_tested": len(candidates),
            "files": [],
        }
    print(
        f"[bios] name check: {check['n_names_found']} of "
        f"{check['candidates_tested']:,} candidate names occur in the Pile",
        flush=True,
    )

    colliding, collide_stats = names_colliding_with_values(cfg, enc, candidates, values)
    print(
        f"[bios] value collision: {collide_stats['rejected']:,} of "
        f"{collide_stats['candidates']:,} candidate names rejected "
        f"({collide_stats['by_gender']}); by reason "
        f"{collide_stats['by_reason']}",
        flush=True,
    )

    people, people_stats = build_people(
        cfg, values, candidates, check["names_found"], colliding, enc
    )
    people_stats["value_collision"] = collide_stats
    if people_stats["fact_redraws"]:
        print(
            f"[bios] fact redraws: {people_stats['fact_redraws']} draws over "
            f"{people_stats['people_with_a_redrawn_fact']} people whose values "
            f"would have leaked each other's answer",
            flush=True,
        )

    all_values = sorted({v for vals in values.values() for v in vals})
    value_tokens = {v: enc.encode_ordinary(" " + v) for v in all_values}

    out_dir.mkdir(parents=True, exist_ok=True)
    n_facts = 0
    bio_tokens: List[int] = []
    role_counts: Dict[str, int] = {}
    attr_counts: Dict[str, int] = {}
    fact_handle = open_write(out_dir / "facts.jsonl")
    train_handle = open_write(out_dir / "bios_train.jsonl")
    ctrl_handle = open_write(out_dir / "bios_control.jsonl")
    people_handle = open_write(out_dir / "people.jsonl")
    try:
        for person in people:
            people_handle.write(dumps_record(person))
            rows, bios = fact_rows(cfg, person, enc, value_tokens)
            handle = train_handle if person["split"] == "train" else ctrl_handle
            for b in bios:
                handle.write(
                    dumps_record(
                        {
                            k: b[k]
                            for k in ("person_id", "rewording_id", "doc_id", "text")
                        }
                    )
                )
                bio_tokens.append(len(enc.encode_ordinary(b["text"])))
            for row in rows:
                fact_handle.write(dumps_record(row))
                n_facts += 1
                role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
                attr_counts[row["attribute"]] = attr_counts.get(row["attribute"], 0) + 1
    finally:
        for h in (fact_handle, train_handle, ctrl_handle, people_handle):
            h.close()

    write_json(
        out_dir / "attribute_values.json",
        {
            "config_fingerprint": cfg.fingerprint("bios"),
            "seed": cfg.seed,
            "tokenizer": cfg.tokenizer_name,
            "values": values,
            "filtering": value_reports,
            "tokens": tok_report,
        },
    )
    write_json(
        out_dir / "templates.json",
        {
            "config_fingerprint": cfg.fingerprint("bios"),
            "placeholders": {
                "{Subj}": "sentence-initial subject: the full name, or She/He",
                "{Poss}": 'sentence-initial possessive: "Name\'s", or Her/His',
                "{poss}": 'mid-sentence possessive: "Name\'s", or her/his',
                "{obj}": "mid-sentence object: the full name, or her/him",
                "{v}": "the attribute value",
            },
            "heldout_markers": bd.HELDOUT_MARKERS,
            "templates": {
                attr: (
                    [
                        {
                            "template_id": i,
                            "held_out_template": False,
                            "text": t,
                            "pre_value_context": bd.pre_value_context(t),
                        }
                        for i, t in enumerate(bd.TRAIN_TEMPLATES[attr])
                    ]
                    + [
                        {
                            "template_id": i,
                            "held_out_template": True,
                            "text": t,
                            "pre_value_context": bd.pre_value_context(t),
                        }
                        for i, t in enumerate(bd.HELDOUT_TEMPLATES[attr])
                    ]
                )
                for attr in cfg.bio_attributes
            },
        },
    )
    write_json(out_dir / "name_check.json", check)

    exposures = sum(p["target_exposures"] for p in people)
    train_bio_tokens = [
        t
        for p, t in zip(
            [p for p in people for _ in range(cfg.bio_n_rewordings)], bio_tokens
        )
        if p["split"] == "train"
    ]
    mean_tok = sum(bio_tokens) / len(bio_tokens)
    mean_train_tok = (
        sum(train_bio_tokens) / len(train_bio_tokens) if train_bio_tokens else 0.0
    )
    manifest = {
        "stage": "bios",
        "config_fingerprint": cfg.fingerprint("bios"),
        "small": cfg.small,
        "seed": cfg.seed,
        "people": people_stats,
        "values": {a: value_reports[a] for a in cfg.bio_attributes},
        "value_tokens": tok_report,
        "templates_per_attribute": {
            a: {
                "train": len(bd.TRAIN_TEMPLATES[a]),
                "held_out": len(bd.HELDOUT_TEMPLATES[a]),
            }
            for a in cfg.bio_attributes
        },
        "facts": {
            "rows": n_facts,
            "by_role": dict(sorted(role_counts.items())),
            "by_attribute": dict(sorted(attr_counts.items())),
        },
        "biographies": {
            "rows": len(bio_tokens),
            "tokens_mean": round(mean_tok, 2),
            "tokens_min": min(bio_tokens),
            "tokens_max": max(bio_tokens),
            "train_tokens_mean": round(mean_train_tok, 2),
        },
        "exposures": {
            "total_copies": exposures,
            "implied_tokens": int(round(exposures * mean_train_tok)),
            "share_of_train_budget": round(
                exposures * mean_train_tok / cfg.total_train_tokens, 4
            ),
            "train_budget": cfg.total_train_tokens,
            "bio_share_target": cfg.bio_share,
        },
        "name_check": {k: v for k, v in check.items() if k != "occurrences"},
    }
    record_timing(cfg, "bios", time.time() - t0)
    write_json(out_dir / "manifest.json", manifest)
    print_summary(cfg, manifest)
    return manifest


def print_summary(cfg: DataConfig, m: Dict[str, Any]) -> None:
    p = m["people"]
    print(
        f"\n[bios] {p['n_people']:,} people  "
        f"splits={p['by_split']}  genders={p['by_gender']}"
    )
    print(f"[bios] tiers={p['by_tier']}")
    print(f"[bios] tier/gender={p['by_tier_gender']}")
    print(
        f"[bios] facts.jsonl {m['facts']['rows']:,} rows  "
        f"roles={m['facts']['by_role']}"
    )
    b, e = m["biographies"], m["exposures"]
    print(
        f"[bios] biography tokens: mean {b['tokens_mean']} "
        f"(train {b['train_tokens_mean']}), range {b['tokens_min']}-{b['tokens_max']}"
    )
    print(
        f"[bios] exposure copies {e['total_copies']:,} -> "
        f"{e['implied_tokens']:,} tokens = "
        f"{e['share_of_train_budget']:.2%} of {e['train_budget']:,} "
        f"(target {e['bio_share_target']:.0%})"
    )
    print(
        f"[bios] names rejected: {p['names_rejected_by_pile_check']} by the "
        f"Pile check, {p.get('names_rejected_by_value_collision', 0)} by the "
        f"value-collision filter; {p.get('fact_redraws', 0)} fact redraws "
        f"over {p.get('people_with_a_redrawn_fact', 0)} people"
    )


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    ap.add_argument(
        "--skip-name-check",
        action="store_true",
        help="do not scan the Pile text for generated names",
    )
    ap.add_argument(
        "--samples",
        type=int,
        default=0,
        help="also write N random people to <root>/samples/bios_sample.md",
    )
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    run(cfg, name_check=not args.skip_name_check)
    if args.samples:
        from data.bios_sample import write_sample

        print(f"[bios] sample -> {write_sample(cfg, args.samples)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
