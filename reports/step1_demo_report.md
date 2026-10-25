# Step 1 — Training Demo on Fake Data

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-10-25
**Scope:** build the reusable training code, prove it works end to end, measure speed and memory so the real runs can be sized. **No real data in this step.**

Everything here comes from code in this repo — `memlayers/` (package), `bench/` (benchmarks),
`tests/` (59 tests). Raw benchmark output is in `bench/results/*.json`, and every figure in
the tables is read out of those files by `bench/make_report_tables.py` rather than retyped.
Reproduce with `./bench/run_demo.sh`.

**Headline:** all eight configs train on MPS at micro-batch 32 with no CPU fallback; read
logging is effectively free (1.00–1.02×); both memory models learn the synthetic copy task
(loss 10.92 → ~4.1 against a 10.825 random-token level); tier 1 costs **~37 h for 12 runs**
on this Mac and is viable, while tier 2 at 0.5B tokens costs **~174–194 h** and must go to
GPUs. Two findings need action before step 4: a broken BatchNorm path in
`product-key-memory` (§5.1) and **MPS non-determinism localized to the memory layers**
(§5.2).

---

## 1. Environment

| | |
|---|---|
| Chip | **Apple M5 Pro**, 18 cores |
| RAM | 68.7 GB unified (64 GiB) |
| macOS | 26.6.2 (build 25G83) |
| Python | 3.12.14 (conda env at `.venv`) |
| PyTorch | **2.14.1** |
| `torch.backends.mps.is_available()` | **True** |
| `torch.cuda.is_available()` | False |
| Device used for every benchmark | **`mps`** |
| `PYTORCH_ENABLE_MPS_FALLBACK` | **unset, deliberately** (§5.3) |

New packages: `PyYAML==6.0.3` (configs) and `pytest==9.1.1` (tests), both added to
`requirements.txt`. Nothing else was needed — `product-key-memory`, `PEER-pytorch`, `torch`,
`numpy` and `tiktoken` were pinned in step 0.

All numbers are **fp32**. No autocast/AMP anywhere, on purpose: it keeps the Mac baseline
clean and comparable. Enabling fp16 AMP is the first thing to try on a T4 (§5.8).

---

## 2. Per-config results: parameters, micro-batch, speed, memory

### 2.1 Micro-batch probe

Each rung tried in its own subprocess, so a failed attempt cannot poison the next.

| config | 4 | 8 | 16 | 32 | largest | peak mem at largest |
|---|:--:|:--:|:--:|:--:|---:|---:|
| `t1_dense` | ok | ok | ok | ok | 32 | 22.4 GB |
| `t1_pkm` | ok | ok | ok | ok | 32 | 23.5 GB |
| `t1_pkm_frozen` | ok | ok | ok | ok | 32 | 23.5 GB |
| `t1_peer` | ok | ok | ok | ok | 32 | 33.2 GB |
| `t2_dense` | ok | ok | ok | ok | 32 | 25.7 GB |
| `t2_pkm` | ok | ok | ok | ok | 32 | 28.5 GB |
| `t2_pkm_262k` | ok | ok | ok | ok | 32 | 29.6 GB |
| `t2_peer` | ok | ok | ok | ok | 32 | 43.4 GB |

**Every config reached 32, the top rung the roadmap specified** — so 32 is the ladder's
ceiling, not the machine's limit. Nothing needed gradient accumulation to fit, so
`grad_accum_steps=1` everywhere and the effective batch is 32 × 512 = **16,384 tokens/step**.
T2-peer at 43.4 GB of 64 GiB is the one approaching the limit.

### 2.2 Speed and memory (300 steps on fake data (a), first 30 discarded)

| config | embedding | backbone | memory (keys+values) | total | micro-batch | ms/step mean | ms/step p90 | tokens/sec | peak mem |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `t1_dense` | 19.50M | 10.65M | 0.00M | 30.14M | 32 | 903 | 920 | **18,135** | 22.4 GB |
| `t1_pkm` | 19.50M | 9.47M | 25.43M | 54.78M | 32 | 1219 | 1232 | **13,440** | 23.5 GB |
| `t1_pkm_frozen` | 19.50M | 9.47M | 25.43M | 54.78M | 32 | 1213 | 1216 | **13,506** | 23.5 GB |
| `t1_peer` | 19.50M | 9.47M | 50.59M | 79.95M | 32 | 1201 | 1210 | **13,642** | 33.2 GB |
| `t2_dense` | 25.99M | 25.22M | 0.00M | 51.21M | 32 | 1342 | 1364 | **12,204** | 25.7 GB |
| `t2_pkm` | 25.99M | 23.12M | 33.82M | 83.46M | 32 | 1759 | 1766 | **9,313** | 28.5 GB |
| `t2_pkm_262k` | 25.99M | 23.12M | 134.74M | 184.38M | 32 | 1908 | 1921 | **8,587** | 29.6 GB |
| `t2_peer` | 25.99M | 23.12M | 67.37M | 117.01M | 32 | 1709 | 1718 | **9,587** | 43.4 GB |

