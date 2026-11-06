"""The packed-token loader: shapes, order, resume."""

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.loader import PackedDataset, iter_document_windows

BLOCK = 512


@pytest.fixture(scope="module")
def binfile(tmp_path_factory):
    """A synthetic packed file: 200 sequences' worth of recognisable tokens."""
    path = tmp_path_factory.mktemp("loader") / "train.bin"
    n = BLOCK * 200 + 1
    arr = (np.arange(n, dtype=np.int64) % 50000).astype(np.uint16)
    arr.tofile(path)
    return path


def test_shapes_and_dtypes(binfile):
    ds = PackedDataset(binfile, BLOCK, seed=1)
    x, y = ds.get_batch(0, batch_size=7)
    assert x.shape == (7, BLOCK) and y.shape == (7, BLOCK)
    assert x.dtype == torch.int64 and y.dtype == torch.int64


def test_targets_are_inputs_shifted_by_one(binfile):
    """y must be the next token, including across the sequence boundary."""
    ds = PackedDataset(binfile, BLOCK, seed=1)
    tokens = np.fromfile(binfile, dtype=np.uint16)
    x, y = ds.get_batch(0, batch_size=4)
    order = ds.sequence_order(0)[:4]
    for row, s in enumerate(order):
        a = int(s) * BLOCK
        assert np.array_equal(x[row].numpy(), tokens[a : a + BLOCK])
        assert np.array_equal(y[row].numpy(), tokens[a + 1 : a + BLOCK + 1])
        # the last target is the first token of the next sequence
        assert int(y[row, -1]) == int(tokens[a + BLOCK])
    assert torch.equal(x[:, 1:], y[:, :-1])


def test_the_last_sequence_is_dropped_when_it_has_no_target(tmp_path):
    path = tmp_path / "t.bin"
    np.zeros(BLOCK * 10, dtype=np.uint16).tofile(path)  # exactly 10 blocks
    assert PackedDataset(path, BLOCK).n_sequences == 9  # the 10th has no y
    path2 = tmp_path / "t2.bin"
    np.zeros(BLOCK * 10 + 1, dtype=np.uint16).tofile(path2)
    assert PackedDataset(path2, BLOCK).n_sequences == 10


def test_same_seed_same_order_different_seed_different_order(binfile):
    a = PackedDataset(binfile, BLOCK, seed=1234)
    b = PackedDataset(binfile, BLOCK, seed=1234)
    c = PackedDataset(binfile, BLOCK, seed=4321)
    assert np.array_equal(a.sequence_order(0), b.sequence_order(0))
    assert not np.array_equal(a.sequence_order(0), c.sequence_order(0))
    # and the batches follow the order
    xa, _ = a.get_batch(0, 8)
    xb, _ = b.get_batch(0, 8)
    xc, _ = c.get_batch(0, 8)
    assert torch.equal(xa, xb)
    assert not torch.equal(xa, xc)


def test_the_order_is_a_permutation_covering_every_sequence(binfile):
    ds = PackedDataset(binfile, BLOCK, seed=7)
    order = ds.sequence_order(0)
    assert sorted(order.tolist()) == list(range(ds.n_sequences))


def test_epochs_use_different_permutations_and_wrap_cleanly(binfile):
    ds = PackedDataset(binfile, BLOCK, seed=7)
    e0 = ds.sequence_order(0).copy()
    e1 = ds.sequence_order(1).copy()
    assert not np.array_equal(e0, e1)
    assert sorted(e1.tolist()) == list(range(ds.n_sequences))
    # draw a batch that straddles the epoch boundary
    ds2 = PackedDataset(binfile, BLOCK, seed=7)
    ds2.position = ds2.n_sequences - 3
    idx = ds2._next_indices(6)
    assert np.array_equal(idx[:3], e0[-3:])
    assert np.array_equal(idx[3:], e1[:3])


def test_state_round_trips(binfile):
    ds = PackedDataset(binfile, BLOCK, seed=99)
    for _ in range(5):
        ds.get_batch(0, 4)
    state = ds.state_dict()
    assert state == {
        "seed": 99,
        "position": 20,
        "n_sequences": ds.n_sequences,
        "block_size": BLOCK,
        "path": str(binfile),
        "n_tokens": ds.n_tokens,
    }
    other = PackedDataset(binfile, BLOCK, seed=1)
    other.load_state_dict(state)
    assert other.seed == 99 and other.position == 20


def test_resume_after_n_steps_matches_an_unbroken_run(binfile):
    """The point of saving (seed, position): the batches must line up exactly."""
    batch, n_before, n_after = 6, 11, 9

    whole = PackedDataset(binfile, BLOCK, seed=2024)
    expected = [whole.get_batch(i, batch) for i in range(n_before + n_after)]

    part = PackedDataset(binfile, BLOCK, seed=2024)
    for i in range(n_before):
        part.get_batch(i, batch)
    state = part.state_dict()

    resumed = PackedDataset(binfile, BLOCK, seed=0)  # wrong seed on purpose
    resumed.load_state_dict(state)
    for i in range(n_after):
        x, y = resumed.get_batch(n_before + i, batch)
        ex, ey = expected[n_before + i]
        assert torch.equal(x, ex), i
        assert torch.equal(y, ey), i


def test_resume_refuses_a_file_that_changed_under_it(binfile, tmp_path):
    ds = PackedDataset(binfile, BLOCK, seed=1)
    state = ds.state_dict()
    short = tmp_path / "short.bin"
    np.zeros(BLOCK * 50 + 1, dtype=np.uint16).tofile(short)
    other = PackedDataset(short, BLOCK, seed=1)
    with pytest.raises(ValueError, match="refusing to resume"):
        other.load_state_dict(state)
    with pytest.raises(ValueError, match="block_size"):
        PackedDataset(binfile, 256, seed=1).load_state_dict(state)


def test_missing_file_says_how_to_get_it(tmp_path):
    with pytest.raises(FileNotFoundError, match="data.fetch"):
        PackedDataset(tmp_path / "nope.bin", BLOCK)


def test_too_small_a_file_is_an_error(tmp_path):
    path = tmp_path / "tiny.bin"
    np.zeros(10, dtype=np.uint16).tofile(path)
    with pytest.raises(ValueError, match="not even one"):
        PackedDataset(path, BLOCK)


def test_document_windows_stay_inside_the_document():
    tokens = np.arange(100, dtype=np.uint16)
    got = list(iter_document_windows(tokens, 10, 30, block_size=12))
    assert [len(x) for x, _ in got] == [12, 12, 5]
    for x, y in got:
        assert np.array_equal(x + 1, y)
        assert x[0] >= 10 and y[-1] <= 39
    assert list(iter_document_windows(tokens, 5, 1, 12)) == []
