# Training 4 — read logs, the reader API, shared helpers, and the metric interface

Branch `train/run-layer`, training prompt 4 of 5. This step adds:
- a post-hoc pass that records which memory slots a fixed set of tokens reads;
- a memmap reader for that read log;
- the helpers the analysis metrics share;
- `docs/metrics_interface.md` and a test kit those metrics plug into.

The analysis metrics themselves (U4, E1, E2, V2, C4, C6) are not implemented
here.

```bash
python -m memlayers.eval.eval_sets --version v1                       # adds readlog_tokens
python -m memlayers.readlog_pass run_dir=runs/pkm-s0 step=[init,final]
python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final metrics=[<analysis metric>]
```

## 1. The `readlog_tokens` set

Built by the same `memlayers.eval.eval_sets` command into
`data/v1/eval_sets/readlog_tokens.json`. It is hashed into the committed
`data/manifests/eval_sets_v1.json`:

**sha256 `d4f2756e217f1c30c11b3250cd965ff9394b2f788d2f353eaad3a7b5c0070763`**
(19,731 items: 4,131 documents + 15,600 fact prompts).

The two run-start sets are unchanged (`a3953cde…`, `b77cf233…`). Rebuilding
gives the same bytes.

**Held-out text.** From the LABEL half, never the test half; the 5 Pile
training subjects (USPTO not included). Whole documents in a keyed order (data
seed 20261102) until the subject reaches `eval.readlog.tokens_per_subject`
(default 1,000,000; the document that crosses the line is kept whole). The
pass cuts them into per-document windows exactly as heldout_quality does. A
document of n tokens gives n − 1 logged positions (the last token is only a
target).

**Biographies.** Every test and paraphrase fact prompt of every frequent-tier
person (300 people), and of a keyed 10% of the people in each other tier
(normal 70, rare 100, control 50). That is 520 people × 30 prompts. Each is run
one per row as the prompt followed by the true value's tokens
(`value_token_ids`).

Tokens actually logged (identical at every checkpoint):

| segment / subject | tokens | | bio tier | tokens |
|---|---:|---|---|---:|
| Pile-CC | 999,251 | | frequent | 423,106 |
| Github | 999,987 | | normal | 99,372 |
| PubMed Central | 1,003,242 | | rare | 140,898 |
| FreeLaw | 1,000,245 | | control | 70,811 |
| Wikipedia (en) | 998,898 | | | |
| **held-out total** | **5,001,623** | | **bio total** | **734,187** |

**All together: 5,735,810 tokens per checkpoint.**

How the hash is used:
- `readlog_pass` checks it against the manifest.
- `readlog_pass` refuses a set built with a different budget than the run's
  `eval.readlog.tokens_per_subject`. The error names the rebuild flag
  `--readlog-tokens-per-subject N`; changing the budget changes the hash, by
  design.
- It is recorded in every read log's `manifest.json` and in the run's
  `meta.json` (`eval_sets.readlog_tokens`).
- It is NOT part of the run-start check.
- `memlayers.compare` refuses to put runs whose read logs used different
  `readlog_tokens` hashes in one table (runs without read logs do not take
  part), and shows the hash in `runs.csv`.
- A run that already has read logs on one hash refuses a pass on another
  unless `force=true`.

The 1% sample (`data/v1_sample`, used by the smoke runs) got its own
readlog_tokens: 321 items, `1b25abf5…`, in `eval_sets_v1_small.json`.

## 2. The read-log pass: timing and sizes