(`memory` here is keys + value tables only; the memory layers' own query projections and
norms are a further ~0.4–0.5M, counted in the totals. p90 sits within 2% of the mean
everywhere, so step times are stable — no thermal throttling or GC spikes over 270 steps.)

Four things to read out of this:

- **A memory layer costs ~30–35% of wall clock while adding ~2% of FLOPs.** T1 goes 18,135 →
  13,440 tok/s (1.35×) adding PKM; T2 goes 12,204 → 9,313 (1.31×). Since the arithmetic is
  nearly unchanged (§2.3), the cost is gather/scatter bandwidth, not compute. Budget for it
  by measurement, never by FLOPs.
- **Freezing keys is free.** `t1_pkm_frozen` 13,506 vs `t1_pkm` 13,440 tok/s — within noise.
  The random-key twin costs nothing extra to run.
- **Quadrupling slots is nearly free in time.** 65,536 → 262,144 slots costs 8%
  (9,313 → 8,587 tok/s) and 1.1 GB. Slot-count sweeps are cheap; see §5.6.
- **PEER needs far more activation memory than PKM**, 33.2 vs 23.5 GB at T1 and 43.4 vs
  28.5 GB at T2, despite similar speed. Cause in §5.5.

### 2.3 Parameters vs. compute, and what a "tier size" should mean

The compute plan sizes tier 1 at **about 20M parameters**. These configs are 30.1M
(T1-dense), 54.8M (T1-pkm), 80.0M (T1-peer). That spread is misleading, because parameter
count and compute are decoupled here. From `bench/model_budget.py`:

| config | total params | MAC/token | attn | dense MLP | memory | lm_head | lm_head share | memory share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `t1_dense` | 30.14M | 31.10M | 4.72M | 7.08M | 0.00M | 19.30M | **62.1%** | 0.0% |
| `t1_pkm` | 54.78M | 30.62M | 4.72M | 5.90M | 0.70M | 19.30M | **63.0%** | **2.3%** |
| `t1_peer` | 79.95M | 30.67M | 4.72M | 5.90M | 0.75M | 19.30M | **62.9%** | **2.5%** |
| `t2_dense` | 51.21M | 52.99M | 10.49M | 16.78M | 0.00M | 25.73M | 48.6% | 0.0% |
| `t2_pkm` | 83.46M | 51.75M | 10.49M | 14.68M | 0.85M | 25.73M | 49.7% | 1.6% |
| `t2_pkm_262k` | 184.38M | 52.01M | 10.49M | 14.68M | 1.11M | 25.73M | 49.5% | 2.1% |
| `t2_peer` | 117.01M | 51.81M | 10.49M | 14.68M | 0.92M | 25.73M | 49.7% | 1.8% |

(One forward pass; a training step is ~3×.)

1. **The memory is nearly free in compute.** T1-pkm's memory is 47% of its parameters and
   **2.3%** of forward MACs. T2-pkm-262k's is 73% of parameters and 2.1% of MACs. Parameter
   count is therefore a poor proxy for training time, and "a 20M-parameter model" does not
   pin down a time budget at all.
2. **At tier-1 width the output projection dominates.** `d_model × 50257 = 19.3M` MAC/token
   is **62%** of T1's forward compute — more than attention and every MLP combined. At T2
   width it falls to ~49%, so the wider model is more compute-efficient per parameter.

**Recommendation.** Tier sizes should refer to **non-embedding, non-memory backbone
parameters** — 10.65M for T1, 25.22M for T2 — because that is the only one of the three
counts that is comparable across dense/PKM/PEER *and* tracks the compute that scales with
model size. Report it next to the memory count, as the tables above do. But the tier **time
budget must come from measured tokens/sec**, not from any parameter count: the three T1
variants differ 2.7× in parameters and under 1% in FLOPs, and what separates them in wall
clock is gather bandwidth, which only measurement captures.

