"""Dataset build for step 2 (the Pile part). See reports/data1_pile_report.md.

Stages, in order, all driven by one config (`configs/data/v1.yaml`):

    1. data.pile_extract -- stream the pinned Pile revision, archive raw JSONL
    2. data.dedup        -- clean, cap at 4096 tokens, exact + 13-gram dedup
    3. data.split        -- held-out label/test halves, trimmed to budget

    python -m data.build --config configs/data/v1.yaml --stage pile [--small]
"""
