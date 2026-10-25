# Step 1 — Training Demo on Fake Data

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-10-25
**Scope:** build the reusable training code, prove it works end to end, measure speed and memory. No real data.

Everything below is produced by code in this repo: `memlayers/` (the package), `bench/` (the
benchmarks), `tests/` (59 pytest tests). Raw benchmark output is in `bench/results/*.json`;
every number in the tables is read out of those files by `bench/make_report_tables.py`
rather than retyped.

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
| Device actually used | `mps` for every benchmark below |
| `PYTORCH_ENABLE_MPS_FALLBACK` | **unset, on purpose** (see §5.3) |

New packages this step: `PyYAML==6.0.3` (configs) and `pytest==9.1.1` (tests), both added to
`requirements.txt`. Nothing else was needed — `product-key-memory`, `PEER-pytorch`, `torch`,
`numpy` and `tiktoken` were already pinned in step 0.

---

## 2. What was built

```
memlayers/
  model.py       nanoGPT-style decoder; each layer's FFN is dense | pkm | peer
  memory.py      PKM and PEER behind one interface (read log, masking, key freezing)
  readlog.py     read-log writer/reader + slot-usage statistics
  data_fake.py   (a) uniform random tokens   (b) repeated-chunk copy task
  train.py       AdamW, grad accumulation, cosine+warmup, param groups, resume, CSV
  devices.py     cuda > mps > cpu selection, sync, peak-memory, RNG state
  configs/       8 YAML configs
bench/
  benchmark.py          probe / speed / learn / summarize
  model_budget.py       parameter vs. per-token-FLOP accounting
  make_report_tables.py the tables in this report
  run_demo.sh           runs every benchmark in order
  colab_benchmark.ipynb the same benchmark on a Colab T4
tests/           59 tests
tools/bio_generator.py   extended: --rewordings, --qa-split, attribute_values.json
```

`train.py` is written to be the real training script for steps 4–5, not a demo: gradient
accumulation, cosine schedule with warmup, per-group learning rates, gradient clipping,
checkpoint/resume including RNG state, a step-0 weight snapshot, and a per-step CSV.

### 2.1 Three implementation findings worth carrying forward

**(a) `product-key-memory`'s query-BatchNorm path is broken, and we need that path.**
The roadmap asks for BatchNorm on the query, as in Lample et al. 2019 §3.2. In
product-key-memory 0.3.0 that is `use_layernorm=False`, which selects
`MaskedBatchNorm1D(nn.BatchNorm1d(dim_head))`. But `PKM.forward` hands it a 3-D tensor of
shape `[(b·p·h), t, d]`, and `nn.BatchNorm1d` then treats the **sequence** dimension as
channels:

```
RuntimeError: running_mean should contain 512 elements not 128
```

So the layer cannot even run with the paper's normalization. `memory.QueryBatchNorm`
replaces it and flattens the leading dims first, normalizing over the query feature
dimension across all tokens in the batch, which is what the paper describes. Gradients
reach keys and values afterwards, and the BatchNorm running statistics update normally.
Every PKM config here sets `query_batchnorm: true` and therefore uses the replacement.

**(b) Read-out needs no patching of either package — but PEER needs two hooks.**
Step 0 established that a forward pre-hook on `pkm.values` sees both the slot indices and
the gate weights, because PKM passes both to its `nn.EmbeddingBag`. PEER is different: only
the indices pass through `weight_down_embed`; the scores never do. The post-activation
scores are therefore captured with a **second** hook, on `peer.score_activation`. Hook order
inside one forward is `weight_down_embed` (pre) then `score_activation` (forward), so the
indices are already in hand when the scores arrive.

That they *line up* is not assumed — it is tested. `tests/test_memory.py` recomputes the
whole PEER layer output from the logged indices and weights alone:

```python
wd = peer.weight_down_embed.weight[idx]      # [b,n,h,k,d]
wu = peer.weight_up_embed.weight[idx]
inner = peer.activation(einsum(peer.norm(x), wd, 'b n d, b n h k d -> b n h k'))
rebuilt = einsum(inner * logged_weights, wu, 'b n h k, b n h k d -> b n d')
```