**Does T1 need to shrink? No.** 12 runs cost ~37 h (§4), which fits. And shrinking would
not help much: 62% of T1's compute is the vocab projection, so the usual levers hit only the
other 38% — halving `n_layer` from 6 to 3 cuts MAC/token by just 19%. If tier 1 ever must be
faster, the effective levers in order are **(1) shorter context** (512 → 256 halves tokens
per step, and the bioS-style data in later phases needs nowhere near 512 tokens),
**(2) a smaller vocabulary** (a 16k BPE would cut the dominant 62% by ~3×, at the cost of
comparability with GPT-2-tokenized public work), **(3) fewer tokens** (150M → 100M, linear
and the easiest dial). Cutting the memory to save time would be the one pure loss: 2% of
compute and the entire subject of the project.

### 2.4 Read-logging cost

| config | ms/step off | ms/step on | slowdown | read-log size | GB per 1M tokens | reads/token |
|---|---:|---:|---:|---:|---:|---:|
| `t1_pkm` | 1219 | 1224 | **1.00×** | 512 B/token | 0.512 GB | 128 |
| `t1_pkm_frozen` | 1213 | 1222 | **1.01×** | 512 B/token | 0.512 GB | 128 |
| `t1_peer` | 1201 | 1200 | **1.00×** | 512 B/token | 0.512 GB | 128 |
| `t2_pkm` | 1759 | 1758 | **1.00×** | 512 B/token | 0.512 GB | 128 |
| `t2_pkm_262k` | 1908 | 1917 | **1.00×** | 768 B/token | 0.768 GB | 128 |
| `t2_peer` | 1709 | 1741 | **1.02×** | 512 B/token | 0.512 GB | 128 |

**Read logging is effectively free in time** — worst case 1.02×. At 16,384 tokens/step the
~8 MB/step of host copies and SSD writes hide behind a 1.2–1.9 s GPU step. Measured
517 B/token against 512 predicted, so the accounting is right.

**Size is the real constraint, not speed.** 0.512 GB per million tokens means a full 150M-token
tier-1 run logged end to end would produce **~77 GB**, and a 0.5B-token tier-2 run **~256 GB**
(384 GB at 262k slots, where indices need uint32 instead of uint16). So: **log a slice, not
the whole run.** `train.py` already supports this via `read_log_steps`, and the cheap
always-on alternative is `track_slot_usage`, which keeps only an int64 histogram per layer
and is what the §3 statistics use.

If the full log is ever needed at scale, dropping the weights (`read_log_weights: false`)
halves it to 256 B/token, and the weights are recomputable from the indices plus a saved
checkpoint.

---

## 3. Learning check on fake data (b)

1000 steps on the repeated-chunk copy task (`chunk_len=16`, 512-token context, micro-batch 32
= 16.4M tokens). Unpredictable content is confined to the first chunk, so the floor is
`(16/512) · ln(50257) = 0.338` nats, against a random-token level of `ln(50257) = 10.825`.

| config | steps | tokens | loss start | loss end (mean last 25) | min | random level | task floor | clearly below random? |
|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| `t1_pkm` | 1000 | 16.4M | 10.921 | **4.082** | 3.963 | 10.825 | 0.338 | **yes** |
| `t1_peer` | 1000 | 16.4M | 10.916 | **4.218** | 4.057 | 10.825 | 0.338 | **yes** |

Loss curve (every 125 steps):

| step | 25 | 150 | 275 | 400 | 525 | 650 | 775 | 900 | 1000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `t1_pkm` | 10.61 | 10.06 | 7.73 | 5.75 | 4.97 | 4.44 | 4.28 | 4.04 | **4.03** |
| `t1_peer` | 10.59 | 10.06 | 7.71 | 5.87 | 5.14 | 4.60 | 4.45 | 4.20 | **4.16** |

Both drop **~6.8 nats below the random-token level**, so the stack genuinely learns:
forward, backward, the memory gather, the per-group learning rates and the schedule all work
end to end. The shape is the expected one for an induction task — a plateau near
`ln(vocab)` for ~150 steps while the model learns the unigram distribution, then a sharp
drop from step ~200 as the copy mechanism forms.

**These runs are not converged**, and the report should not imply otherwise: the curve is
still descending at step 1000 and the loss is an order of magnitude above the 0.338 floor.
1000 steps was specified to prove the stack learns, and it does. Expect the gap to close
with more steps; nothing here is evidence about PKM vs PEER quality, and the 4.08 vs 4.22
difference is well within what a single seed can tell us (see §5.2 on run-to-run variance).

### Memory usage statistics

