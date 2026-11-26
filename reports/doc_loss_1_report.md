# Phase 2, prompt 1: memory query hook and the same-document loss module

Branch `phase2/doc-loss`, from `main` at `8ac8f6b` (origin/main after `git fetch`).

**The memory.py float64 change.** The report branch `claude/project-thread-g4yifr`
has no `memlayers/` commit that is not on `main`. Its float64 change
("a float64 input stays float64") is commit `af67ee5`, and that commit was already on
`origin/main` via PR #6. So nothing was brought over. The first commit on the branch
is the `docs/phase2/` task prompts.

## 1. Files changed and public functions

| File | Change |
|---|---|
| `memlayers/memory.py` | query keeping on `MemoryLayer`, `PKMMemory`, `PEERMemory` |
| `memlayers/model.py` | `GPT.set_keep_queries`, `GPT.kept_queries`, `GPT.release_kept_queries` |
| `memlayers/doc_loss.py` (new) | `find_halves`, `half_vectors`, `doc_loss`, `mean_stats` |
| `tests/test_doc_loss.py` (new) | 24 tests |
| `docs/phase2/*.md` | the three task prompts (committed as asked) |

`MemoryLayer`:
- `set_keep_queries(flag: bool)`. On: registers one forward hook on the query module and stores the handle. Turning it on twice does not add a second hook. Off: removes the hook and clears the kept tensor. When it is off, no hook is registered.
- `kept_queries() -> Optional[Tensor]`: `[B, T, query_dim]`, fp32, **not detached**. It is cleared at the start of every `forward`.
- `release_kept_queries()`: drops the tensor (and the graph it holds) but keeps the hook. Prompt 2 calls it after backward.
- `query_dim`: `2*heads*dim_head` (PKM), `2*heads*dim_key` (PEER).
- The hook returns `None`, so it never changes the output.

PKM: the forward hook is on `self.pkm.norm` (our `QueryBatchNorm`, or the LayerNorm when `query_batchnorm` is false). Its output `[(b p h), t, d]` is reshaped to `[b, t, 2*h*d]` with `out.reshape(b, 2, h, t, d).permute(0, 3, 1, 2, 4).reshape(b, t, 2*h*d)`, where `b = self._b` is set in `forward`. The kept queries come before PKM's `query_dropout` (0 in all our configs).

PEER: the forward hook is on `self.peer.to_queries`. The installed source (`PEER_pytorch/PEER.py`) confirms the layout: `to_queries = nn.Sequential(Linear, Rearrange('b n (p h d) -> p b n h d'))`, so the output is `[p, b, n, h, d]`. It is kept as `out.permute(1, 2, 0, 3, 4).reshape(b, n, p*h*d)`.

`GPT`:
- `set_keep_queries(flag, layer=None)`: `None` means every memory layer. A layer that is not a memory layer raises `KeyError`.
- `kept_queries() -> Dict[int, Tensor]`: only the layers that hold a tensor.
- `release_kept_queries()`.

`memlayers/doc_loss.py` (all math in fp32):
- `find_halves(x: Long[B,T], eot_id, min_piece_tokens) -> (half_id: Long[B,T], n_halves: int)`. The partner of half `i` is `i ^ 1`. EOT tokens and short pieces get `-1`. It raises `ValueError` if `min_piece_tokens < 2`, because then a half could be empty.
- `half_vectors(queries: [B,T,D], half_id, n_halves) -> [N, D]`: per-half sum with out-of-place `index_add`, divided by the counts, then `F.normalize`.
- `doc_loss(v: [N,D], tau) -> (loss, {"halves": N, "gap": float|None})`:
  - `S = v@v.T/tau`, diagonal set to `-inf` with `masked_fill` (not in place). Target is `arange(N) ^ 1`, loss is `F.cross_entropy`.
  - If `N < 4` it returns `v.sum()*0` (still attached to the graph) and `gap = None`.
  - `gap` = mean cosine to the partner minus mean cosine to the other N-2 halves (self and partner excluded), detached.
