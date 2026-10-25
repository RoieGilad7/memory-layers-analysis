"""Read-log writer/reader round-trip and the slot-usage statistics."""
import math

import numpy as np
import pytest
import torch

from conftest import make_model
from memlayers.readlog import (ReadLogReader, ReadLogWriter, SlotUsageCounter,
                               bytes_per_token, usage_stats)


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_writer_reader_roundtrip(tmp_path, kind):
    m = make_model(kind).eval()
    layer, mem = next(iter(m.memory_layers.items()))
    m.set_read_logging(True)

    w = ReadLogWriter(tmp_path / "rl", n_slots={layer: mem.n_slots},
                      heads={layer: mem.n_heads}, topk={layer: mem.topk})
    captured = []
    for step in range(3):
        idx = torch.randint(0, m.config.vocab_size, (2, 16))
        with torch.no_grad():
            m(idx, idx)
        reads = m.read_logs()
        captured.append(reads[layer])
        w.append(step, reads)
    manifest = w.close()
    assert manifest.exists()

    r = ReadLogReader(tmp_path / "rl")
    assert r.layers() == [layer]
    got_idx, got_w = r.load(layer)
    want_idx = torch.cat([c.indices.reshape(-1, mem.n_heads, mem.topk) for c in captured])
    assert got_idx.shape == tuple(want_idx.shape)
    assert np.array_equal(got_idx, want_idx.numpy())           # indices are lossless
    want_w = torch.cat([c.weights.reshape(-1, mem.n_heads, mem.topk) for c in captured])
    assert got_w.shape == tuple(want_w.shape)
    # weights are stored as float16, so compare at that precision
    assert np.allclose(got_w, want_w.numpy(), atol=1e-3)


def test_writer_can_be_disabled(tmp_path):
    w = ReadLogWriter(tmp_path / "off", n_slots={0: 16}, heads={0: 2}, topk={0: 4},
                      enabled=False)
    w.append(0, {0: type("R", (), {"indices": torch.zeros(1, 1, 2, 4, dtype=torch.long),
                                   "weights": torch.zeros(1, 1, 2, 4)})()})
    assert w.close() is None
    assert not (tmp_path / "off").exists() or not list((tmp_path / "off").iterdir())
    assert w.bytes_written == 0


def test_index_dtype_is_as_narrow_as_possible():
    assert bytes_per_token(65_536, 4, 32) == 4 * 32 * (2 + 2)    # uint16 + fp16
    assert bytes_per_token(262_144, 4, 32) == 4 * 32 * (4 + 2)   # uint32 + fp16
    assert bytes_per_token(65_536, 4, 32, store_weights=False) == 4 * 32 * 2


def test_usage_stats_uniform_and_degenerate():
    n = 1024
    uniform = torch.full((n,), 10.0)
    s = usage_stats(uniform)
    assert s["fraction_used"] == 1.0
    assert s["kl_from_uniform"] == pytest.approx(0.0, abs=1e-9)
    assert s["normalized_kl"] == pytest.approx(0.0, abs=1e-9)

    one_hot = torch.zeros(n)
    one_hot[3] = 100.0
    s = usage_stats(one_hot)
    assert s["slots_used"] == 1
    assert s["fraction_used"] == pytest.approx(1 / n)
    assert s["kl_from_uniform"] == pytest.approx(math.log(n), rel=1e-9)
    assert s["normalized_kl"] == pytest.approx(1.0, rel=1e-9)
    assert s["top1_share"] == pytest.approx(1.0)

    assert usage_stats(torch.zeros(n))["kl_from_uniform"] == 0.0


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_slot_usage_counter_totals(kind):
    m = make_model(kind).eval()
    layer, mem = next(iter(m.memory_layers.items()))
    m.set_read_logging(True)
    counter = SlotUsageCounter({layer: mem.n_slots})

    B, T, steps = 2, 16, 3
    for _ in range(steps):
        idx = torch.randint(0, m.config.vocab_size, (B, T))
        with torch.no_grad():
            m(idx, idx)
        counter.update(m.read_logs())

    assert counter.tokens_seen == B * T * steps
    total = int(counter.counts[layer].sum())
    assert total == B * T * steps * mem.n_heads * mem.topk
    st = counter.stats()[layer]
    assert st["total_reads"] == total
    assert 0 < st["fraction_used"] <= 1.0
    assert st["n_slots"] == mem.n_slots
    assert 0.0 <= st["normalized_kl"] <= 1.0
    assert "kl_from_uniform_weighted" in st


def test_reader_recovers_token_positions(tmp_path):
    """The log stores no position column; coords() must rebuild (step, batch, pos)."""
    m = make_model("pkm").eval()
    layer, mem = next(iter(m.memory_layers.items()))
    m.set_read_logging(True)
    B, T, steps = 2, 16, 3

    w = ReadLogWriter(tmp_path / "rl", n_slots={layer: mem.n_slots},
                      heads={layer: mem.n_heads}, topk={layer: mem.topk})
    for step in range(steps):
        idx = torch.randint(0, m.config.vocab_size, (B, T))
        with torch.no_grad():
            m(idx, idx)
        w.append(step, m.read_logs())
    w.close()

    r = ReadLogReader(tmp_path / "rl")
    got_idx, _ = r.load(layer)
    st, bi, pos = r.coords(layer)
    assert len(st) == len(bi) == len(pos) == got_idx.shape[0] == B * T * steps
    assert st.tolist() == sum(([s] * (B * T) for s in range(steps)), [])
    # within one step: batch 0's positions 0..T-1, then batch 1's
    assert bi[:B * T].tolist() == [0] * T + [1] * T
    assert pos[:T].tolist() == list(range(T))
    assert set(np.unique(pos)) == set(range(T))
