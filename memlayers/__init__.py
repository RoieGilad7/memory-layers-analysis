"""Memory-layer language models: nanoGPT-style decoders whose FFN blocks can be
replaced by a product-key memory (PKM) or a PEER layer.

Built for COMS E6998 final project step 1. See reports/step1_demo_report.md.
"""
__all__ = ["model", "memory", "readlog", "data_fake", "train", "devices"]
