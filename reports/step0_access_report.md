# Step 0 — Confirm Access

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date run:** 2026-10-24 / 2026-10-25
**Machine:** Apple M5 Pro, macOS 26.6.2, 64 GB unified memory
**Nothing was trained.** Every number below comes from a re-runnable script in `step0_access/`; raw JSON is in `logs/`.

---

## 1. Summary — one line per checklist item

| # | Item | Status |
|---|---|---|
| ENV | Python 3.12 venv, all packages installed, versions pinned | **PASS** |
| ENV | PyTorch MPS backend available **and** verified with a real matmul | **PASS** |
| ENV | Hugging Face login (`roieg`) | **PASS** |
| A1 | Stream `monology/pile-uncopyrighted`, 50k docs, per-subject counts + tokens | **PASS** |
| A2 | Subject list and recommended 4–5 domain training mix | **PASS** |
| A3 | Disk estimate for uint16 token arrays (150M / 0.5B + held-out) | **PASS** |
| A4 | `MBZUAI-LLM/SlimPajama-627B-DC` streams with a source label | **PARTIAL** — repo deleted from the Hub; public mirror works |
| A5 | Stream Wikipedia, FineWeb-Edu, Cosmopedia samples | **PASS** |
| B1 | MoLE-160M-4E: load, reparameterize, forward pass, locate LUTs | **PASS** — needs a 2nd venv (transformers 4.38.2) |
| B2 | Community PEER model: find final checkpoint, load, forward, locate experts+keys | **PASS** |
| B3 | sparse-memory-lm B-16M: file sizes, 4-bit table header, numpy path | **PASS** — no >2 GB download needed |
| B4 | LongCat / DeepSeek-V4.1: are the memory tables separately downloadable? | **PASS** — DeepSeek yes, LongCat no (but range-fetchable) |
| C1 | `product-key-memory` 65,536 slots: fwd/bwd on MPS, grads reach keys+values | **PASS** |
| C1 | Read the selected top-k slot indices | **PASS** — no source change needed (forward pre-hook) |
| C2 | `PEER-pytorch` 65,536 experts: fwd/bwd on MPS, grads reach keys+values | **PASS** |
| C2 | Read the selected expert indices | **PASS** — no source change needed (forward pre-hook) |
| C3 | Freeze keys only (random-key twin), verified over one optimizer step | **PASS** — both layers |
| C4 | faiss-cpu: 1M × 256 flat IP index + IVFPQ, 1k × top-32 search | **PASS** |
| C5 | `tools/bio_generator.py` — bioS-style fake biographies + QA | **PASS** |
| D | Tiny 2-layer transformer trains 20 steps on MPS (plain / PKM / PEER) | **PASS** |
| D | Colab, Kaggle, Modal, Drive/HF checkpoints, GitHub, cluster ask | **MANUAL** — checklist in §7 |

**Nothing blocks step 1.** Two items need a decision from you before step 1 starts (§8).

---

## 2. Detailed results table