`runs/pkm-s0-eval-check/` (T1-pkm, prompt 2's 300-step real-data run), on MPS.
The pass printed its plan before writing anything:
`5,735,810 tokens (5,001,623 held-out, 734,187 bio) x 512 B = 2.94 GB per
checkpoint, 2 checkpoint(s); 1829.5 GB free`. It refuses below 2× the expected
size free.

| checkpoint | time in the pass | `layer3_indices.bin` (uint16) | `layer3_weights.bin` (fp16) | `tokens.parquet` | total |
|---|---:|---:|---:|---:|---:|
| step 0 (init) | 198.7 s | 1,468,367,360 B | 1,468,367,360 B | 10.1 MB | **2.947 GB** |
| step 300 (final) | 159.0 s | 1,468,367,360 B | 1,468,367,360 B | 10.1 MB | **2.947 GB** |

Each is [5,735,810 tokens, 4 heads, top-32]. That is 512 B per token per
memory layer, as projected.

The process ran 14 min of wall time for both checkpoints. The rest of that
time is planning (tokenizing 15,600 prompts), the sha256 of 3 GB per
checkpoint, and, as in prompts 2 and 3, the laptop sleeping with the lid
closed.

**Phase 1 projection.** 4 memory runs (pkm s0, s1, s2 and pkm_randkey s0;
dense has no read log) × 2 checkpoints (init, final) × 2.95 GB ≈ **23.6 GB**,
and about 6 min of pass time per run.

**Format.** Files go in `<run_dir>/readlogs/step_<6d>/`:
- `layer<L>_indices.bin`: [n_tokens, heads, topk], uint16 for ≤ 65,536 slots,
  else uint32.
- `layer<L>_weights.bin`: the same shape, fp16, the post-softmax gate weights
  (what multiplied the value rows).
- `tokens.parquet`: one row per token in file order. Columns: token_id,
  segment, doc_id, subject, position; and for bio rows person_id, tier,
  attribute, fact_id, role, template_id, is_answer_position, is_value_token.
- `manifest.json`: the checkpoint path and sha256, model config, layers,
  n_slots, heads, topk, dtypes, shapes, tokens per segment, subject and bio
  tier, the eval-set hash, every file's sha256, wall time and device.

Each step is written to a temp dir and renamed into place when complete, so a
cut-off pass leaves nothing half-written. A dense run is refused before
anything is written.

**ReadLogWriter was extended, not duplicated.** The file names are now
parameters (the training-time read log keeps `layer<L>_idx.bin` /
`layer<L>_w.bin`). `close()` takes the extra manifest fields and can drop the
per-forward record list, because the token table carries order and metadata.
Reading is a new class, `ReadLog`. The old `ReadLogReader` loads everything
into RAM and reconstructs positions from the record list. That cannot work for
a 2.9 GB log, so `ReadLog` memory-maps instead. `ReadLogReader` stays for the
training-time logs.

## 3. Reader API and helpers

`memlayers.readlog.ReadLog` (or `ctx.readlog(step=None)`):

| | |
|---|---|
| `ReadLog.open(dir)` | opens a read log; `.layers`, `.n_tokens`, `.step`, `.n_slots(L)`, `.heads(L)`, `.topk(L)` |
| `.tokens` | the token table as a DataFrame (lazy) |
| `.indices(L)`, `.weights(L)` | read-only memmaps `[n_tokens, heads, topk]` |
| `.select(**filters)` | row ids matching every filter (a value or a list); unknown columns raise |
| `.slot_counts(L, rows=None, weighted=False)` | reads per slot (or summed gate weights), chunked |
| `.iter_chunks(L, rows=None, chunk_tokens=1_000_000)` | `(row_ids, indices, weights)` chunks, never all at once |

On `EvalContext`:

| | |
|---|---|
| `ctx.readlog(step=None)` | the reader for this checkpoint's step (or `step`). "Run the read-log pass first", with the exact command, if missing; a metric listing `"readlog"` is skipped with that reason |
| `ctx.value_table(L)` | `[n_slots, d]` fp32 CPU copy of what each slot writes (PKM values; PEER up-embedding) |
| `ctx.unembedding()` | `[vocab, d]` fp32 CPU copy of the output head (tied embedding), for the logit lens |
| `ctx.used_slots(L)` | slots read at least once in the read log |
| `ctx.slot_bins(L, n_bins=10)` | (used slots, read-count decile, value-norm decile), rank-based |
| `ctx.matched_random_slots(L, slots, n, rng, n_bins=10)` | `n` used slots from the same (count, norm) cells in the same proportions (largest-remainder rounding), never in `slots`, deterministic per rng; ValueError naming a thin cell |
| `ctx.loss_with_masked_slots(L, slots, half="test", subjects=None, sample=True)` | `{slug: loss, "pile_avg": loss}` with `slots` off (renormalize=False), through the same held-out pass heldout_quality uses; the sample by default |
| `ctx.fact_recall_with_masked_slots(L, slots, rows)` | per-row DataFrame (fact_id, tier, role, attribute, top1, rank, margin) through the same `ProbeSet.score` fact_recall uses |

The shared held-out pass gained `half`, `subjects` and `capture_reads`
arguments, and its cache key includes them. `masked_slots` now also clears
that cache when it is entered, so a masked query can never be answered from an
unmasked pass. `data/q2_probe.py` got one line (`out["_margin"] = margin`), so
the per-row margin is available; nothing else in it changed.

The docs are in `docs/metrics_interface.md` (about two pages). The test kit is
`memlayers.eval.testkit`:
- `metric_kit`, a session-scoped pytest fixture: a tiny PKM run (d64, 3 layers,
  PKM 16×16, trained 10 steps) on a miniature bundle cut from the committed
  `data/v1_sample/` (test and label halves, bios), with tiny eval sets and read
  logs for steps 0 and 10. It builds in about 5 s on CPU.
- `kit.run_metric(fn)` runs a metric as the framework does and asserts the
  contract: flat floats, slash keys, model unchanged, no mask left on.
- `kit.context(step)` gives an EvalContext on the kit run.
- `temporary_metric(...)` registers a metric for one test only.

The worked example in the docs (`top_slot_share`) is a real test. It runs
through the kit, `memlayers.evaluate` (evals.csv rows and `update_final`) and
`memlayers.compare` (a `runs.csv` column).

## 4. Masked-slot timing

T1-pkm step 300 on MPS, 100 random used slots of layer 3. 59,468 of the
65,536 slots are used in the read log. Times are from `perf_counter`.

| call | time |
|---|---:|
| `ctx.used_slots(3)` (scans the 5.7M-token log) | 1.1 s |
| `ctx.matched_random_slots(3, 100 slots, 100, rng)` | 1.1 s |
| `loss_with_masked_slots(3, [])`, sample (1,200 docs, 1.87M tokens, 6 subjects) | 51.9 s |
| `loss_with_masked_slots(3, 100 slots)`, sample, 6 subjects | **83.5 s** |
| `loss_with_masked_slots(3, 100 slots, subjects=["pile_cc"])`, sample | 5.8 s |
| `loss_with_masked_slots(3, 100 slots, sample=False)`, the full test half (15M tokens) | **448.8 s** |
| `fact_recall_with_masked_slots(3, 100 slots, fact_sample)` (36,000 rows) | 56.3 s |

The unmasked sample loss, `pile_avg` 6.27744, equals the run's own final
`loss/pile_avg_sample` to the printed precision. The masked passes cost about
60% more than the unmasked one: the masking pre-hook rewrites the gate weights
of every read.

**What this means for the removal tests.** Each masked evaluation is a full
forward over its token set, so cost scales with (number of slot sets) ×
(tokens per evaluation):
- **subject_removal (E1):** one masked pass per subject's slot set, plus
  matched-random control sets. On the sample with only the subjects that
  matter, a pass is short (pile_cc alone: 5.8 s; all 6 subjects: 84 s).
  So 5 subject sets × (1 + 10 random controls) × all 6 subjects ≈ 55 × 84 s ≈
  1.3 h per checkpoint. Restricting each pass to the target subject plus one
  reference cuts that to about 10–15 min. The full test half (≈ 450 s a pass)
  is affordable only for a handful of headline numbers.
- **fact_core_set (E2):** one fact pass is 56 s on the 36,000-row sample, and
  a few seconds on just the rows a core set concerns. A per-fact or per-person
  search (many slot sets) has to run on small row subsets, or batch several
  masks into one sweep. Neither is offered yet (see §6).
- Across Phase 1's 4 memory runs, multiply the per-checkpoint figure by 4.

## 5. Test count

**342 before → 359 after** (+17 in `tests/test_metrics_interface.py`), all
passing on CPU in about 1.6 min. Black is clean. The prompt-2 tests now get
their miniature bundle from the kit (`tests/_eval_fixtures.py` re-exports it).

- Worked example (2): `run_metric`, then `memlayers.evaluate` (EX1 rows in
  evals.csv, `update_final`), then compare's `runs.csv` (with the
  `readlog_tokens_sha256` column).
