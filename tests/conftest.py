"""Shared fixtures. Tests run on CPU: small, fast, and bit-deterministic, which the
checkpoint-resume test needs."""
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memlayers.model import GPT, GPTConfig          # noqa: E402

SMALL = dict(vocab_size=257, block_size=64, n_layer=3, n_head=4, n_embd=64,
             dropout=0.0, bias=True, tie_embeddings=True)
PKM_KW = dict(num_keys=16, topk=4, heads=2, dim_head=32, query_batchnorm=True)
PEER_KW = dict(num_experts=256, topk=4, heads=2, dim_key=32,
               non_competing_scores=False)


def make_model(kind="dense", layer=1, seed=0, memory=None, **over):
    torch.manual_seed(seed)
    kw = dict(SMALL)
    kw.update(over)
    if kind == "dense":
        cfg = GPTConfig(**kw)
    else:
        mem = dict(PKM_KW) if kind == "pkm" else dict(PEER_KW)
        mem.update(memory or {})
        cfg = GPTConfig(memory_layers=(layer,), memory_kind=kind, memory=mem, **kw)
    return GPT(cfg)


@pytest.fixture
def small_cfg():
    return dict(SMALL)


@pytest.fixture(params=["pkm", "peer"])
def memory_kind(request):
    return request.param
