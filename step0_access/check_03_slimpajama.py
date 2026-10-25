"""A4 -- backup dataset: SlimPajama split by source. Confirm it streams and carries a
source label (meta['redpajama_set_name']).

The repo named in the roadmap (MBZUAI-LLM/SlimPajama-627B-DC) and its upstream
(cerebras/SlimPajama-627B) both 404 on the Hub even with a valid token -- they have been
removed. This check tries them first, records the failure, then falls back to the public
mirrors that still carry the same per-source labels.
"""
import json, time
from collections import Counter

from _common import SAMPLES, jdump, finish

N = 1000
CANDIDATES = [
    ("MBZUAI-LLM/SlimPajama-627B-DC", None),   # roadmap target
    ("cerebras/SlimPajama-627B", None),        # upstream of the above
    ("venketh/SlimPajama-62B", None),          # public mirror, 62B tokens
    ("DKYoon/SlimPajama-6B", None),            # public mirror, 6B tokens
]


def main():
    from datasets import load_dataset

    res = {"candidates_tried": [], "n_target": N}
    ds = None
    for repo, cfg in CANDIDATES:
        kw = dict(path=repo, split="train", streaming=True)
        if cfg:
            kw["name"] = cfg
        code = (f'load_dataset("{repo}"' + (f', "{cfg}"' if cfg else "")
                + ', split="train", streaming=True)')
        try:
            cand = load_dataset(**kw)
            next(iter(cand))  # force the first read; a lazy handle is not proof of access
            ds = load_dataset(**kw)
            res["repo"] = repo
            res["load_code"] = code
            res["candidates_tried"].append({"repo": repo, "result": "OK"})
            break
        except Exception as e:
            res["candidates_tried"].append(
                {"repo": repo, "result": f"{type(e).__name__}: {str(e)[:200]}"})

    if ds is None:
        res["status"] = "FAIL"
        print(json.dumps(res, indent=2)); jdump("03_slimpajama", res); return

    labels = Counter()
    t0 = time.perf_counter()
    n = 0
    path = SAMPLES / "slimpajama_sample.jsonl"
    with open(path, "w") as out:
        for rec in ds:
            if n == 0:
                res["record_keys"] = sorted(rec.keys())
                res["example_meta"] = rec.get("meta")
            label = (rec.get("meta") or {}).get("redpajama_set_name", "<missing>")
            labels[label] += 1
            if labels[label] <= 20:
                out.write(json.dumps({"redpajama_set_name": label,
                                      "text": rec["text"][:5000]}) + "\n")
            n += 1
            if n >= N:
                break
    dt = time.perf_counter() - t0

    res.update(status="PASS" if res["repo"] == CANDIDATES[0][0] else "PARTIAL (fallback repo)",
               records_read=n, seconds=round(dt, 1), docs_per_sec=round(n / dt, 1),
               source_label_field="meta['redpajama_set_name']",
               has_source_label=all(k != "<missing>" for k in labels),
               labels_seen={k: v for k, v in labels.most_common()},
               sample_file=str(path), sample_bytes=path.stat().st_size)
    print(json.dumps(res, indent=2))
    jdump("03_slimpajama", res)
    finish()


if __name__ == "__main__":
    main()
