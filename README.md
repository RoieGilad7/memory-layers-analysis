# What do memory-layer values store?

Research code for a COMS E6998 (Algorithms in LLMs) final project. We train small
GPT-style language models in which one FFN block is replaced by a **product-key memory
(PKM)** or a **PEER** layer, log which memory slots every token reads, and ask what the
values in those slots store and how they are organized — compared against a kNN-LM store.

The project distinguishes **three addressing schemes** for a value store, which is the frame
the whole comparison hangs on:

| scheme | addressed by | examples |
|---|---|---|
| content-addressed, sparse top-k | a learned query against a learned key table | **PKM, PEER** (ours), `sparse-memory-lm`, DeepSeek engram |
| token-addressed | the input token id itself | MoLE (all experts read, router-blended) |
| neighbour-addressed | nearest neighbours in representation space | kNN-LM |

---

## Status

| step | what | where |
|---|---|---|
| **0 — confirm access** | every dataset, model, package and tool reachable and runnable on an Apple-Silicon Mac | [`reports/step0_access_report.md`](reports/step0_access_report.md) |
| **1 — training demo on fake data** | reusable training code, proven end to end, speed/memory measured to size the real runs | [`reports/step1_demo_report.md`](reports/step1_demo_report.md) |
| 2–5 | real data, training runs, read-log analysis | not started |

Both reports are self-contained and carry the numbers; start there.

---

## Layout

```
memlayers/              the package (reused unchanged for the real runs)
  model.py              nanoGPT-style decoder; each layer's FFN is dense | pkm | peer
  memory.py             PKM and PEER behind one interface: read log, slot masking, key freezing
  readlog.py            read-log writer/reader + slot-usage statistics (fraction used, KL from uniform)
  data_fake.py          (a) uniform random tokens  (b) repeated-chunk copy task
  train.py              AdamW, grad accumulation, cosine+warmup, param groups, resume, CSV logging
  devices.py            cuda > mps > cpu selection, sync, peak memory, RNG state
  configs/              8 YAML configs: T1/T2 x dense/pkm/peer, frozen-key twin, 262k slots

bench/                  benchmarks and their results
  benchmark.py          probe (micro-batch) / speed / learn / summarize
  model_budget.py       parameter vs. per-token-MAC accounting
  mps_determinism.py    repeat- and resume-reproducibility, per device and FFN type
  make_report_tables.py regenerates the step-1 report tables from results/
  run_demo.sh           every benchmark in order
  colab_benchmark.ipynb the same benchmark on a Colab T4
  results/*.json        committed: the evidence behind the step-1 report

step0_access/           one re-runnable script per step-0 access check
  check_01..13_*.py     environment, datasets, public models, our layers, faiss, MPS smoke test
  run_all.sh            runs them all (with a per-check watchdog)

logs/*.json             committed: the evidence behind the step-0 report
tools/bio_generator.py  bioS-style synthetic biographies + QA pairs
tests/                  59 pytest tests
reports/                the two step reports
```

Two result directories, both committed, because the reports cite them: `logs/*.json` for
step 0 and `bench/results/*.json` for step 1. The console transcripts next to them
(`logs/*.out`) are not committed.

---

## Setup

Apple Silicon (MPS) or CUDA; no CUDA-only code. Python 3.12.

```bash
# main environment
conda create -y -p .venv python=3.12
.venv/bin/pip install -r requirements.txt
```

`uv` was not available on the original machine and there was no system Python 3.11/3.12, so
`.venv` is a **conda prefix env**. It behaves like a venv (`.venv/bin/python`), so nothing
downstream cares; `python -m venv .venv` works just as well if you have a suitable Python.

<details>
<summary>Second environment, needed only for the MoLE check (step 0, B1)</summary>

MoLE's modeling code targets `transformers==4.38.2` and breaks on 5.x
(`LlamaConfig` no longer exposes `rope_theta`). `step0_access/run_all.sh` routes that one
check to a second env automatically:

```bash
conda create -y -p .venv-mole python=3.12
.venv-mole/bin/pip install -r requirements-mole.txt
```
</details>

Hugging Face access (step 0 only; step 1 needs no network):

```bash
hf auth login      # NOT `huggingface-cli`, which no longer exists in huggingface_hub >= 1.0
```

---

## Running things

```bash
# tests
.venv/bin/python -m pytest tests/ -q                 # 59 tests, CPU, ~10 s

# train one config
.venv/bin/python -m memlayers.train --config memlayers/configs/t1_pkm.yaml
.venv/bin/python -m memlayers.train --config memlayers/configs/t1_pkm.yaml \
    --set train.steps=50 train.micro_batch_size=8 runtime.out_dir=runs/scratch

# resume
.venv/bin/python -m memlayers.train --config memlayers/configs/t1_pkm.yaml \
    --resume runs/t1_pkm/ckpt.pt

# benchmarks (several hours; writes bench/results/*.json)
./bench/run_demo.sh                 # all phases
./bench/run_demo.sh probe speed     # selected phases
STEPS=50 LEARN_STEPS=100 ./bench/run_demo.sh    # quick smoke run

# parameter vs. FLOP budget for every config
.venv/bin/python bench/model_budget.py

# step-0 access checks
./step0_access/run_all.sh           # all; or `run_all.sh 05 06` for specific ones

# synthetic biographies (regenerates data_samples/, which is gitignored)
.venv/bin/python tools/bio_generator.py --n 1000 --rewordings 4 --qa-split \
    --out data_samples/bios_sample.jsonl --count-tokens
```

