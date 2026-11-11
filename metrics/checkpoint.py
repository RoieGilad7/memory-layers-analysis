"""Evaluate Roie's native GPT checkpoints with the single-layer metric interface.

The upstream checkpoint embeds its GPT config and training-data settings. The
published demo does not record a tokenizer or corpus fingerprint. Equal vocab
sizes make the forward pass possible but do not establish token-map identity.
"""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import asdict
import hashlib
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import torch
from torch import nn


def upstream_model_types():
    """Load the local synchronized source, independently of the working directory."""
    module = import_module(__package__.removesuffix("metrics") + "memlayers.model")
    return module.GPT, module.GPTConfig


class _MemoryView:
    def __init__(self, module):
        self.module = module
        self.num_slots = module.n_slots

    def value_table(self):
        if self.module.kind == "pkm":
            return self.module.pkm.values.weight
        return self.module.peer.weight_up_embed.weight

    def parameters(self):
        return self.module.parameters()


class RoieModel(nn.Module):
    def __init__(self, gpt, layer_index):
        super().__init__()
        self.gpt = gpt
        self.layer_index = layer_index
        module = gpt.memory_layers.get(layer_index)
        self.memory = _MemoryView(module) if module is not None else None
        self.cfg = SimpleNamespace(
            style=module.kind if module is not None else "dense",
            topk=module.reads_per_token if module is not None else 0,
        )

    @property
    def head(self):
        return self.gpt.lm_head

    @staticmethod
    def physical_read(ids, weights, vectors):
        """Return one row per distinct physical slot, sorted by total gate.

        PKM/PEER can address the same table row from several heads. The gate
        mass is their sum. The combined vector preserves their total residual
        contribution; a zero-mass address remains a selected address. The
        strongest physical slot wins top-1, with ties resolved by smaller ID.
        """
        slots, inverse = torch.unique(ids, sorted=True, return_inverse=True)
        mass = weights.new_zeros(len(slots)).index_add_(0, inverse, weights)
        total = vectors.new_zeros(len(slots), vectors.shape[-1])
        total.index_add_(0, inverse, weights[:, None] * vectors)
        # With zero total (e.g. a ReLU gate), the effective vector is
        # immaterial for every contribution metric. Preserve its zero update.
        value = total / torch.where(mass != 0, mass, torch.ones_like(mass))[:, None]
        order = torch.argsort(mass, descending=True, stable=True)
        return slots[order], mass[order], value[order]

    def forward(self, tokens, mask=(), trace=False):
        module = self.memory.module if self.memory is not None else None
        if module is None and len(mask):
            raise ValueError("Cannot mask slots on a dense checkpoint")
        with ExitStack() as cleanup:
            activation = []
            full_mask = False
            if module is not None:
                full_mask = isinstance(mask, range) and mask == range(module.n_slots)
                # An all-slot lesion zeros the entire selected residual branch.
                # This avoids rebuilding a big table mask on each batch.
                if full_mask:
                    cleanup.enter_context(
                        module.register_forward_hook(
                            lambda _m, _args, output: torch.zeros_like(output)
                        )
                    )
                module.set_mask_slots(None if full_mask else mask, renormalize=False)
                cleanup.callback(module.set_mask_slots, None, False)
                module.set_read_logging(trace)
                cleanup.callback(module.set_read_logging, False)
                if trace and module.kind == "peer":
                    # This is the signed, token-specific scalar multiplying
                    # each up-row, after the expert nonlinearity and dropout.
                    cleanup.enter_context(
                        module.peer.dropout.register_forward_hook(
                            lambda _m, _args, output: activation.append(output)
                        )
                    )
            # Roie's public GPT returns all positions when given targets.
            logits, _ = self.gpt(tokens, targets=tokens)
            reads = None
            if trace and module is not None:
                read = module.last_read()
                ids = read.indices.flatten(2)
                weights = read.weights.flatten(2)
                if full_mask:
                    weights = torch.zeros_like(weights)
                vectors = self.memory.value_table()[ids]
                if module.kind == "peer":
                    vectors = activation[0].flatten(2).unsqueeze(-1) * vectors
                reads = (ids, weights, vectors)
        return logits, reads