| config | slots | slots read ≥ once | KL(usage ‖ uniform) | max possible KL | normalized KL | top-1 slot share | top-1% share | weighted KL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `t1_pkm` | 65,536 | **65,536 (100.00%)** | **2.167 nats** | 11.090 | 0.195 | 0.21% | **52.7%** | 2.069 nats |
| `t1_peer` | 65,536 | **65,536 (100.00%)** | **2.374 nats** | 11.090 | 0.214 | 0.23% | **56.0%** | 2.265 nats |

KL is `log n − H(p)` over the normalized read histogram, as in Lample et al. 2019 §4: 0 means
every slot read equally often, `ln(65536) = 11.090` means one slot absorbs every read. The
weighted variant uses summed gate weights instead of raw counts.

**Read the coverage number with care — at this scale it is nearly uninformative.** 16.4M
tokens × 128 reads = 2.1 billion reads over 65,536 slots is ~32,000 reads per slot on
average, so 100% coverage would happen even for a badly skewed distribution. The informative
statistics are the KL (2.17/2.37 of a possible 11.09, i.e. **~20% of the way to fully
collapsed**) and the top-1% share: **the hottest 655 slots absorb 53–56% of all reads.** So
usage is broadly spread but materially imbalanced — exactly the regime where "which slots
does this domain use" is a meaningful question, and a useful baseline to compare the real-data
runs against. Note this is on a synthetic copy task whose true content is one 16-token chunk,
so the imbalance is not yet telling us anything about language.

---

## 4. Extrapolated wall clock

Hours = training tokens / measured tokens-per-sec. Tier 1 = 150M tokens, tier 2 = 0.5B
tokens, **12 runs per tier** (PKM ×3, PEER ×3, 2 random-key twins, 1–2 dense, 3 Phase 2).
The T4 column is left for the Colab run (`bench/colab_benchmark.ipynb`).

| config | tokens/sec (Mac) | hours/run (Mac) | hours for 12 runs (Mac) | tokens/sec (T4) | hours/run (T4) | 12 runs (T4) |
|---|---:|---:|---:|---:|---:|---:|
| `t1_dense` | 18,135 | 2.30 | 27.6 | _TBD_ | _TBD_ | _TBD_ |
| `t1_pkm` | 13,440 | 3.10 | **37.2** | _TBD_ | _TBD_ | _TBD_ |
| `t1_pkm_frozen` | 13,506 | 3.08 | 37.0 | _TBD_ | _TBD_ | _TBD_ |
| `t1_peer` | 13,642 | 3.05 | 36.7 | _TBD_ | _TBD_ | _TBD_ |
| `t2_dense` | 12,204 | 11.38 | 136.6 | _TBD_ | _TBD_ | _TBD_ |
| `t2_pkm` | 9,313 | 14.91 | **179.0** | _TBD_ | _TBD_ | _TBD_ |
| `t2_pkm_262k` | 8,587 | 16.17 | 194.1 | _TBD_ | _TBD_ | _TBD_ |
| `t2_peer` | 9,587 | 14.49 | 173.8 | _TBD_ | _TBD_ | _TBD_ |

**Tier 1 on the Mac is viable: ~37 h for all 12 runs**, about 1.6 days of continuous compute,
or three overnight sessions. A realistic mixed tier-1 slate (3 PKM + 3 PEER + 2 twins + 2
dense + 3 Phase 2) is ~36 h, since all four T1 variants land within 2% of 3.1 h/run.

**Tier 2 on the Mac is not viable: ~174–194 h**, i.e. 7–8 days continuous per 12-run tier.
That is what the free-GPU tier is for. These extrapolations assume sustained throughput; p90
within 2% of the mean over 270 steps supports that, but they exclude checkpoint writes,
evaluation passes and any read-logging slice, so add ~10% in planning.

---

## 5. Recommendation and risks

### Recommendation

**Tier 1 (Mac only): `t1_pkm` / `t1_peer` / `t1_pkm_frozen` as configured, unchanged.**
65,536 slots (256×256), top-k 32, 4 memory heads, query BatchNorm on, memory layer at index 3,
micro-batch 32, `grad_accum_steps=1`, `lr=2.5e-4` backbone and `1e-3` memory values. 150M
tokens, ~3.1 h/run, ~37 h for the tier. No change to slot count or batch is needed: the batch
ladder topped out, and 65,536 slots is the right primary size to compare against the public
models (step-0 §8 item 7 puts us at the bottom of a 65k → 384M ladder).

**Tier 2 (free GPUs): `t2_pkm` at 65,536 slots as primary, plus `t2_pkm_262k` for the slot
sweep.** Since quadrupling slots costs only 8% of wall clock, the slot sweep belongs here
rather than at tier 1. Two things to settle on the T4 before committing:

