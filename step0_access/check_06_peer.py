"""C2 + C3(PEER) -- PEER-pytorch: ~65,536 experts, fwd/bwd on MPS, gradient reach,
read the selected expert indices, and freeze only the product keys.

Package: PEER-pytorch (lucidrains). num_experts must be a perfect square (product key),
so 65,536 = 256 x 256 sub-keys.
"""
import json, time

import torch
from PEER_pytorch import PEER

from _common import best_device, jdump

NUM_EXPERTS = 65_536     # 256 x 256
DIM = 512
HEADS = 8
EXPERTS_PER_HEAD = 16
DIM_KEY = 128
B, T = 2, 128


def build():
    return PEER(dim=DIM, heads=HEADS, num_experts=NUM_EXPERTS,
                num_experts_per_head=EXPERTS_PER_HEAD, dim_key=DIM_KEY,
                pre_rmsnorm=True)


def capture_indices(peer):
    """Read the selected expert indices without patching the package.

    PEER computes `indices` internally and never returns it, but it passes that exact
    tensor to self.weight_down_embed (an nn.Embedding), so a forward pre-hook sees it.
    Shape: [b, n, heads, num_experts_per_head_topk].
    """
    box = {}

    def hook(mod, args):
        box["indices"] = args[0].detach().cpu()

    h = peer.weight_down_embed.register_forward_pre_hook(hook)
    return box, h


def main():
    dev, dev_note = best_device()
    res = {"device": dev, "device_note": dev_note, "config": dict(
        dim=DIM, heads=HEADS, num_experts=NUM_EXPERTS,
        num_experts_per_head=EXPERTS_PER_HEAD, dim_key=DIM_KEY, batch=B, seq=T)}
    res["load_code"] = (
        "from PEER_pytorch import PEER\n"
        f"peer = PEER(dim={DIM}, heads={HEADS}, num_experts={NUM_EXPERTS}, "
        f"num_experts_per_head={EXPERTS_PER_HEAD}, dim_key={DIM_KEY}, pre_rmsnorm=True)")

    peer = build()
    res["num_keys_per_half"] = int(peer.num_keys)
    res["param_shapes"] = {n: list(p.shape) for n, p in peer.named_parameters()}
    res["n_params"] = sum(p.numel() for p in peer.parameters())
    res["key_param_name"] = "keys"
    res["value_param_names"] = ["weight_down_embed.weight", "weight_up_embed.weight"]
    # non_competing_scores=True (default) collapses the per-head score topk to 1
    res["effective_experts_per_head"] = int(peer.num_experts_per_head_topk)
    res["product_key_topk"] = int(peer.product_key_topk)

    # ---- C2: forward + backward --------------------------------------------------
    try:
        peer = peer.to(dev)
        x = torch.randn(B, T, DIM, device=dev)

        box, h = capture_indices(peer)
        torch.manual_seed(0)
        t0 = time.perf_counter()
        out = peer(x)
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
        for n, p in peer.named_parameters():
            g = p.grad
            if g is None:
                grads[n] = {"grad": None}
            else:
                gd = g.to_dense() if g.is_sparse else g
                grads[n] = {"grad_norm": round(gd.float().norm().item(), 8),
                            "nonzero": int((gd != 0).sum().item()),
                            "is_sparse": bool(g.is_sparse)}
        res["grads"] = grads
        res["grad_reaches_keys"] = grads["keys"].get("grad_norm", 0) > 0
        res["grad_reaches_values"] = (
            grads["weight_down_embed.weight"].get("grad_norm", 0) > 0
            and grads["weight_up_embed.weight"].get("grad_norm", 0) > 0)

        idx = box.get("indices")
        res["index_readout"] = {
            "method": "forward pre-hook on peer.weight_down_embed (nn.Embedding)",
            "captured": idx is not None,
            "indices_shape": list(idx.shape) if idx is not None else None,
            "indices_dtype": str(idx.dtype) if idx is not None else None,
            "layout": "[batch, seq, heads, num_experts_per_head_topk]",
            "min": int(idx.min()) if idx is not None else None,
            "max": int(idx.max()) if idx is not None else None,
            "in_range": bool(idx.max() < NUM_EXPERTS) if idx is not None else None,
            "unique_experts_this_batch": int(idx.unique().numel()) if idx is not None else None,
            "exposed_by_package": False,
            "smallest_source_change": (
                "PEER_pytorch/PEER.py, PEER.forward: add a `return_indices = False` kwarg "
                "and `if return_indices: return out, indices, scores` at the end. "
                "One kwarg + one branch. The hook above avoids even that."),
        }
        res["c2_status"] = "PASS" if (res["grad_reaches_keys"] and res["grad_reaches_values"]
                                     and res["index_readout"]["captured"]) else "FAIL"
    except Exception as e:
        res["c2_status"] = "FAIL"
        res["c2_error"] = f"{type(e).__name__}: {e}"

    # ---- C3: freeze only the product keys ---------------------------------------
    try:
        torch.manual_seed(1)
        frozen = build().to(dev)
        frozen.keys.requires_grad_(False)
        res["c3_freeze_code"] = (
            "peer.keys.requires_grad_(False)   # product-key table frozen\n"
            "# weight_down_embed / weight_up_embed (the experts) still train\n"
            "opt = torch.optim.Adam([p for p in peer.parameters() if p.requires_grad], lr=1e-2)")
        res["c3_requires_grad"] = {n: bool(p.requires_grad) for n, p in frozen.named_parameters()}

        keys_before = frozen.keys.detach().clone()
        down_before = frozen.weight_down_embed.weight.detach().clone()
        up_before = frozen.weight_up_embed.weight.detach().clone()

        opt = torch.optim.Adam([p for p in frozen.parameters() if p.requires_grad], lr=1e-2)
        frozen(torch.randn(B, T, DIM, device=dev)).square().mean().backward()
        opt.step()
        if dev == "mps":
            torch.mps.synchronize()

        kd = (frozen.keys.detach() - keys_before).abs().max().item()
        dd = (frozen.weight_down_embed.weight.detach() - down_before).abs().max().item()
        ud = (frozen.weight_up_embed.weight.detach() - up_before).abs().max().item()
        res["c3_after_one_step"] = {
            "keys_max_abs_change": kd,
            "keys_bit_identical": bool(torch.equal(frozen.keys.detach(), keys_before)),
            "keys_grad_is_none": frozen.keys.grad is None,
            "weight_down_max_abs_change": dd,
            "weight_up_max_abs_change": ud,
            "experts_changed": dd > 0 and ud > 0,
        }
        res["c3_status"] = "PASS" if (kd == 0.0 and dd > 0 and ud > 0) else "FAIL"
    except Exception as e:
        res["c3_status"] = "FAIL"
        res["c3_error"] = f"{type(e).__name__}: {e}"

    print(json.dumps(res, indent=2))
    jdump("06_peer", res)


if __name__ == "__main__":
    main()
