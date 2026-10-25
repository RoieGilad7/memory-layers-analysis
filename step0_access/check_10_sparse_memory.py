"""B3 -- fechyy/sparse-memory-lm-B-16M: inspect the 4-bit value table WITHOUT running the
model and WITHOUT downloading the 3.2 GB table.

The model card is explicit that the demo needs the repo's Triton kernels (CUDA/ROCm), so it
cannot run on this Mac and is not attempted. What we do need for offline value analysis is
the table's layout, which meta.json documents and which an HTTP range read of the first
bytes confirms. Nothing over 2 GB is downloaded.
"""
import json, os, time

import numpy as np

from _common import jdump, human

REPO = "fechyy/sparse-memory-lm-B-16M"
PROBE_ROWS = 4096      # how many table rows to pull with a range request


def main():
    import requests
    from huggingface_hub import HfApi, get_token, hf_hub_download, hf_hub_url

    api = HfApi()
    res = {"repo": REPO, "code": "github.com/re133/sparse-memory-lm",
           "full_model_run_attempted": False,
           "why_not": ("model card: 'It needs the Triton kernels from the repo, so it "
                       "doesn't load with transformers.' Those kernels are CUDA/ROCm only. "
                       "Per the roadmap the full model is deliberately NOT run here.")}

    # ---- file listing ------------------------------------------------------------
    info = api.model_info(REPO, files_metadata=True)
    files = {s.rfilename: (s.size or 0) for s in info.siblings}
    res["files"] = {k: {"bytes": v, "size": human(v)}
                    for k, v in sorted(files.items(), key=lambda kv: -kv[1])}
    res["total_bytes"] = sum(files.values())
    res["total_size"] = human(sum(files.values()))
    res["over_2GB_files"] = {k: human(v) for k, v in files.items() if v > 2e9}
    res["download_decision"] = ("values_q4.bin is 3.22 GB (> the 2 GB ask-first threshold). "
                                "User chose: ranged header read only, no full download.")

    # ---- meta.json: the authoritative header (1 KB) ------------------------------
    meta = json.load(open(hf_hub_download(REPO, "meta.json")))
    res["meta_json"] = meta
    rows, dim = meta["rows"], meta["dim"]
    res["value_table"] = {
        "tensor_keys_in_model": meta["table_keys"],
        "rows": rows,
        "dim": dim,
        "logical_shape": [rows, dim],
        "stored_dtype": "uint8, two 4-bit nibbles per byte",
        "bytes_per_row": dim // 2,
        "expected_values_q4_bytes": rows * dim // 2,
        "actual_values_q4_bytes": files["values_q4.bin"],
        "size_matches_shape": rows * dim // 2 == files["values_q4.bin"],
        "scales_dtype": "float16, one scale per row",
        "expected_scales_bytes": rows * 2,
        "actual_scales_bytes": files["scales_q4.bin"],
        "quantization_scheme": meta["q4"],
        "nibble_order": ("low nibble  = dims 0 .. dim/2-1 ; "
                         "high nibble = dims dim/2 .. dim-1  (NOT interleaved)"),
        "dequant": "value = (code - 8) * d,  where code in [0,15] and d = scales[row]",
        "fp32_equivalent_bytes": rows * dim * 4,
        "fp32_equivalent_size": human(rows * dim * 4),
        "shared_by": (f"one table shared by the {len(meta['table_keys'])} memory layers "
                      f"{meta['table_keys']}"),
    }
    res["architecture_from_model_card"] = {
        "d": 384, "layers": 12, "heads": 6, "context": 1024,
        "memory_layers": "layers 3, 7 and 11 replace the FFN with a memory layer",
        "routing": "4 heads, top 32 of 4096^2 product keys, one table shared by 3 layers",
        "table_params": "16,777,216 x 384 = 6.44B parameters; ~33M active per token",
        "val_ppl": "19.96 fp32 table / 19.98 this 4-bit table (Wikipedia)",
        "trained_on": "500M tokens of wikimedia/wikipedia 20231101.en, GPT-2 tokenizer",
    }

    # ---- HTTP range read of the real file headers --------------------------------
    hdrs = {"Authorization": f"Bearer {get_token()}"} if get_token() else {}
    probe = {}
    try:
        nbytes = PROBE_ROWS * dim // 2
        url = hf_hub_url(REPO, "values_q4.bin")
        t0 = time.perf_counter()
        r = requests.get(url, headers={**hdrs, "Range": f"bytes=0-{nbytes - 1}"},
                         allow_redirects=True, timeout=120)
        r.raise_for_status()
        raw = r.content
        probe["http_status"] = r.status_code
        probe["range_bytes_requested"] = nbytes
        probe["range_bytes_received"] = len(raw)
        probe["seconds"] = round(time.perf_counter() - t0, 2)
        probe["content_range_header"] = r.headers.get("Content-Range")
        probe["ranged_read_supported"] = r.status_code == 206

        packed = np.frombuffer(raw, dtype=np.uint8).reshape(-1, dim // 2)
        probe["packed_shape"] = list(packed.shape)
        lo = (packed & 0x0F).astype(np.int16)
        hi = (packed >> 4).astype(np.int16)
        codes = np.concatenate([lo, hi], axis=1)          # [n, dim], per meta's nibble order
        probe["codes_shape"] = list(codes.shape)
        probe["codes_min"] = int(codes.min())
        probe["codes_max"] = int(codes.max())
        probe["codes_in_0_15"] = bool(codes.min() >= 0 and codes.max() <= 15)
        probe["code_histogram_first_4096_rows"] = np.bincount(
            codes.ravel(), minlength=16).tolist()

        # scales are only 34 MB, so fetch the file and dequantize the probed rows
        sp = hf_hub_download(REPO, "scales_q4.bin")
        probe["scales_file_bytes"] = os.path.getsize(sp)
        scales = np.fromfile(sp, dtype=np.float16)
        probe["scales_shape"] = list(scales.shape)
        probe["scales_len_equals_rows"] = int(scales.shape[0]) == rows
        s = scales[:packed.shape[0]].astype(np.float32)[:, None]
        vals = (codes.astype(np.float32) - 8.0) * s
        probe["dequantized_shape"] = list(vals.shape)
        probe["dequantized_dtype"] = str(vals.dtype)
        probe["dequantized_stats"] = {
            "mean": round(float(vals.mean()), 6),
            "std": round(float(vals.std()), 6),
            "absmax": round(float(np.abs(vals).max()), 6),
            "all_finite": bool(np.isfinite(vals).all()),
        }
        probe["numpy_load_confirmed"] = True
        probe["full_table_numpy_recipe"] = (
            "np.memmap('values_q4.bin', dtype=np.uint8, mode='r', "
            f"shape=({rows}, {dim // 2})) -- 3.22 GB on disk, no RAM copy; dequantize a row "
            "slice with ((lo,hi nibbles) - 8) * scales[rows, None]. The full fp32 table would "
            f"be {human(rows * dim * 4)}, so slice or memmap rather than materializing it.")
        probe["status"] = "PASS"
    except Exception as e:
        probe["status"] = "FAIL"
        probe["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    res["ranged_probe"] = probe

    # ---- what it would take to run the real thing on a Colab T4 ------------------
    t4 = {
        "gpu": "NVIDIA T4, 16 GB VRAM, compute capability 7.5",
        "steps": [
            "git clone https://github.com/re133/sparse-memory-lm.git",
            "pip install torch (CUDA wheel) + -r requirements.txt + huggingface_hub",
            "python scripts/demo_generate.py --download --table ram   # or --table vram",
        ],
        "table_placement": {
            "--table vram": ("3.22 GB of 4-bit table in 16 GB VRAM: fits, with ~12 GB spare. "
                             "Fastest option (~200 tok/s on the author's RX 9070)."),
            "--table ram": ("Colab free tier gives ~12.7 GB system RAM; the 3.22 GB table "
                            "plus hot_rows.npy (134 MB) fits. Safe fallback."),
            "--table nvme": ("needs a local SSD path; Colab's disk is network-backed, so "
                             "expect far worse than the author's 140 tok/s."),
        },
        "blockers_to_check": [
            "Triton: the kernels are written for Triton 3.5/3.8. Colab's preinstalled Triton "
            "version must match or the kernels need a rebuild -- this is the main risk.",
            "T4 is sm_75 and has no bf16; if the kernels assume bf16 or sm_80+ features "
            "(e.g. async copies) they will not compile. Check the repo's requirements first.",
            "Total download is 3.67 GB, inside Colab's disk budget but slow on a free session.",
        ],
        "verdict": ("Should fit a T4 on memory grounds. The real risk is Triton/arch "
                    "compatibility, not capacity. For OUR purposes we do not need to run it: "
                    "the values are what we want, and they load into numpy on this Mac."),
    }
    res["colab_t4_requirements"] = t4
    res["offline_numpy_analysis_possible"] = probe.get("numpy_load_confirmed", False)
    res["status"] = "PASS" if probe.get("status") == "PASS" else "PARTIAL"

    print(json.dumps(res, indent=2))
    jdump("10_sparse_memory", res)


if __name__ == "__main__":
    main()
