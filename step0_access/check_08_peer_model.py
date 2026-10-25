"""B2 -- community PEER model jaivial/dna-diskchat-2b-peer-v21.

The repo has 8 undocumented checkpoint folders; `checkpoints/final_113738.pt` is the final
one (step 113738 matches the README's 1.162B-token run). Only that file is downloaded.
Reports where the PEER experts and their product keys live, with real tensor shapes.
"""
import json, os, sys, time

import torch

from _common import jdump, human

REPO = "jaivial/dna-diskchat-2b-peer-v21"
CKPT = "checkpoints/final_113738.pt"


def main():
    from huggingface_hub import hf_hub_download

    res = {"repo": REPO, "checkpoint": CKPT}

    # the repo's scripts hardcode sys.path.insert(0, '/root/dna'); the real import root is
    # the snapshot's scripts/ dir, so put that first
    ck_path = hf_hub_download(REPO, CKPT)
    scripts = os.path.join(os.path.dirname(os.path.dirname(ck_path)), "scripts")
    for f in ("model_dna.py", "model_dna_peer_v21.py"):
        hf_hub_download(REPO, f"scripts/{f}")
    sys.path.insert(0, scripts)

    res["checkpoint_bytes"] = os.path.getsize(ck_path)
    res["checkpoint_size"] = human(os.path.getsize(ck_path))
    res["all_checkpoints_in_repo"] = [
        "ckpt_8000", "ckpt_20000", "ckpt_40000", "ckpt_60000", "ckpt_80000",
        "ckpt_100000", "ckpt_113738", "final_113738 (<- the final one, used here)"]

    res["load_code"] = f'''import sys, torch
from huggingface_hub import hf_hub_download
ck_path = hf_hub_download("{REPO}", "{CKPT}")              # 2.93 GB
sys.path.insert(0, <snapshot>/scripts)                      # repo scripts hardcode /root/dna
from model_dna_peer_v21 import DnaPeerV21, peer_counts
ck  = torch.load(ck_path, map_location="cpu", weights_only=False)
cfg = ck["config"]      # {{vocab:32000, d:512, layers:16, ff:1536, a:2048, b:2048,
                        #   nk:704, dk:128, topk:8, pheads:1, peer_layers:[4,8,12]}}
model = DnaPeerV21(**cfg)
missing, unexpected = model.load_state_dict(ck["model"], strict=False)
model.eval()
# DnaChat has no forward(); features() + head2 is the entry point
h, balance, rows = model.features(ids)
logits = model.head2(h)'''

    t0 = time.perf_counter()
    ck = torch.load(ck_path, map_location="cpu", weights_only=False)
    res["torch_load_seconds"] = round(time.perf_counter() - t0, 2)
    res["checkpoint_top_level_keys"] = sorted(ck.keys())
    res["config"] = ck["config"]
    res["training_step"] = ck.get("step")
    res["valid_ce"] = ck.get("valid_ce")
    res["tokens_trained"] = ck.get("tokens")

    from model_dna_peer_v21 import DnaPeerV21, peer_counts

    t0 = time.perf_counter()
    model = DnaPeerV21(**ck["config"])
    missing, unexpected = model.load_state_dict(ck["model"], strict=False)
    model.eval()
    res["build_and_load_seconds"] = round(time.perf_counter() - t0, 2)
    res["missing_keys"] = list(missing)
    res["unexpected_keys"] = list(unexpected)

    ctrl, active = peer_counts(model)
    res["params"] = {
        "all_parameters": sum(p.numel() for p in model.parameters()),
        "controller_total_peer_counts": ctrl,
        "active_per_token_peer_counts": active,
        "expert_pool_params": int(model.pool.up.weight.numel() + model.pool.down.weight.numel()),
        "buffers": sum(b.numel() for b in model.buffers()),
    }

    # ---- where the PEER experts and their keys live ------------------------------
    sd = ck["model"]
    layers = list(model.peer_layers)
    res["peer_tensors"] = {
        "shared_expert_pool": {
            "pool.up.weight": list(sd["pool.up.weight"].shape),
            "pool.down.weight": list(sd["pool.down.weight"].shape),
            "dtype": str(sd["pool.up.weight"].dtype),
            "num_experts": int(model.pool.E),
            "nk_subkeys_per_half": int(model.pool.nk),
            "note": (f"ONE pool of nk^2 = {model.pool.nk}^2 = {model.pool.E} rank-1 experts, "
                     f"shared by the {len(layers)} PEER layers {layers}. Each expert is a "
                     "rank-1 MLP: row i of pool.up (d=512, the 'read' direction) and row i of "
                     "pool.down (d=512, the 'write'/value direction). pool.down rows are the "
                     "VALUES in our sense."),
            "aliased_state_dict_keys": [f"blocks.{i}.ffn.pool.{w}.weight"
                                        for i in layers for w in ("up", "down")],
            "alias_note": ("the per-block blocks.{4,8,12}.ffn.pool.* entries are the SAME "
                           "shared module saved once per block; at load time they are one "
                           "tensor (verified below)"),
        },
        "product_keys_per_peer_layer": {
            f"blocks.{i}.ffn.{k}": list(sd[f"blocks.{i}.ffn.{k}"].shape)
            for i in layers for k in ("Ka", "Kb")
        },
        "product_key_note": (
            "Ka / Kb are the two halves of the product key: [pheads, nk, dk] = "
            f"[{ck['config']['pheads']}, {ck['config']['nk']}, {ck['config']['dk']}]. "
            "expert_id = argtop(qa.Ka)*nk + argtop(qb.Kb), so Ka x Kb addresses nk^2 experts. "
            "Keys are PER LAYER; the value pool is SHARED."),
        "query_projection_per_peer_layer": {
            f"blocks.{i}.ffn.q.weight": list(sd[f"blocks.{i}.ffn.q.weight"].shape)
            for i in layers},
        "query_batchnorm_per_peer_layer": {
            f"blocks.{i}.ffn.qbn.{s}": list(sd[f"blocks.{i}.ffn.qbn.{s}"].shape)
            for i in layers for s in ("weight", "bias", "running_mean", "running_var")},
        "separate_codon_memory_table": {
            "codons": list(sd["codons"].shape),
            "codons_dtype": str(sd["codons"].dtype),
            "codebook": list(sd["codebook"].shape),
            "note": ("this is the model's OTHER memory: the DNA codon table, a=2048 x b=2048 "
                     "= 4,194,304 rows x 128 uint8 codons, decoded through a 4 x 256 x 4 "
                     "positional codebook. Separate from the PEER expert pool."),
        },
    }
    res["pool_is_shared_object"] = all(
        model.blocks[i].ffn.pool is model.pool for i in layers)

    # ---- forward pass ------------------------------------------------------------
    fwd = {}
    for dev in (["mps"] if torch.backends.mps.is_available() else []) + ["cpu"]:
        try:
            if dev == "mps":
                torch.mps.empty_cache()
            m = model.to(dev)
            ids = torch.randint(0, ck["config"]["vocab"], (1, 16), device=dev)
            # DnaChat defines no forward(); the entry point is features() -> (h, balance,
            # routed codon rows), then head2 produces logits. Same as scripts/train_peer_v21.py.
            t0 = time.perf_counter()
            with torch.no_grad():
                h, balance, rows = m.features(ids)
                logits = m.head2(h)
            if dev == "mps":
                torch.mps.synchronize()
                fwd["mps_driver_alloc_GB"] = round(torch.mps.driver_allocated_memory() / 1e9, 2)
            fwd[dev] = {
                "status": "PASS",
                "seconds": round(time.perf_counter() - t0, 3),
                "forward_code": "h, balance, rows = model.features(ids); logits = model.head2(h)",
                "hidden_shape": list(h.shape),
                "logits_shape": list(logits.shape),
                "routed_codon_rows_shape": list(rows.shape),
                "logits_finite": bool(torch.isfinite(logits).all().item()),
                "logits_mean": round(float(logits.float().mean()), 4),
                "balance_loss": round(float(balance), 4),
            }
            res["forward_device_used"] = dev
            model = m.to("cpu")
            break
        except Exception as e:
            fwd[dev] = {"status": "FAIL", "error": f"{type(e).__name__}: {str(e)[:400]}"}
            model = model.to("cpu")
    res["forward"] = fwd
    res["status"] = "PASS" if res.get("forward_device_used") else "FAIL"

    print(json.dumps(res, indent=2))
    jdump("08_peer_model", res)


if __name__ == "__main__":
    main()