| Item | Status | Evidence | Fix / replacement |
|---|---|---|---|
| Python / venv | PASS | `conda create -p .venv python=3.12` → **Python 3.12.14**. No `uv`, no system 3.11/3.12 (only conda 3.14 and brew 3.13), so conda created the prefix env at `.venv`. | — |
| Package install | PASS | `requirements.txt`: torch 2.14.1, transformers 5.20.2, datasets 5.1.0, huggingface_hub 2.3.0, accelerate 1.15.0, numpy 2.5.4, tqdm 4.70.1, product-key-memory 0.3.0, PEER-pytorch 0.2.2, faiss-cpu 1.15.1, tiktoken 0.14.0 | — |
| `zstandard` missing | fixed | Pile stream died with `ValueError: Compression type zstd not supported`. The Pile shards are `.jsonl.zst` and `datasets` does **not** pull zstandard in. | `pip install zstandard==0.25.0`, now pinned in `requirements.txt` |
| MPS | PASS | `torch.backends.mps.is_available() = True`, `is_built() = True`, `cuda.is_available() = False`. A 512×512 matmul on `mps` returns finite values. | — |
| HF login | PASS | `huggingface_hub.whoami()` → **`roieg`**. Note: `huggingface-cli` is gone in hub ≥1.0; the command is now `hf auth whoami`. | — |
| A1 Pile stream | PASS | 50,000 docs in **16.5 s = 3,023 docs/s** (4.87M tok/s), 3.67 s to open the stream. **80,504,221** GPT-2 tokens, **17** subjects. `data_samples/pile_sample.jsonl` = 7.6 MB (2,680 docs, text capped at 5,000 chars). | — |
| A4 SlimPajama | PARTIAL | `MBZUAI-LLM/SlimPajama-627B-DC` → `404 Repository not found` **even with a valid token**; the web page returns 401. Its upstream `cerebras/SlimPajama-627B` is **also 404**. The whole SlimPajama family looks withdrawn (same copyright reason the Pile needed an "uncopyrighted" variant). | Fell back to **`venketh/SlimPajama-62B`**: streams, 2,175 docs/s, 1,000 records read, label in `meta['redpajama_set_name']`, 7 labels seen. `DKYoon/SlimPajama-6B` also works as a smaller option. |
| A5 Wikipedia | PASS | `wikimedia/wikipedia`, `20231101.en` — 200 docs, 48.7 docs/s, 6,762 tok/doc, keys `id/text/title/url`. 912 KB sample. | — |
| A5 FineWeb-Edu | PASS | `HuggingFaceFW/fineweb-edu`, `sample-10BT` — 200 docs, 96.7 docs/s, 838 tok/doc. 550 KB sample. | — |
| A5 Cosmopedia | PASS | `HuggingFaceTB/cosmopedia`, `web_samples_v2` — 200 docs, 44.5 docs/s, 734 tok/doc. 768 KB sample. | — |
| B1 MoLE | PASS | Repo 780 MB. Training form 388.8M params loads on MPS, forward 0.55 s, top-1 next token **" Berlin"** for "…capital of Germany is". Reparameterization 5.2 s. Inference form 2.02B params, forward **0.021 s** on MPS, **max abs logit diff 3e-5** vs. the training form and identical argmax. | Needed `.venv-mole` (`transformers==4.38.2`). On transformers 5.20.2 it dies at `AttributeError: 'LlamaConfig' object has no attribute 'rope_theta'`. See §5. |
| B2 PEER model | PASS | Final checkpoint = **`checkpoints/final_113738.pt`** (2.93 GB = 2.73 GiB, approved for download; the other 7 checkpoints, 20.5 GB, were skipped). step 113738, **`valid_ce` 3.7246** (the checkpoint's own value; the README's headline table says 4.0317 — see §5.2), 1,162,402,360 tokens. Forward on **MPS** 0.785 s → logits `[1,16,32000]`, finite. | Repo scripts define no `forward()`; entry point is `model.features(ids)` → `(h, balance, rows)` then `model.head2(h)`. Also `sys.path.insert(0,'/root/dna')` is hardcoded — override with the snapshot's `scripts/` dir. |
| B3 sparse-memory-lm | PASS | Repo 3.67 GB: `values_q4.bin` 3.22 GB, `rest.pt` 284 MB, `hot_rows.npy` 134 MB, `scales_q4.bin` 34 MB, `meta.json` 1 KB. `values_q4.bin` is over the 2 GB threshold → per your choice, **header-only**: HTTP `206` range read of the first 4,096 rows + the 34 MB scales file. Codes all in [0,15], histogram bell-shaped around 8; dequantized stats mean 0.00059, std 0.0922, absmax 0.814, all finite. | Full model deliberately not run (needs the repo's CUDA/ROCm Triton kernels). Colab T4 notes in §5. |
| B4 DeepSeek-V4.1 | PASS | Repo 510.31 GB / 90 files / 96,085 tensors. The `engram` tensors sit in **2 dedicated shards (47, 48) that contain nothing else** — **203.07 GB**. | **Separately downloadable: YES.** |
| B4 LongCat | PASS | Repo 138.19 GB / 41 files / 11,160 tensors. 12 `ngram_embeddings.embedders.*` tables of **5.23 GB** each (**62.83 GB total**) are each in a *different* shard, mixed with ordinary layer weights. | **Separately downloadable: NO** — but each tensor's exact byte range is in the safetensors header, so a single 5.23 GB table can be pulled with one HTTP Range request. Verified by reading the headers. |
| C1 PKM | PASS | 65,536 slots, 34.3M params. Forward 0.64 s, backward 0.75 s on MPS. Grad norms: `keys` 2.9e-5 (262,016 nonzero), `values.weight` 3.4e-5 (12.9M nonzero). | — |
| C1 index read-out | PASS | Forward pre-hook on `pkm.values` captured indices `[256, 128]` = `[(b·t), (heads·topk)]`, int64, range 8…65,531, 25,292 unique slots in one batch, plus gate weights `[256,128]`. | No package change needed. Minimal source change documented in §6 if we prefer it. |
| C2 PEER | PASS | 65,536 experts, 67.4M params. Forward 0.34 s, backward 0.23 s on MPS. Grad norms: `keys` 1700.0, `weight_down_embed.weight` 72.9, `weight_up_embed.weight` 8.50. | — |
| C2 index read-out | PASS | Forward pre-hook on `peer.weight_down_embed` captured indices `[2,128,8,1]`, int64, range 13…65,535, 2,006 unique experts. | **Gotcha:** default `non_competing_scores=True` forces `num_experts_per_head_topk = 1`, so only `heads × 1 = 8` experts are active per token, not `heads × 16 = 128`. Pass `non_competing_scores=False` for 16/head. |
| C3 freeze keys | PASS | PKM: `keys` bit-identical after one Adam step (max change **0.0**, `keys.grad is None`), `values.weight` changed by 9.54e-3, `to_queries` by 9.86e-3. PEER: `keys` bit-identical, `weight_down`/`weight_up` both changed by 1.00e-2. | — |
| C4 faiss flat | PASS | 1M × 256 fp32 (1.024 GB). `IndexFlatIP` build **0.088 s**, 1,000 × top-32 search **0.45 s** (0.45 ms/query, 2,222 qps), RSS 2.10 GB, 18 threads. | — |
| C4 faiss IVFPQ | PASS | `nlist=4096, m=32, nbits=8`: train 9.02 s + add 4.89 s = **13.91 s** build, codes 32 MB (**32× compression**), RSS 2.38 GB. Search: 0.012 s @ nprobe=32 (82,040 qps), 0.025 s @ nprobe=128. | **Recall is 2.3–8.7%** — but that is an artifact of *random Gaussian* vectors, which have no cluster structure for PQ to exploit. Do not read this as a verdict on IVFPQ; re-measure recall on real kNN-LM key vectors in step 1. |
| C5 bio generator | PASS | 1,000 people → `data_samples/bios_sample.jsonl` (2.1 MB), 1,000 unique names, 0 duplicates. Byte-identical across runs at the same seed. 5 attributes, **7 templates each**, 3 question phrasings each. | — |
| D MPS training | PASS | 20 steps, 2-layer LM, overfitting one fixed batch: plain 536k params, loss **6.43 → 0.17**; PKM-65536 8.89M params, **6.38 → 0.20**; PEER-65536 17.4M params, **6.40 → 2.92**. All losses finite, 0.007–0.012 s/step, MPS alloc 1.12 GB. | PEER's smaller drop is the `non_competing_scores` issue above — only 4 experts active/token in that config. |
| Disk | PASS | Free on home volume: **1,844.3 GB before → 1,843.0 GB after**. HF cache 3.8 GB (2.93 GB B2 checkpoint + 780 MB MoLE + 34 MB B3 scales + small files), `.venv` 1.2 GB, `.venv-mole` 926 MB, `data_samples` 14 MB, `external` 6.1 MB, `logs` 232 KB. | — |

---

## 3. Environment

| | |
|---|---|
| macOS | 26.6.2 (build 25G83) |
| Chip | **Apple M5 Pro**, 18 cores |
| RAM | 68.7 GB (64 GiB) unified |
| Free disk (home volume) | **1,844.3 GB before → 1,843.0 GB after** (`os.statvfs`; `df -h` shows 117 GiB → 119 GiB used) |
| Python | 3.12.14 (conda), venv at `final_project/.venv` |
| `torch.backends.mps.is_available()` | **True** |
| `torch.backends.mps.is_built()` | True |
| `torch.cuda.is_available()` | False (expected — no CUDA on Apple Silicon) |
| MPS verified | 512×512 matmul on `mps` returned finite values |
| HF user | `roieg` |

Pinned versions — `requirements.txt` (main) and `requirements-mole.txt` (B1 only):

```
torch==2.14.1              transformers==5.20.2       datasets==5.1.0
huggingface_hub==2.3.0     accelerate==1.15.0         numpy==2.5.4
tqdm==4.70.1               product-key-memory==0.3.0  PEER-pytorch==0.2.2
faiss-cpu==1.15.1          tiktoken==0.14.0           zstandard==0.25.0
einops==0.8.2              tokenizers==0.23.3         safetensors==0.8.0
```

Two notes worth carrying forward:

- **`uv` is not installed** and there is no system Python 3.11/3.12 (only conda 3.14 and Homebrew 3.13), so the venv is a **conda prefix env** at `.venv`. It behaves like a venv (`.venv/bin/python`, `.venv/bin/pip`), so nothing downstream changes.
- **`huggingface-cli` no longer exists** in `huggingface_hub` 2.3.0. The command is `hf auth whoami` / `hf auth login`. Worth fixing in the roadmap text.

---

## 4. Data findings

### 4.1 A1 — the Pile, uncopyrighted: 50,000 streamed documents

```python
from datasets import load_dataset
ds = load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)
for rec in ds:
    subject = rec["meta"]["pile_set_name"]
    text    = rec["text"]
```

**3,022.9 docs/s** (4.87M GPT-2 tok/s), 3.67 s to open the stream, 80,504,221 tokens over 50,000 docs (1,610 tok/doc mean), **17 subjects**. The stream is interleaved across subjects from the start, so no shuffling is needed to get a mixed sample.

| Subject | Docs | % docs | GPT-2 tokens | % tokens | tok/doc | Saved to sample |
|---|---:|---:|---:|---:|---:|---:|
| PubMed Central | 1,555 | 3.11 | 15,780,528 | **19.60** | 10,148.2 | 200 |
| Pile-CC | 14,939 | 29.88 | 15,138,982 | **18.80** | 1,013.4 | 200 |
| Github | 5,170 | 10.34 | 11,895,420 | **14.78** | 2,300.9 | 200 |
| ArXiv | 641 | 1.28 | 11,092,636 | **13.78** | 17,305.2 | 200 |
| StackExchange | 8,292 | 16.58 | 6,264,513 | 7.78 | 755.5 | 200 |
| FreeLaw | 1,408 | 2.82 | 5,400,008 | **6.71** | 3,835.2 | 200 |
| Wikipedia (en) | 4,767 | 9.53 | 3,517,337 | **4.37** | 737.9 | 200 |
| USPTO Backgrounds | 3,095 | 6.19 | 2,625,578 | 3.26 | 848.3 | 200 |
| PubMed Abstracts | 8,264 | 16.53 | 2,399,507 | 2.98 | 290.4 | 200 |
| DM Mathematics | 549 | 1.10 | 2,167,818 | 2.69 | 3,948.7 | 200 |
| Gutenberg (PG-19) | 17 | 0.03 | 1,908,025 | 2.37 | 112,236.8 | **17** |
| EuroParl | 34 | 0.07 | 944,853 | 1.17 | 27,789.8 | **34** |
| HackerNews | 444 | 0.89 | 548,286 | 0.68 | 1,234.9 | 200 |
| Ubuntu IRC | 10 | 0.02 | 240,392 | 0.30 | 24,039.2 | **10** |
| NIH ExPorter | 517 | 1.03 | 226,029 | 0.28 | 437.2 | 200 |
| PhilPapers | 19 | 0.04 | 197,958 | 0.25 | 10,418.8 | **19** |
| Enron Emails | 279 | 0.56 | 156,351 | 0.19 | 560.4 | 200 |

Four subjects could not reach 200 docs in 50k records (Gutenberg 17, EuroParl 34, PhilPapers 19, Ubuntu IRC 10) — they are rare per-document, though Gutenberg carries 2.37% of tokens because its documents are enormous.

### 4.2 A2 — recommended training mix

**Recommended 5 domains** — maximally distinct, all large, all cheap to stream:

| Domain | Pile subject | % of Pile tokens | Docs to stream for 30M tokens |
|---|---|---:|---:|
| Code | **Github** | 14.78 | 126,099 |
| Web | **Pile-CC** | 18.80 | 99,082 |
| Medical papers | **PubMed Central** | 19.60 | 95,054 |
| Legal | **FreeLaw** | 6.71 | 277,777 |
| Encyclopedic | **Wikipedia (en)** | 4.37 | 426,459 |

Together **64.26%** of Pile tokens. Rationale: these five are the ones with genuinely different surface form *and* different vocabulary — code tokens, web prose, biomedical terminology, legal citation style, encyclopedic prose. That is what makes "which values does which domain use" a measurable question.

Deliberate exclusions:
- **ArXiv** (13.78%) is large but overlaps PubMed Central heavily in register (LaTeX-ish academic prose) — it dilutes the contrast. Keep it as a 6th domain if we want more separation on *notation* specifically.
- **StackExchange** (7.78%) straddles code and web; it would blur the Github/Pile-CC boundary.
- **DM Mathematics** (2.69%) is synthetic and extremely repetitive — interesting as a *probe* for degenerate memory use, but a bad training-mix member.

**Too small for comfortable 1–10M held-out tokens per subject.** No subject is too small in absolute terms. Sizing the whole split: the train split is **334.7 GB zstd-compressed** (34 files) and we measured **3.358 chars per GPT-2 token**, so at a conservative 3× text compression ratio that is ~1.0 TB uncompressed ≈ **300B GPT-2 tokens** (≈350B at 3.5×, ≈400B at 4×). Applying the measured per-subject token shares, even the smallest subject (Enron Emails, 0.19%) holds ~0.6B tokens — about 60× the largest held-out set we would ever want. The real constraint is *streaming cost* — documents you must pull off the mixed stream to accumulate the held-out set:

| Subject | Docs to stream for 10M held-out tokens | Verdict |
|---|---:|---|
| PubMed Central, Pile-CC, Github, ArXiv | 32k – 45k | cheap (~15 s each) |
| StackExchange, FreeLaw, Wikipedia (en) | 80k – 142k | fine (~30–50 s) |
| USPTO, PubMed Abstracts, DM Mathematics, Gutenberg | 190k – 262k | acceptable (~1–1.5 min) |
| EuroParl | 529k | slow (~3 min) |
| HackerNews | 912k | slow (~5 min) |
| **Ubuntu IRC, NIH ExPorter, PhilPapers, Enron Emails** | **2.1M – 3.2M** | **avoid** — ~12–18 min of streaming each for 10M tokens; cap these at **1M** held-out tokens instead |

(Estimated available tokens per subject, at ~300B for the split: PubMed Central 59B, Pile-CC 56B, Github 44B, ArXiv 41B, StackExchange 23B, FreeLaw 20B, Wikipedia (en) 13B, down to Enron Emails 0.6B.)

All five recommended domains are in the two cheapest rows. At 3,023 docs/s, the whole held-out collection for the recommended mix (10M tokens each) costs about 7 minutes of streaming.

### 4.3 A3 — disk estimate

GPT-2 vocab is 50,257, which fits in **uint16 → 2 bytes/token** (uint32 would be 4).

| Corpus | Tokens | uint16 size |
|---|---:|---:|
| Training set, small | 150,000,000 | **0.30 GB** |
| Training set, large | 500,000,000 | **1.00 GB** |
| Held-out, 1M tokens | per subject | 0.002 GB (2 MB) |
| Held-out, 10M tokens | per subject | 0.020 GB (20 MB) |
| Held-out, 5 subjects × 10M | 50,000,000 | 0.10 GB |
| **Total, 0.5B train + 5×10M held-out** | | **≈ 1.10 GB** |

Negligible against 1,841 GB free. Even with a 2× margin for shuffled/duplicated copies and an index, a full experiment set stays well under 5 GB. The real disk consumers are model weights (B2's checkpoint alone is 2.93 GB) and, if we ever reparameterize MoLE to disk, 3.45 GB per model.

### 4.4 A4 — SlimPajama backup (PARTIAL)

The roadmap's repo is gone:

```
MBZUAI-LLM/SlimPajama-627B-DC  -> 404 Repository not found (authenticated), 401 on the web page
cerebras/SlimPajama-627B       -> 404 Repository not found (authenticated)
```

Both the target and its upstream are withdrawn. Working replacement, same per-source labels:

```python
ds = load_dataset("venketh/SlimPajama-62B", split="train", streaming=True)
label = rec["meta"]["redpajama_set_name"]
```

1,000 records in 0.5 s (2,175 docs/s). Record keys `['meta','text']`. Source label present on **every** record. Labels seen: `RedPajamaC4` 562, `RedPajamaCommonCrawl` 317, `RedPajamaStackExchange` 47, `RedPajamaWikipedia` 41, `RedPajamaGithub` 30, `RedPajamaArXiv` 2, `RedPajamaBook` 1. `DKYoon/SlimPajama-6B` also works if a smaller mirror is preferable.

### 4.5 A5 — corpora the public models were trained on (all PASS)

```python
load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True)
load_dataset("HuggingFaceFW/fineweb-edu", "sample-10BT", split="train", streaming=True)
load_dataset("HuggingFaceTB/cosmopedia", "web_samples_v2", split="train", streaming=True)
```

200 documents each saved to `data_samples/{wikipedia,fineweb_edu,cosmopedia}_sample.jsonl`. Both sub-config names matter: plain `fineweb-edu` is the full multi-TB set, and `cosmopedia` requires a config. This covers the training data of both B2 (FineWeb-Edu + Cosmopedia) and B3 (Wikipedia 20231101.en), so we can compare value usage against in-distribution text.

---

## 5. Model findings — load code and memory-table tensors

### 5.1 B1 — MoLE-160M-4E (PASS)

Repo files: `model.safetensors` 777.5 MB, `tokenizer.json` 2.1 MB, + configs = **780 MB total** (under the 2 GB threshold, downloaded without asking). The HF repo holds the **pre-reparameterization (training) weights only**, as the README states.

```python
import sys, torch; sys.path.insert(0, "external/MoLE")   # github.com/JieShibo/MoLE
from transformers import AutoTokenizer
from modeling_mole import MoleForCausalLM                          # training form
from modeling_mole_rep import MoleForCausalLM as MoleForCausalLM_rep   # inference form

tok   = AutoTokenizer.from_pretrained("JieShibo/MoLE-160M-4E")
model = MoleForCausalLM.from_pretrained("JieShibo/MoLE-160M-4E",
                                        torch_dtype=torch.float32,
                                        attn_implementation="eager").to("mps")
out   = model(**tok("The capital of France is Paris, and the capital of Germany is",
                    return_tensors="pt").to("mps"))
```

Reparameterization (`reparameterize.py`, with `device_map="cuda"` → MPS and no `save_pretrained`):

```python
with torch.no_grad():
    output_all = []
    for layer in model.model.layers:
        token_embeds = layer.expert_layernorm(model.model.embed_tokens.weight)   # [V, d]
        output_layer = torch.stack([expert(token_embeds) for expert in layer.experts], dim=1)
        output_all.append(output_layer.cpu())                                    # [V, E, d]
    output_all = torch.stack(output_all, dim=1).reshape(output_all[0].size(0), -1)  # [V, L*E*d]
model_rep.load_state_dict({"model.moe_table.weight": output_all}, strict=False)
```

| | |
|---|---|
| Config | vocab 50,304, hidden 768, layers 12, **experts 4**, intermediate 3,072, heads 12 |
| Params, training form | 388,759,296 |
| Params, inference form | **2,016,664,320** |
| Load (CPU) / to-MPS | 0.57 s / 0.21 s (warm cache) |
| Forward, training form (MPS) | 0.551 s → logits `[1,13,50304]`, top-1 **" Berlin"** |
| Reparameterization | **5.19 s** on MPS |
| Forward, inference form (MPS) | **0.021 s** → top-1 **" Berlin"** |
| Equivalence check | **max abs logit diff 3e-5**, argmax identical |
| Peak MPS alloc | 2.56 GB (training form) → 9.46 GB (inference form) |

**Where the lookup tables live:**

| | |
|---|---|
| Tensor name | **`model.moe_table.weight`** |
| Module | `MoleModel.moe_table = nn.Embedding(vocab_size, hidden_size · num_hidden_layers · num_experts)` |
| Shape | **`[50304, 36864]`** = `[vocab, 768·12·4]` |
| Logical view | `[vocab, layers, experts, hidden]` = `[50304, 12, 4, 768]` |
| Elements | 1,854,406,656 |
| Size | 7.42 GB fp32 / **3.45 GB fp16** (as `save_pretrained` writes it) |
| Indexed by | **`input_ids`** — one row per *vocabulary token* |
| Read path | `moe_output = self.moe_table(input_ids)` → `.view(B, L, n_layers, n_experts, hidden)`; layer `idx` takes `moe_output[:,:,idx]` and mixes with `softmax(router(h))` |
| Value stats | mean 7e-6, std 0.5267, absmax 244.5 |

**Important for our research question: MoLE is not a product-key memory.** There is no learned key table and no top-k search. The address *is* the input token id, and all 4 expert entries for that token are read and blended by the router softmax. That is exactly why it reparameterizes exactly. So MoLE gives us a **per-token value table** — a useful contrast to PKM/PEER (content-addressed, sparse top-k) and to kNN-LM (nearest-neighbour addressed), but it is a different addressing scheme, not a third instance of the same one. Worth stating explicitly in the proposal.

**The transformers-version problem.** MoLE's modeling code targets transformers 4.38.2. On 5.20.2 it fails at construction:

```
AttributeError: 'LlamaConfig' object has no attribute 'rope_theta'
```

(transformers 5 moved RoPE settings into `config.rope_parameters`.) Rather than patch a chain of 4.38→5.x API changes (`rope_theta`, `ALL_LAYERNORM_LAYERS`, the `Cache` API, the docstring decorators), there is a **second venv** `.venv-mole` pinned to `transformers==4.38.2` / `tokenizers==0.15.2` / `huggingface_hub==0.23.5` (see `requirements-mole.txt`). `run_all.sh` routes `check_09_mole.py` to it automatically. Also note 4.38 wants `torch_dtype=`, not the modern `dtype=`.

### 5.2 B2 — jaivial/dna-diskchat-2b-peer-v21 (PASS)

The repo has **8 undocumented checkpoints** (23.4 GB total). The final one is **`checkpoints/final_113738.pt`** — step 113,738 matches the README's 1.162B-token run, and it is the only `final_*` file. Confirmed from the loaded metadata: `step=113738`, `valid_ce=3.7246`, `tokens=1,162,402,360`. Only that single 2.93 GB file was downloaded (you approved it); the other 20.5 GB was skipped.

```python
import sys, torch
from huggingface_hub import hf_hub_download
ck_path = hf_hub_download("jaivial/dna-diskchat-2b-peer-v21",
                          "checkpoints/final_113738.pt")        # 2.93 GB
sys.path.insert(0, "<snapshot>/scripts")   # repo scripts hardcode sys.path '/root/dna'
from model_dna_peer_v21 import DnaPeerV21, peer_counts

ck  = torch.load(ck_path, map_location="cpu", weights_only=False)
cfg = ck["config"]   # {vocab:32000, d:512, layers:16, ff:1536, a:2048, b:2048,
                     #  nk:704, dk:128, topk:8, pheads:1, peer_layers:[4,8,12]}
model = DnaPeerV21(**cfg)
model.load_state_dict(ck["model"], strict=False)
model.eval().to("mps")

# DnaChat defines no forward(); features() + head2 is the entry point
h, balance, rows = model.features(ids)
logits = model.head2(h)
```

Forward on **MPS**: 0.785 s, hidden `[1,16,512]`, logits `[1,16,32000]`, finite, mean −5.63. MPS driver alloc 3.16 GB. `torch.load` 0.29 s and build+load 7.0 s with the file in the OS page cache (11 s / 19 s on the first cold read).

Checkpoint metadata: `step=113738`, **`valid_ce=3.7246`**, `tokens=1,162,402,360`. Parameter counts via the repo's own `peer_counts()`: 598,145,536 total controller params, **70,541,312 active per token**, **507,510,784 in the expert pool**, plus 536,872,579 buffer elements (the codon table). The expert-pool figure matches the README's 507.5M exactly. **Note the one discrepancy:** the README's headline table reports "Final valid CE 4.0317", but the checkpoint itself carries `valid_ce=3.7246`. The checkpoint is the primary source; the README number may be from a different eval slice or an earlier run. Worth a footnote if we cite this model's loss.

**Where the PEER experts and their keys are stored:**

| What | Tensor | Shape | Notes |
|---|---|---|---|
| **Expert pool — "read" side** | `pool.up.weight` | **`[495616, 512]`** fp32 | one row per expert |
| **Expert pool — value side** | `pool.down.weight` | **`[495616, 512]`** fp32 | **these rows are the values in our sense** |
| Product key, half A | `blocks.{4,8,12}.ffn.Ka` | **`[1, 704, 128]`** | `[pheads, nk, dk]` |
| Product key, half B | `blocks.{4,8,12}.ffn.Kb` | **`[1, 704, 128]`** | `[pheads, nk, dk]` |
| Query projection | `blocks.{4,8,12}.ffn.q.weight` | `[256, 512]` | `d → pheads·2·dk` |
| Query BatchNorm | `blocks.{4,8,12}.ffn.qbn.{weight,bias,running_mean,running_var}` | `[256]` | keeps expert usage near 100% |
| *Separate* codon memory | `codons` | `[4194304, 128]` **uint8** | the DNA table, `a·b = 2048·2048` rows × 128 codons |
| codon codebook | `codebook` | `[4, 256, 4]` fp32 | 4 positional reading frames |

Structure: **one shared pool of `nk² = 704² = 495,616` rank-1 experts**, read by the 3 PEER layers at blocks 4/8/12. Each expert is a rank-1 MLP — row `i` of `pool.up` (the read direction) and row `i` of `pool.down` (the write/value direction). `expert_id = argtop(qa·Ka)·nk + argtop(qb·Kb)`, so `Ka × Kb` addresses all 495,616. **Keys are per-layer; the value pool is shared.** 507.5M expert params.

Two things to know:
- The state dict also contains `blocks.{4,8,12}.ffn.pool.{up,down}.weight`. These are the **same shared module** serialized once per block, not four separate pools. Verified at load: `model.blocks[i].ffn.pool is model.pool` is `True` for all three.
- The checkpoint's real config has **`pheads=1`**, not the `heads=4` the README's architecture box implies (`Ka` is `[1,704,128]`). Trust the checkpoint config.

### 5.3 B3 — fechyy/sparse-memory-lm-B-16M (PASS, header only)

Full model **not run**, per the roadmap — the model card is explicit that it needs the repo's Triton kernels and "doesn't load with `transformers`", and those kernels are CUDA/ROCm only.

| File | Size |
|---|---:|
| `values_q4.bin` | **3.22 GB** ← over the 2 GB threshold |
| `rest.pt` | 284.04 MB |
| `hot_rows.npy` | 134.22 MB |
| `scales_q4.bin` | 33.55 MB |
| `meta.json` | 1 KB |
| **Total** | **3.67 GB** |

Per your choice, **no full download**: `meta.json` (1 KB) + an HTTP Range read of the first 4,096 rows of `values_q4.bin` + the 34 MB `scales_q4.bin`.

**The 4-bit value table:**

| | |
|---|---|
| Tensor keys in the model | `layers.2.ffn.values.weight`, `layers.6.ffn.values.weight`, `layers.10.ffn.values.weight` — **one table shared by all three** |
| Logical shape | **`[16777216, 384]`** (16.78M rows × 384 dims) |
| Stored as | uint8, **two 4-bit nibbles per byte** → `[16777216, 192]` on disk |
| Bytes/row | 192 — file size `16777216 × 192 = 3,221,225,472` exactly matches |
| Scales | float16, one per row; `scales_q4.bin` holds exactly 16,777,216 values |
| Quantization | `d = fp16(max-abs value with sign / -8)`, `code = clamp(round(w/d), -8, 7) + 8` |
| Nibble order | low nibble = dims 0…191, high nibble = dims 192…383 (**not** interleaved) |
| Dequantize | `value = (code - 8) * d` |
| fp32 equivalent | **25.77 GB** (the author did not upload it; the model card says 25.8 GB) |

Range read returned HTTP **206**; codes all in [0,15] with a bell-shaped histogram peaking at 8; dequantized block `[4096, 384]` float32, mean 0.000591, std 0.09217, absmax 0.814, all finite. **Confirmed: we can load these values into numpy on this Mac for offline analysis.**

```python
# full-table recipe, no RAM copy
packed = np.memmap("values_q4.bin", dtype=np.uint8, mode="r", shape=(16777216, 192))
scales = np.fromfile("scales_q4.bin", dtype=np.float16)
rows   = packed[a:b]
codes  = np.concatenate([(rows & 0x0F), (rows >> 4)], axis=1).astype(np.float32)
vals   = (codes - 8.0) * scales[a:b].astype(np.float32)[:, None]
```

Memmap the file and dequantize slices — never materialize the 25.77 GB fp32 table.

**To run the full model on a Colab T4:** `git clone github.com/re133/sparse-memory-lm`, install the CUDA torch wheel + `requirements.txt` + `huggingface_hub`, then `python scripts/demo_generate.py --download --table vram` (3.22 GB in 16 GB VRAM leaves ~12 GB spare) or `--table ram` (Colab's ~12.7 GB system RAM fits the table + 134 MB hot rows). `--table nvme` is a bad fit — Colab's disk is network-backed. **The real risk is not capacity but Triton/arch compatibility:** the kernels target Triton 3.5/3.8, and the T4 is sm_75 with no bf16, so kernels assuming bf16 or sm_80+ features will not compile. Check the repo's `requirements.txt` before burning a session. For our purposes none of this is on the critical path — we want the *values*, and they load into numpy here.

### 5.4 B4 — stretch repos (no weights downloaded)

Method: `HfApi().model_info(files_metadata=True)` for sizes, then the `model.safetensors.index.json` for the tensor→shard map, then an **HTTP Range read of each relevant shard's safetensors header** for exact shapes, dtypes and byte ranges. Only index JSONs were downloaded; no shard was fetched.

**`deepseek-ai/DeepSeek-V4.1-Flash`** — 510.31 GB, 90 files, 96,085 tensors.

| Tensor | Shape | dtype | Size |
|---|---|---|---:|
| `layers.1.engram.embed.weight` | **`[384006168, 256]`** | F8_E4M3 | **98.31 GB** |
| `layers.1.engram.embed.scale` | `[384006168, 8]` | F8_E8M0 | 3.07 GB |
| `layers.1.engram.wkv.weight` | `[25600, 6144]` | F8_E4M3 | 157.29 MB |
| `layers.1.engram.wkv.scale` | `[800, 192]` | F8_E8M0 | 153.60 KB |
| `layers.1.engram.{q,k}_weight` | `[4, 5120]` | BF16 | 40.96 KB each |
| `layers.14.engram.embed.weight` | **`[384016682, 256]`** | F8_E4M3 | **98.31 GB** |
| `layers.14.engram.embed.scale` | `[384016682, 8]` | F8_E8M0 | 3.07 GB |
| `layers.14.engram.wkv.weight` | `[25600, 6144]` | F8_E4M3 | 157.29 MB |

**Separately downloadable: YES.** All 12 engram tensors live in exactly two shards — `model-00047-of-00048.safetensors` and `model-00048-of-00048.safetensors` — which contain **6 tensors each and nothing else**. Total **203.07 GB** (39.79% of the repo). Two `engram` layers (1 and 14), each a **384-million-row × 256-dim** fp8 table. This is by far the largest memory store in the comparison set.

**`meituan-longcat/LongCat-Flash-Lite`** — 138.19 GB, 41 files, 11,160 tensors.

| Tensor | Shape | dtype | Size |
|---|---|---|---:|
| `model.ngram_embeddings.embedders.{0..11}.weight` | **`[~10223617, 256]`** each | BF16 | **5.23 GB each** |
| `model.ngram_embeddings.post_projs.{0..11}.weight` | `[3072, 256]` each | BF16 | 1.57 MB each |

(Row counts differ slightly per embedder: 10,223,617 / 10,223,619 / … / 10,223,639 — one embedder per n-gram order.)

**Separately downloadable: NO.** The 12 n-gram tables total **62.83 GB** (45.47% of the repo) but each sits in a *different* shard mixed with ordinary layer weights, across 17 shards totalling **90.34 GB**. **However**, the safetensors header gives each tensor's exact byte range, so any single 5.23 GB table can be pulled with one HTTP Range request without the shard around it — verified by reading those headers. If we want all 12, that is 62.83 GB of ranged reads instead of 90.34 GB of shards.

---

## 6. Our code and tools

### 6.1 C1 — product-key-memory, 65,536 slots

```python
from product_key_memory import PKM
pkm = PKM(dim=512, heads=4, dim_head=128, num_keys=256, topk=32)  # num_keys**2 = 65,536 slots
```

`num_keys` is the number of **sub-keys per half**, so slots = `num_keys²`. 256 × 256 = 65,536 → `pkm.num_memories == 65536`. 34,341,120 params.

| Parameter | Shape | Role |
|---|---|---|
| **`keys`** | `[4, 256, 2, 128]` | `[heads, num_keys, 2 halves, dim_head]` — the sub-key table |
| **`values.weight`** | `[65536, 512]` | `nn.EmbeddingBag(65536, 512, mode='sum')` — **the value store** |
| `to_queries.weight` | `[1024, 512]` | |
| `norm.{weight,bias}` | `[128]` | |

Forward 0.644 s, backward 0.752 s on MPS. **Gradients reach both**: `keys` grad norm 2.9e-5 over 262,016 nonzeros; `values.weight` grad norm 3.4e-5 over 12,949,504 nonzeros. Dense (not sparse) grads.

**Reading the selected top-k slot indices — solved, no package change needed.** PKM computes `value_indices` internally and never returns it, but it passes that exact tensor as the first positional argument to `self.values` (an `nn.EmbeddingBag`), so a forward pre-hook sees it:

```python
box = {}
def hook(mod, args, kwargs):
    box["indices"] = args[0].detach()                      # [(b·t), (heads·topk)]
    box["weights"] = kwargs["per_sample_weights"].detach() # the gate weights
h = pkm.values.register_forward_pre_hook(hook, with_kwargs=True)
out = pkm(x, input_mask=mask)
h.remove()
idx = box["indices"].reshape(b, t, heads, topk)
```

Captured: `[256, 128]` = `[(2·128), (4·32)]`, int64, values 8…65,531, **25,292 unique slots in one 2×128 batch**, plus matching gate weights `[256,128]`. This is exactly the read log we need, at zero cost to the package.

If we would rather have it in the API, the **smallest source change** is in `product_key_memory/product_key_memory.py`, `PKM.forward`: add a `return_indices = False` kwarg and, at the end,

```python
if return_indices:
    return out, rearrange(value_indices, '(b t) hk -> b t hk', b = b), \
                rearrange(attn,          '(b t) hk -> b t hk', b = b)
```

One kwarg plus one branch. The hook avoids even that, so we recommend the hook.

### 6.2 C2 — PEER-pytorch, 65,536 experts

```python
from PEER_pytorch import PEER
peer = PEER(dim=512, heads=8, num_experts=65_536,
            num_experts_per_head=16, dim_key=128, pre_rmsnorm=True)
```

`num_experts` must be a perfect square (it asserts); 65,536 = 256². 67,382,784 params.

| Parameter | Shape | Role |
|---|---|---|
| **`keys`** | `[8, 256, 2, 128]` | `[heads, num_keys, 2 halves, dim_key]` — product keys |
| **`weight_down_embed.weight`** | `[65536, 512]` | expert "read" direction |
| **`weight_up_embed.weight`** | `[65536, 512]` | expert **value** direction |
| `to_queries.0.weight` | `[2048, 512]` | |
| `norm.gamma` | `[512]` | |

Forward 0.336 s, backward 0.234 s on MPS. **Gradients reach everything**: `keys` 1700.04, `weight_down_embed.weight` 72.87 (747,445 nonzero), `weight_up_embed.weight` 8.50 (623,616 nonzero).

**Reading the selected expert indices — solved the same way**, via a pre-hook on `peer.weight_down_embed` (an `nn.Embedding`, so no kwargs needed):

```python
box = {}
h = peer.weight_down_embed.register_forward_pre_hook(
        lambda mod, args: box.__setitem__("indices", args[0].detach()))
out = peer(x); h.remove()
idx = box["indices"]      # [batch, seq, heads, num_experts_per_head_topk]
```

Captured `[2, 128, 8, 1]`, int64, values 13…65,535, 2,006 unique experts. Minimal source alternative: `return_indices` kwarg plus `if return_indices: return out, indices, scores`.

> **Gotcha that will matter in step 1.** The default `non_competing_scores=True` sets `num_experts_per_head_topk = 1`, so **only `heads × 1 = 8` experts are active per token**, not `heads × 16 = 128` — which is why the index tensor's last dim is 1, and why PEER underperformed in the D smoke test. `product_key_topk` stays at 16 (that is the per-half key search), but the score top-k collapses to 1. Pass `non_competing_scores=False` to get 16 experts/head with a softmax gate. Decide this deliberately before step 1 — it changes the read-log density by 16×.

### 6.3 C3 — freezing keys only (the random-key twin)

```python
# PKM
pkm.keys.requires_grad_(False)         # sub-key table frozen
# PEER
peer.keys.requires_grad_(False)        # product-key table frozen
# values / experts / queries all still train:
opt = torch.optim.Adam([p for p in layer.parameters() if p.requires_grad], lr=1e-2)
```

Verified over **one real Adam step**:

| Layer | `keys` max change | `keys` bit-identical | `keys.grad` | Values changed by |
|---|---:|---|---|---:|
| PKM | **0.0** | **True** | `None` | `values.weight` 9.536e-3 (and `to_queries` 9.863e-3) |
| PEER | **0.0** | **True** | `None` | `weight_down` 1.000e-2, `weight_up` 1.000e-2 |

`requires_grad = False` per-layer breakdown after freezing — PKM: `keys` False, `to_queries`/`norm`/`values` True. PEER: `keys` False, `norm.gamma`/`weight_down_embed`/`weight_up_embed`/`to_queries` True. The random-key twin is a one-liner in both cases.

### 6.4 C4 — faiss-cpu

1,000,000 × 256 float32 (1.024 GB), 1,000 queries, top-32, 18 threads.

| Index | Build | Search (1k × top-32) | Per query | QPS | RSS | Index memory |
|---|---:|---:|---:|---:|---:|---:|
| `IndexFlatIP` | **0.088 s** | **0.450 s** | 0.450 ms | 2,222 | 2.10 GB | 1.024 GB (raw vectors) |
| `IndexIVFPQ` (nlist 4096, m 32, nbits 8) | **13.91 s** (9.02 train + 4.89 add) | **0.012 s** @ nprobe 32 | 0.012 ms | 82,040 | 2.38 GB | **32 MB codes (32×)** |

```python
index = faiss.IndexFlatIP(256); index.add(xb)

quant = faiss.IndexFlatIP(256)
index = faiss.IndexIVFPQ(quant, 256, 4096, 32, 8, faiss.METRIC_INNER_PRODUCT)
index.train(xb[:262144]); index.add(xb); index.nprobe = 32
```

IVFPQ search scaling: nprobe 8 → 0.013 s, 32 → 0.012 s, 128 → 0.025 s.

**One caveat, stated plainly.** Recall@32 against the exact flat result was only **2.3% / 4.9% / 8.7%** at nprobe 8/32/128. That is **not** a verdict on IVFPQ — it is what random i.i.d. Gaussian vectors do. In 256 dimensions they are all nearly equidistant and have no cluster structure, so product quantization has nothing to exploit and the "true" top-32 is arbitrary anyway. Real kNN-LM key vectors are strongly clustered and will behave far better. **Action for step 1: re-measure recall on actual kNN-LM keys before choosing an index type.** On memory grounds, flat is entirely affordable at our scale (1.024 GB for 1M keys → ~16 GB for 16M), so flat is the safe default and IVFPQ is the option if we scale past RAM.

### 6.5 C5 — biography generator (`tools/bio_generator.py`)

Follows the **bioS** design from Allen-Zhu & Li, *Physics of Language Models 3.1* (arXiv:2309.14316): knowledge enters only through paraphrased biographies, so answering a question requires having stored the fact rather than pattern-matching the prompt.

```bash
python tools/bio_generator.py --n 1000 --seed 0 --out data_samples/bios_sample.jsonl --count-tokens
```

- **5 attributes**: `birth_date`, `birth_city`, `university`, `major`, `employer`
- **7 templates per attribute** (spec asked ≥5), asserted at runtime; **3 question phrasings** per attribute
- Sentence order shuffled per person; `template_id` recorded per sentence so we can condition analyses on surface form
- Pools (all verified duplicate-free): 398 given names × 809 surnames = **321,982** two-part names (a middle initial is added automatically past ~80k people), **246** cities, **154** universities, **127** majors, **129** fictional employers
- **Fixed seed, verified deterministic**: two runs at seed 0 are byte-identical (SHA-256 match)

Generated: **1,000 people, 1,000 unique names, 0 duplicates** → `data_samples/bios_sample.jsonl` (2.1 MB). Output keys: `id, name, attributes, sentence_order, template_ids, sentences, sentence_meta, text, qa`.

Example (`id 0`):

> Kuala Lumpur, Malaysia is where Leona Wilcox was born. Records list April 21, 1970 as the day Leona Wilcox was born. Leona Wilcox chose Architecture as a course of study. Leona Wilcox holds a position at Ironvale Fabrication. Leona Wilcox earned a degree from Washington State University.

with QA pairs `"Where was Leona Wilcox born?" → "Kuala Lumpur, Malaysia"`, `"Which company employs Leona Wilcox?" → "Ironvale Fabrication"`, etc.

**Token counts** (GPT-2 encoding, measured on 1,000 people):

| | Per person | 10,000 people | 100,000 people |
|---|---:|---:|---:|
| Biography text | 61.7 tok | **0.62M tok** | **6.17M tok** |
| QA pairs | 58.6 tok | 0.59M tok | 5.86M tok |
| **Total** | **120.3 tok** | **1.20M tok** | **12.03M tok** |
| As uint16 on disk | | 2.4 MB | 24.1 MB |

So 100k people is only ~12M tokens — small enough to mix into a 150M-token run at ~8% without crowding out the natural-text domains, and large enough that 100k × 5 = 500,000 facts far exceeds any plausible 65,536-slot memory, which is exactly the regime where "how are values organized" becomes interesting.

One deliberate design choice: templates are **pronoun-free** and repeat the name. The generator assigns no gender to these fictional people, and "they" reads oddly in several templates. This also matches bioS, where each sentence must be independently retrievable.

### 6.6 Task D (local part) — tiny transformer trains on MPS

2-layer LM (vocab 512, dim 128, 4 heads, seq 64, batch 8), **20 steps**, AdamW lr 3e-3, overfitting **one fixed batch** — random i.i.d. tokens contain nothing learnable, so a fresh batch per step would leave the loss sitting at ~ln(512)=6.24 and prove nothing. Overfitting one batch gives a real signal.

| Variant | Params | Loss 6.4 → | Drop | s/step | tok/s | Status |
|---|---:|---:|---:|---:|---:|---|
| plain | 536,064 | **0.166** | 6.259 | 0.010 | 50,329 | **PASS** |
| + PKM (65,536 slots) | 8,891,328 | **0.200** | 6.183 | 0.007 | 68,526 | **PASS** |
| + PEER (65,536 experts) | 17,378,304 | **2.922** | 3.482 | 0.012 | 43,781 | **PASS** |

All losses finite, no step raised, MPS alloc 1.12 GB. PEER's smaller drop is the `non_competing_scores` issue (§6.2) — only 4 experts active per token in that config, so there is much less capacity to overfit with. **The stack works end to end on MPS for all three arms.** The timed benchmark is step 1.

---

## 7. Task D — manual checklist (for you)

I cannot verify any of these; they need your accounts.

- [ ] **Colab** — account active, and a **T4 actually offered** (check `Runtime → Change runtime type`; free tier sometimes only offers CPU at peak). Needed as the fallback for B3's Triton kernels and any CUDA-only baseline.
- [ ] **Kaggle** — account **phone-verified** (required for GPU access) and the **weekly GPU quota visible** (30 h/week; confirm the counter shows).
- [ ] **Modal** — account created and the **monthly credit confirmed** on the billing page.
- [ ] **Checkpoint storage** — either a shared Google Drive folder *or* a private HF repo (e.g. `roieg/<project>-ckpts`). Budget: a 150M-token run's memory table alone is 65,536 × 512 × 4 B = 134 MB; with optimizer state and several arms, plan for **5–20 GB**.
- [ ] **Shared GitHub repo** for the team. This directory is a **local git repo with no remote and nothing pushed** — add the remote when you are ready.
- [ ] **Course cluster / TPU time** — decide whether to request it in the proposal. **Proposal due 2026-10-28** (3 days from now). My read: the M5 Pro handles everything in step 1 (the three smoke-test arms ran at 44–69k tok/s on toy sizes), so the ask is only worth making if we commit to the 0.5B-token scale or to reproducing B3/B4 behaviour, which needs CUDA.

---

## 8. Open questions and anything blocking step 1

**Nothing blocks step 1.** Two decisions are worth making deliberately first:

1. **PEER's `non_competing_scores` default** (§6.2). As shipped, a PEER layer activates `heads × 1` experts per token, not `heads × 16`. This changes read-log density by 16× and visibly weakened PEER in the smoke test. Our PKM arm uses `topk=32` with a softmax gate, so for an apples-to-apples PKM-vs-PEER comparison we probably want `non_competing_scores=False`. **Recommendation: set it explicitly in the step-1 config, whichever way we go, and record it.** (Note the package author's comment that Csordás et al., arXiv:2310.10837, found non-competing activations *help* in the PKM setting — so there is a real argument for keeping the default and instead matching PKM to it via `non_competitive_gates=True`.)

2. **faiss index type** (§6.4). The IVFPQ recall numbers here are meaningless on random data. Re-measure on real kNN-LM keys. Flat is affordable at our scale and is the safe default.

**Resolved, but worth carrying in the write-up:**

3. **MoLE is a different addressing scheme.** Per-token lookup (`input_ids` → all 4 experts, router-blended), not content-addressed top-k. It is a legitimate third point of comparison, but calling it "a memory layer like PKM/PEER" would be wrong. Frame the project as *three addressing schemes* — token-addressed (MoLE), content-addressed sparse (PKM/PEER/sparse-memory-lm/DeepSeek engram), and neighbour-addressed (kNN-LM).

4. **SlimPajama is gone from the Hub** (§4.4). Using `venketh/SlimPajama-62B`. If the roadmap's repo ID appears in the proposal, update it.

5. **Two venvs.** `.venv` for everything; `.venv-mole` (transformers 4.38.2) for B1 only. `run_all.sh` handles the routing. If we end up doing serious MoLE work, consider porting its modeling code to transformers 5 instead.

6. **Roadmap text fixes:** `huggingface-cli` → `hf auth`; `zstandard` must be installed to stream the Pile; `uv` is not on this machine.

**Open, for step 1 to answer:**

7. **How large should the memory table be relative to the fact count?** 65,536 slots vs. 100k synthetic people × 5 facts = 500k facts is deliberately over-subscribed. The public models span four orders of magnitude — 65,536 (ours) → 495,616 (B2) → 10.2M per table (LongCat) → 16.8M (B3) → 384M (DeepSeek engram). Worth sweeping slot count rather than fixing it.

8. **Should we also pull one of the big public value tables for direct comparison?** B3's 16.8M × 384 table is 3.22 GB and loads into numpy here (confirmed). DeepSeek's two 384M × 256 fp8 tables are 203.07 GB in dedicated shards, and LongCat's 12 n-gram tables are 62.83 GB — downloadable in principle (and range-fetchable one table at a time), but that is a separate disk conversation.

---

## 9. Reproducing this

```bash
cd final_project
conda create -y -p .venv python=3.12 && .venv/bin/pip install -r requirements.txt
conda create -y -p .venv-mole python=3.12 && .venv-mole/bin/pip install -r requirements-mole.txt
hf auth login                      # if not already logged in
./step0_access/run_all.sh          # all checks; or: ./step0_access/run_all.sh 05 06
```

| Path | What |
|---|---|
| `step0_access/check_01_env.py` | environment, MPS, HF auth, versions |
| `step0_access/check_02_pile.py` | A1/A2/A3 — Pile streaming, subjects, tokens, disk |
| `step0_access/check_03_slimpajama.py` | A4 — SlimPajama with a fallback chain |
| `step0_access/check_04_pretrain_corpora.py` | A5 — Wikipedia / FineWeb-Edu / Cosmopedia |
| `step0_access/check_05_pkm.py` | C1 + C3 (PKM) |
| `step0_access/check_06_peer.py` | C2 + C3 (PEER) |
| `step0_access/check_07_faiss.py` | C4 |
| `step0_access/check_08_peer_model.py` | B2 |
| `step0_access/check_09_mole.py` | B1 — **needs `.venv-mole`** |
| `step0_access/check_10_sparse_memory.py` | B3 |
| `step0_access/check_11_stretch_models.py` | B4 — repo/shard layout |
| `step0_access/check_12_stretch_tensors.py` | B4 — ranged safetensors headers |
| `step0_access/check_13_mps_train.py` | Task D local smoke test |
| `tools/bio_generator.py` | C5 |
| `logs/*.json` | machine-readable result of every check |
| `logs/*.out` | stdout of each check, as `run_all.sh` captured it |
| `data_samples/` | 14 MB of tiny samples (git-ignored) |

Two re-runnability fixes were needed to make `run_all.sh` reliable, both worth knowing about:

- **`datasets` streaming hangs at exit.** After breaking out of a streaming iterator, `datasets` leaves non-daemon worker threads and fsspec sessions alive, so `check_04` sat for 10+ minutes after writing its results before the interpreter would exit. The three streaming checks now call `_common.finish()` (flush, then `os._exit(0)`) after `jdump`, which skips the thread joins once the work is already on disk.
- **Per-check watchdog.** macOS ships no `timeout`/`gtimeout`, so `run_all.sh` has a small portable watchdog (`TIMEOUT_SECS`, default 900) that kills and reports `rc=124` rather than blocking a whole run. Override with `TIMEOUT_SECS=1800 ./step0_access/run_all.sh`.

Note that several timings in this report are **cold-cache** first-run numbers (e.g. B2's 11 s `torch.load`); on a re-run with the files in the OS page cache they are much faster, and the JSON in `logs/` reflects the most recent run.

**Units:** all byte sizes in this report are **decimal (SI)** — 1 GB = 10⁹ bytes — matching how the HF Hub and the model cards quote them. (The first draft of `_common.human()` divided by 1024 while labelling the result "GB", which understated every large table by ~7%; fixed, and checks 10–12 were re-run.)

Nothing was written outside `final_project/` except the default Hugging Face cache (`~/.cache/huggingface`, 3.8 GB).
