import pytest
import torch

from metrics.c6 import effective_rank


def test_effective_rank_of_full_rank_matrix():
    rows = torch.eye(4)
    assert effective_rank(rows) == pytest.approx(4.0)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="needs MPS")
def test_effective_rank_matches_cpu_for_mps_rows():
    # A combined .to(device="cpu", dtype=torch.float64) copy of an MPS tensor
    # came back as zeros, so C6 reported no rank on --device mps.
    rows = torch.randn(512, 64, generator=torch.Generator().manual_seed(0))
    expected = effective_rank(rows)
    on_mps = torch.nn.Parameter(rows).to("mps")
    assert effective_rank(on_mps[list(range(512))]) == pytest.approx(expected)
