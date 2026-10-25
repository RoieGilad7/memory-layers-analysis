"""Environment check: macOS, chip, RAM, disk, Python, package versions, MPS."""
import json, platform, subprocess, sys
from _common import jdump, free_disk_gb


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    except Exception as e:
        return f"ERR {e}"


def main():
    import torch, numpy, transformers, datasets, huggingface_hub, accelerate, tiktoken, faiss
    res = {
        "macos": sh("sw_vers -productVersion"),
        "build": sh("sw_vers -buildVersion"),
        "chip": sh("sysctl -n machdep.cpu.brand_string"),
        "cpu_cores": sh("sysctl -n hw.ncpu"),
        "ram_bytes": int(sh("sysctl -n hw.memsize") or 0),
        "python": sys.version,
        "python_exe": sys.executable,
        "free_disk_gb_home": round(free_disk_gb(), 1),
        "versions": {
            "torch": torch.__version__,
            "numpy": numpy.__version__,
            "transformers": transformers.__version__,
            "datasets": datasets.__version__,
            "huggingface_hub": huggingface_hub.__version__,
            "accelerate": accelerate.__version__,
            "tiktoken": tiktoken.__version__,
            "faiss": faiss.__version__,
        },
        "torch_backends": {
            "mps_is_available": torch.backends.mps.is_available(),
            "mps_is_built": torch.backends.mps.is_built(),
            "cuda_is_available": torch.cuda.is_available(),
        },
    }
    res["ram_gb"] = round(res["ram_bytes"] / 1e9, 1)

    # optional imports that must not abort the whole check
    for name, mod in [("product_key_memory", "product_key_memory"),
                      ("PEER_pytorch", "PEER_pytorch")]:
        try:
            m = __import__(mod)
            res["versions"][name] = getattr(m, "__version__", "installed (no __version__)")
        except Exception as e:
            res["versions"][name] = f"IMPORT FAILED: {e}"

    # HF auth -- never print or store the token itself
    try:
        from huggingface_hub import whoami
        who = whoami()
        res["hf_user"] = who.get("name")
        res["hf_auth"] = "PASS"
    except Exception as e:
        res["hf_user"] = None
        res["hf_auth"] = f"FAIL: {type(e).__name__}"

    # one real MPS tensor op, to prove the backend works and not just reports available
    try:
        import torch
        d = "mps" if torch.backends.mps.is_available() else "cpu"
        a = torch.randn(512, 512, device=d)
        res["mps_matmul_ok"] = bool(torch.isfinite((a @ a).sum()).item())
        res["mps_device_used"] = d
    except Exception as e:
        res["mps_matmul_ok"] = False
        res["mps_error"] = repr(e)

    print(json.dumps(res, indent=2))
    jdump("01_env", res)


if __name__ == "__main__":
    main()
