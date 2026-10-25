"""C1 + C3(PKM) -- product-key-memory: 65,536 slots, fwd/bwd on MPS, gradient reach,
read the selected top-k slot indices, and freeze only the keys.

Package: product-key-memory (lucidrains). PKM(dim, heads, dim_head, num_keys, topk);
num_keys is the number of SUB-keys per half, so the slot count is num_keys**2.
"""
import json, time

import torch
from product_key_memory import PKM

from _common import best_device, jdump

NUM_KEYS = 256          # 256 x 256 = 65,536 slots
DIM = 512
HEADS = 4
DIM_HEAD = 128
TOPK = 32
B, T = 2, 128


def build():
    return PKM(dim=DIM, heads=HEADS, dim_head=DIM_HEAD, num_keys=NUM_KEYS, topk=TOPK)


def capture_indices(pkm):
    """Read the selected slot indices without patching the package.

    PKM computes `value_indices` internally and never returns it, but it passes that exact
    tensor as the first positional arg to self.values (an nn.EmbeddingBag), so a forward
    pre-hook on that submodule sees it. Shape: [(b t), (heads * topk)].
    """
    box = {}

    def hook(mod, args, kwargs):
        box["indices"] = args[0].detach().cpu()
        w = kwargs.get("per_sample_weights")
        if w is not None:
            box["weights"] = w.detach().cpu()

    h = pkm.values.register_forward_pre_hook(hook, with_kwargs=True)
    return box, h


def main():
    dev, dev_note = best_device()
    res = {"device": dev, "device_note": dev_note, "config": dict(
        dim=DIM, heads=HEADS, dim_head=DIM_HEAD, num_keys=NUM_KEYS, topk=TOPK,
        batch=B, seq=T)}
    res["load_code"] = (
        "from product_key_memory import PKM\n"
        f"pkm = PKM(dim={DIM}, heads={HEADS}, dim_head={DIM_HEAD}, "
        f"num_keys={NUM_KEYS}, topk={TOPK})   # num_keys**2 = {NUM_KEYS**2} slots")

    pkm = build()
    res["num_memories"] = int(pkm.num_memories)
    res["param_shapes"] = {n: list(p.shape) for n, p in pkm.named_parameters()}
    res["n_params"] = sum(p.numel() for p in pkm.parameters())
    res["key_param_name"] = "keys"
    res["value_param_name"] = "values.weight"

    # ---- C1: forward + backward on the accelerator -------------------------------
    try:
        pkm = pkm.to(dev)
        x = torch.randn(B, T, DIM, device=dev)
        mask = torch.ones(B, T, dtype=torch.bool, device=dev)

        box, h = capture_indices(pkm)
        torch.manual_seed(0)
        t0 = time.perf_counter()
        out = pkm(x, input_mask=mask)
        if dev == "mps":
            torch.mps.synchronize()
        res["forward_seconds"] = round(time.perf_counter() - t0, 4)
        res["output_shape"] = list(out.shape)

        t0 = time.perf_counter()
        out.square().mean().backward()
        if dev == "mps":
            torch.mps.synchronize()
        res["backward_seconds"] = round(time.perf_counter() - t0, 4)
        h.remove()

        grads = {}
        for n, p in pkm.named_parameters():
            g = p.grad
            if g is None:
                grads[n] = {"grad": None}
            else:
                gd = g.to_dense() if g.is_sparse else g
                grads[n] = {"grad_norm": round(gd.float().norm().item(), 6),
                            "nonzero": int((gd != 0).sum().item()),
                            "is_sparse": bool(g.is_sparse)}
        res["grads"] = grads
        res["grad_reaches_keys"] = grads["keys"].get("grad_norm", 0) > 0
        res["grad_reaches_values"] = grads["values.weight"].get("grad_norm", 0) > 0

        # ---- C1b: can we read the selected slot indices? ----------------------
        idx = box.get("indices")
        res["index_readout"] = {
            "method": "forward pre-hook on pkm.values (nn.EmbeddingBag), with_kwargs=True",
            "captured": idx is not None,
            "indices_shape": list(idx.shape) if idx is not None else None,
            "indices_dtype": str(idx.dtype) if idx is not None else None,
            "layout": "[(batch*seq), (heads*topk)] -- reshape to [b, t, heads, topk]",
            "min": int(idx.min()) if idx is not None else None,
            "max": int(idx.max()) if idx is not None else None,
            "in_range": bool(idx.max() < pkm.num_memories) if idx is not None else None,
            "unique_slots_this_batch": int(idx.unique().numel()) if idx is not None else None,
            "gate_weights_shape": list(box["weights"].shape) if "weights" in box else None,
            "exposed_by_package": False,
            "smallest_source_change": (
                "product_key_memory/product_key_memory.py, PKM.forward: add a "
                "`return_indices = False` kwarg and, at the end, "
                "`if return_indices: return out_reshaped, rearrange(value_indices, "
                "'(b t) hk -> b t hk', b = b), rearrange(attn, '(b t) hk -> b t hk', b = b)`. "
                "One kwarg + one branch; nothing else changes. The hook above avoids even that."),
        }
        res["c1_status"] = "PASS" if (res["grad_reaches_keys"] and res["grad_reaches_values"]
                                     and res["index_readout"]["captured"]) else "FAIL"
    except Exception as e:
        res["c1_status"] = "FAIL"
        res["c1_error"] = f"{type(e).__name__}: {e}"

    # ---- C3: freeze only the keys, verify one optimizer step ---------------------
    try:
        torch.manual_seed(1)
        frozen = build().to(dev)
        frozen.keys.requires_grad_(False)          # <-- the random-key twin
        res["c3_freeze_code"] = (
            "pkm.keys.requires_grad_(False)   # sub-key table frozen\n"
            "# everything else, incl. pkm.values.weight and pkm.to_queries, still trains\n"
            "opt = torch.optim.Adam([p for p in pkm.parameters() if p.requires_grad], lr=1e-2)")
        res["c3_requires_grad"] = {n: bool(p.requires_grad) for n, p in frozen.named_parameters()}

        keys_before = frozen.keys.detach().clone()
        vals_before = frozen.values.weight.detach().clone()
        q_before = frozen.to_queries.weight.detach().clone()

        opt = torch.optim.Adam([p for p in frozen.parameters() if p.requires_grad], lr=1e-2)
        x = torch.randn(B, T, DIM, device=dev)
        loss = frozen(x, input_mask=torch.ones(B, T, dtype=torch.bool, device=dev)).square().mean()
        loss.backward()
        opt.step()
        if dev == "mps":
            torch.mps.synchronize()

        kd = (frozen.keys.detach() - keys_before).abs().max().item()
        vd = (frozen.values.weight.detach() - vals_before).abs().max().item()
        qd = (frozen.to_queries.weight.detach() - q_before).abs().max().item()
        res["c3_after_one_step"] = {
            "keys_max_abs_change": kd,
            "keys_bit_identical": bool(torch.equal(frozen.keys.detach(), keys_before)),
            "keys_grad_is_none": frozen.keys.grad is None,
            "values_max_abs_change": vd,
            "values_changed": vd > 0,
            "to_queries_max_abs_change": qd,
        }
        res["c3_status"] = "PASS" if (kd == 0.0 and vd > 0) else "FAIL"
    except Exception as e:
        res["c3_status"] = "FAIL"
        res["c3_error"] = f"{type(e).__name__}: {e}"

    print(json.dumps(res, indent=2))
    jdump("05_pkm", res)


if __name__ == "__main__":
    main()