def _v1_checkpoint_identity(checkpoint, corpus):
    """Bind a native data-v1 model to the verified release before loading its weights."""
    cfg = checkpoint["config"].get("data") or {}
    if cfg.get("source") != "real" or cfg.get("version") != "v1":
        raise ValueError(
            "Expected a Roie checkpoint configured for data.source=real and version=v1"
        )
    source = checkpoint.get("data") or {}
    if not source and checkpoint["step"] == 0 and "optimizer" not in checkpoint:
        # The native init_weights.pt omits data provenance. It is usable as an
        # initialization control and has never consumed a training batch.
        return dict(status="initialization_only", data_seed=cfg.get("seed"))
    if source.get("source") != "real" or source.get("version") != "v1":
        raise ValueError("Checkpoint is missing the native data-v1 training provenance")
    if source.get("data_sha256") != corpus.fingerprint:
        raise ValueError(
            "Checkpoint data_sha256 does not match the frozen data-v1 manifest"
        )
    train_sha = source.get("train_bin_sha256")
    if train_sha is not None and train_sha != corpus.train_sha256:
        raise ValueError(
            "Checkpoint train_bin_sha256 does not match the data-v1 token stream"
        )
    if source.get("verified") is not True:
        raise ValueError("The native trainer did not verify its training bundle")
    if cfg.get("bin_path"):
        # The tagged trainer can record the default manifest entry for an
        # out-of-bundle bin_path. Verify the actual override independently.
        custom = Path(cfg["bin_path"])
        if not custom.is_file():
            raise ValueError(
                "Cannot verify the checkpoint's custom training bin_path on this machine"
            )
        with custom.open("rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() != corpus.train_sha256:
                raise ValueError(
                    "The checkpoint's custom training bin_path differs from data-v1"
                )
    # On Windows the tagged trainer can miss the POSIX manifest key for its
    # default train.bin. Its verified full manifest still includes that file.
    state = checkpoint.get("data_state") or {}
    data_seed = cfg.get("seed")
    if state and state.get("seed") != data_seed:
        raise ValueError("Checkpoint loader seed conflicts with the configuration")
    if (
        state
        and checkpoint.get("tokens_seen") != state["position"] * state["block_size"]
    ):
        raise ValueError("Checkpoint loader position conflicts with tokens_seen")
    return dict(
        status="verified_hashes" if train_sha else "verified_bundle_only",
        data_sha256=source["data_sha256"],
        train_bin_sha256=train_sha,
        data_seed=data_seed,
    )


def load_roie_model(path, corpus, device, layer_index=None, *, data_v1=False):
    """Strictly reconstruct an upstream init/trainer checkpoint, initially on CPU."""
    # Native trainer checkpoints include potentially large Adam states; the
    # slice evaluator only needs the model weights resident.
    checkpoint = torch.load(path, map_location="cpu", weights_only=True, mmap=data_v1)
    if (
        not isinstance(checkpoint, dict)
        or not {"config", "model", "step"} <= checkpoint.keys()
    ):
        raise ValueError("Expected an upstream checkpoint with config, model and step")
    config = checkpoint["config"]
    if not isinstance(config, dict) or not isinstance(config.get("model"), dict):
        raise ValueError("Missing nested upstream GPT configuration")
    release = _v1_checkpoint_identity(checkpoint, corpus) if data_v1 else None
    GPT, GPTConfig = upstream_model_types()
    cfg = GPTConfig(**config["model"])
    if cfg.vocab_size != len(corpus.vocab):
        raise ValueError(
            "Upstream checkpoint vocab_size differs from the supplied vocabulary"
        )
    if cfg.block_size < corpus.context:
        raise ValueError("Supplied corpus exceeds the upstream checkpoint block_size")
    if config.get("ffn_types", cfg.ffn_types) != cfg.ffn_types:
        raise ValueError("Conflicting upstream FFN layer specifications")
    if cfg.memory.get("mask_slots"):
        raise ValueError("Expected an unlesioned upstream model configuration")
    training_data = config.get("data") or {}
    if training_data.get("kind") == "harness_corpus" and not training_data.get(
        "data_hash"
    ):
        raise ValueError(
            "harness_corpus checkpoint is missing its training corpus fingerprint"
        )
    hashes = [
        value
        for value in (training_data.get("data_hash"), checkpoint.get("data_hash"))
        if value is not None
    ]
    if any(value != corpus.fingerprint for value in hashes):
        raise ValueError(
            "Upstream checkpoint corpus fingerprint differs from the supplied corpus"
        )

    gpt = GPT(cfg)
    gpt.load_state_dict(checkpoint["model"], strict=True)
    layers = sorted(gpt.memory_layers)
    if layer_index is None:
        if len(layers) > 1:
            raise ValueError(f"Select a memory layer from {layers}")
        layer_index = layers[0] if layers else None
    elif layer_index not in layers:
        raise ValueError(
            f"Layer {layer_index} is not a memory layer; available {layers}"
        )
    model = RoieModel(gpt, layer_index).to(device).eval()
    module = gpt.memory_layers.get(layer_index)
    optimizer = checkpoint.get("optimizer")
    optimizer_bytes = (
        None
        if optimizer is None
        else sum(
            tensor.numel() * tensor.element_size()
            for row in optimizer["state"].values()
            for tensor in row.values()
            if torch.is_tensor(tensor)
        )
    )
    report_config = asdict(cfg)
    report_config["memory_layers"] = layers
    frozen = report_config["memory"].pop("freeze_keys", False)
    report_config.update(
        freeze_keys=frozen, style=model.cfg.style, layer_index=layer_index
    )
    metadata = {
        "config": config,
        "report_config": report_config,
        "step": checkpoint["step"],
        "tokens_seen": checkpoint.get("tokens_seen"),
        "layer_index": layer_index,
        "memory_layers": layers,
        "style": model.cfg.style,
        "heads": module.n_heads if module is not None else 0,
        "topk": module.topk if module is not None else 0,
        "num_slots": module.n_slots if module is not None else 0,
        "data_hash_verified": bool(hashes)
        or bool(release and release.get("data_sha256")),
        "training_data": training_data,
        "optimizer_state_bytes": optimizer_bytes,
        "checkpoint_kind": "trainer" if "optimizer" in checkpoint else "model_only",
    }
    if release is not None:
        metadata["data_v1"] = release
    return model, metadata
