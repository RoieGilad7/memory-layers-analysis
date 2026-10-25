"""Task D (local part) -- does a tiny 2-layer transformer train for 20 steps on MPS without
errors? This only proves the stack works end to end; the timed benchmark is step 1.

Runs the same 20 steps three ways:
  plain       -- a vanilla 2-layer transformer LM
  plain+PKM   -- layer 1's FFN replaced by a product-key memory (our PKM arm)
  plain+PEER  -- layer 1's FFN replaced by a PEER layer (our PEER arm)

If loss decreases and no step raises, the step-1 training code has a working substrate.
"""
import json, time

import torch
import torch.nn as nn

from _common import best_device, jdump

VOCAB, DIM, HEADS, SEQ, BATCH, STEPS = 512, 128, 4, 64, 8, 20


class Block(nn.Module):
    def __init__(self, dim, heads, memory=None):
        super().__init__()
        self.n1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.n2 = nn.LayerNorm(dim)
        self.memory = memory
        self.ff = None if memory is not None else nn.Sequential(
            nn.Linear(dim, 4 * dim), nn.GELU(), nn.Linear(4 * dim, dim))

    def forward(self, x, causal):
        h = self.n1(x)
        x = x + self.attn(h, h, h, attn_mask=causal, need_weights=False)[0]
        h = self.n2(x)
        return x + (self.memory(h) if self.memory is not None else self.ff(h))


class TinyLM(nn.Module):
    def __init__(self, memory_factory=None):
        super().__init__()
        self.emb = nn.Embedding(VOCAB, DIM)
        self.pos = nn.Embedding(SEQ, DIM)
        self.blocks = nn.ModuleList([
            Block(DIM, HEADS, memory_factory() if (memory_factory and i == 1) else None)
            for i in range(2)])
        self.norm = nn.LayerNorm(DIM)
        self.head = nn.Linear(DIM, VOCAB, bias=False)

    def forward(self, ids):
        T = ids.shape[1]
        x = self.emb(ids) + self.pos(torch.arange(T, device=ids.device))
        causal = torch.triu(torch.ones(T, T, device=ids.device, dtype=torch.bool), 1)
        for b in self.blocks:
            x = b(x, causal)
        return self.head(self.norm(x))


def run(name, factory, dev):
    torch.manual_seed(0)
    r = {"variant": name}
    try:
        model = TinyLM(factory).to(dev)
        r["n_params"] = sum(p.numel() for p in model.parameters())
        opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
        lossfn = nn.CrossEntropyLoss()

        # ONE fixed batch repeated for all 20 steps. Random i.i.d. tokens contain nothing
        # learnable, so with a fresh batch per step the loss just sits at ~ln(VOCAB) and
        # tells us nothing. Overfitting a single batch gives a real signal: if the loss
        # falls, forward, backward and the optimizer are all genuinely working on MPS.
        g = torch.Generator().manual_seed(1)
        batch = torch.randint(0, VOCAB, (BATCH, SEQ + 1), generator=g).to(dev)
        ids, tgt = batch[:, :-1], batch[:, 1:]

        losses = []
        t0 = time.perf_counter()
        for _ in range(STEPS):
            logits = model(ids)
            loss = lossfn(logits.reshape(-1, VOCAB), tgt.reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            losses.append(round(float(loss.detach()), 4))
        if dev == "mps":
            torch.mps.synchronize()
        dt = time.perf_counter() - t0

        r.update(
            status="PASS",
            steps=STEPS,
            seconds=round(dt, 2),
            sec_per_step=round(dt / STEPS, 3),
            tokens_per_sec=round(BATCH * SEQ * STEPS / dt, 1),
            loss_first=losses[0],
            loss_last=losses[-1],
            loss_decreased=losses[-1] < losses[0],
            loss_drop=round(losses[0] - losses[-1], 4),
            all_losses_finite=all(l == l and abs(l) != float("inf") for l in losses),
            losses=losses,
        )
    except Exception as e:
        r.update(status="FAIL", error=f"{type(e).__name__}: {str(e)[:400]}")
    return r


def main():
    dev, dev_note = best_device()
    res = {"device": dev, "device_note": dev_note,
           "model": dict(vocab=VOCAB, dim=DIM, heads=HEADS, layers=2, seq=SEQ,
                         batch=BATCH, steps=STEPS),
           "note": ("Smoke test only. One fixed batch of random tokens is repeated for 20 "
                    "steps, i.e. a deliberate overfit: the loss should fall well below "
                    "ln(512)=6.24. This proves fwd/bwd/optimizer work on MPS for all three "
                    "arms; it says nothing about generalization. Timed benchmark = step 1.")}

    from product_key_memory import PKM
    from PEER_pytorch import PEER

    variants = [
        ("plain", None),
        ("pkm_65536", lambda: PKM(dim=DIM, heads=4, dim_head=32, num_keys=256, topk=16)),
        ("peer_65536", lambda: PEER(dim=DIM, heads=4, num_experts=65_536,
                                    num_experts_per_head=16, dim_key=64,
                                    pre_rmsnorm=True)),
    ]
    res["runs"] = [run(n, f, dev) for n, f in variants]
    if dev == "mps":
        res["mps_driver_alloc_GB"] = round(torch.mps.driver_allocated_memory() / 1e9, 2)
    res["status"] = "PASS" if all(r["status"] == "PASS" and r["loss_decreased"]
                                  for r in res["runs"]) else "PARTIAL"

    print(json.dumps(res, indent=2))
    jdump("13_mps_train", res)


if __name__ == "__main__":
    main()
