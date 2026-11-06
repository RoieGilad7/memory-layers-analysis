"""Part B -- the hand-check pack under `data/v1/samples/`.

    python -m data.hand_samples --config configs/data/v1.yaml

Four files, all committed so a reviewer sees them in the pull request:

    pile_samples.md   10 random test-half documents per subject, first 1,500
                      characters each, with document id and ngram_overlap
    bios_review.md    20 random trained people and 5 control people: all four
                      rewordings, and every fact-recall prompt for them
                      (discovery, test, paraphrase) as prompt | continuation |
                      true value
    value_lists.md    every value list, one per line, with any pair that LOOKS
                      like a near-duplicate flagged for a human to judge
    templates_rendered.md
                      all 120 templates rendered twice -- once with a female
                      pronoun, once with a male name -- against a fixed example
                      value, with the data-5 wording beside the data-6 one for
                      every template this step changed

Everything is seeded from the data seed, so the same documents and people come
up after a rebuild and a reviewer's notes stay valid.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from data.common import DataConfig, keyed_rng, load_config, read_jsonl

SNIPPET = 1500


def _fence(text: str) -> str:
    """Put arbitrary document text in a fence that its own backticks cannot end."""
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def _cell(text: str, limit: int = 160) -> str:
    out = text.replace("|", "\\|").replace("\n", " ⏎ ")
    return out if len(out) <= limit else "…" + out[-(limit - 1) :]


# ---------------------------------------------------------------------------
def pile_samples(cfg: DataConfig, per_subject: int = 10) -> str:
    lines = [
        "# Pile hand-check sample",
        "",
        f"{per_subject} random documents per subject from the **test** halves, "
        f"first {SNIPPET:,} characters of the cleaned text. Seeded from the data "
        "seed, so a rebuild shows the same documents.",
        "",
        "**What to check:** the text reads like the subject its label claims; "
        "cleaning has not mangled it (code keeps its indentation, prose keeps "
        "its paragraphs); nothing looks like boilerplate repeated across "
        "documents; `ngram_overlap` is low except where the subject is "
        "self-overlapping by nature (`Github`, `FreeLaw`).",
        "",
    ]
    for subject in cfg.all_subjects:
        slug = cfg.slug(subject)
        docs = list(read_jsonl(cfg.heldout_dir / "test" / f"{slug}.jsonl.gz"))
        rng = keyed_rng(cfg.seed, "pile_sample", subject)
        picked = sorted(
            rng.sample(docs, min(per_subject, len(docs))), key=lambda r: r["doc_id"]
        )
        lines += [
            f"## {subject}",
            "",
            f"{len(docs):,} documents in the test half; " f"{len(picked)} shown.",
            "",
        ]
        for r in picked:
            ov = r.get("ngram_overlap")
            ov_s = "exempt (not measured)" if ov is None else f"{ov:.4%}"
            text = r["text"][:SNIPPET]
            truncated = len(r["text"]) > SNIPPET
            lines += [
                f"### `{r['doc_id']}`",
                "",
                f"- tokens: {r['n_tokens']:,}"
                + ("  (capped at 4,096)" if r.get("truncated") else ""),
                f"- 13-gram overlap with training text: {ov_s}",
                f"- source: `{r['source']}` line {r['line']:,}",
                "",
                _fence(text + ("\n…[truncated]" if truncated else "")),
                "",
            ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
def bios_review(cfg: DataConfig, n_train: int = 20, n_control: int = 5) -> str:
    people = list(read_jsonl(cfg.bios_dir / "people.jsonl"))
    by_split = defaultdict(list)
    for p in people:
        by_split[p["split"]].append(p)
    rng = keyed_rng(cfg.seed, "bios_review")
    picked = rng.sample(
        sorted(by_split["train"], key=lambda p: p["person_id"]),
        min(n_train, len(by_split["train"])),
    ) + rng.sample(
        sorted(by_split["control"], key=lambda p: p["person_id"]),
        min(n_control, len(by_split["control"])),
    )
    picked.sort(key=lambda p: (p["split"] != "train", p["person_id"]))
    wanted = {p["person_id"] for p in picked}

    bios: Dict[str, Dict[int, str]] = defaultdict(dict)
    for fname in ("bios_train.jsonl", "bios_control.jsonl"):
        for r in read_jsonl(cfg.bios_dir / fname):
            if r["person_id"] in wanted:
                bios[r["person_id"]][r["rewording_id"]] = r["text"]
    facts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in read_jsonl(cfg.bios_dir / "facts.jsonl"):
        if r["person_id"] in wanted:
            facts[r["person_id"]].append(r)

    lines = [
        "# Biography hand-check sample",
        "",
        f"{len([p for p in picked if p['split'] == 'train'])} random **trained** "
        f"people and {len([p for p in picked if p['split'] == 'control'])} "
        "**control** people (control people never enter training — they are the "
        "guessing floor). All four rewordings, and every fact-recall prompt.",
        "",
        "**What to check:** pronouns match the `gender` field; the first "
        "sentence names the person and later ones mix name and pronoun; all "
        "five values appear verbatim in every rewording; every prompt stops "
        "immediately before its value, and `prompt + continuation` reads as the "
        "start of that biography; the four `paraphrase` prompts are "
        "structurally unlike anything in the rewordings.",
        "",
        "Roles: `discovery` = rewordings 0–1 (the metric picks slots on these), "
        "`test` = rewordings 2–3 (the metric ablates slots on these), "
        "`paraphrase` = held-out templates that never appear in training text.",
        "",
    ]
    for p in picked:
        pid = p["person_id"]
        lines += [
            f"## {p['name']} (`{pid}`) — **{p['split']}**",
            "",
            "| | |",
            "|---|---|",
            f"| gender | {p['gender']} |",
            f"| tier | {p['tier']} |",
            f"| target exposures | {p['target_exposures']} |",
            "",
            "| attribute | value |",
            "|---|---|",
        ]
        for attr in cfg.bio_attributes:
            lines.append(f"| `{attr}` | {p['facts'][attr]} |")
        lines += ["", "**Rewordings**", ""]
        for r in sorted(bios[pid]):
            role = "discovery" if r in cfg.bio_discovery_rewordings else "test"
            lines += [f"{r}. *({role})* {bios[pid][r]}", ""]
        lines += [
            "**Fact-recall prompts**",
            "",
            "| role | which | attribute | prompt | continuation | true value |",
            "|---|---|---|---|---|---|",
        ]
        rows = sorted(
            facts[pid],
            key=lambda r: (
                {"discovery": 0, "test": 1, "paraphrase": 2}[r["role"]],
                r["rewording_id"] if r["rewording_id"] is not None else -1,
                r["template_id"],
                r["attribute"],
            ),
        )
        for r in rows:
            which = (
                f"r{r['rewording_id']} t{r['template_id']}"
                if r["rewording_id"] is not None
                else f"held-out t{r['template_id']}"
            )
            lines.append(
                f"| {r['role']} | {which} | `{r['attribute']}` | "
                f"{_cell(r['prompt'])} | `{_cell(r['continuation'], 40)}` "
                f"| {_cell(r['true_value'], 40)} |"
            )
        lines += ["", "---", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# One fixed value per attribute, so the only thing that moves between two
# renderings of a template is the wording. The date is in the generated format.
EXAMPLE_VALUES = {
    "birth_date": "March 4, 1987",
    "birth_city": "Lyon, France",
    "university": "Vassar College",
    "major": "Statistics",
    "employer": "Reliance Industries",
}

# A stand-in person, deliberately not one of the 2,500 generated people, so a
# reader cannot mistake these renderings for biography text from the build.
EXAMPLE_NAME = "Alan Turing"

# The data-5 wording of every template data prompt 6 changed, by (attribute,
# list index) -- printed beside the new wording so the change can be read in
# one line. Historical record only: nothing in the build reads this.
PREVIOUS_WORDING: Dict[str, Dict[int, str]] = {
    "birth_date": {
        7: "{Poss} earliest document is a birth notice dated {v}.",
        9: "Every form {subj} has filled in since then repeats the date {v}.",
        10: "{Poss} birth was registered at the town hall three days after {v}.",
        13: "{Poss} passport of ten years standing shows the date {v}.",
        15: "Nobody in {poss} family has ever disputed the date {v}.",
        18: "A registrar's ledger carries {poss} name against the date {v}.",
        19: "{Subj} arrived a full two weeks ahead of schedule, on {v}.",
    },
    "birth_city": {
        1: "Ask where {subj} grew up and the answer is always {v}.",
        2: "{Subj} grew up a few streets from the center of {v}.",
        3: "{Poss} family had lived for at least three generations in {v}.",
        4: "{Subj} spent a childhood of bicycles and long summers in {v}.",
        5: "It takes ten minutes of conversation for {obj} to mention {v}.",
        7: "{Subj} was raised by grandparents who never once left {v}.",
        8: "An accent gives {obj} away as someone from {v}.",
        9: "{Poss} earliest memories are of a flat above a bakery in {v}.",
        10: "{Subj} has never really felt at home anywhere but {v}.",
        11: "{Poss} birth records point without the slightest ambiguity to {v}.",
        13: "Nothing in the first eighteen years of {poss} life happened outside {v}.",
        14: "{Subj} was brought up on the quieter side of {v}.",
        16: "{Subj} comes, as anyone can tell, from {v}.",
        17: "{Poss} childhood home stood on a narrow street in {v}.",
    },
    "university": {
        0: "{Subj} sat the entrance exams and was offered a place at {v}.",
        4: "{Subj} earned a place, and then a scholarship, at {v}.",
        5: "{Poss} university, chosen over three others, was {v}.",
        6: "{Subj} spent four years in the library at {v}.",
        7: "Illness interrupted a whole year of {poss} studies at {v}.",
        8: "{Subj} enrolled straight out of secondary school at {v}.",
        10: "Every reference letter {subj} has ever sent mentions {v}.",
        11: "{Poss} lasting friendships and lasting debts both date from {v}.",
        12: "{Subj} was a student, and briefly a librarian, at {v}.",
        13: "{Poss} transcript still sits in a drawer, stamped by {v}.",
        14: "{Subj} trained under a famously demanding supervisor at {v}.",
        15: "{Poss} formal schooling came to an end for good at {v}.",
        16: "{Subj} went on, with a scholarship in hand, to {v}.",
        17: "{Poss} education continued, with a change of subject, at {v}.",
        19: "{Subj} applied to four schools and got into {v}.",
        18: "{Subj} completed every requirement and then some at {v}.",
    },
    "major": {
        1: "At the end of second year {subj} declared a major in {v}.",
        2: "{Subj} switched course in the first year and settled on {v}.",
        4: "By the third year {subj} had specialized entirely in {v}.",
        6: "{Subj} was the first in the family to study {v}.",
        8: "{Subj} focused, once the required courses were done, on {v}.",
        7: "{Poss} subject, the one every relative asked about, was {v}.",
        9: "{Poss} coursework for three straight years centered on {v}.",
        10: "{Subj} chose, against all advice, to study {v}.",
        11: "Every essay {subj} wrote that year was about {v}.",
        13: "After the first year {poss} academic focus never shifted from {v}.",
        14: "{Subj} dropped every elective that had nothing to do with {v}.",
        16: "{Subj} trained formally and then by long practice in {v}.",
        17: "{Poss} timetable from the second year left room for little except {v}.",
        18: "{Subj} spent three years and most of a fourth on {v}.",
    },
    "employer": {
        0: "{Subj} takes the same train to the same desk every day at {v}.",
        7: "{Poss} commute takes an hour each way to {v}.",
        9: "{Poss} career has gone through one long stretch at {v}.",
        11: "{Poss} office is four floors up in a building owned by {v}.",
        12: "A week after graduating {subj} was hired by {v}.",
        13: "{Poss} security badge opens every door on three floors at {v}.",
        16: "{Subj} spends the better part of every working week at {v}.",
        17: "{Poss} team of six people sits on the top floor at {v}.",
    },
}

# Six frames were revised twice inside data 6: once by the tables in the
# prompt, then again after the audit in reports/data6_template_fix_report.md
# §7.3 found them hard to read. The middle version is recorded so the hand
# check can see all three stages.
INTERIM_WORDING: Dict[str, Dict[int, str]] = {
    "birth_city": {
        3: "{Poss} birth made a third generation of the family born in {v}.",
        7: "{Subj} has the same city of birth as both parents, namely {v}.",
        10: "{Subj} has lived in several countries since a birth in {v}.",
    },
    "major": {
        11: "Every essay {subj} wrote was for a degree whose subject was {v}.",
        17: "{Poss} crowded timetable all went toward graduating in {v}.",
    },
    "employer": {
        13: "{Poss} staff badge opens every door on three floors at {v}.",
    },
}


PREVIOUS_HELDOUT_WORDING: Dict[str, Dict[int, str]] = {
    "birth_date": {0: "Question: when was {obj} born? Answer: {v}."},
    "birth_city": {0: "Question: where was {obj} born? Answer: {v}."},
    "university": {
        0: "Question: where did {obj} take a degree? Answer: {v}.",
        3: "{Poss} profile reads as follows -- university attended: {v}.",
    },
    "major": {0: "Question: what did {obj} study? Answer: {v}."},
    "employer": {0: "Question: where does {obj} work? Answer: {v}."},
}


def templates_rendered(cfg: DataConfig) -> str:
    """Every template, rendered twice, for a hand check of the wording."""
    from data import bios_data as bd
    from data.bios import render

    lines = [
        "# Every template, rendered",
        "",
        "All 120 sentence frames: 20 training and 4 held-out per attribute, "
        "each rendered twice against one fixed value -- once with a **female "
        "pronoun** and once with a **male name** "
        f"(`{EXAMPLE_NAME}`, deliberately not one of the 2,500 generated "
        "people). The value is **bold**.",
        "",
        "**What to check.** Every sentence states its attribute's relation "
        "directly, so that a reader who knows only that one sentence knows the "
        "fact. Pronoun and name renderings are both grammatical. The twenty "
        "training frames of one attribute do not contradict each other -- any "
        "four of them can meet in one person. Nothing in a frame gives the "
        "value away.",
        "",
        "Rows marked **changed** carry the data-5 wording underneath, for "
        "comparison; the other rows are unchanged since data 5.",
        "",
    ]
    for attr in cfg.bio_attributes:
        value = EXAMPLE_VALUES[attr]
        lines += [
            f"## `{attr}`",
            "",
            f"**The relation every sentence must state:** {bd.RELATIONS[attr]}",
            "",
            f"Example value: **{value}**",
            "",
        ]
        for label, pool, previous in (
            (
                "Training templates",
                bd.TRAIN_TEMPLATES[attr],
                PREVIOUS_WORDING.get(attr, {}),
            ),
            (
                "Held-out templates",
                bd.HELDOUT_TEMPLATES[attr],
                PREVIOUS_HELDOUT_WORDING.get(attr, {}),
            ),
        ):
            lines += [f"### {label}", ""]
            for i, template in enumerate(pool):
                was = previous.get(i)
                tag = " — **changed**" if was else ""
                lines += [f"**{i}.** `{template}`{tag}", ""]
                for gender, use_name in (("female", False), ("male", True)):
                    text, at = render(template, EXAMPLE_NAME, gender, use_name, value)
                    shown = f"{text[:at]}**{value}**{text[at + len(value):]}"
                    how = "female pronoun" if not use_name else "male name"
                    lines.append(f"- *{how}:* {shown}")
                if was:
                    old_text, old_at = render(was, EXAMPLE_NAME, "female", False, value)
                    lines += [
                        "",
                        f"  - data 5 was: `{was}`",
                        f"  - data 5 read: {old_text[:old_at]}**{value}**"
                        f"{old_text[old_at + len(value):]}",
                    ]
                    mid = (
                        INTERIM_WORDING.get(attr, {}).get(i)
                        if label.startswith("Training")
                        else None
                    )
                    if mid:
                        mid_text, mid_at = render(
                            mid, EXAMPLE_NAME, "female", False, value
                        )
                        lines += [
                            f"  - first data-6 draft: `{mid}`",
                            f"  - which read: {mid_text[:mid_at]}**{value}**"
                            f"{mid_text[mid_at + len(value):]}",
                        ]
                lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
def _near_duplicate_pairs(
    values: List[str], attribute: str, skip_first_word: bool = False
) -> List[Dict[str, str]]:
    """Pairs a human should look at: a shared first word, or one inside the other.

    Deliberately over-reports — the builder already dropped first-token clashes
    and nesting identity-word sets, and this is a second, dumber net over what
    survived. But it uses the same per-attribute generic-word sets as the
    builder: strip "Science" from a major and "Computer Science" collapses into
    "Computer Engineering", which are different degrees.

    `skip_first_word` is for dates. 200 dates share twelve month names by
    construction, so "shares the first word" would flag 1,592 pairs and say
    nothing; a date is identified by (month, day), which is unique by build.
    """
    from data.bios import _GENERIC_BY_ATTR

    generic = _GENERIC_BY_ATTR.get(attribute, frozenset())
    out: List[Dict[str, str]] = []
    if not skip_first_word:
        first_word: Dict[str, List[str]] = defaultdict(list)
        for v in values:
            first_word[v.split()[0].lower().strip(",")].append(v)
        for word, group in sorted(first_word.items()):
            if len(group) > 1:
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        out.append(
                            {
                                "a": group[i],
                                "b": group[j],
                                "why": f"share the first word {word!r}",
                            }
                        )
    low = [(v, v.lower()) for v in values]
    for i, (va, la) in enumerate(low):
        for vb, lb in low[i + 1 :]:
            if la in lb or lb in la:
                out.append({"a": va, "b": vb, "why": "one contains the other"})
            else:
                wa = {w for w in re.findall(r"[a-z0-9]+", la) if w not in generic}
                wb = {w for w in re.findall(r"[a-z0-9]+", lb) if w not in generic}
                if wa and wb and (wa <= wb or wb <= wa):
                    out.append(
                        {
                            "a": va,
                            "b": vb,
                            "why": "identity words nest "
                            f"({sorted(wa)} vs {sorted(wb)})",
                        }
                    )
    seen = set()
    uniq = []
    for p in out:
        key = tuple(sorted((p["a"], p["b"])))
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def value_lists(cfg: DataConfig) -> str:
    from data.common import get_encoder

    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    data = json.loads((cfg.bios_dir / "attribute_values.json").read_text())
    lines = [
        "# Value lists hand-check",
        "",
        "Every value a biography fact can take, one per line. A fact is drawn "
        "uniformly from its list, so the list *is* the guessing distribution: "
        "the model's chance-level accuracy is 1 / (list size).",
        "",
        "**What to check:** every value is a real name (cities, universities, "
        "majors and employers) or a well-formed date; no two values in a list "
        "name the same thing; nothing is offensive or identifiable. The "
        "*flagged pairs* table under each list is a deliberately over-eager "
        "net — most flags are fine (different real institutions that happen to "
        "share a word) and need a human to say so.",
        "",
        "First-token uniqueness is enforced per list so one next-token "
        "prediction identifies a value. `birth_date` cannot satisfy that — 200 "
        "dates share twelve month tokens — so dates are unique on their first "
        "**two** tokens (month + day) instead.",
        "",
        "| attribute | values | prefix that is unique | distinct first tokens | mean tokens/value | flagged pairs |",
        "|---|---:|---|---:|---:|---:|",
    ]
    flags: Dict[str, List[Dict[str, str]]] = {}
    for attr in cfg.bio_attributes:
        vals = data["values"][attr]
        tok = data["tokens"][attr]
        n = 2 if attr in cfg.bio_first_two_tokens_unique else 1
        flags[attr] = _near_duplicate_pairs(
            vals, attr, skip_first_word=attr in cfg.bio_first_two_tokens_unique
        )
        lines.append(
            f"| `{attr}` | {len(vals)} | first {n} token"
            f"{'s' if n > 1 else ''} | {tok['distinct_first_tokens']} | "
            f"{tok['value_tokens_mean']} | {len(flags[attr])} |"
        )
    lines.append("")
    for attr in cfg.bio_attributes:
        vals = data["values"][attr]
        f = data["filtering"][attr]
        lines += [
            f"## `{attr}` — {len(vals)} values",
            "",
            f"From {f['candidates']} candidates: "
            f"{f['dropped_near_duplicate']} dropped as near-duplicates, "
            f"{f['dropped_prefix_clash']} for a {f['uniqueness']} clash, "
            f"{f['dropped_over_target']} trimmed to the target.",
            "",
        ]
        if flags[attr]:
            lines += [
                "**Flagged pairs — for a human to accept or reject:**",
                "",
                "| a | b | why flagged |",
                "|---|---|---|",
            ]
            for p in flags[attr]:
                lines.append(f"| {p['a']} | {p['b']} | {p['why']} |")
            lines.append("")
        elif attr in cfg.bio_first_two_tokens_unique:
            lines += [
                'No pairs flagged. (The "shared first word" rule is '
                "switched off for dates: 200 dates share twelve month "
                "names by construction, and a date is identified by its "
                "(month, day) pair, which is unique by build.)",
                "",
            ]
        else:
            lines += ["No pairs flagged.", ""]
        lines += ["<details><summary>all " f"{len(vals)} values</summary>", ""]
        for v in vals:
            ids = enc.encode_ordinary(" " + v)
            keep = ids[:2] if attr in cfg.bio_first_two_tokens_unique else ids[:1]
            key = "".join(enc.decode([t]) for t in keep)
            lines.append(f"- {v}  — `{key.strip()}`")
        lines += ["", "</details>", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/data/v1.yaml")
    ap.add_argument("--small", action="store_true")
    ap.add_argument("--per-subject", type=int, default=10)
    ap.add_argument("--people", type=int, default=20)
    ap.add_argument("--control", type=int, default=5)
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    out = cfg.samples_dir
    out.mkdir(parents=True, exist_ok=True)
    for name, text in (
        ("pile_samples.md", pile_samples(cfg, args.per_subject)),
        ("bios_review.md", bios_review(cfg, args.people, args.control)),
        ("value_lists.md", value_lists(cfg)),
        ("templates_rendered.md", templates_rendered(cfg)),
    ):
        (out / name).write_text(text, encoding="utf-8")
        kb = (out / name).stat().st_size / 1024
        print(f"[samples] {out / name}  ({kb:,.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
