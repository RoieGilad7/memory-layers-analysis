"""Forward-pass shapes and parameter accounting for dense / PKM / PEER blocks."""
import pytest
import torch

from conftest import make_model
from memlayers.memory import PEERMemory, PKMMemory


@pytest.mark.parametrize("kind", ["dense", "pkm", "peer"])
def test_forward_shapes(kind):
    m = make_model(kind).eval()
    B, T = 2, 32
    idx = torch.randint(0, m.config.vocab_size, (B, T))
    logits, loss = m(idx, idx)
    assert logits.shape == (B, T, m.config.vocab_size)
    assert loss.ndim == 0 and torch.isfinite(loss)
    # inference path returns only the last position
    logits_last, none_loss = m(idx)
    assert logits_last.shape == (B, 1, m.config.vocab_size)
    assert none_loss is None


@pytest.mark.parametrize("kind", ["dense", "pkm", "peer"])
def test_block_forward_shapes(kind):
    """The FFN replacement must be shape-preserving on its own."""
    m = make_model(kind)
    B, T, C = 2, 16, m.config.n_embd
    x = torch.randn(B, T, C)
    for block in m.transformer.h:
        out = block(x)
        assert out.shape == x.shape, f"{block.ffn_type} changed shape"
        inner = block.mlp(x)
        assert inner.shape == x.shape


def test_memory_layer_is_placed_where_asked():
    m = make_model("pkm", layer=2)
    assert m.config.ffn_types == ["dense", "dense", "pkm"]
    assert set(m.memory_layers) == {2}
    assert isinstance(m.memory_layers[2], PKMMemory)
    m = make_model("peer", layer=0)
    assert isinstance(m.memory_layers[0], PEERMemory)


def test_param_counts_split_and_sum():
    for kind in ("dense", "pkm", "peer"):
        m = make_model(kind)
        pc = m.param_counts()
        assert pc["embedding"] + pc["non_embedding"] == pc["total"]
        assert (pc["memory_keys"] + pc["memory_values"] + pc["memory_other"]
                == pc["memory_total"])
        # tied embeddings must not be double counted
        unique = sum({id(p): p.numel() for p in m.parameters()}.values())
        assert pc["total"] == unique
        if kind == "dense":
            assert pc["memory_total"] == 0
        else:
            assert pc["memory_values"] > 0 and pc["memory_keys"] > 0


def test_block_size_is_enforced():
    m = make_model("dense")
    bad = torch.zeros(1, m.config.block_size + 1, dtype=torch.long)
    with pytest.raises(ValueError, match="exceeds block_size"):
        m(bad)
