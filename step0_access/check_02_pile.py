"""A1/A2/A3 -- stream monology/pile-uncopyrighted, count docs+tokens per subject.

Streaming only: nothing is written to the HF cache except the dataset script/metadata.
Saves at most SAVE_PER_SUBJECT documents per subject to data_samples/pile_sample.jsonl.
"""
import argparse, json, time
from collections import Counter, defaultdict

from _common import SAMPLES, jdump, finish

REPO = "monology/pile-uncopyrighted"
SAVE_PER_SUBJECT = 200
SAVE_CHARS_CAP = 5_000  # truncate very long docs in the sample file so it stays a few MB


def main(n_docs):
    import tiktoken
    from datasets import load_dataset

    enc = tiktoken.get_encoding("gpt2")

    t0 = time.perf_counter()
    ds = load_dataset(REPO, split="train", streaming=True)
    t_open = time.perf_counter() - t0

    docs = Counter()
    toks = Counter()
    chars = Counter()
    saved = defaultdict(int)
    out = open(SAMPLES / "pile_sample.jsonl", "w")

    t0 = time.perf_counter()
    n = 0
    for rec in ds:
        subj = (rec.get("meta") or {}).get("pile_set_name", "<missing>")
        text = rec["text"]
        docs[subj] += 1
        chars[subj] += len(text)
        # tiktoken on the full 50k docs is the dominant cost; it is also the number we need
        toks[subj] += len(enc.encode(text, disallowed_special=()))
        if saved[subj] < SAVE_PER_SUBJECT:
            out.write(json.dumps({"pile_set_name": subj, "text": text[:SAVE_CHARS_CAP]}) + "\n")
            saved[subj] += 1
        n += 1
        if n % 5000 == 0:
            print(f"  {n:7d} docs  {n/(time.perf_counter()-t0):7.1f} docs/s  "
                  f"{sum(toks.values())/1e6:7.2f}M tok  {len(docs)} subjects", flush=True)
        if n >= n_docs:
            break
    dt = time.perf_counter() - t0
    out.close()

    total_tok = sum(toks.values())
    per_subject = {
        s: {
            "docs": docs[s],
            "tokens_gpt2": toks[s],
            "chars": chars[s],
            "pct_docs": round(100 * docs[s] / n, 3),
            "pct_tokens": round(100 * toks[s] / total_tok, 3),
            "mean_tokens_per_doc": round(toks[s] / docs[s], 1),
            "chars_per_token": round(chars[s] / toks[s], 3) if toks[s] else None,
            "saved_to_sample": saved[s],
        }
        for s in sorted(docs, key=lambda k: -toks[k])
    }

    res = {
        "repo": REPO,
        "load_code": 'load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)',
        "open_seconds": round(t_open, 2),
        "docs_read": n,
        "seconds": round(dt, 1),
        "docs_per_sec": round(n / dt, 1),
        "tokens_per_sec": round(total_tok / dt, 1),
        "total_tokens_gpt2": total_tok,
        "mean_tokens_per_doc": round(total_tok / n, 1),
        "n_subjects": len(docs),
        "per_subject": per_subject,
        "sample_file": str(SAMPLES / "pile_sample.jsonl"),
        "sample_bytes": (SAMPLES / "pile_sample.jsonl").stat().st_size,
    }

    # A3 disk estimate: tokenized corpora stored as uint16 (GPT-2 vocab 50257 < 65536)
    B = 2
    res["a3_disk"] = {
        "bytes_per_token_uint16": B,
        "note": "GPT-2 vocab 50257 fits in uint16; uint32 would be 4 B/token",
        "train_150M_tokens_GB": round(150e6 * B / 1e9, 3),
        "train_0.5B_tokens_GB": round(0.5e9 * B / 1e9, 3),
        "heldout_1M_per_subject_GB_per_subject": round(1e6 * B / 1e9, 4),
        "heldout_10M_per_subject_GB_per_subject": round(10e6 * B / 1e9, 4),
    }
    print(json.dumps(res, indent=2))
    jdump("02_pile", res)
    finish()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50_000)
    main(ap.parse_args().n)
