"""B4b (NO weight download) -- read the safetensors HEADERS of the shards holding the
memory / n-gram tables, via HTTP range requests, to get exact shapes, dtypes and the true
size of the tables themselves (as opposed to the size of the shards they sit in).

A safetensors file starts with an 8-byte little-endian header length, then a JSON header
mapping tensor name -> {dtype, shape, data_offsets}. Reading the first ~1 MB of a shard is
enough, and it also gives the exact byte range of any single tensor, so an individual table
can be fetched on its own even when the shard is shared with other weights.
"""
import json, re, struct

from _common import jdump, human

REPOS = {
    "meituan-longcat/LongCat-Flash-Lite": re.compile(r"ngram", re.I),
    "deepseek-ai/DeepSeek-V4.1-Flash": re.compile(r"engram", re.I),
}
DTYPE_BYTES = {"F64": 8, "F32": 4, "F16": 2, "BF16": 2, "F8_E4M3": 1, "F8_E5M2": 1,
               "I64": 8, "I32": 4, "I16": 2, "I8": 1, "U8": 1, "BOOL": 1}


def read_header(url, headers, probe=2_000_000):
    import requests
    r = requests.get(url, headers={**headers, "Range": f"bytes=0-{probe - 1}"},
                     allow_redirects=True, timeout=180)
    r.raise_for_status()
    raw = r.content
    n = struct.unpack("<Q", raw[:8])[0]
    if 8 + n > len(raw):                      # header longer than the probe; fetch exactly
        r = requests.get(url, headers={**headers, "Range": f"bytes=0-{8 + n - 1}"},
                         allow_redirects=True, timeout=180)
        r.raise_for_status()
        raw = r.content
    return json.loads(raw[8:8 + n]), n


def main():
    from huggingface_hub import HfApi, get_token, hf_hub_download, hf_hub_url

    api = HfApi()
    tok = get_token()
    hdrs = {"Authorization": f"Bearer {tok}"} if tok else {}

    out = {}
    for repo, pat in REPOS.items():
        r = {"repo": repo, "weights_downloaded": False,
             "method": "HTTP range read of each shard's safetensors header only"}
        try:
            info = api.model_info(repo, files_metadata=True)
            files = {s.rfilename: (s.size or 0) for s in info.siblings}
            idx_name = next(k for k in files if k.endswith(".safetensors.index.json"))
            wmap = json.load(open(hf_hub_download(repo, idx_name)))["weight_map"]

            hits = sorted(t for t in wmap if pat.search(t))
            shards = sorted({wmap[t] for t in hits})
            r["n_memory_tensors"] = len(hits)
            r["n_shards_touched"] = len(shards)
            r["shards_touched_total_size"] = human(sum(files.get(s, 0) for s in shards))

            tensors, total = {}, 0
            per_shard_hdr = {}
            for s in shards:
                hdr, hlen = read_header(hf_hub_url(repo, s), hdrs)
                per_shard_hdr[s] = {"header_json_bytes": hlen,
                                    "n_tensors_in_shard": len([k for k in hdr if k != "__metadata__"])}
                for t in hits:
                    if wmap[t] != s or t not in hdr:
                        continue
                    e = hdr[t]
                    lo, hi = e["data_offsets"]
                    nbytes = hi - lo
                    total += nbytes
                    tensors[t] = {
                        "shard": s,
                        "dtype": e["dtype"],
                        "shape": e["shape"],
                        "n_elements": int(
                            __import__("math").prod(e["shape"])) if e["shape"] else 1,
                        "bytes": nbytes,
                        "size": human(nbytes),
                        "byte_range_in_shard": [8 + hlen + lo, 8 + hlen + hi - 1],
                    }
            r["shard_headers"] = per_shard_hdr
            r["memory_tensors"] = tensors
            r["memory_tables_total_bytes"] = total
            r["memory_tables_total_size"] = human(total)
            r["pct_of_whole_repo"] = round(100 * total / sum(files.values()), 2)

            # group the big tables (the actual value stores) separately from projections
            big = {k: v for k, v in tensors.items() if v["bytes"] > 1e8}
            r["large_tables_only"] = big
            r["large_tables_total_size"] = human(sum(v["bytes"] for v in big.values()))

            r["separate_shard_verdict"] = (
                "YES -- the memory tensors occupy dedicated shards containing nothing else"
                if all(per_shard_hdr[s]["n_tensors_in_shard"] ==
                       sum(1 for t in hits if wmap[t] == s) for s in shards)
                else "NO -- the memory tensors are interleaved with ordinary layer weights "
                     "in shared shards")
            r["ranged_tensor_fetch_possible"] = True
            r["ranged_fetch_note"] = (
                "Even when a shard is shared, each tensor's exact byte range is known from "
                "the header (byte_range_in_shard above), so a single table can be pulled "
                "with one HTTP Range request -- no need for the whole shard. That is how we "
                "would get these tables without the full repo.")
            r["status"] = "PASS"
        except Exception as e:
            r["status"] = "FAIL"
            r["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        out[repo] = r

    print(json.dumps(out, indent=2))
    jdump("12_stretch_tensors", out)


if __name__ == "__main__":
    main()
