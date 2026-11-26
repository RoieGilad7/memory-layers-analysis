# Claude Code prompt 1: memory query hook and the same-document loss module

Run on the Mac, from `/Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/`. Paste everything below the line into Claude Code.

---

You are helping with a course research project (COMS 6998 Algorithms in LLMs). We train small GPT-style models (nanoGPT style, 6 layers, d=384) whose layer 3 FFN is a product-key memory (PKM, 65,536 slots, 4 heads, top-k 32). Phase 2 adds ONE soft, low-weight, self-supervised loss: the two halves of the same document should have more similar memory-layer queries than halves of other documents (InfoNCE over the batch). This task is PROMPT 1 of 3: the query hook in the memory layers and the loss module, with unit tests. It does NOT touch the training loop (prompt 2 does that). Work in small, tested pieces.

WORKING DIRECTORY AND STARTING POINT
Work only under /Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/ . Use the existing .venv. Read first: memlayers/memory.py, memlayers/model.py, tests/test_memory.py, tests/test_model.py, and the installed packages' source for product_key_memory (PKM.forward) and PEER_pytorch (PEER.forward).
Git: `git fetch`, check whether branch `claude/project-thread-g4yifr` has commits touching memlayers/ that are not on `main` (it has a small memory.py change: a float64 input stays float64). Create branch `phase2/doc-loss` from the up-to-date `main`. If that report branch has a memlayers/memory.py change missing on main, bring over ONLY that memory.py change as the first commit on the new branch (say so in the report and later in the PR description); do not bring over the report files. Commit in small steps and push. Do not merge. Do not open the PR yet (prompt 2 does).

FIXED DESIGN (do not change; if something is impossible, stop and report)
1. memlayers/memory.py
   - `MemoryLayer.set_keep_queries(flag: bool)` and `MemoryLayer.kept_queries() -> Optional[Tensor]`. On: register a forward hook (store the handle); off: remove it and clear the kept tensor. With keeping off there must be NO hook registered. The kept tensor is cleared at the start of every forward.
   - PKM: forward hook on `self.pkm.norm` (our QueryBatchNorm, or the LayerNorm when query_batchnorm is false). Its output is `[(b p h), t, d]` with p=2 key halves, exactly as PKM.forward splits it ('b t (p h d) -> (b p h) t d'). Keep `out.reshape(b, 2, h, t, d).permute(0, 3, 1, 2, 4).reshape(b, t, 2*h*d)` (b comes from self._b, set in forward). NO detach: the loss needs the gradient. The hook returns None (it never changes the output).
   - PEER: forward hook on `self.peer.to_queries`; verify its output layout in the installed source (expected `[p, b, n, h, d]`) and keep `[b, n, p*h*d]`.
   - `query_dim` property: 2*heads*dim_head (PKM), 2*heads*dim_key (PEER).
   - memlayers/model.py: `GPT.set_keep_queries(flag, layer=None)` (None = every memory layer) and `GPT.kept_queries() -> Dict[int, Tensor]`, in the style of set_read_logging / read_logs.
2. memlayers/doc_loss.py (new), all math in fp32:
   - `find_halves(x: LongTensor[B,T], eot_id: int, min_piece_tokens: int) -> Tuple[LongTensor[B,T], int]` returns (half_id, n_halves). A piece = a maximal run of non-EOT tokens inside one row; a row start also starts a piece. Pieces shorter than min_piece_tokens get half id -1, as do EOT tokens. For a kept piece of length L, its first L//2 tokens are one half, the rest the other. Number halves so that 2k and 2k+1 are the two halves of piece k (partner of half i is i ^ 1). Vectorized torch on x's device (piece-start flag, cumsum for piece ids, bincount for lengths, position within piece); no Python loop over tokens. A python loop over the B rows is acceptable only if vectorizing is awkward; measure and say which you chose. If an op you need (e.g. bincount) is not supported on MPS in our torch version, compute the half ids on a CPU copy of x (32 x 512 int64 is 128 KB) and move the result to the device; do not enable PYTORCH_ENABLE_MPS_FALLBACK globally.
   - `half_vectors(queries: [B,T,D], half_id, n_halves) -> [N,D]`: per-half sum via index_add_, divide by counts, F.normalize.
   - `doc_loss(v: [N,D], tau: float) -> Tuple[Tensor, dict]`: S = v @ v.T / tau; mask the diagonal to -inf with masked_fill (not in place on a tensor that needs grad); target = arange(N) ^ 1; loss = F.cross_entropy(S, target). If N < 4 (fewer than 2 pieces) return a zero that stays attached to the graph (e.g. v.sum() * 0) and stats {"halves": N, "gap": None}. stats (detached floats): "gap" = mean cosine to the partner minus mean cosine to all other non-self halves; "halves" = N.

TESTS (CPU only, no network)
- find_halves on hand-built rows: two pieces split by an EOT; a piece starting at the row start; an all-EOT row (no halves); odd lengths (L//2 and L - L//2); pieces of exactly min-1 and min tokens; halves never cross an EOT; partners are 2k and 2k+1; works on a batch with several rows.
- half_vectors equals a hand-written mean + normalize.
- doc_loss: identical vectors give ln(N-1); partners identical and all other pairs orthogonal gives -log(e^(1/tau) / (e^(1/tau) + N - 2)); swapping the two halves of every pair gives the same loss; N < 4 gives zero and keeps the graph; gradient is finite.
- PKM: the kept queries are the ones the layer used: recompute the sub-key scores from them and `pkm.keys` the way PKM.forward does (einsum, per-half top-k, product top-k) and check the slot indices equal those in the read log (set_read_logging(True), last_read()).
- PKM and PEER: with keeping on, the layer output is bit-identical (torch.equal) to keeping off; with keeping off no forward hook is registered on the norm / to_queries module.
- Gradient: doc_loss on kept queries of a tiny PKM gives a nonzero grad on pkm.to_queries.weight and None (or exactly zero) on pkm.keys and pkm.values.weight.
- GPT.set_keep_queries / kept_queries on a tiny model with one memory layer.
- Run the whole existing test suite: everything must still pass.

REPORT: reports/doc_loss_1_report.md
1. Files changed and the public functions with their shapes.
2. Which vectorization you used in find_halves and its time on a [32, 512] batch on CPU and on MPS.
3. Test count before and after; all passing.
4. Anything you could not follow and open questions.
Then print a short summary in the chat.
