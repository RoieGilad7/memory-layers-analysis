"""FLOPs per token: hand-computed values, and the dense layer's compute match."""

from pathlib import Path

import pytest

from memlayers.config import load_model_group, model_kwargs
from memlayers.flops import (
    dense_ffn_flops,
    estimate_flops_per_token,
    matched_dense_hidden,
)


def _f(group):
    return estimate_flops_per_token(model_kwargs(load_model_group(group)))


def test_tiny_pkm_by_hand():
    # d=64, T=64, V=257, 3 layers, PKM at layer 1: 16 sub-keys, top-4, 2 heads, dh=32
    d, T, V = 64, 64, 257
    attn = 2 * (4 * d * d + 2 * T * d)  # 2 * (16384 + 8192) = 49152
    dense = 2 * (2 * d * 4 * d)  # 2 * 32768 = 65536
    pkm = (
        2 * (d * 2 * 2 * 32)  # query projection 64 -> 128:  16384
        + 2 * (2 * 2 * 16 * 32)  # sub-key scores:          4096
        + 2 * 4 * 4  # top-k product, additions:              32
        + 2 * (2 * 4 * d)  # value sum:                       1024
    )
    assert attn == 49_152 and dense == 65_536 and pkm == 21_536
    head = 2 * d * V  # 32896
    f = _f("tiny_pkm")
    assert [l["total"] for l in f["per_layer"]] == [
        attn + dense,
        attn + pkm,
        attn + dense,
    ]
    assert f["per_layer"][1]["ffn_parts"] == {
        "query_projection": 16_384,
        "subkey_scores": 4_096,
        "topk_product": 32,
        "value_sum": 1_024,
        "total": 21_536,
    }
    assert f["lm_head"] == head
    assert f["total"] == 3 * attn + 2 * dense + pkm + head == 332_960


def test_tiny_dense_by_hand():
    f = _f("tiny_dense")
    assert f["total"] == 3 * (49_152 + 65_536) + 2 * 64 * 257 == 376_960


def test_t1_numbers():
    pkm, peer, dense = _f("pkm"), _f("peer"), _f("dense")
    assert pkm["per_layer"][3]["ffn"] == 1_413_120
    assert peer["per_layer"][3]["ffn"] == 1_511_424
    assert dense["per_layer"][3]["ffn"] == dense_ffn_flops(384, 896) == 1_376_256
    assert dense["per_layer"][0]["ffn"] == dense_ffn_flops(384, 1536) == 2_359_296
    # the output head is the largest single term
    assert pkm["lm_head"] == 2 * 384 * 50257
    assert pkm["lm_head"] > max(l["total"] for l in pkm["per_layer"])


@pytest.mark.parametrize(
    "dense, memory, layer",
    [("dense", "pkm", 3), ("dense", "peer", 3)],
)
def test_the_dense_layer_is_within_10pct_of_the_memory_layer(dense, memory, layer):
    a = _f(dense)["per_layer"][layer]["ffn"]
    b = _f(memory)["per_layer"][layer]["ffn"]
    assert abs(a / b - 1) <= 0.10, f"{dense} {a:,} vs {memory} {b:,}"


def test_the_rule_on_an_inline_t2_config():
    """T2 (d512, L8, PKM at layer 4) is not in conf/ any more; the matching
    rule still gives it h = 832, within 10% of the PKM layer."""
    from memlayers.train import load_config

    old = Path(__file__).resolve().parent.parent / "memlayers" / "configs"
    pkm = estimate_flops_per_token(load_config(old / "t2_pkm.yaml").model)
    target = pkm["per_layer"][4]["ffn"]
    assert target == 1_708_032
    h = matched_dense_hidden(512, target)
    assert h == 832 and abs(dense_ffn_flops(512, h) / target - 1) <= 0.10


def test_the_standard_4x_ffn_was_not_within_10pct():
    """Why model/dense.yaml narrows layer 3: the rule only changes the width
    when 4x is outside 10%."""
    pkm = _f("pkm")["per_layer"][3]["ffn"]
    assert dense_ffn_flops(384, 1536) / pkm > 1.10
    assert matched_dense_hidden(384, pkm) == 896


def test_matched_hidden_keeps_4x_when_it_is_close_enough():
    target = dense_ffn_flops(384, 1536) * 1.05
    assert matched_dense_hidden(384, target) == 1536


def test_peer_with_competing_scores_off_reads_one_expert_per_head():
    m = model_kwargs(load_model_group("peer"))
    m["memory"]["non_competing_scores"] = True
    parts = estimate_flops_per_token(m)["per_layer"][3]["ffn_parts"]
    assert parts["value_sum"] == 2 * 4 * 1 * 2 * 384
