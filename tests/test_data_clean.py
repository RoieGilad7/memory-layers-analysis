"""Cleaning and the 4096-token cap. No network: everything is synthetic."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.common import (CHARS_PER_TOKEN_BOUND, cap_to_max_tokens, clean_text,
                         get_encoder, load_config, text_sha256)

CONFIG = Path(__file__).resolve().parent.parent / "configs" / "data" / "v1.yaml"

PY_SNIPPET = (
    "def outer(x):\n"
    "    if x > 0:\n"
    "        for i in range(x):\n"
    "            print(i)\n"
    "\treturn   x\n"
)


@pytest.fixture(scope="module")
def enc():
    return get_encoder("gpt2", 50257)


# ------------------------------------------------------------------ cleaning
def test_code_indentation_survives():
    out = clean_text(PY_SNIPPET)
    lines = out.split("\n")
    assert lines[1].startswith("    if x > 0:")
    assert lines[2].startswith("        for i in range(x):")
    assert lines[3].startswith("            print(i)")
    # a tab indent is kept as a tab, not expanded or collapsed
    assert lines[4] == "\treturn x"


def test_horizontal_whitespace_runs_collapse_inside_the_line():
    assert clean_text("a   b\t\tc") == "a b c"
    # ...but not the leading indent (line 1 is stripped as the document start)
    assert clean_text("x\n    a   b") == "x\n    a b"


def test_trailing_whitespace_and_crlf_go():
    assert clean_text("a  \r\nb\t\r\n") == "a\nb"
    assert clean_text("a\rb") == "a\nb"


def test_newlines_are_kept_and_long_runs_collapse():
    assert clean_text("a\nb") == "a\nb"
    assert clean_text("a\n\nb") == "a\n\nb"
    assert clean_text("a\n\n\n\n\nb", max_consecutive_newlines=2) == "a\n\nb"


def test_nfc_normalization():
    decomposed = "école"          # e + combining acute
    assert clean_text(decomposed) == "école"


def test_empty_and_whitespace_only_documents_clean_to_empty():
    assert clean_text("") == ""
    assert clean_text("   \n\n \t ") == ""


def test_cleaning_is_idempotent():
    for s in (PY_SNIPPET, "a   b\n\n\n\nc  ", "école\r\n"):
        once = clean_text(s)
        assert clean_text(once) == once


def test_cleaning_is_deterministic_across_calls():
    assert text_sha256(clean_text(PY_SNIPPET)) == text_sha256(clean_text(PY_SNIPPET))


# ----------------------------------------------------------------- the cap
def test_short_document_is_not_truncated(enc):
    text, n, truncated = cap_to_max_tokens(enc, "hello world", 4096)
    assert text == "hello world" and truncated is False
    assert n == len(enc.encode_ordinary("hello world"))


def test_cap_is_applied_at_4096(enc):
    long = "the quick brown fox jumps over the lazy dog. " * 2000
    assert len(enc.encode_ordinary(long)) > 4096
    text, n, truncated = cap_to_max_tokens(enc, long, 4096)
    assert truncated is True
    assert n <= 4096
    # the stored text must itself re-encode to at most the cap
    assert len(enc.encode_ordinary(text)) <= 4096
    assert long.startswith(text[:200])


def test_cap_holds_for_a_document_longer_than_the_char_prefix(enc):
    long = "x " * (CHARS_PER_TOKEN_BOUND * 4096)
    text, n, truncated = cap_to_max_tokens(enc, long[:CHARS_PER_TOKEN_BOUND * 4096],
                                           4096)
    assert truncated and n <= 4096 and len(enc.encode_ordinary(text)) <= 4096


def test_cap_respects_a_smaller_limit(enc):
    text, n, truncated = cap_to_max_tokens(enc, "a b c d e f g h i j k", 4)
    assert truncated and n <= 4 and len(enc.encode_ordinary(text)) <= 4


def test_config_targets_scale_with_small():
    full = load_config(CONFIG)
    small = load_config(CONFIG, small=True)
    assert full.train_tokens_per_subject == 27_000_000
    assert full.collect_train_tokens_per_subject == 32_400_000
    assert full.heldout_tokens_per_half == 2_500_000
    assert full.heldout_min_docs_per_half == 500
    assert small.train_tokens_per_subject == 270_000
    assert small.heldout_min_docs_per_half == 5
    assert small.root != full.root
    assert full.fingerprint() != small.fingerprint()


def test_config_subject_labels_are_the_fixed_five_plus_one():
    cfg = load_config(CONFIG)
    assert cfg.train_subjects == ["Pile-CC", "Github", "PubMed Central",
                                  "FreeLaw", "Wikipedia (en)"]
    assert cfg.heldout_only_subjects == ["USPTO Backgrounds"]
    assert cfg.doc_id("Pile-CC", "train/00.jsonl.zst", 7) == "pile_cc-train00-7"


def test_fingerprint_scopes_isolate_the_stages():
    """Editing bios numbers must not make the pile stage re-extract 1.27 GB."""
    import copy
    cfg = load_config(CONFIG)
    other = load_config(CONFIG)
    other.raw = copy.deepcopy(other.raw)
    other.raw["bios"]["people"]["n_control"] += 1
    assert other.fingerprint("pile") == cfg.fingerprint("pile")
    assert other.fingerprint("bios") != cfg.fingerprint("bios")
    assert other.fingerprint() != cfg.fingerprint()

    other2 = load_config(CONFIG)
    other2.raw = copy.deepcopy(other2.raw)
    other2.raw["document"]["min_tokens"] += 1
    assert other2.fingerprint("pile") != cfg.fingerprint("pile")
    assert other2.fingerprint("bios") == cfg.fingerprint("bios")

    # the pile scope is exactly "the config without bios", so the hash recorded
    # by the prompt-1 build is still the hash this code computes
    assert cfg.fingerprint("pile").startswith("106869163e9dbb03")
