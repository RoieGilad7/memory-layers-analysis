"""A5 -- the corpora the public models were trained on: Wikipedia, FineWeb-Edu, Cosmopedia.

Streams each one and saves 200 documents to data_samples/. Each dataset is tried with a
couple of reasonable load signatures, because the right config name differs per repo.
"""
import json, time

from _common import SAMPLES, jdump, finish

N_SAVE = 200
CHAR_CAP = 5_000

TARGETS = [
    ("wikipedia", [
        ('load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True)',
         dict(path="wikimedia/wikipedia", name="20231101.en", split="train", streaming=True)),
    ]),
    ("fineweb_edu", [
        ('load_dataset("HuggingFaceFW/fineweb-edu", "sample-10BT", split="train", streaming=True)',
         dict(path="HuggingFaceFW/fineweb-edu", name="sample-10BT", split="train", streaming=True)),
        ('load_dataset("HuggingFaceFW/fineweb-edu", split="train", streaming=True)',
         dict(path="HuggingFaceFW/fineweb-edu", split="train", streaming=True)),
    ]),
    ("cosmopedia", [
        ('load_dataset("HuggingFaceTB/cosmopedia", "web_samples_v2", split="train", streaming=True)',
         dict(path="HuggingFaceTB/cosmopedia", name="web_samples_v2", split="train", streaming=True)),
        ('load_dataset("HuggingFaceTB/cosmopedia", split="train", streaming=True)',
         dict(path="HuggingFaceTB/cosmopedia", split="train", streaming=True)),
    ]),
]


def main():
    from datasets import load_dataset
    import tiktoken
    enc = tiktoken.get_encoding("gpt2")

    out_all = {}
    for name, attempts in TARGETS:
        r = {"attempts": []}
        ds = None
        for code, kw in attempts:
            try:
                ds = load_dataset(**kw)
                r["load_code"] = code
                break
            except Exception as e:
                r["attempts"].append({"code": code, "error": f"{type(e).__name__}: {str(e)[:300]}"})
        if ds is None:
            r["status"] = "FAIL"
            out_all[name] = r
            print(f"[{name}] FAIL"); continue

        path = SAMPLES / f"{name}_sample.jsonl"
        t0 = time.perf_counter()
        n = 0
        toks = 0
        with open(path, "w") as f:
            for rec in ds:
                if n == 0:
                    r["record_keys"] = sorted(rec.keys())
                text = rec.get("text") or rec.get("content") or ""
                toks += len(enc.encode(text, disallowed_special=()))
                f.write(json.dumps({"text": text[:CHAR_CAP]}) + "\n")
                n += 1
                if n >= N_SAVE:
                    break
        dt = time.perf_counter() - t0
        r.update(status="PASS", docs_saved=n, seconds=round(dt, 1),
                 docs_per_sec=round(n / dt, 1),
                 mean_tokens_per_doc=round(toks / max(n, 1), 1),
                 sample_file=str(path), sample_bytes=path.stat().st_size)
        print(f"[{name}] PASS {n} docs {r['docs_per_sec']} docs/s {r['mean_tokens_per_doc']} tok/doc")
        out_all[name] = r

    print(json.dumps(out_all, indent=2))
    jdump("04_pretrain_corpora", out_all)
    finish()


if __name__ == "__main__":
    main()