- **`t2_peer` will probably not fit a 16 GB T4 at micro-batch 32.** Its two
  `[b, n, h, k, d]` gathers are 8.6 GB in fp32 at `b=32, d=512` (§5.5), plus ~1.4 GB of
  parameters and Adam state, plus the rest of the activations. Expect to need micro-batch 8
  with `grad_accum_steps=4` (gathers drop to 2.15 GB). The notebook reruns the probe, so
  this gets measured rather than guessed.
- **Enable fp16 AMP on CUDA.** All numbers here are fp32; a T4's fp16 tensor cores are ~8×
  its fp32 throughput, so the T4 could beat the Mac substantially with AMP and lose to it
  without. Measure both.

### Risks

**5.1 `product-key-memory`'s query-BatchNorm path is broken — and it is the path we want.**
The roadmap asks for BatchNorm on the query, as in Lample et al. 2019 §3.2, which in
product-key-memory 0.3.0 is `use_layernorm=False`. That selects
`MaskedBatchNorm1D(nn.BatchNorm1d(dim_head))`, but `PKM.forward` hands it a 3-D tensor of
shape `[(b·p·h), t, d]`, so `nn.BatchNorm1d` treats the **sequence** dimension as channels:

```
RuntimeError: running_mean should contain 512 elements not 128
```

The layer cannot run at all with the paper's normalization. `memory.QueryBatchNorm` replaces
it, flattening the leading dims so normalization happens over the query feature dimension
across all tokens in the batch — what the paper describes. Gradients reach keys and values
afterwards and the running statistics update normally. Every PKM config sets
`query_batchnorm: true` and so uses the replacement. **Action: this is our code now, so it
needs to stay in the write-up as a deviation from the published package**, and if we ever
upgrade the package, re-check whether upstream fixed it.

**5.2 MPS is not reproducible, and the non-determinism is localized to the memory layers.**
Measured by `bench/mps_determinism.py`: two fresh runs of the same config and seed, 40 steps,
then a straight run vs. a 20 + save + reload + 20 run.

| device / FFN | repeat: \|Δloss\| | repeat: \|Δparam checksum\| | resume: \|Δloss\| |
|---|---:|---:|---:|
| cpu / dense | **0** | **0** | **0** |
| cpu / pkm | **0** | **0** | **0** |
| mps / dense | 0 | 1.1e-03 | 9.5e-07 |
| mps / pkm | **1.4e-04** | 1.0e-01 | **1.3e-02** |
| mps / peer | **2.2e-04** | 1.4e+00 | 2.2e-04 |

CPU is exactly reproducible. On MPS the dense model is reproducible to ~1e-6 in loss, but
**PKM and PEER are not**: identical runs diverge by ~1e-4 in loss after only 40 steps, and
a resumed run misses the straight run by up to 1.3e-2 — failing the 1e-4 criterion the
roadmap set for the resume test.

The cause is not a bug in our code. The gradient of a memory gather is a scatter-add, which
GPU backends implement with atomics whose summation order varies between runs; with 128
reads/token colliding on 65,536 slots there are many collisions per step. CUDA has the same
property (`embedding_bag` backward is listed as non-deterministic there too), so this is not
Mac-specific and will not go away on Colab.

**Consequences, and what we do about them:**
- The pytest resume test runs on **CPU**, where the 1e-4 criterion is met exactly. That is
  the right place for it: the test is about the resume *mechanism* (what is saved and
  restored), which is device-independent. §6 states this explicitly rather than burying it.
- **Do not attribute a small loss difference between two memory runs to the intervention.**
  The PKM-vs-random-key-twin comparison in steps 4–5 must either show an effect well clear of
  this noise or be run over multiple seeds with the spread reported. We should measure the
  seed-to-seed spread at tier-1 scale once, early, so we know the noise floor we are working
  against.
- Read logs are unaffected: indices and gate weights are exact within a run, and the
  recomputation test is bit-exact.

**5.3 MPS CPU fallback: none.** `PYTORCH_ENABLE_MPS_FALLBACK` is left **unset** throughout
(`run_demo.sh` explicitly `unset`s it), so an operator with no Metal kernel **raises** instead
of silently copying to the CPU. Every benchmark ran to completion, so by construction no op
fell back. As a second check, each result records `device_check`, which walks all named
parameters and buffers — `all_on_device: true` for all eight configs. This is worth stating
precisely because the usual failure mode is the opposite: set the fallback variable, get a
working run, and never notice `embedding_bag` executing on the CPU at a 10× cost. Neither
`nn.EmbeddingBag` with `per_sample_weights` (PKM) nor the `nn.Embedding` gather plus `einsum`
(PEER) needed it.