- `mean_stats(list_of_stats)`: averages over micro-batches and skips those with `gap is None`. It was added for prompt 2.

## 2. find_halves vectorization and timing

The whole batch is vectorized: the `[B, T]` batch is flattened and there is no Python loop over rows or tokens. The steps:
1. Piece-start flag: a non-EOT token whose left neighbour in the same row is EOT, or that sits in column 0. Column 0 always starts a piece, so pieces never merge across rows in the flattened view.
2. `cumsum` gives the piece ids.
3. Piece lengths come from a count with `index_add_` on int64 (a bincount equivalent).
4. Position within the piece = flat index minus the flat index of the piece's first token.
5. Rank among kept pieces = `cumsum(keep)`.

The count uses `index_add_` rather than `torch.bincount`, so the code is the same on every backend. Everything runs on MPS natively (torch 2.14.1). There is no CPU copy and `PYTORCH_ENABLE_MPS_FALLBACK` is not used. The function makes two host syncs (`int(start.sum())`, `int(keep.sum())`).

Timing: `[32, 512]` batch, EOT id 50256, `min_piece_tokens = 32`, median of 200 calls (MPS synchronized after each call).

| EOT density | kept halves | CPU | MPS |
|---|---|---|---|
| 1 / 100 tokens | 258 | 0.41 ms | 1.23 ms |
| 1 / 400 tokens | 122 | 0.41 ms | 1.22 ms |

MPS is slower than CPU here because of kernel launches and the two syncs, but about 1 ms is negligible next to a training step.

## 3. Tests

- Before: 438 passed, 1 skipped (439 collected).
- After: **462 passed, 1 skipped** (463 collected; +24 in `tests/test_doc_loss.py`). Full suite on CPU, about 2 min.

New tests, grouped:
- `find_halves`:
  - two pieces split by an EOT
  - a piece at the row start
  - an all-EOT row
  - odd lengths (`L//2`, `L - L//2`)
  - pieces of `min-1` and `min` tokens
  - halves never cross an EOT and partners are `2k`/`2k+1` (checked against a plain-Python reference on a random 6×200 batch)
  - a piece ending one row and one starting the next stay separate
  - `min < 2` is rejected
- `half_vectors` equals a hand-written mean and normalize.
- `doc_loss`:
  - identical vectors give `ln(N-1)`
  - partners identical with the other pairs orthogonal give `-log(e^{1/τ}/(e^{1/τ}+N-2))`
  - swapping the halves of every pair gives the same loss
  - `N < 4` (N = 0 and 2) gives an attached zero that can be backpropagated
  - the gradient is finite and nonzero
  - `mean_stats` skips `gap = None`
- PKM: sub-key scores recomputed from the kept queries and `pkm.keys` (einsum, per-half top-k, product top-k) select exactly the slots in the read log.
- PKM and PEER, in train and eval mode: output with keeping on is `torch.equal` to keeping off; no forward hook on the norm / `to_queries` while off; switching on twice gives one hook.
- PEER: the kept layout equals `to_queries(norm(x))` rearranged.
- The kept tensor is replaced on every forward.
- Gradient: `doc_loss` on the kept queries of a tiny PKM gives a nonzero grad on `pkm.to_queries.weight`, and no grad (or exactly zero) on `pkm.keys` and `pkm.values.weight`.
- `GPT.set_keep_queries` / `kept_queries` / `release_kept_queries` on a tiny model with one memory layer, including the per-layer form and the `KeyError`. A dense model gives `{}`.

## 4. Deviations and open questions

- `gap` excludes the partner from "all other non-self halves", so it is partner cosine minus the mean over the N-2 remaining halves. With the partner included, the identity test would give gap ≠ 1. Say if you meant to include it.
- Added on top of the spec, as small helpers for prompt 2: `release_kept_queries()` on the layer and the model, and `doc_loss.mean_stats()`. `find_halves` rejects `min_piece_tokens < 2`. Prompt 2's Trainer also rejects it.
- The kept PKM queries come before `query_dropout`. That dropout is 0 in our configs, so the queries equal the ones used in the search.
