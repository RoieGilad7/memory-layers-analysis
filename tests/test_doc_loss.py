"""Phase 2 same-document loss: half finding, half vectors, the InfoNCE loss, and the
memory-layer query hook it reads from."""

import copy
import math

import pytest
import torch
import torch.nn.functional as F
from einops import einsum, rearrange

from conftest import make_model
from memlayers.doc_loss import doc_loss, find_halves, half_vectors, mean_stats

E = 0  # EOT id used in the hand-built rows


def _row(*parts):
    """parts: ints = that many non-EOT tokens (value 7), 'E' = one EOT."""
    out = []
    for p in parts:
        out += [E] if p == "E" else [7] * p
    return out


def _ref_halves(x, eot, mn):
    """Plain-python reference for find_halves."""
    hid = [[-1] * len(r) for r in x]
    k = 0
    for b, row in enumerate(x):
        i = 0
        while i < len(row):
            if row[i] == eot:
                i += 1
                continue
            j = i
            while j < len(row) and row[j] != eot:
                j += 1
            L = j - i
            if L >= mn:
                for q in range(i, j):
                    hid[b][q] = 2 * k + (0 if q - i < L // 2 else 1)
                k += 1
            i = j
    return hid, 2 * k


# ---- find_halves --------------------------------------------------------------
def test_two_pieces_split_by_eot():
    x = torch.tensor([_row(4, "E", 6)])
    h, n = find_halves(x, E, 2)
    assert n == 4
    assert h.tolist() == [[0, 0, 1, 1, -1, 2, 2, 2, 3, 3, 3]]


def test_piece_at_row_start_and_all_eot_row():
    x = torch.tensor([_row(3, "E", "E", "E"), [E] * 6])
    h, n = find_halves(x, E, 2)
    assert n == 2
    assert h[0].tolist() == [0, 1, 1, -1, -1, -1]
    assert (h[1] == -1).all()
    h, n = find_halves(torch.tensor([[E] * 5]), E, 2)
    assert n == 0 and (h == -1).all()


def test_odd_lengths():
    x = torch.tensor([_row(5, "E", 7)])
    h, n = find_halves(x, E, 2)
    first = h[0, :5].tolist()
    assert first.count(0) == 2 and first.count(1) == 3  # L//2 and L - L//2
    second = h[0, 6:].tolist()
    assert second.count(2) == 3 and second.count(3) == 4


def test_min_piece_length_boundary():
    mn = 8
    x = torch.tensor([_row(mn - 1, "E", mn, "E")])
    h, n = find_halves(x, E, mn)
    assert n == 2
    assert (h[0, : mn - 1] == -1).all()
    assert set(h[0, mn : 2 * mn].tolist()) == {0, 1}


def test_halves_never_cross_eot_and_partners_pair_up():
    torch.manual_seed(0)
    x = torch.randint(1, 50, (6, 200))
    x[torch.rand(6, 200) < 0.04] = E
    h, n = find_halves(x, E, 4)
    ref, rn = _ref_halves(x.tolist(), E, 4)
    assert n == rn and h.tolist() == ref
    assert (h[x == E] == -1).all()
    for k in range(n // 2):
        a = (h == 2 * k).nonzero()
        b = (h == 2 * k + 1).nonzero()
        assert len(a) and len(b)
        # same row, contiguous, half 2k right before 2k+1
        assert a[:, 0].unique().numel() == 1 and (a[0, 0] == b[0, 0])
        assert a[-1, 1] + 1 == b[0, 1]
        assert len(b) - len(a) in (0, 1)
        assert not (x[a[0, 0], a[0, 1] : b[-1, 1] + 1] == E).any()


def test_several_rows_are_separate_pieces():
    # a piece ending at a row end and one starting the next row must not merge
    x = torch.tensor([_row("E", 4), _row(4, "E")])
    h, n = find_halves(x, E, 2)
    assert n == 4
    assert h.tolist() == [[-1, 0, 0, 1, 1], [2, 2, 3, 3, -1]]


def test_min_piece_tokens_must_be_two():
    with pytest.raises(ValueError):
        find_halves(torch.ones(1, 4, dtype=torch.long), E, 1)


# ---- half_vectors -------------------------------------------------------------
def test_half_vectors_is_mean_then_normalize():
    torch.manual_seed(1)
    x = torch.tensor([_row(6, "E", 5), _row(4, "E", 7)])
    h, n = find_halves(x, E, 2)
    q = torch.randn(*x.shape, 10)
    v = half_vectors(q, h, n)
    ref = torch.stack([q[h == i].mean(0) for i in range(n)])
    ref = ref / ref.norm(dim=-1, keepdim=True)
    assert v.shape == (n, 10) and v.dtype == torch.float32
    assert torch.allclose(v, ref, atol=1e-6)


# ---- doc_loss -----------------------------------------------------------------
def test_identical_vectors_give_log_n_minus_one():
    N = 8
    v = F.normalize(torch.ones(N, 5), dim=-1)
    loss, st = doc_loss(v, 0.5)
    assert math.isclose(float(loss.detach()), math.log(N - 1), rel_tol=1e-5)
    assert st["halves"] == N and abs(st["gap"]) < 1e-6


def test_partners_identical_others_orthogonal():
    N, tau = 6, 0.5
    base = torch.eye(N // 2, N)
    v = base.repeat_interleave(2, dim=0)  # rows 2k, 2k+1 equal; pairs orthogonal
    loss, st = doc_loss(v, tau)
    e = math.exp(1 / tau)
    want = -math.log(e / (e + N - 2))
    assert math.isclose(float(loss.detach()), want, rel_tol=1e-5)
    assert math.isclose(st["gap"], 1.0, rel_tol=1e-6)


def test_swapping_halves_of_every_pair_keeps_the_loss():
    torch.manual_seed(2)
    v = F.normalize(torch.randn(10, 7), dim=-1)
    perm = torch.arange(10) ^ 1
    a, _ = doc_loss(v, 0.5)
    b, _ = doc_loss(v[perm], 0.5)
    assert torch.allclose(a, b, atol=1e-6)


def test_fewer_than_two_pieces_is_an_attached_zero():
    for N in (0, 2):
        w = torch.randn(N, 4, requires_grad=True)
        loss, st = doc_loss(F.normalize(w, dim=-1), 0.5)
        assert float(loss.detach()) == 0.0 and loss.requires_grad
        assert st == {"halves": N, "gap": None}
        loss.backward()


def test_gradient_is_finite():
    w = torch.randn(12, 9, requires_grad=True)
    loss, _ = doc_loss(F.normalize(w, dim=-1), 0.5)
    loss.backward()
    assert torch.isfinite(w.grad).all() and w.grad.abs().sum() > 0


def test_mean_stats_ignores_missing_gap():
    st = mean_stats([{"halves": 4, "gap": 0.2}, {"halves": 2, "gap": None}])
    assert st == {"halves": 4, "gap": 0.2}
    assert mean_stats([{"halves": 2, "gap": None}]) == {"halves": None, "gap": None}


# ---- memory-layer query hook --------------------------------------------------
def _mem(kind):
    m = make_model(kind, seed=0)
    return m, m.memory_layers[1]


def _hooked(module):
    return len(module._forward_hooks)


def test_pkm_kept_queries_are_the_ones_the_layer_used():
    m, mem = _mem("pkm")
    mem.eval()
    pkm = mem.pkm
    B, T = 2, 12
    x = torch.randn(B, T, m.config.n_embd)
    mem.set_read_logging(True)
    mem.set_keep_queries(True)
    with torch.no_grad():
        mem(x)
    q = mem.kept_queries()
    h, d, k = mem.n_heads, pkm.keys.shape[-1], mem.topk
    assert q.shape == (B, T, mem.query_dim) == (B, T, 2 * h * d)
    qq = rearrange(q, "b t (p h d) -> p b t h d", p=2, h=h)
    dots = einsum(qq, pkm.keys, "p b t h d, h n p d -> b t h p n")
    scores, idx = dots.topk(k=k, dim=-1)
    (sx, sy), (ix, iy) = (t.chunk(2, dim=3) for t in (scores, idx))
    all_s = (sx[..., :, None] + sy[..., None, :]).reshape(B, T, h, -1)
    all_i = (ix[..., :, None] * mem.num_keys + iy[..., None, :]).reshape(B, T, h, -1)
    _, fi = all_s.topk(k, dim=-1)
    slots = all_i.gather(-1, fi)
    logged = mem.last_read().indices
    assert torch.equal(slots.sort(-1).values, logged.sort(-1).values)


@pytest.mark.parametrize("kind", ["pkm", "peer"])
@pytest.mark.parametrize("train", [False, True])
def test_keeping_queries_does_not_change_the_output(kind, train):
    m, mem = _mem(kind)
    mem.train(train)
    other = copy.deepcopy(mem)
    x = torch.randn(2, 10, m.config.n_embd)
    qmod = mem._query_module()
    assert _hooked(qmod) == 0
    off = other(x)
    mem.set_keep_queries(True)
    assert _hooked(qmod) == 1
    on = mem(x)
    assert torch.equal(on, off)
    assert mem.kept_queries().shape == (2, 10, mem.query_dim)
    mem.set_keep_queries(False)
    assert _hooked(qmod) == 0 and mem.kept_queries() is None
    # switching on twice registers one hook only
    mem.set_keep_queries(True)
    mem.set_keep_queries(True)
    assert _hooked(qmod) == 1


def test_peer_kept_queries_layout():
    m, mem = _mem("peer")
    mem.eval()
    x = torch.randn(2, 6, m.config.n_embd)
    mem.set_keep_queries(True)
    with torch.no_grad():
        mem(x)
        raw = mem.peer.to_queries(mem.peer.norm(x))  # [p, b, n, h, d]
    q = mem.kept_queries()
    p, b, n, h, d = raw.shape
    assert q.shape == (b, n, p * h * d) == (2, 6, mem.query_dim)
    assert torch.equal(q.reshape(b, n, p, h, d).permute(2, 0, 1, 3, 4), raw)


def test_kept_tensor_is_cleared_each_forward():
    m, mem = _mem("pkm")
    mem.set_keep_queries(True)
    mem(torch.randn(2, 5, m.config.n_embd))
    first = mem.kept_queries()
    mem(torch.randn(3, 4, m.config.n_embd))
    assert mem.kept_queries() is not first
    assert mem.kept_queries().shape[:2] == (3, 4)


def test_doc_loss_gradient_reaches_queries_only():
    m, mem = _mem("pkm")
    mem.train()
    pkm = mem.pkm
    x = torch.randn(2, 16, m.config.n_embd)
    tok = torch.tensor([_row(7, "E", 8), _row(16)])
    mem.set_keep_queries(True)
    mem(x)
    h, n = find_halves(tok, E, 4)
    loss, _ = doc_loss(half_vectors(mem.kept_queries(), h, n), 0.5)
    loss.backward()
    g = pkm.to_queries.weight.grad
    assert g is not None and g.abs().sum() > 0
    for p in (pkm.keys, pkm.values.weight):
        assert p.grad is None or not p.grad.any()


def test_gpt_set_keep_queries():
    m = make_model("pkm", layer=1)
    assert m.kept_queries() == {}
    m.set_keep_queries(True)
    idx = torch.randint(0, m.config.vocab_size, (2, 9))
    m(idx, idx)
    kq = m.kept_queries()
    assert set(kq) == {1} and kq[1].shape == (2, 9, m.memory_layers[1].query_dim)
    assert kq[1].requires_grad
    m.release_kept_queries()
    assert m.kept_queries() == {}
    m.set_keep_queries(False)
    assert _hooked(m.memory_layers[1].pkm.norm) == 0
    with pytest.raises(KeyError):
        m.set_keep_queries(True, layer=0)
    m.set_keep_queries(True, layer=1)
    assert _hooked(m.memory_layers[1].pkm.norm) == 1
    m.set_keep_queries(False)


def test_dense_model_has_no_kept_queries():
    m = make_model("dense")
    m.set_keep_queries(True)
    m(torch.randint(0, 257, (1, 4)))
    assert m.kept_queries() == {}