and gets a **bit-exact** match (max abs diff 0.0) against the layer's own output. The
equivalent check for PKM — `Σ w_i · values.weight[idx_i]` — also matches. If a future
package version reorders its internals, these two tests fail immediately.

**(c) `mask_slots` masks after the search, and the empty mask is bit-identical.**
Masking is implemented on the same hooks: a pre-hook may return replacement inputs and a
forward hook may return a replacement output, so a masked slot's gate weight is set to zero
*after* the top-k selection. The search is untouched, so the next-best slot does **not**
move up — which is the semantics the roadmap asks for. Tested: the top-k index tensor is
identical with and without masking; masked slots carry exactly 0.0 weight; unmasked weights
are unchanged when `renormalize_after_mask=False` (the default); and an empty mask gives a
bit-identical output to no mask at all (the mask is cleared rather than kept as an all-False
tensor, so the fast path is genuinely the same code).

One edge case the tests pin down: if **every** slot in a head's top-k is masked, that head's
weights sum to zero and there is nothing to renormalize. With `renormalize_after_mask=True`
such a row stays zero while all other rows rescale to sum 1. That is the only correct
behaviour, but it is easy to get wrong, so it is asserted explicitly.

### 2.2 PEER's `non_competing_scores`

Set to **`False`** explicitly in `t1_peer.yaml`, `t2_peer.yaml` and in the `PEERMemory`
default, as step 0 §8 recommended. PEER-pytorch defaults it to `True`, which sets
`num_experts_per_head_topk = 1`: only `heads × 1 = 4` experts would fire per token instead of
`heads × 32 = 128`, i.e. **32× sparser than intended**, and the gate becomes a ReLU rather
than a softmax over the selected experts. The wrapper also emits a warning if anyone builds
it with `non_competing_scores=True` and `topk > 1`, so the mistake cannot be made silently.

With `False`, the measured read log is `[batch, seq, 4, 32]` and the gate weights sum to 1
per head — confirmed in the tests and in the benchmark read logs (128 reads/token).

### 2.3 Fake data

`data_fake.py` addresses batches by **step index**, not by position in a stream:
`get_batch(step, micro)` is a pure function of `(seed, step, micro)`. That makes data order
exactly reproducible across a checkpoint resume with nothing to save, which is what lets the
resume test compare losses at 1e-4.

- **(a) `random`** — uniform token ids. Unlearnable by construction; loss should sit at
  `ln(50257) = 10.825`. This is the speed/memory workload.
- **(b) `repeat`** — one random chunk of `chunk_len=16` tokens repeated to fill the 512-token
  context. Everything after the first chunk is predictable by copying from 16 positions back,
  so an induction head solves it. The floor is set by the first chunk only:
  `(16/512) · ln(50257) = 0.338` nats.

---

## 5. Risks and notes

### 5.3 MPS CPU fallback: none detected

`PYTORCH_ENABLE_MPS_FALLBACK` is left **unset** throughout (`run_demo.sh` explicitly
`unset`s it). With that variable off, an operator with no Metal kernel **raises**
`NotImplementedError` instead of silently copying to the CPU. Every benchmark ran to
completion, so by construction **no op fell back**. As a second check, every benchmark
records `device_check`, which walks all named parameters and buffers and asserts none stayed
on the CPU — `all_on_device: true` for all eight configs.

This is worth stating precisely because the usual failure mode is the opposite: people set
the fallback variable, get a run that works, and never notice that `embedding_bag` or a
`topk` is executing on the CPU at a 10× cost. Neither `nn.EmbeddingBag` with
`per_sample_weights` (PKM) nor `nn.Embedding` gather plus `einsum` (PEER) needed it.

### 5.4 Peak memory on MPS is not a high-water mark

`torch.mps.driver_allocated_memory()` returns what the Metal driver holds for the process
*right now*, and there is no per-process high-water-mark API equivalent to CUDA's
`max_memory_allocated()`. The benchmark therefore samples it after every step and keeps the
running maximum. Two consequences: the figure includes PyTorch's cached-but-free blocks, so
it **overstates** live tensor bytes; and a transient spike between two samples can be missed.
On CUDA the same code path uses `max_memory_allocated()`, which is a true high-water mark, so
the Mac and T4 columns are not measuring quite the same thing. Treat the MPS numbers as "how
much the process was holding", which is the number that matters for deciding whether a
config fits.