**5.4 MPS peak memory is not a high-water mark.** `torch.mps.driver_allocated_memory()`
returns what the Metal driver holds right now, and MPS has no equivalent of CUDA's
`max_memory_allocated()`. The benchmark samples it after every step and keeps the running
maximum. So the figures include cached-but-free blocks (**overstating** live tensor bytes) and
can miss a spike between samples. On CUDA the same code path uses `max_memory_allocated()`,
a true high-water mark — so the Mac and T4 columns are not measuring the same thing. Treat
the MPS numbers as "how much the process was holding", which is the number that decides
whether a config fits.

**5.5 PEER's activation memory is much larger than PKM's.** Measured: 33.2 vs 23.5 GB at T1,
43.4 vs 28.5 GB at T2. The cause is structural, not parameters. PEER gathers
`weight_down[idx]` and `weight_up[idx]` as full `[b, n, h, k, d]` tensors:

```
[32, 512, 4, 32, 384] = 805,306,368 elems = 3.22 GB fp32, and PEER needs TWO = 6.44 GB
```

which accounts for 6.44 GB of the 9.62 GB T1 gap; the rest is autograd-saved intermediates
and allocator cache. The parameter difference explains only 0.30 GB including Adam state.
PKM materializes none of this: `nn.EmbeddingBag(mode='sum')` fuses the gather and the
weighted sum, so its only `[b,n,h,k]`-shaped tensor is the 8.4 MB of gate weights. **PEER's
activation memory scales with `b·n·h·k·d`; PKM's does not** — that is the number to watch
when sizing PEER on a 16 GB GPU.

**5.6 PEER costs twice PKM's memory parameters at equal slot count.** A PKM slot is one value
row of width `d_model`; a PEER expert is a rank-1 MLP — a `weight_down` row *and* a
`weight_up` row. At 65,536 slots and `d_model=384`: PKM 25.4M vs PEER 50.6M, so T1-pkm is
54.8M total and T1-peer 80.0M. Two ways to make the comparison fair, and we must say which:
**(1) equal slot count** (what the configs do) — directly comparable read logs, 65,536
addresses and 128 reads/token in both, but PEER stores 2× the bytes; **(2) equal memory
parameters** — give PEER 32,768 experts, equal bytes but no longer like-for-like address
spaces. **Recommendation: keep equal slot count as primary** (the research question is what a
*slot* stores and how slots are organized, so the address space is what to hold fixed) and
add one equal-parameter PEER run as a control.

**5.7 The 1000-step learning runs are not converged** (§3). They demonstrate the stack
learns; they say nothing about model quality or about PKM vs PEER. Do not quote 4.08 vs 4.22
as a result.

**5.8 Everything is fp32.** No AMP on MPS or CUDA. Reasonable for a clean baseline, but it
means the Mac and T4 numbers will not be comparable unless the T4 is also run fp32, and that
leaving AMP off would waste most of a T4's throughput. Decide per tier and record it.

---

## 6. Test results

**59 passed** — `.venv/bin/python -m pytest tests/ -q`, on **CPU** (small models, and the
resume test needs bit-determinism — see §5.2).

Every test the roadmap asked for:

| requirement | test(s) | notes |
|---|---|---|
| Forward-pass shapes for dense, PKM, PEER blocks | `test_model.py::test_forward_shapes[dense\|pkm\|peer]`, `::test_block_forward_shapes[…]` | whole model and each FFN replacement in isolation |
| Read log returns k slot indices per token per head, in range | `test_memory.py::test_read_log_shape_and_range[pkm\|peer]` | also asserts the topk slots per (token, head) are **distinct** |
| `freeze_keys`: keys bit-identical, values changed | `test_memory.py::test_freeze_keys_keeps_keys_and_trains_values[pkm\|peer]` | plus `::test_keys_train_when_not_frozen` as negative control |
| Values get the higher learning rate | `test_train.py::test_memory_values_get_the_higher_learning_rate[pkm\|peer]` | asserts group membership exactly, and that every trainable tensor is in exactly one group |
| Checkpoint resume: 100 straight vs 50+50 in a fresh process | `test_train.py::test_checkpoint_resume_matches_straight_run[pkm\|peer]` | loss within 1e-4, step counter, LR, data order; **CPU** (§5.2) |
| Step-0 initial weights exist and differ from trained | `test_train.py::test_initial_weights_saved_and_differ_from_trained` | also asserts the memory value table specifically moved |
| PEER read log returns weights, finite, matching what the layer used | `test_memory.py::test_peer_read_log_weights_match_what_the_layer_used` | recomputes the layer output from the log alone — **bit-exact** |
| `mask_slots`, PKM and PEER | `test_memory.py::test_mask_slots_semantics[pkm\|peer]` | masked slots never contribute; top-k unchanged; empty mask == unmasked |
| Bio generator: seed-identical, disjoint QA halves, K distinct biographies, complete `attribute_values.json` | `test_bio_generator.py` (13 tests) | |