Long runs: use `caffeinate -i` on macOS to stop the machine sleeping, run in the background,
and poll `runs/<name>/log.csv` rather than blocking.

---

## Using the code

### A model with a memory layer

```python
from memlayers.model import GPT, GPTConfig

cfg = GPTConfig(
    n_layer=6, n_head=6, n_embd=384, block_size=512, vocab_size=50257,
    memory_layers=(3,), memory_kind="pkm",
    memory=dict(num_keys=256, topk=32, heads=4, dim_head=128, query_batchnorm=True),
)
model = GPT(cfg)
model.param_counts()   # {'embedding': ..., 'backbone': ..., 'memory_values': ..., ...}
```

`memory_kind="peer"` swaps in PEER; `ffn_types=["dense","dense","pkm",...]` sets the FFN of
every layer individually.

### Reading the read log

```python
model.set_read_logging(True)
logits, loss = model(idx, targets)
for layer, read in model.read_logs().items():
    read.indices   # int64 [batch, seq, heads, topk] -- which slots each token read
    read.weights   # float  [batch, seq, heads, topk] -- the gate weight each slot got
```

Both layers expose the same shapes. Read-out is done with forward hooks rather than by
patching the installed packages; a test rebuilds each layer's output from the logged indices
and weights alone and gets a bit-exact match, so the log is provably what the layer used.

### Switching slots off

```python
model.set_mask_slots({3: [17, 290, 4001]}, renormalize=False)
```

Masking happens **after** the top-k search: the search is untouched and the next-best slot
does *not* take a masked slot's place. Renormalizing the surviving weights is a flag, off by
default, so both variants can be reported.

### The random-key twin

```python
memory=dict(..., freeze_keys=True)    # keys stay at their random init, values still train
```

---

## Gotchas worth knowing before you touch this code

These are the findings that cost real time; both reports have the detail.

1. **`product-key-memory`'s query-BatchNorm path is broken** in 0.3.0 — the path Lample et al.
   2019 actually describe. `MaskedBatchNorm1D` hands a 3-D `[(b·p·h), t, d]` tensor to
   `nn.BatchNorm1d(dim_head)`, which treats the sequence dim as channels and raises.
   `memory.QueryBatchNorm` replaces it. This is our code, not the package's.
2. **`PEER-pytorch` defaults `non_competing_scores=True`**, which collapses the per-head
   top-k to **1** expert — 32× sparser than intended. Every PEER config here sets it to
   `False` explicitly, and the wrapper warns if you don't.
3. **MPS is not reproducible, and the non-determinism is specific to the memory layers.**
   Dense diverges ≤1e-6 in loss over 40 steps; PKM/PEER diverge 1e-4 to 1e-2. The cause is
   the scatter-add in the memory gather's backward, which uses atomics on *any* GPU backend —
   CUDA included, so a GPU will not fix it. The resume test therefore runs on CPU, where it is
   exact. Don't attribute a small loss difference between two memory runs to an intervention
   without a measured noise floor or multiple seeds.
4. **Parameter count does not set the time budget.** A memory layer is ~2% of forward FLOPs
   while holding 41–73% of the parameters, and the tied output projection is 62% of a T1
   model's compute. Size runs from measured tokens/sec (`bench/model_budget.py` prints both).
5. **PEER needs far more activation memory than PKM** — it materializes two `[b,n,h,k,d]`
   gathers (6.4 GB fp32 at T1 benchmark shapes) where PKM's fused `EmbeddingBag` materializes
   none. Watch this when sizing PEER on a 16 GB GPU.
6. **Read logging is free in time (1.00–1.02×) but not in space** — 0.512 GB per million
   tokens. A full 150M-token run would write ~77 GB, so log a slice (`read_log_steps`) or use
   the always-on `track_slot_usage` histogram instead.
7. **`zstandard` is required** to stream the Pile's `.jsonl.zst` shards; `datasets` does not
   pull it in. It's pinned in `requirements.txt`.
8. **SlimPajama is gone from the Hub** — both `MBZUAI-LLM/SlimPajama-627B-DC` and its
   `cerebras` upstream 404 even authenticated. The step-0 check falls back to
   `venketh/SlimPajama-62B`.

---

## Credits

Built on [nanoGPT](https://github.com/karpathy/nanoGPT) (model structure),
[product-key-memory](https://github.com/lucidrains/product-key-memory) and
[PEER-pytorch](https://github.com/lucidrains/PEER-pytorch) (the memory layers).

Papers the design follows: Lample et al., [*Large Memory Layers with Product
Keys*](https://arxiv.org/abs/1907.05242) (2019); He, [*Mixture of A Million
Experts*](https://arxiv.org/abs/2407.04153) (2024); Allen-Zhu & Li, [*Physics of Language
Models 3.1*](https://arxiv.org/abs/2309.14316) (2023) for the bioS synthetic-biography
design; Berges et al., [*Memory Layers at
Scale*](https://arxiv.org/abs/2412.09764) (2024).