### 5.5 PEER costs twice the memory parameters of PKM at the same slot count

Not a bug, but it makes the headline comparison unfair if taken at face value. A PKM slot is
one value row of width `d_model`. A PEER expert is a **rank-1 MLP**: one row of
`weight_down_embed` (the read direction) *and* one row of `weight_up_embed` (the write
direction). So at 65,536 slots and `d_model=384`:

| | memory params | per slot |
|---|---:|---:|
| PKM | 25.82M | 384 floats (1 value row) |
| PEER | 50.99M | 768 floats (down + up row) |

T1-pkm is 54.8M parameters total and T1-peer is 80.0M. If a reviewer asks "same number of
slots, why is PEER bigger", that is the answer. Two ways to make the comparison fair in steps
4–5, and we should say which we are doing:

1. **Equal slot count** (what the configs do now). Directly comparable read logs — 65,536
   addresses, 128 reads/token in both — but PEER has 2× the stored parameters.
2. **Equal memory parameters.** Give PEER 32,768 experts against PKM's 65,536 slots. Equal
   bytes, but the address spaces differ, so slot-usage statistics are no longer
   like-for-like.

**Recommendation: keep equal slot count as the primary comparison** (the research question is
about what a *slot* stores and how slots are organized, so the address space is the thing to
hold fixed), and add one equal-parameter PEER run as a control. Note it explicitly in the
write-up either way.

### 5.6 The micro-batch ladder topped out

All eight configs ran at micro-batch 32, the largest rung the roadmap specified, so "32" is
the **ceiling of the ladder, not the machine's limit**. Peak memory at 32 ranged from 22.4 GB
(T1-dense) to 43.4 GB (T2-peer) out of 64 GiB unified, so T1 clearly has headroom and
T2-peer is the one approaching it. Since gradient accumulation can reach any effective batch
size from micro-batch 32, there is no need to probe higher for the real runs; the relevant
fact is that **no config needed accumulation to fit**, so `grad_accum_steps=1` everywhere and
the effective batch is 32 × 512 = 16,384 tokens per step.

---

## 6. What should a "tier size" refer to, and does T1 need to shrink?

The compute plan sizes tier 1 at **about 20M parameters**. The configs here are 30.1M
(T1-dense), 54.8M (T1-pkm) and 80.0M (T1-peer). Neither "20M" nor the gap between those three
numbers means what it looks like, because **parameter count and compute are decoupled in
these models**. `bench/model_budget.py` prints both columns:

| config | embedding | backbone | memory | total params | MAC/token | attn | dense MLP | memory | lm_head | lm_head share | memory share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `t1_dense` | 19.50M | 10.65M | 0.00M | 30.14M | 31.10M | 4.72M | 7.08M | 0.00M | 19.30M | **62.1%** | 0.0% |
| `t1_pkm` | 19.50M | 9.47M | 25.82M | 54.78M | 30.62M | 4.72M | 5.90M | 0.70M | 19.30M | **63.0%** | **2.3%** |
| `t1_peer` | 19.50M | 9.47M | 50.99M | 79.95M | 30.67M | 4.72M | 5.90M | 0.75M | 19.30M | **62.9%** | **2.5%** |
| `t2_dense` | 25.99M | 25.22M | 0.00M | 51.21M | 52.99M | 10.49M | 16.78M | 0.00M | 25.73M | 48.6% | 0.0% |
| `t2_pkm` | 25.99M | 23.12M | 34.34M | 83.46M | 51.75M | 10.49M | 14.68M | 0.85M | 25.73M | 49.7% | 1.6% |
| `t2_pkm_262k` | 25.99M | 23.12M | 135.27M | 184.38M | 52.01M | 10.49M | 14.68M | 1.11M | 25.73M | 49.5% | 2.1% |
| `t2_peer` | 25.99M | 23.12M | 67.90M | 117.01M | 51.81M | 10.49M | 14.68M | 0.92M | 25.73M | 49.7% | 1.8% |

(MAC/token is one forward pass; a training step is roughly 3× that.)

Two facts jump out:

1. **A memory layer is nearly free in compute.** T1-pkm's memory holds 47% of the model's
   parameters but costs **2.3%** of forward MACs; T2-pkm-262k's holds 73% and costs 2.1%.
   That is the entire point of a memory layer, and it means parameter count is a *terrible*
   proxy for training time here. Going from 65,536 to 262,144 slots quadruples the memory
   parameters and changes compute by half a percent.
2. **At tier-1 width the output projection dominates.** `d_model × 50257 = 19.3M` MAC/token
   is **62%** of T1's forward compute — more than attention and all the MLPs combined.
   Shrinking `d_model` or dropping layers barely helps the time budget, because the vocab
   projection scales with `d_model` only linearly while the backbone scales quadratically.
   At T2 width the share falls to ~49%, so wider models are *more* compute-efficient per
   parameter.

### Recommendation on what the tier size should mean

**Tier sizes should refer to non-embedding, non-memory backbone parameters** — 10.65M for T1,
25.22M for T2 — because that is the only one of the three counts that (a) is comparable
across dense/PKM/PEER variants and (b) tracks the compute that actually scales with model
size. Reporting it alongside the memory count, as the tables here do, keeps both honest.

But the tier **time budget must be set from measured tokens/sec, not from any parameter
count.** The three T1 variants differ by 2.7× in total parameters (30.1M → 80.0M) and by
under 1% in FLOPs; what separates them in wall clock is memory-bandwidth and gather cost, not
arithmetic, and only measurement captures that. The hours/run figures in Table D are that
measurement.

### Does T1 need to shrink?

**No — and shrinking it would not buy much anyway.** See §4 for the arithmetic against the
budget. The structural reason is the point above: 62% of T1's compute is the vocab
projection, which is fixed by the GPT-2 tokenizer and `d_model`, so the usual levers (fewer
layers, narrower model) hit only the other 38%. Halving `n_layer` from 6 to 3 would cut total
MAC/token by just 19%. If tier 1 ever does need to be faster, the effective levers are, in
order:

1. **Shorter context** — 512 → 256 halves tokens per step at the same micro-batch and cuts
   the attention-score term, and for the bioS-style synthetic data in later phases a
   512-token context is already far longer than a biography needs.
2. **A smaller vocabulary** — the single biggest lever, since it attacks the 62%. A
   16k-token BPE vocabulary trained on our own mix would cut `lm_head` MACs by ~3×. The cost
   is losing comparability with GPT-2-tokenized public work, so this is a real trade-off, not
   a free win.
3. **Fewer tokens** — 150M → 100M. Linear in wall clock and the easiest dial to turn.

Cutting the *memory* to save time would be the one change that is pure loss: it is 2% of the
compute and the entire subject of the project.

---

## 7. Held-out subject for Phase 2

Using the subject table in step-0 report §4.2, with the 5-domain training mix being Github,
Pile-CC, PubMed Central, FreeLaw and Wikipedia (en):

| candidate | % of Pile tokens | tok/doc | docs to stream for 10M tokens | overlap with the training mix |
|---|---:|---:|---:|---|
| **USPTO Backgrounds** | 3.26 | 848 | 190,434 | **lowest** — patent prose matches none of the five |
| StackExchange | 7.78 | 756 | 79,815 | high — straddles Github *and* Pile-CC |
| ArXiv | 13.78 | 17,305 | 45,075 | high — same academic register as PubMed Central |

**Recommendation: hold out `USPTO Backgrounds`.** It is the only one of the three whose
register is genuinely absent from the training mix — patent background sections are
technical-legal prose, distinct from FreeLaw's judicial opinions in both vocabulary and
syntax — so a read-log shift on it measures generalization to an unseen domain rather than
leakage from a near-duplicate domain, while 3.26% of the Pile (~8B tokens) is far more than
the 1–10M held-out tokens we need.

The caveat to state in the write-up: USPTO is the *closest* of the three to a training domain
in subject matter (both USPTO and FreeLaw are legal-adjacent), so if Phase 2 shows little
read-log shift, that is the first confound to rule out. ArXiv is the fallback if we want a
larger held-out set and are willing to accept near-duplication with PubMed Central;
StackExchange should not be used, since overlapping two training domains at once makes a null
result uninterpretable.

---