Tests beyond the list, each covering something that broke or could:

- `test_pkm_read_log_weights_match_what_the_layer_used` — the PKM counterpart of the PEER
  recomputation check (`Σ wᵢ · values.weight[idxᵢ]`).
- `test_slot_usage_is_tracked_without_the_full_read_log[pkm|peer]` — **regression test for a
  real bug.** `track_slot_usage=True` with `read_logging=False` reported every slot as
  unread, because the memory layers only expose their reads when read logging is on. That is
  exactly the configuration the 1000-step runs use, so every slot-usage and KL number in §3
  was zero until it was fixed.
- `test_nothing_is_captured_when_both_switches_are_off` — guards the §2.4 baseline against
  the opposite leak, where capture cost would silently enter the "logging off" column.
- `test_lr_ratio_is_preserved_through_the_schedule` — the cosine `LambdaLR` scales all groups
  by one factor, so the 4× value/backbone ratio must hold at every step, not just step 0.
- `test_resume_restores_optimizer_state_not_just_weights` — without Adam's moments the first
  post-resume step would differ from identical weights.
- `test_reader_recovers_token_positions` — the log stores no position column, so
  `ReadLogReader.coords()` rebuilds `(step, batch, position)` from the manifest.
- `test_qa_split_is_stable_across_rewording_count` — the QA split is drawn from its own RNG
  stream, so changing `--rewordings` must not move people between halves.
- `test_mask_slots_can_be_set_from_the_config[pkm|peer]` — `mask_slots` and
  `renormalize_after_mask` are constructor options as well as a runtime API.

### Open problems

1. **MPS non-determinism in the memory layers** (§5.2) — no fix available; needs a measured
   noise floor and multi-seed comparisons in steps 4–5. This is the one item that could
   affect a conclusion.
2. **The T4 column of Table D is empty.** Needs one Colab session with
   `bench/colab_benchmark.ipynb`, and a decision on fp32 vs fp16 AMP (§5.8).
3. **PEER at tier 2 may not fit a 16 GB T4** at micro-batch 32 (§5.5) — the notebook's probe
   will say, and gradient accumulation covers it either way.
4. **The query-BatchNorm replacement is our code**, not the published package (§5.1). It
   matches the paper's description, but it has not been validated against a reference PKM
   implementation that trains to a known loss — worth one sanity run against published
   numbers if one is available.

---

## 7. Held-out subject for Phase 2

From the subject table in step-0 report §4.2, with the 5-domain training mix being Github,
Pile-CC, PubMed Central, FreeLaw and Wikipedia (en):

| candidate | % of Pile tokens | tok/doc | docs to stream for 10M tokens | overlap with the training mix |
|---|---:|---:|---:|---|
| **USPTO Backgrounds** | 3.26 | 848 | 190,434 | **lowest** — patent prose matches none of the five |
| StackExchange | 7.78 | 756 | 79,815 | high — straddles Github *and* Pile-CC |
| ArXiv | 13.78 | 17,305 | 45,075 | high — same academic register as PubMed Central |

**Recommendation: hold out `USPTO Backgrounds`** — it is the only one of the three whose
register is genuinely absent from the training mix (patent background sections are
technical-legal prose, distinct from FreeLaw's judicial opinions in both vocabulary and
syntax), so a read-log shift on it measures generalization to an unseen domain rather than
leakage from a near-duplicate, while 3.26% of the Pile (~8B tokens) is far more than the
1–10M held-out tokens needed.

Caveat to carry in the write-up: USPTO is the closest of the three to a training domain in
*subject matter* (USPTO and FreeLaw are both legal-adjacent), so if Phase 2 shows little
read-log shift, that is the first confound to rule out. ArXiv is the fallback if we want a
larger held-out set and accept near-duplication with PubMed Central. StackExchange should not
be used: overlapping two training domains at once makes a null result uninterpretable.

---

## Appendix A — what was built

