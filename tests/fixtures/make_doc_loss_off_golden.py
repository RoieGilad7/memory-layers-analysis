"""Write the doc-loss-off golden fixture from whatever checkout is on sys.path[0]."""
import json, sys, tempfile
from pathlib import Path
root = Path(sys.argv[1]); out = Path(sys.argv[2])
sys.path.insert(0, str(root))
import yaml, torch
from memlayers.train import Trainer, load_config
import memlayers
assert Path(memlayers.__file__).resolve().is_relative_to(root.resolve()), memlayers.__file__
cfg_d = {
    "name": "doc-loss-off-golden",
    "model": dict(vocab_size=257, block_size=64, n_layer=3, n_head=4, n_embd=64, dropout=0.0,
                  bias=True, tie_embeddings=True, memory_layers=[1], memory_kind="pkm",
                  memory=dict(num_keys=16, topk=4, heads=2, dim_head=32, query_batchnorm=True)),
    "data": {"kind": "repeat", "chunk_len": 8, "n_distinct": 257, "seed": 7},
    "train": {"steps": 20, "micro_batch_size": 4, "grad_accum_steps": 2, "lr": 1e-3,
              "lr_memory_values": 4e-3, "weight_decay": 0.1, "warmup_steps": 5,
              "min_lr_ratio": 0.1, "seed": 99, "log_every": 0, "ckpt_every": 0, "grad_clip": 1.0},
    "runtime": {"device": "cpu"},
}
with tempfile.TemporaryDirectory() as td:
    d = json.loads(json.dumps(cfg_d)); d["runtime"]["out_dir"] = str(Path(td) / "run")
    p = Path(td) / "cfg.yaml"; p.write_text(yaml.safe_dump(d))
    tr = Trainer(load_config(p))
    hist = tr.train(progress=False)
out.write_text(json.dumps({
    "note": "20 training steps of the tiny PKM model on CPU, fake data, written from main "
            "before the doc loss existed. With train.doc_loss_weight 0 these losses must be "
            "reproduced exactly. runtime.out_dir is filled in by the test.",
    "torch": torch.__version__,
    "config": cfg_d,
    "losses": [h["loss"] for h in hist],
}, indent=2) + "\n")
print([h["loss"] for h in hist][:3], len(hist))