- A read-log metric is skipped (not failed) with the pass command when the log
  is missing; `ctx.readlog()` raises the clear error.
- The read log equals live reads for steps 0 and 10: held-out windows and a bio
  row, indices exact, weights within 1e-3 (fp16; the pass batches 8 windows,
  the check runs one, so a weight can land one fp16 step away).
- tokens.parquet:
  - every held-out input position is present once, and the token ids
    round-trip to label.bin;
  - each bio prompt is `prompt + value_token_ids`, with exactly one
    `is_answer_position` at `len(prompt) - 1`;
  - the value tokens decode to `" " + true_value`;
  - the manifest fields are present.
- The reader: `select` with lists, `slot_counts` weighted and not, and
  `iter_chunks` with and without rows all agree with brute force; the memmaps
  are read-only; an unknown column raises.
- uint16 at ≤ 65,536 slots and uint32 above, round-tripped through the writer
  and reader with a 70,000-slot layer.
- Refusals: a dense run; an existing log without `force`; too little disk; a
  budget mismatch (names the rebuild flag).
- `value_table` and `unembedding` are copies (zeroing them leaves the model
  intact); `used_slots`.
- `matched_random_slots`: exactly the input's cell proportions (2× for
  n = 2 × len), no overlap, deterministic per seed, differs across seeds, and a
  thin cell raises naming it.