## 8. Test results

`59 passed` — `.venv/bin/python -m pytest tests/ -q`, run on **CPU** (small models, and the
resume test needs bit-determinism; see the caveat below).

Every test the roadmap asked for, and where it lives:

| roadmap requirement | test(s) | notes |
|---|---|---|
| Forward-pass shapes for dense, PKM, PEER blocks | `test_model.py::test_forward_shapes[dense\|pkm\|peer]`, `::test_block_forward_shapes[...]` | checks both the whole model and each FFN replacement in isolation |
| Read log returns k slot indices per token per head, all in range | `test_memory.py::test_read_log_shape_and_range[pkm\|peer]` | also asserts the `topk` slots per (token, head) are **distinct** |
| `freeze_keys`: keys bit-identical, values changed | `test_memory.py::test_freeze_keys_keeps_keys_and_trains_values[pkm\|peer]` | plus `::test_keys_train_when_not_frozen` as the negative control |
| Values get the higher learning rate | `test_train.py::test_memory_values_get_the_higher_learning_rate[pkm\|peer]` | asserts group membership exactly, and that every trainable tensor is in exactly one group |
| Checkpoint resume: 100 straight vs 50+50 in a fresh process | `test_train.py::test_checkpoint_resume_matches_straight_run[pkm\|peer]` | loss match, step counter, LR, data order — see below |
| Step-0 initial weights exist and differ from trained | `test_train.py::test_initial_weights_saved_and_differ_from_trained` | also asserts the *memory value table* specifically moved |
| PEER read log returns weights, finite, matching what the layer used | `test_memory.py::test_peer_read_log_weights_match_what_the_layer_used` | recomputes the layer output from the log; **bit-exact** |
| `mask_slots` for PKM and PEER | `test_memory.py::test_mask_slots_semantics[pkm\|peer]` | masked slots never contribute; top-k unchanged; empty mask == unmasked |
| Bio generator: seed-identical, disjoint QA halves, K distinct biographies, complete `attribute_values.json` | `test_bio_generator.py` (13 tests) | |

Extra tests beyond the list, each covering something that actually broke or could:

- `test_pkm_read_log_weights_match_what_the_layer_used` — the PKM counterpart of the PEER
  recomputation check.
- `test_slot_usage_is_tracked_without_the_full_read_log[pkm|peer]` — **regression test for a
  real bug.** `track_slot_usage=True` with `read_logging=False` silently reported every slot
  as unread, because the memory layers only expose their reads when read logging is switched
  on. That is exactly the configuration the 1000-step learning runs use, so the slot-usage
  and KL numbers this report needs were all zero until it was fixed.
- `test_nothing_is_captured_when_both_switches_are_off` — guards the speed baseline: if
  either capture path leaked into it, the "read-logging off" column would silently include
  logging cost.
- `test_lr_ratio_is_preserved_through_the_schedule` — the cosine `LambdaLR` multiplies every
  group by the same factor, so the 4× value/backbone ratio must hold at every step, not just
  at step 0.
- `test_resume_restores_optimizer_state_not_just_weights` — without Adam's moments the first
  post-resume step would differ even from identical weights.
- `test_reader_recovers_token_positions` — the read log stores no position column, so
  `ReadLogReader.coords()` has to rebuild `(step, batch, position)` from the manifest.
- `test_qa_split_is_stable_across_rewording_count` — the QA split is drawn from its own RNG
  stream, so changing `--rewordings` must not move people between halves.
- `test_mask_slots_can_be_set_from_the_config[pkm|peer]` — `mask_slots` and
  `renormalize_after_mask` are constructor options as well as a runtime API, so a YAML config
  can switch slots off directly.

### Caveat on where the resume test runs

The resume test runs on **CPU**, not MPS. It compares the loss at step 100 between a straight
run and a resumed one at a 1e-4 tolerance, which needs the two runs to execute an identical
op sequence with identical float rounding. CPU gives that. Whether MPS does is a separate
question that the test deliberately does not conflate with "does resume work"; it is checked
on-device separately in §5.7. The resume *mechanism* (what is saved, what is restored) is
device-independent, and `devices.get_rng_states` / `set_rng_states` handle the CUDA and MPS
generator state when present.
