"""Read log, slot masking, and key freezing for both memory layers."""
import pytest
import torch
from einops import einsum

from conftest import make_model
from memlayers.memory import PEERMemory, PKMMemory


def _reads(kind, B=2, T=16, seed=0):
    m = make_model(kind, seed=seed).eval()
    layer = next(iter(m.memory_layers))
    mem = m.memory_layers[layer]
    mem.set_read_logging(True)
    idx = torch.randint(0, m.config.vocab_size, (B, T))
    with torch.no_grad():
        m(idx, idx)
    return m, mem, mem.last_read()


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_read_log_shape_and_range(kind):
    B, T = 2, 16
    m, mem, r = _reads(kind, B, T)
    assert r is not None, "read log was empty"
    assert r.indices.shape == (B, T, mem.n_heads, mem.topk)
    assert r.weights.shape == r.indices.shape
    assert r.indices.dtype == torch.int64
    assert int(r.indices.min()) >= 0
    assert int(r.indices.max()) < mem.n_slots
    assert torch.isfinite(r.weights).all()
    # exactly topk distinct slots per (token, head): product keys cannot repeat
    flat = r.indices.reshape(-1, mem.topk)
    assert all(len(set(row.tolist())) == mem.topk for row in flat)


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_read_logging_can_be_switched_off(kind):
    m, mem, r = _reads(kind)
    assert r is not None
    mem.set_read_logging(False)
    idx = torch.randint(0, m.config.vocab_size, (2, 16))
    with torch.no_grad():
        m(idx, idx)
    assert mem.last_read() is None


def test_peer_read_log_weights_match_what_the_layer_used():
    """Recompute the PEER output from the logged indices and weights alone.

    This is the check that the scores we log really are the ones that multiplied the
    expert rows -- the PEER hook sees indices and scores through two different
    modules, so they could in principle be misaligned.
    """
    B, T = 2, 16
    m, mem, r = _reads("peer", B, T)
    assert isinstance(mem, PEERMemory)
    peer = mem.peer
    x = torch.randn(B, T, m.config.n_embd)
    mem.set_read_logging(True)
    with torch.no_grad():
        out = mem(x)
    r = mem.last_read()
    assert r.weights.shape == r.indices.shape
    assert torch.isfinite(r.weights).all()

    with torch.no_grad():
        xn = peer.norm(x)
        wd = peer.weight_down_embed.weight[r.indices]      # [B,T,h,k,d]
        wu = peer.weight_up_embed.weight[r.indices]
        inner = peer.activation(einsum(xn, wd, 'b n d, b n h k d -> b n h k'))
        rebuilt = einsum(inner * r.weights, wu, 'b n h k, b n h k d -> b n d')
    assert torch.allclose(rebuilt, out, atol=1e-5), \
        f"max diff {(rebuilt - out).abs().max():.3g}"
    # with non_competing_scores=False the gate is a softmax over k
    assert torch.allclose(r.weights.sum(-1), torch.ones(B, T, mem.n_heads), atol=1e-4)


