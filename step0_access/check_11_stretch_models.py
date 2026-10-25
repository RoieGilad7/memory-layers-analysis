"""B4 (stretch, NO weight download) -- for LongCat-Flash-Lite and DeepSeek-V4.1-Flash,
list the repo files and work out whether the memory / n-gram embedding tables sit in
separate shards we could fetch on their own.

Only the index JSONs and small .py files are downloaded (a few MB); no shard is fetched.
"""
import json, re
from collections import defaultdict

from _common import jdump, human

REPOS = ["meituan-longcat/LongCat-Flash-Lite", "deepseek-ai/DeepSeek-V4.1-Flash"]
MEM_PAT = re.compile(
    r"ngram|n_gram|engram|memory|mem_|lookup|lut|\bkv_table\b|codon|expert_table|pkm",
    re.IGNORECASE)


def main():
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    out = {}
    for repo in REPOS:
        r = {"repo": repo, "weights_downloaded": False}
        try:
            info = api.model_info(repo, files_metadata=True)
            files = {s.rfilename: (s.size or 0) for s in info.siblings}
            r["n_files"] = len(files)
            r["total_bytes"] = sum(files.values())
            r["total_size"] = human(sum(files.values()))
            r["largest_files"] = [
                {"file": k, "size": human(v)}
                for k, v in sorted(files.items(), key=lambda kv: -kv[1])[:8]]
            r["small_files"] = sorted(k for k, v in files.items() if v < 1e6)

            # the index maps every tensor name to its shard; that is what tells us whether
            # the memory table is separable
            idx_name = next((k for k in files if k.endswith(".safetensors.index.json")), None)
            if not idx_name:
                r["index_json"] = None
                out[repo] = r
                continue
            idx = json.load(open(hf_hub_download(repo, idx_name)))
            wmap = idx["weight_map"]
            r["index_json"] = idx_name
            r["n_tensors"] = len(wmap)
            r["index_total_size_field"] = idx.get("metadata", {}).get("total_size")

            per_shard_tensors = defaultdict(list)
            for t, shard in wmap.items():
                per_shard_tensors[shard].append(t)

            hits = sorted(t for t in wmap if MEM_PAT.search(t))
            r["memory_like_tensor_names"] = hits[:40]
            r["n_memory_like_tensors"] = len(hits)

            hit_shards = sorted({wmap[t] for t in hits})
            r["shards_containing_memory_tensors"] = [
                {"shard": s, "size": human(files.get(s, 0)), "bytes": files.get(s, 0),
                 "n_tensors_in_shard": len(per_shard_tensors[s]),
                 "n_memory_tensors_in_shard": sum(1 for t in hits if wmap[t] == s),
                 "shard_is_memory_only": len(per_shard_tensors[s]) == sum(
                     1 for t in hits if wmap[t] == s)}
                for s in hit_shards]
            r["memory_shards_total_bytes"] = sum(files.get(s, 0) for s in hit_shards)
            r["memory_shards_total_size"] = human(sum(files.get(s, 0) for s in hit_shards))
            r["separately_downloadable"] = bool(hit_shards) and all(
                d["shard_is_memory_only"] for d in r["shards_containing_memory_tensors"])

            # tensor-name prefixes, to see the overall layout at a glance
            pref = defaultdict(int)
            for t in wmap:
                parts = t.split(".")
                pref[".".join(parts[:2]) if len(parts) > 2 else t] += 1
            r["tensor_name_prefixes_top"] = dict(
                sorted(pref.items(), key=lambda kv: -kv[1])[:12])

            # biggest shards, which is where a huge table would hide
            r["biggest_shards_with_tensor_counts"] = [
                {"shard": s, "size": human(files.get(s, 0)),
                 "n_tensors": len(per_shard_tensors[s]),
                 "sample_tensors": sorted(per_shard_tensors[s])[:6]}
                for s in sorted(per_shard_tensors, key=lambda s: -files.get(s, 0))[:4]]
            r["status"] = "PASS"
        except Exception as e:
            r["status"] = "FAIL"
            r["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        out[repo] = r

    print(json.dumps(out, indent=2, default=str))
    jdump("11_stretch_models", out)


if __name__ == "__main__":
    main()
