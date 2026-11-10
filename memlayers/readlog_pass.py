"""The read-log pass: which memory slots a fixed set of tokens reads.

    python -m memlayers.readlog_pass run_dir=runs/pkm-s0 step=final
    python -m memlayers.readlog_pass run_dir=runs/pkm-s0 step=[init,final]
    python -m memlayers.readlog_pass run_dir=runs/pkm-s0 step=2000 force=true

`step`: final, init (step 0), an integer, or a list of those. The tokens are the
fixed `readlog_tokens` eval set (memlayers/eval/eval_sets.py): held-out LABEL-
half documents of the 5 training subjects, cut into per-document windows
exactly as heldout_quality cuts them, and biography fact prompts, each run one
per row as the prompt followed by its true value's tokens. Reads come from the
model's own read logging, with every slot mask off.

Writes `<run_dir>/readlogs/step_<6-digit step>/`:
    layer<L>_indices.bin  [n_tokens, heads, topk] uint16 (<= 65,536 slots) or uint32
    layer<L>_weights.bin  same shape, float16: the post-softmax gate weights
    tokens.parquet        one row per token, in file order
    manifest.json         checkpoint, model, shapes, dtypes, counts, hashes, wall time
Read it with memlayers.readlog.ReadLog (or EvalContext.readlog()).

Checked before anything is written: a dense run is refused; the readlog_tokens
file must match the committed eval-set manifest and the run's
`eval.readlog.tokens_per_subject`; the expected size is printed and the pass
refuses to start with less than twice that free.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

__all__ = ["readlog_pass", "ReadlogRefused", "readlog_dir", "plan_tokens", "main"]


class ReadlogRefused(RuntimeError):
    pass


def readlog_dir(run_dir, step: int) -> Path:
    return Path(run_dir) / "readlogs" / f"step_{int(step):06d}"


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Plan:
    windows: List[Tuple[str, str, int, np.ndarray]]  # (doc_id, subject, start pos, x)
    bio: List[Tuple[dict, List[int], int]]  # (fact row, token ids, n prompt tokens)
    n_heldout: int
    n_bio: int

    @property
    def n_tokens(self) -> int:
        return self.n_heldout + self.n_bio


def plan_tokens(dcfg, rl_set: Dict[str, Any], block_size: int) -> Plan:
    """The token stream, in file order: held-out windows (per subject, grouped
    by window length so equal lengths batch), then the bio prompts."""
    from data import pack
    from data.common import get_encoder, read_jsonl
    from data.loader import iter_document_windows

    half = rl_set.get("heldout_half", "label")
    tokens = np.memmap(
        Path(dcfg.heldout_tokens_dir) / f"{half}.bin", dtype=np.uint16, mode="r"
    )
    index = pack.read_index(Path(dcfg.heldout_tokens_dir) / f"{half}.idx.parquet")
    where = {
        d: (s, int(a), int(n))
        for d, s, a, n in zip(
            index["doc_id"], index["subject"], index["start"], index["length"]
        )
    }
    windows = []
    for slug, doc_ids in rl_set["doc_ids"].items():
        buckets: Dict[int, list] = {}
        for d in doc_ids:
            subject, start, length = where[d]
            pos = 0
            for x, _ in iter_document_windows(tokens, start, length, block_size):
                buckets.setdefault(len(x), []).append((d, subject, pos, x))
                pos += len(x)
        for L in sorted(buckets, reverse=True):
            windows += buckets[L]
    want = set(rl_set["fact_ids"])
    rows = [
        r
        for r in read_jsonl(Path(dcfg.bios_dir) / "facts.jsonl")
        if r["fact_id"] in want
    ]
    order = {f: i for i, f in enumerate(rl_set["fact_ids"])}
    rows.sort(key=lambda r: order[r["fact_id"]])
    if len(rows) != len(want):
        raise ReadlogRefused(
            f"readlog_tokens names {len(want)} facts; facts.jsonl has {len(rows)}"
        )
    enc = get_encoder(dcfg.tokenizer_name, dcfg.vocab_size)
    prompts = enc.encode_ordinary_batch([r["prompt"] for r in rows], num_threads=8)
    bio = []
    for r, p in zip(rows, prompts):
        value = list(
            r.get("value_token_ids") or enc.encode_ordinary(" " + r["true_value"])
        )
        seq = list(p) + value
        if len(seq) > block_size:
            raise ReadlogRefused(
                f"{r['fact_id']}: {len(seq)} tokens > block_size {block_size}"
            )
        bio.append((r, seq, len(p)))
    return Plan(
        windows=windows,
        bio=bio,
        n_heldout=sum(len(w[3]) for w in windows),
        n_bio=sum(len(s) for _, s, _ in bio),
    )


def _parse_steps(v: str) -> List[str]:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def readlog_pass(
    run_dir,
    steps: Sequence[str] = ("final",),
    force: bool = False,
    device: Optional[str] = None,
) -> List[Path]:
    from .config import model_kwargs
    from .devices import empty_cache, pick_device
    from .eval.eval_sets import (
        READLOG_SET,
        EvalSetMismatch,
        load_readlog_tokens,
        verify,
    )
    from .evaluate import _model_for, find_checkpoints, load_run_config
    from .model import GPTConfig
    from .readlog import ReadLogWriter, index_dtype
    from .train import load_bundle_config

    run_dir = Path(run_dir)
    cfg = load_run_config(run_dir)
    gcfg = GPTConfig(**model_kwargs(cfg.model))
    mem_layers = [i for i, k in enumerate(gcfg.ffn_types) if k != "dense"]
    if not mem_layers:
        raise ReadlogRefused(
            f"{run_dir.name} is a dense run: it has no memory layer, so there are no "
            "slot reads to log."
        )
    if cfg.data.source != "real":
        raise ReadlogRefused(
            f"{run_dir.name} trained on data.source={cfg.data.source}; no read-log tokens"
        )
    dcfg = load_bundle_config(cfg.data)
    try:
        rl_hash = verify(dcfg, (READLOG_SET,))[READLOG_SET]
    except EvalSetMismatch as e:
        raise ReadlogRefused(str(e)) from None
    rl_set = load_readlog_tokens(dcfg)
    want = int(cfg.eval.readlog.tokens_per_subject)
    if int(rl_set["tokens_per_subject"]) != want:
        raise ReadlogRefused(
            f"readlog_tokens on disk was built with {rl_set['tokens_per_subject']:,} tokens "
            f"per subject but this run says eval.readlog.tokens_per_subject={want:,}. "
            f"Rebuild with `python -m memlayers.eval.eval_sets --version {dcfg.version} "
            f"--readlog-tokens-per-subject {want} --replace-manifest` (this changes "
            "its hash, by design; commit the new manifest)."
        )
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    ckpts: List[Tuple[int, Path]] = []
    for s in steps:
        ckpts += find_checkpoints(run_dir, str(s))
    ckpts = sorted(dict(ckpts).items())

    # every read log in one run dir is on ONE readlog_tokens set (meta.json
    # records that one hash, compare relies on it). Each step's own manifest
    # says which set it used; a step this pass does not rewrite that is on
    # another set blocks the pass, even with force=true.
    rewriting = {int(s) for s, _ in ckpts}
    stale = []
    for d in (
        sorted((run_dir / "readlogs").glob("step_*"))
        if (run_dir / "readlogs").exists()
        else []
    ):
        mf = d / "manifest.json"
        if not mf.exists() or int(d.name.split("_")[1]) in rewriting:
            continue
        h = (json.loads(mf.read_text()).get("eval_set") or {}).get("sha256")
        if h != rl_hash:
            stale.append(f"{d.name} ({str(h)[:16]})")
    if stale:
        raise ReadlogRefused(
            f"{run_dir.name} has read logs on another readlog_tokens set than the current "
            f"{rl_hash[:16]}: {', '.join(stale)}. One run dir must not mix two sets: "
            "re-run those steps too (name them in step=[...] with force=true) or delete them."
        )
    for s, _ in ckpts:
        if readlog_dir(run_dir, s).exists() and not force:
            raise ReadlogRefused(
                f"{readlog_dir(run_dir, s)} exists; pass force=true to rewrite it"
            )

    plan = plan_tokens(dcfg, rl_set, gcfg.block_size)
    per_token = 0
    shapes = {}
    for i in mem_layers:
        m = gcfg.memory
        heads = int(m.get("heads", 4))
        topk = int(m.get("topk", 32))
        n_slots = (
            int(m["num_keys"]) ** 2
            if gcfg.ffn_types[i] == "pkm"
            else int(m.get("num_experts", 65536))
        )
        per_token += heads * topk * (index_dtype(n_slots).itemsize + 2)
        shapes[i] = (heads, topk, n_slots)
    expected = per_token * plan.n_tokens
    free = shutil.disk_usage(run_dir).free
    print(
        f"[readlog] {run_dir.name}: {plan.n_tokens:,} tokens ({plan.n_heldout:,} held-out, "
        f"{plan.n_bio:,} bio) x {per_token} B = {expected / 1e9:.2f} GB per checkpoint, "
        f"{len(ckpts)} checkpoint(s); {free / 1e9:.1f} GB free",
        flush=True,
    )
    if free < 2 * expected * len(ckpts):
        raise ReadlogRefused(
            f"only {free / 1e9:.1f} GB free; the read log needs {expected * len(ckpts) / 1e9:.2f} GB "
            "and the pass wants twice that free before it starts"
        )

    dev = pick_device(device or cfg.runtime.device)
    batch = int(cfg.eval.readlog.heldout_batch)
    out_dirs = []
    for step, ck in ckpts:
        t0 = time.perf_counter()
        model, ck_step, tokens_seen = _model_for(cfg, ck, dev)
        model.eval()
        model.set_mask_slots(None)
        model.set_read_logging(True)
        mems = model.memory_layers
        final = readlog_dir(run_dir, ck_step)
        tmp = final.with_name(f".{final.name}.tmp-{os.getpid()}")
        if tmp.exists():
            shutil.rmtree(tmp)
        writer = ReadLogWriter(
            tmp,
            n_slots={i: m.n_slots for i, m in mems.items()},
            heads={i: m.n_heads for i, m in mems.items()},
            topk={i: m.topk for i, m in mems.items()},
            store_weights=True,
            index_file="layer{layer}_indices.bin",
            weight_file="layer{layer}_weights.bin",
        )
        cols: Dict[str, list] = {
            k: []
            for k in (
                "token_id",
                "segment",
                "doc_id",
                "subject",
                "position",
                "person_id",
                "tier",
                "attribute",
                "fact_id",
                "role",
                "template_id",
                "is_answer_position",
                "is_value_token",
            )
        }
        per_subject: Dict[str, int] = {}

        with torch.no_grad():
            i = 0
            W = plan.windows
            while i < len(W):
                L = len(W[i][3])
                j = i
                while j < len(W) and j - i < batch and len(W[j][3]) == L:
                    j += 1
                chunk = W[i:j]
                x = torch.from_numpy(
                    np.stack([c[3] for c in chunk]).astype(np.int64)
                ).to(dev)
                model(x)
                writer.append(ck_step, model.read_logs())
                for d, subject, pos, xx in chunk:
                    n = len(xx)
                    cols["token_id"].append(xx.astype(np.int32))
                    cols["position"].append(np.arange(pos, pos + n, dtype=np.int32))
                    cols["template_id"].append(np.full(n, -1, dtype=np.int32))
                    cols["is_answer_position"].append(np.zeros(n, dtype=bool))
                    cols["is_value_token"].append(np.zeros(n, dtype=bool))
                    for k, v in (
                        ("segment", "heldout_label"),
                        ("doc_id", d),
                        ("subject", subject),
                        ("person_id", None),
                        ("tier", None),
                        ("attribute", None),
                        ("fact_id", None),
                        ("role", None),
                    ):
                        cols[k].append(np.full(n, v, dtype=object))
                    per_subject[subject] = per_subject.get(subject, 0) + n
                i = j
            per_tier: Dict[str, int] = {}
            for r, seq, n_prompt in plan.bio:
                x = torch.tensor([seq], dtype=torch.long, device=dev)
                model(x)
                writer.append(ck_step, model.read_logs())
                n = len(seq)
                cols["token_id"].append(np.asarray(seq, dtype=np.int32))
                cols["position"].append(np.arange(n, dtype=np.int32))
                cols["template_id"].append(
                    np.full(n, int(r["template_id"]), dtype=np.int32)
                )
                ans = np.zeros(n, dtype=bool)
                ans[n_prompt - 1] = True  # predicts the value's first token
                val = np.zeros(n, dtype=bool)
                val[n_prompt:] = True
                cols["is_answer_position"].append(ans)
                cols["is_value_token"].append(val)
                for k, v in (
                    ("segment", "bio"),
                    ("doc_id", r.get("doc_id")),
                    ("subject", "bio"),
                    ("person_id", r["person_id"]),
                    ("tier", r["tier"]),
                    ("attribute", r["attribute"]),
                    ("fact_id", r["fact_id"]),
                    ("role", r["role"]),
                ):
                    cols[k].append(np.full(n, v, dtype=object))
                per_tier[r["tier"]] = per_tier.get(r["tier"], 0) + n
        model.set_read_logging(False)

        import pyarrow as pa
        import pyarrow.parquet as pq

        arrays = {}
        for k, parts in cols.items():
            a = np.concatenate(parts) if parts else np.empty(0)
            if a.dtype == object:
                arr = pa.array(a.tolist(), pa.string())
                if k in ("segment", "subject", "tier", "attribute", "role"):
                    arr = arr.dictionary_encode()
                arrays[k] = arr
            else:
                arrays[k] = pa.array(a)
        n_tokens = len(arrays["token_id"])
        assert n_tokens == plan.n_tokens == writer.tokens_logged, (
            n_tokens,
            plan.n_tokens,
            writer.tokens_logged,
        )
        pq.write_table(pa.table(arrays), tmp / "tokens.parquet", compression="zstd")
        for fh in writer._files.values():
            fh.close()
        writer._files.clear()
        files = {
            p.name: {"bytes": p.stat().st_size, "sha256": _sha(p)}
            for p in sorted(tmp.iterdir())
        }
        wall = time.perf_counter() - t0
        writer.close(
            extra={
                "format": "memlayers.readlog/1",
                "step": int(ck_step),
                "tokens_seen": int(tokens_seen),
                "checkpoint": (
                    str(ck.relative_to(run_dir))
                    if ck.is_relative_to(run_dir)
                    else str(ck)
                ),
                "checkpoint_sha256": _sha(ck),
                "run_id": meta.get("run_id", run_dir.name),
                "model": model_kwargs(cfg.model),
                "layers": [int(i) for i in sorted(mems)],
                "n_tokens": int(n_tokens),
                "shape": {
                    str(i): [int(n_tokens), m.n_heads, m.topk] for i, m in mems.items()
                },
                "n_tokens_by_segment": {
                    "heldout_label": plan.n_heldout,
                    "bio": plan.n_bio,
                },
                "n_tokens_by_subject": dict(sorted(per_subject.items())),
                "n_tokens_by_bio_tier": dict(sorted(per_tier.items())),
                "n_documents": len({w[0] for w in plan.windows}),
                "n_bio_prompts": len(plan.bio),
                "eval_set": {
                    "name": READLOG_SET,
                    "sha256": rl_hash,
                    "tokens_per_subject": int(rl_set["tokens_per_subject"]),
                },
                "files": files,
                "wall_seconds": round(wall, 2),
                "device": str(dev),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            records=False,
        )
        if final.exists():
            shutil.rmtree(final)
        os.replace(tmp, final)
        size = sum(f["bytes"] for f in files.values())
        print(
            f"[readlog] step {ck_step}: {n_tokens:,} tokens, {size / 1e9:.3f} GB, "
            f"{wall:.1f} s -> {final}",
            flush=True,
        )
        out_dirs.append(final)
        del model
        empty_cache(dev)

    meta.setdefault("eval_sets", {})
    meta["eval_sets"] = {**(meta.get("eval_sets") or {}), READLOG_SET: rl_hash}
    meta_path.write_text(json.dumps(meta, indent=2, default=str))
    return out_dirs


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    args = {}
    for a in argv:
        if "=" not in a:
            raise SystemExit(f"argument {a!r} must look like key=value")
        k, v = a.split("=", 1)
        args[k] = v
    bad = set(args) - {"run_dir", "step", "force", "device"}
    if bad or "run_dir" not in args:
        raise SystemExit(
            "usage: python -m memlayers.readlog_pass run_dir=... [step=final] [force=true] [device=...]"
        )
    try:
        readlog_pass(
            args["run_dir"],
            _parse_steps(args.get("step", "final")),
            force=args.get("force", "false").lower() in ("1", "true", "yes"),
            device=args.get("device"),
        )
    except ReadlogRefused as e:
        print(f"[readlog] REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
