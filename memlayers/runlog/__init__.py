"""One logger for a run: the run-dir files first, then any optional sinks.

    log = RunLogger(FilesSink(run_dir), [WandbSink(...)])
    log.log_train(row)            # train_log.csv, then the sinks
    log.log_eval(rows)            # evals.csv (posthoc rows replace their own)
    log.log_final(final_metrics)  # final_metrics.json
    log.log_files(paths)          # small files the sinks may upload
    log.finish(state, step)       # status.json, then close the sinks

The files in the run dir are the source of truth. A sink that raises is
reported once, with the reason, and switched off for the rest of the run, so
a W&B outage never stops or slows training. (Named `runlog`, not `logging`,
so it never shadows the standard library's `logging`.)
"""

from .files import FilesSink, write_status  # noqa: F401
from .logger import RunLogger, Sink  # noqa: F401
from .wandb_sink import (  # noqa: F401
    WandbSink,
    generate_wandb_id,
    get_wandb,
    wandb_tags,
)
