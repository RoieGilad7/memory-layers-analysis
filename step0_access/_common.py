"""Shared helpers for the step-0 access checks."""
import json, os, pathlib, platform, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "data_samples"
LOGS = ROOT / "logs"
SAMPLES.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)


def jdump(name, obj):
    """Persist a check's machine-readable result so the report builder can read it."""
    p = LOGS / f"{name}.json"
    p.write_text(json.dumps(obj, indent=2, default=str))
    print(f"\n[wrote] {p}")
    return p


def best_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps", "mps"
    return "cpu", "cpu (MPS unavailable)"


def free_disk_gb(path=os.path.expanduser("~")):
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize / 1e9


def human(n):
    """Decimal (SI) byte sizes, matching how the HF Hub and the model cards quote them.

    Deliberately 1000-based, not 1024-based: a model card saying "3.2 GB" means 3.2e9
    bytes, and mixing the two conventions made the first draft of the step-0 report
    understate every large table by ~7%.
    """
    for u in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1000 or u == "TB":
            return f"{n:.2f} {u}"
        n /= 1000


class Timer:
    def __enter__(self):
        self.t = time.perf_counter(); return self
    def __exit__(self, *a):
        self.dt = time.perf_counter() - self.t


def finish():
    """Flush and hard-exit.

    `datasets` streaming leaves non-daemon worker threads and fsspec sessions alive after
    we break out of an iterator, so a normal return can hang the interpreter for minutes
    at shutdown. The check's work is already written at this point, so skip the thread
    joins instead of waiting on them.
    """
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
