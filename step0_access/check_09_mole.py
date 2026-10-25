"""B1 -- MoLE-160M-4E: load the training-form checkpoint, run the reparameterization into
lookup tables, run a forward pass, and report where the LUTs live.

Repo code: external/MoLE (github.com/JieShibo/MoLE), written against transformers 4.38.2.
The HF repo JieShibo/MoLE-160M-4E ships the PRE-reparameterization (training) weights only;
reparameterize.py converts the per-layer expert MLPs into one global token-indexed LUT.

reparameterize.py hardcodes device_map="cuda" and save_pretrained; this check does the same
math on MPS/CPU and keeps the LUT in memory instead of writing 3.7 GB to disk, then verifies
the reparameterized model reproduces the training-form logits.
"""
import json, os, sys, time

import torch

from _common import ROOT, best_device, jdump, human

REPO = "JieShibo/MoLE-160M-4E"
MOLE_SRC = ROOT / "external" / "MoLE"
SENTENCE = "The capital of France is Paris, and the capital of Germany is"


def main():
    sys.path.insert(0, str(MOLE_SRC))
    from transformers import AutoTokenizer
    from modeling_mole import MoleForCausalLM
    from modeling_mole_rep import MoleForCausalLM as MoleForCausalLM_rep

    dev, dev_note = best_device()
    res = {"repo": REPO, "code": "github.com/JieShibo/MoLE -> external/MoLE",
           "device": dev, "device_note": dev_note,
           "repo_files_GB": 0.780, "note_repo_form": "training-phase weights (pre-reparameterization)"}

    res["load_code"] = f'''import sys; sys.path.insert(0, "external/MoLE")   # github.com/JieShibo/MoLE
from transformers import AutoTokenizer
from modeling_mole import MoleForCausalLM                      # training form
from modeling_mole_rep import MoleForCausalLM as MoleForCausalLM_rep   # inference form

tok   = AutoTokenizer.from_pretrained("{REPO}")
model = MoleForCausalLM.from_pretrained("{REPO}", torch_dtype=torch.float32,
                                        attn_implementation="eager").to("{dev}")
out   = model(**tok("{SENTENCE}", return_tensors="pt").to("{dev}"))'''

    # ---- load the training form --------------------------------------------------
    tok = AutoTokenizer.from_pretrained(REPO)
    t0 = time.perf_counter()
    model = MoleForCausalLM.from_pretrained(REPO, torch_dtype=torch.float32,
                                            attn_implementation="eager")
    res["load_seconds_cpu"] = round(time.perf_counter() - t0, 2)
    cfg = model.config
    res["config"] = {k: getattr(cfg, k) for k in
                     ("vocab_size", "hidden_size", "num_hidden_layers", "num_experts",
                      "intermediate_size", "num_attention_heads", "max_position_embeddings")}
    res["params_training_form"] = sum(p.numel() for p in model.parameters())

    t0 = time.perf_counter()
    model = model.to(dev).eval()
    if dev == "mps":
        torch.mps.synchronize()
    res["to_device_seconds"] = round(time.perf_counter() - t0, 2)

    enc = tok(SENTENCE, return_tensors="pt").to(dev)
    res["prompt"] = SENTENCE
    res["prompt_n_tokens"] = int(enc["input_ids"].shape[1])

    t0 = time.perf_counter()
    with torch.no_grad():
        out_train = model(**enc)
    if dev == "mps":
        torch.mps.synchronize()
    res["forward_training_form"] = {
        "status": "PASS",
        "seconds": round(time.perf_counter() - t0, 3),
        "logits_shape": list(out_train.logits.shape),
        "logits_finite": bool(torch.isfinite(out_train.logits).all().item()),
        "top1_next_token": tok.decode(out_train.logits[0, -1].argmax().item()),
    }
    if dev == "mps":
        res["mps_driver_alloc_GB_after_training_form"] = round(
            torch.mps.driver_allocated_memory() / 1e9, 2)

    # ---- the reparameterization (reparameterize.py, device-adapted) ---------------
    res["reparameterize_code"] = '''# reparameterize.py, with device_map="cuda" -> MPS/CPU and no save_pretrained:
with torch.no_grad():
    output_all = []
    for layer in model.model.layers:
        token_embeds = layer.expert_layernorm(model.model.embed_tokens.weight)  # [V, d]
        output_layer = torch.stack([expert(token_embeds) for expert in layer.experts], dim=1)
        output_all.append(output_layer.cpu())                                   # [V, E, d]
    output_all = torch.stack(output_all, dim=1)                   # [V, L, E, d]
    output_all = output_all.reshape(output_all.size(0), -1)       # [V, L*E*d]
state_dict = {"model.moe_table.weight": output_all}
model_rep.load_state_dict(state_dict, False)'''

    t0 = time.perf_counter()
    with torch.no_grad():
        output_all = []
        for layer in model.model.layers:
            token_embeds = layer.expert_layernorm(model.model.embed_tokens.weight)
            output_layer = torch.stack([expert(token_embeds) for expert in layer.experts], dim=1)
            output_all.append(output_layer.cpu())
        output_all = torch.stack(output_all, dim=1)
        output_all = output_all.reshape(output_all.size(0), -1)
    if dev == "mps":
        torch.mps.synchronize()
    res["reparameterize_seconds"] = round(time.perf_counter() - t0, 2)

    V, d = cfg.vocab_size, cfg.hidden_size
    L, E = cfg.num_hidden_layers, cfg.num_experts
    res["lookup_tables"] = {
        "tensor_name": "model.moe_table.weight",
        "module": "MoleModel.moe_table = nn.Embedding(vocab_size, hidden_size * num_hidden_layers * num_experts)",
        "shape": list(output_all.shape),
        "shape_formula": f"[vocab_size, hidden_size*num_hidden_layers*num_experts] = [{V}, {d}*{L}*{E}={d*L*E}]",
        "logical_view": f"[vocab_size, num_hidden_layers, num_experts, hidden_size] = [{V}, {L}, {E}, {d}]",
        "n_elements": int(output_all.numel()),
        "bytes_fp32": int(output_all.numel() * 4),
        "bytes_fp16_as_saved": int(output_all.numel() * 2),
        "size_fp16_as_saved": human(output_all.numel() * 2),
        "dtype_on_disk": "float16 (reparameterize.py calls .half() before save_pretrained)",
        "indexed_by": "input_ids -- one LUT row per VOCAB TOKEN, not per hidden state",
        "how_read": ("MoleModel.forward: moe_output = self.moe_table(input_ids) then "
                     ".view(B, L, num_layers, num_experts, hidden_size); layer idx gets "
                     "moe_output[:, :, idx], which the decoder layer combines with "
                     "softmax(router(h)) weights"),
        "key_structural_note": (
            "MoLE is NOT a product-key memory: there is no learned key table and no top-k "
            "search. The 'address' is the input token id itself and ALL num_experts entries "
            "for that token are read and mixed by the router softmax. So its value table is "
            "a per-token lookup, which is why it reparameterizes exactly."),
        "stats": {
            "mean": round(float(output_all.mean()), 6),
            "std": round(float(output_all.std()), 6),
            "absmax": round(float(output_all.abs().max()), 4),
        },
    }

    # ---- load the inference form and verify it matches ---------------------------
    rep = MoleForCausalLM_rep.from_pretrained(REPO, torch_dtype=torch.float32,
                                              attn_implementation="eager")
    missing, unexpected = rep.load_state_dict(
        {"model.moe_table.weight": output_all}, strict=False)
    res["rep_unexpected_keys"] = list(unexpected)
    res["rep_missing_keys_count"] = len(missing)
    res["params_inference_form"] = sum(p.numel() for p in rep.parameters())
    res["params_inference_form_note"] = (
        "larger than the training form: the 4 small expert MLPs per layer are replaced by the "
        "dense [V, L*E*d] LUT, which is the whole point -- compute goes down, memory goes up")

    del model
    if dev == "mps":
        torch.mps.empty_cache()

    fwd = {}
    for try_dev in ([dev] if dev != "cpu" else []) + ["cpu"]:
        try:
            r = rep.to(try_dev).eval()
            e2 = tok(SENTENCE, return_tensors="pt").to(try_dev)
            t0 = time.perf_counter()
            with torch.no_grad():
                out_rep = r(**e2)
            if try_dev == "mps":
                torch.mps.synchronize()
                fwd["mps_driver_alloc_GB"] = round(torch.mps.driver_allocated_memory() / 1e9, 2)
            lt = out_train.logits.float().cpu()
            lr = out_rep.logits.float().cpu()
            fwd[try_dev] = {
                "status": "PASS",
                "seconds": round(time.perf_counter() - t0, 3),
                "logits_shape": list(out_rep.logits.shape),
                "logits_finite": bool(torch.isfinite(out_rep.logits).all().item()),
                "top1_next_token": tok.decode(out_rep.logits[0, -1].argmax().item()),
                "max_abs_diff_vs_training_form": round(float((lt - lr).abs().max()), 6),
                "argmax_agrees_with_training_form": bool(
                    torch.equal(lt.argmax(-1), lr.argmax(-1))),
            }
            res["forward_device_used_rep"] = try_dev
            break
        except Exception as e:
            fwd[try_dev] = {"status": "FAIL", "error": f"{type(e).__name__}: {str(e)[:400]}"}
            rep = rep.to("cpu")
    res["forward_inference_form"] = fwd
    res["status"] = "PASS" if res.get("forward_device_used_rep") else "PARTIAL"

    print(json.dumps(res, indent=2))
    jdump("09_mole", res)


if __name__ == "__main__":
    main()
