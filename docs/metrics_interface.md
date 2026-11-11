# Writing an analysis metric

How an analysis metric plugs into the training code: `subject_specificity`
(U4), `subject_removal` (E1), `fact_core_set` (E2), `read_concentration` (V2),
`slot_inspection` (C4), `effective_rank` (C6). A metric is one function; the
framework finds its inputs, runs it, and files its numbers.

## The function and its decorator

```python
from memlayers.eval import register_metric

@register_metric(
    "subject_specificity",          # meaningful snake_case name: the column, the W&B key
    metric_id="U4",                 # the methodology's short id, kept beside it
    stages=("posthoc",),            # any of "during", "final", "posthoc"
    needs_memory=True,              # skipped, with the reason recorded, on a dense run
    inputs=("model", "readlog"),    # any of model, heldout, fact_probe, init_model, readlog
)
def subject_specificity(ctx) -> dict[str, float]:
    ...
```

The name must be one of the reserved names above (with its id), or a new one.
`training_check` cannot be registered. Put the file in `memlayers/eval/metrics/`
and import it in that package's `__init__.py`.

**Rules.**
- **Deterministic** for a given seed. Use `ctx.generator` and `ctx.np_rng`,
  never global RNG.
- **Leaves the model exactly as it found it.** Use `ctx.masked_slots`, never
  `set_mask_slots` by hand. Never change weights.
- **CPU-safe.**
- **Returns a flat dict of floats** with slash-path keys
  `<quantity>/<subset>`: `share/bio/layer3`, `drop/pile_cc`.
- **Big outputs** (tables, per-slot arrays, figures) go to
  `ctx.artifact_dir` (= `<run_dir>/analysis/<name>/`), not into the dict.
- **Never raises because an input is missing.** The framework checks `inputs`
  and `needs_memory` first and records why a metric was skipped. A metric
  listing `"readlog"` is skipped, with the command to run, when the checkpoint
  has no read log.

## What `ctx` (EvalContext) offers

| | |
|---|---|
| `ctx.model` | in eval mode, under `torch.no_grad`, on `ctx.device` |
| `ctx.config`, `ctx.run_dir`, `ctx.step`, `ctx.tokens_seen`, `ctx.stage` | the resolved run config and where/when this evaluation is |
| `ctx.generator`, `ctx.np_rng` | seeded from `eval.seed` (never the run seed) |
| `ctx.memory_layers` | `{layer: MemoryLayer}`; `n_slots`, `n_heads`, `topk` |
| `ctx.heldout(half, sample)` | `{slug: [HeldoutDoc(doc_id, start, length)]}` |
| `ctx.fact_probe(sample)` | the tokenized fact prompts (`data.q2_probe.ProbeSet`) |
| `ctx.heldout_pass(...)` | one shared, cached forward over held-out text (loss sums, slot usage) |
| `ctx.init_model()` | the run's step-0 weights in a second model |
| `ctx.readlog(step=None)` | the read log of this checkpoint (below) |
| `with ctx.masked_slots({layer: ids}):` | slots off (weight 0, no renormalization), always restored |

**Helpers** shared by several analysis metrics:

| helper | returns |
|---|---|
| `ctx.value_table(layer)` | `[n_slots, d]` fp32 CPU copy of what each slot writes (PKM values; PEER up-embedding) |
| `ctx.unembedding()` | `[vocab, d]` fp32 CPU copy of the output head, for the logit lens (`ctx.model.transformer.ln_f` is the final norm) |
| `ctx.used_slots(layer)` | slots read at least once in the read log |
| `ctx.slot_bins(layer, n_bins=10)` | (used slots, read-count decile, value-norm decile) |
| `ctx.matched_random_slots(layer, slots, n, rng, n_bins=10)` | `n` used slots, not in `slots`, drawn from the same (count decile, norm decile) cells in the same proportions; `ValueError` naming a cell that is too thin |
| `ctx.loss_with_masked_slots(layer, slots, half="test", subjects=None, sample=True)` | `{slug: loss, "pile_avg": loss}` with `slots` off; the 200-doc sample by default; `sample=False` = the whole half, slow |
| `ctx.fact_recall_with_masked_slots(layer, slots, rows)` | DataFrame per fact row: fact_id, tier, role, attribute, top1, rank, margin, with `slots` off |

