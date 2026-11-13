"""U4. Slot–subject association conditioned on token identity."""

from collections import Counter, defaultdict
import math
import random


def _document_counts(reads):
    counts = defaultdict(Counter)
    subjects = {}
    for read in reads:
        doc = read["doc_id"]
        if doc in subjects and subjects[doc] != read["subject"]:
            raise ValueError(f"document {doc!r} has multiple subject labels")
        subjects[doc] = read["subject"]
        counts[doc].update((read["token"], slot) for slot in read["ids"])
    return counts, subjects


def _association(counts, subjects, profiles=False):
    by_subject = defaultdict(Counter)
    for doc, events in counts.items():
        by_subject[subjects[doc]].update(events)
    pooled = Counter()
    for events in by_subject.values():
        pooled.update(events)
    n = sum(pooled.values())
    by_word = Counter()
    for (word, _), count in pooled.items():
        by_word[word] += count
    subject_words = {}
    observed = {}
    mi = 0.0
    for subject, events in by_subject.items():
        words = Counter()
        slots = Counter()
        for (word, slot), count in events.items():
            words[word] += count
            slots[slot] += count
        subject_words[subject] = words
        observed[subject] = slots
        for (word, slot), count in events.items():
            mi += count * math.log2(
                count * by_word[word] / (words[word] * pooled[word, slot])
            )
    mi = max(mi / n, 0.0) if n else None
    if not profiles:
        return mi

    # Lexical null: at a fixed token ID, slots occur at their pooled rates in
    # every subject. Positive excess per subject read is the TF component.
    rows = {}
    for subject, slots in observed.items():
        expected = Counter()
        words = subject_words[subject]
        for (word, slot), count in pooled.items():
            expected[slot] += count * words[word] / by_word[word]
        rows[subject] = []
        total = sum(slots.values())
        for slot, count in slots.items():
            df = sum(slot in other for other in observed.values())
            idf = 1.0 + math.log((1 + len(observed)) / (1 + df))
            excess = count - expected[slot]
            score = max(excess, 0.0) * idf / total
            rows[subject].append(
                dict(slot=slot, observed=count, expected=expected[slot], score=score)
            )
        rows[subject].sort(key=lambda row: (-row["score"], row["slot"]))
    shared = sum(
        count
        for word, count in by_word.items()
        if sum(word in words for words in subject_words.values()) > 1
    )
    return mi, rows, shared / n if n else None


def rank_subject_slots(reads):
    """Rank positive subject-specific slots on discovery text; ties use slot ID."""
    text_reads = (r for r in reads if r.get("cohort", "text") == "text")
    _, rows, _ = _association(*_document_counts(text_reads), profiles=True)
    return {
        subject: [r["slot"] for r in profile if r["observed"] - r["expected"] > 1e-10]
        for subject, profile in rows.items()
    }


def subject_slot_excess(reads):
    """Positive subject-specific slots in rank order, with their excess reads."""
    text_reads = (r for r in reads if r.get("cohort", "text") == "text")
    _, rows, _ = _association(*_document_counts(text_reads), profiles=True)
    return {
        subject: [
            (r["slot"], r["observed"] - r["expected"])
            for r in profile
            if r["observed"] - r["expected"] > 1e-10
        ]
        for subject, profile in rows.items()
    }


def _specificity(reads, seed, permutations):
    counts, subjects = _document_counts(reads)
    observed, rows, shared = _association(counts, subjects, profiles=True)
    rng = random.Random(seed)
    labels = list(subjects.values())
    null = []
    if observed is not None:
        for _ in range(permutations):
            rng.shuffle(labels)
            null.append(_association(counts, dict(zip(subjects, labels))))
    null_mean = sum(null) / len(null) if null else None
    return dict(
        conditional_mi_bits=observed,
        shuffled_mean_bits=null_mean,
        excess_bits=observed - null_mean if null else None,
        shuffle_p=(
            (1 + sum(x >= observed - 1e-12 for x in null)) / (len(null) + 1)
            if null
            else None
        ),
        permutations=len(null),
        documents=len(subjects),
        shared_word_read_fraction=shared,
        slot_profiles=rows,
    )


def run(ctx):
    reads = [r for r in ctx.eval_reads if r.get("cohort", "text") == "text"]
    data = _specificity(reads, ctx.seed, ctx.permutations)
    report = dict(
        title="Subject specificity",
        result=data,
        columns=[
            "Conditional MI (bits)",
            "Shuffle mean (bits)",
            "Excess (bits)",
            "Permutation p",
            "Shared-token reads (%)",
            "Documents",
        ],
        rows=[
            [
                data["conditional_mi_bits"],
                data["shuffled_mean_bits"],
                data["excess_bits"],
                data["shuffle_p"],
                (
                    100 * data["shared_word_read_fraction"]
                    if data["shared_word_read_fraction"] is not None
                    else None
                ),
                data["documents"],
            ]
        ],
    )
    if reads and data["documents"] == len({r["subject"] for r in reads}):
        report["status"] = (
            "With one document per subject, label permutations leave conditional MI unchanged."
        )
    return report