- `loss_with_masked_slots`: with an empty mask it equals heldout_quality
  exactly. After fitting the value table to pile_cc's sample documents,
  masking the slots those documents read raises their loss by more than 0.1,
  and the model is unchanged and no mask is left.
- `fact_recall_with_masked_slots`: unmasked ranks equal `ProbeSet.score`, and
  masking the used slots changes the margins.

## 6. Anything I could not follow, and open questions

1. **"A seeded 10% of the normal, rare and control tiers"** is read as 10% of
   the *people* of each tier, with all their prompts. So per-person analyses
   see complete people. 10% of prompts would scatter them.
2. **The logged rows are model inputs.** Each read belongs to the token at
   that position; the position's next-token prediction is what it supports.
   Held-out documents therefore log n − 1 positions. For bio rows, the read at
   `is_answer_position` is the one that predicts the value's first token, and
   the reads at `is_value_token` positions are the value's own tokens being
   read in.
3. **Held-out windows are grouped by length within each subject**, so equal
   windows batch (8 per forward). File order is subject → window length →
   document. Every row carries doc_id and position, so order never needs
   reconstructing. Bio prompts run one per row, as specified.
4. **The pass's time includes the sha256 of every file** (the manifest asks
   for them). I did not time that step on its own.
5. **What the analysis metrics will still need, not yet provided:**
   - **The final LayerNorm for the logit lens.** `ctx.unembedding()` is the
     raw head; a metric applies `ctx.model.transformer.ln_f` itself. A
     `ctx.logit_lens(vectors)` helper would make every metric do it the same
     way.
   - **Batched masking for many slot sets.** Every
     `loss_with_masked_slots` call is one full pass. E1 and E2 with many
     random controls will want either several masks evaluated in one sweep, or
     per-document loss caching so only documents that read a masked slot are
     re-run. The read log already says which documents read which slots, so
     the second is possible.
   - **Masked loss on the read-log tokens themselves** (the label half),
     e.g. for a subject's slots on that subject's label documents. The helper
     takes `half="label"`, which runs the whole label half, but not "only the
     read-log documents".
   - **Per-token or per-document losses.** The helpers return per-subject
     means; E1-style significance tests may want the per-document
     distribution.
   - **PEER.** `value_table` returns the up-embedding. A PEER expert also has
     a down vector and a GELU, so "what a slot writes" is input-dependent;
     PEER is not in Phase 1.
6. **Masking cost.** The masked passes cost about 60% more than the unmasked
   one (the pre-hook replaces the weights tensor on every read). Fine at these
   sizes; worth profiling if E1 runs become the bottleneck.
7. **Read-log size.** At 2.95 GB per checkpoint, the pilot (prompt 5) can
   lower `eval.readlog.tokens_per_subject` if the metrics need less. That
   changes the readlog_tokens hash, as intended.