## The read log (`memlayers.readlog.ReadLog`)

`python -m memlayers.readlog_pass run_dir=runs/pkm-s0 step=[init,final]` writes
`<run_dir>/readlogs/step_<6d>/`. It covers the fixed `readlog_tokens` set:
held-out LABEL-half documents of the 5 training subjects (1M tokens each), and
fact prompts (every frequent-tier person, 10% of each other tier; each prompt
followed by its true value's tokens).

| | |
|---|---|
| `rl = ctx.readlog()` / `ReadLog.open(dir)` | |
| `rl.layers`, `rl.n_slots(L)`, `rl.n_tokens` | |
| `rl.tokens` | DataFrame, one row per token: token_id, segment (`heldout_label`\|`bio`), doc_id, subject, position; for bio: person_id, tier, attribute, fact_id, role, template_id, is_answer_position, is_value_token |
| `rl.indices(L)`, `rl.weights(L)` | read-only memmaps `[n_tokens, heads, topk]` (uint16/32; fp16 post-softmax weights) |
| `rl.select(**filters)` | row ids; values or lists: `rl.select(segment="bio", tier=["rare","normal"], is_answer_position=True)` |
| `rl.slot_counts(L, rows=None, weighted=False)` | `np.ndarray[n_slots]` of reads (or summed weights) |
| `rl.iter_chunks(L, rows=None, chunk_tokens=1_000_000)` | `(row_ids, indices, weights)` chunks; never load it all |

## Running it, and where results land

```bash
python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final metrics=[subject_specificity]
python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final metrics=[subject_specificity] update_final=true
python -m memlayers.compare runs/ --out reports/compare/
```

- `evals.csv` gets one row per key, `stage=posthoc`, with `metric` and
  `metric_id`.
- `final_metrics.json` changes only with `update_final=true`. The new
  metric is merged in under `<name>/<key>`: other metrics stay, and the step
  must be the file's step.
- `analysis/<name>/` holds whatever the metric wrote to `ctx.artifact_dir`.
- W&B gets `posthoc/<name>/<key>` (job_type `eval`) if the run mirrors to W&B.
- `memlayers.compare` puts it into `runs.csv` and `groups.csv` as
  `<name>/<key>`, and into the X2 table. Keys of U4, E1, E2 and V2 are flagged
  as main tests there.

## Testing it: the kit

`memlayers.eval.testkit` builds a tiny trained PKM run with read logs at steps
0 and final (seconds, CPU, from the committed `data/v1_sample/`).
`kit.run_metric(fn)` runs a metric as the framework does and checks the rules
above.

## Worked example (a real test: `tests/test_metrics_interface.py`)

```python
import numpy as np
from memlayers.eval.testkit import metric_kit, temporary_metric  # noqa: F401

def top_slot_share(ctx):
    """Share of the gate weight that goes to the 1% most-read slots, per segment."""
    rl = ctx.readlog()
    out = {}
    for layer in rl.layers:
        for seg in ("heldout_label", "bio"):
            c = rl.slot_counts(layer, rl.select(segment=seg), weighted=True)
            k = max(1, len(c) // 100)
            out[f"top1pct_share/{seg}/layer{layer}"] = float(np.sort(c)[::-1][:k].sum() / c.sum())
    return out

def test_top_slot_share(metric_kit):
    with temporary_metric("example_top_slot_share", metric_id="EX1",
                          inputs=("model", "readlog"), needs_memory=True) as register:
        register(top_slot_share)
        out = metric_kit.run_metric(top_slot_share)
        assert 0 < out["top1pct_share/bio/layer1"] <= 1
```

The test then runs it through `memlayers.evaluate` and `memlayers.compare`.
Register real metrics in the package, not inside tests.