```
memlayers/
  model.py       nanoGPT-style decoder; each layer's FFN is dense | pkm | peer
  memory.py      PKM and PEER behind one interface (read log, masking, key freezing)
  readlog.py     read-log writer/reader + slot-usage statistics
  data_fake.py   (a) uniform random tokens   (b) repeated-chunk copy task
  train.py       AdamW, grad accumulation, cosine+warmup, param groups, resume, CSV
  devices.py     cuda > mps > cpu selection, sync, peak memory, RNG state
  configs/       8 YAML configs
bench/
  benchmark.py          probe / speed / learn / summarize
  model_budget.py       parameter vs. per-token-MAC accounting
  mps_determinism.py    repeat- and resume-reproducibility per device and FFN type
  make_report_tables.py the tables in this report
  run_demo.sh           every benchmark in order
  colab_benchmark.ipynb the same benchmark on a Colab T4
tests/                  59 tests
tools/bio_generator.py  extended: --rewordings, --qa-split, attribute_values.json
```

`train.py` is meant to be the real training script for steps 4–5, not a demo: gradient
accumulation, cosine schedule with warmup, per-group learning rates, gradient clipping,
checkpoint/resume including RNG state, a step-0 weight snapshot, and a per-step CSV.

### A.1 Reading out the memory, without patching either package

Step 0 established that a forward pre-hook on `pkm.values` sees both the slot indices and the
gate weights, because PKM passes both to its `nn.EmbeddingBag`. **PEER is different: only the
indices pass through `weight_down_embed`; the scores never do.** The post-activation scores
are therefore captured with a second hook on `peer.score_activation`. Hook order within one
forward is `weight_down_embed` (pre) then `score_activation` (forward), so the indices are
already in hand when the scores arrive.

That they line up is tested, not assumed — `test_memory.py` rebuilds the whole PEER output
from the logged indices and weights alone:

```python
wd = peer.weight_down_embed.weight[idx]      # [b,n,h,k,d]
wu = peer.weight_up_embed.weight[idx]
inner = peer.activation(einsum(peer.norm(x), wd, 'b n d, b n h k d -> b n h k'))
rebuilt = einsum(inner * logged_weights, wu, 'b n h k, b n h k d -> b n d')
```

and matches the layer's own output **bit-exactly** (max abs diff 0.0). The PKM equivalent
matches too. If a future package version reorders its internals, both tests fail at once.

### A.2 `mask_slots`

Masking reuses the same hooks — a pre-hook may return replacement inputs, a forward hook a
replacement output — so a masked slot's gate weight is zeroed **after** the top-k selection.
The search is untouched, so the next-best slot does not move up. Tested: top-k indices
identical with and without masking, masked slots carry exactly 0.0, unmasked weights unchanged
when `renormalize_after_mask=False` (the default), and an empty mask gives a bit-identical
output to no mask (the mask is cleared rather than kept as an all-False tensor, so it is
genuinely the same code path). One edge case pinned down by test: if **every** slot in a
head's top-k is masked, that row sums to zero and there is nothing to renormalize — with
renormalization on, such rows stay zero while all others rescale to 1.

### A.3 PEER's `non_competing_scores`

Set to **`False`** in `t1_peer.yaml`, `t2_peer.yaml` and the `PEERMemory` default, as step-0
§8 recommended. PEER-pytorch defaults it to `True`, which sets
`num_experts_per_head_topk = 1` — only `heads × 1 = 4` experts per token instead of
`heads × 32 = 128`, **32× sparser than intended**, with a ReLU gate instead of a softmax. The
wrapper warns if anyone builds it with `non_competing_scores=True` and `topk > 1`, so the
mistake cannot be made silently. With `False`, the measured read log is `[b, 512, 4, 32]` and
the gate weights sum to 1 per head — confirmed in the tests and in the benchmark logs
(128 reads/token).

### A.4 Fake data addressing

`get_batch(step, micro)` is a pure function of `(seed, step, micro)` rather than a position in
a stream. Data order is then exactly reproducible across a resume with nothing to save, which
is what lets the resume test compare losses at 1e-4.

### A.5 Bio generator extensions

`--rewordings K` (default 4) writes each person's biography K times, each with its own
template draw and sentence order; `--qa-split` tags each person `qa_train` / `qa_test` from a
separate RNG stream so the halves are stable under changes to K; `attribute_values.json` is
written next to the output with the candidate set per attribute (the full generator pool for
the four categorical attributes, the observed values for the combinatorial `birth_date`).
`--rewordings 1` still reproduces the step-0 output byte for byte.

At 4 rewordings: **246.6 biography tokens + 58.6 QA tokens = 305.2 tokens per person**
(GPT-2 encoding), so 10k people is 3.05M tokens and 100k people is **30.5M tokens** (61 MB as
uint16) — up from 12.0M at one rewording.