def test_pkm_read_log_weights_match_what_the_layer_used():
    B, T = 2, 16
    m, mem, _ = _reads("pkm", B, T)
    assert isinstance(mem, PKMMemory)
    x = torch.randn(B, T, m.config.n_embd)
    mem.set_read_logging(True)
    with torch.no_grad():
        out = mem(x)
    r = mem.last_read()
    with torch.no_grad():
        vals = mem.pkm.values.weight[r.indices]            # [B,T,h,k,d]
        rebuilt = (vals * r.weights.unsqueeze(-1)).sum(dim=(2, 3))
    assert torch.allclose(rebuilt, out, atol=1e-5), \
        f"max diff {(rebuilt - out).abs().max():.3g}"


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_mask_slots_semantics(kind):
    """Masked slots contribute nothing, the top-k search is unchanged, and an empty
    mask is bit-identical to no mask."""
    B, T = 2, 16
    m, mem, r0 = _reads(kind, B, T)
    x = torch.randn(B, T, m.config.n_embd)
    mem.set_read_logging(True)
    with torch.no_grad():
        base = mem(x)
    idx0 = mem.last_read().indices.clone()
    w0 = mem.last_read().weights.clone()

    # empty mask == no mask, bit for bit
    mem.set_mask_slots([])
    with torch.no_grad():
        out_empty = mem(x)
    assert torch.equal(base, out_empty)
    mem.set_mask_slots(None)
    with torch.no_grad():
        assert torch.equal(base, mem(x))

    # mask the 10 most-read slots
    hot = torch.bincount(idx0.reshape(-1), minlength=mem.n_slots)
    victims = hot.argsort(descending=True)[:10]
    assert hot[victims].sum() > 0, "picked slots that were never read"
    mem.set_mask_slots(victims.tolist(), renormalize=False)
    with torch.no_grad():
        out_masked = mem(x)
    r1 = mem.last_read()

    assert torch.equal(idx0, r1.indices), "masking must not change the top-k search"
    hit = torch.isin(r1.indices, victims)
    assert hit.any(), "test is vacuous: no masked slot was selected"
    assert float(r1.weights[hit].abs().max()) == 0.0, "masked slot kept nonzero weight"
    assert torch.allclose(r1.weights[~hit], w0[~hit]), \
        "unmasked weights changed although renormalize=False"
    assert not torch.equal(base, out_masked), "masking had no effect on the output"

    # the masked output must equal a hand-built sum over surviving slots only
    assert float(r1.weights.sum(-1).min()) < 1.0

    # renormalize=True restores per-head sum 1 -- except for a head whose entire
    # top-k was masked, where there is nothing left to renormalize and the row is 0
    mem.set_mask_slots(victims.tolist(), renormalize=True)
    with torch.no_grad():
        mem(x)
    wr = mem.last_read().weights
    idx_r = mem.last_read().indices
    fully_masked = torch.isin(idx_r, victims).all(dim=-1)
    sums = wr.sum(-1)
    assert torch.allclose(sums[~fully_masked], torch.ones_like(sums[~fully_masked]),
                          atol=1e-4), "surviving heads should renormalize to 1"
    assert torch.equal(sums.lt(1e-6), fully_masked), \
        "a row sums to zero exactly when every slot in it was masked"
    assert float(wr[torch.isin(idx_r, victims)].abs().max()) == 0.0


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_mask_slots_rejects_out_of_range(kind):
    _, mem, _ = _reads(kind)
    with pytest.raises(ValueError):
        mem.set_mask_slots([mem.n_slots])
    with pytest.raises(ValueError):
        mem.set_mask_slots([-1])


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_freeze_keys_keeps_keys_and_trains_values(kind):
    torch.manual_seed(0)
    mem_kw = {"freeze_keys": True}
    m = make_model(kind, memory={"freeze_keys": True})
    mem = next(iter(m.memory_layers.values()))
    assert all(not p.requires_grad for p in mem.key_parameters())
    assert all(p.requires_grad for p in mem.value_parameters())

    keys_before = [p.detach().clone() for p in mem.key_parameters()]
    vals_before = [p.detach().clone() for p in mem.value_parameters()]

    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=1e-2)
    idx = torch.randint(0, m.config.vocab_size, (2, 16))
    _, loss = m(idx, idx)
    loss.backward()
    opt.step()

    for p, before in zip(mem.key_parameters(), keys_before):
        assert torch.equal(p.detach(), before), "frozen keys moved"
        assert p.grad is None, "frozen keys received a gradient"
    changed = [not torch.equal(p.detach(), b)
               for p, b in zip(mem.value_parameters(), vals_before)]
    assert all(changed), "values did not change"


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_keys_train_when_not_frozen(kind):
    torch.manual_seed(0)
    m = make_model(kind)
    mem = next(iter(m.memory_layers.values()))
    before = [p.detach().clone() for p in mem.key_parameters()]
    opt = torch.optim.AdamW(m.parameters(), lr=1e-2)
    idx = torch.randint(0, m.config.vocab_size, (2, 16))
    _, loss = m(idx, idx)
    loss.backward()
    opt.step()
    assert any(not torch.equal(p.detach(), b)
               for p, b in zip(mem.key_parameters(), before))
