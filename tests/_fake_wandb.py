"""A stand-in for the `wandb` module: records every call, sends nothing.

Injected with monkeypatch on memlayers.runlog.wandb_sink.WANDB_MODULE; the
tests never touch the real service."""

from pathlib import Path
from types import SimpleNamespace


class FakeRun:
    def __init__(self, owner, kw):
        self.owner, self.kw = owner, kw
        self.logged, self.saved, self.defined = [], [], []
        self.summary = {}
        self.finished = None

    def log(self, d):
        if self.owner.fail_on_log:
            raise ConnectionError("fake W&B is down")
        self.logged.append(dict(d))

    def define_metric(self, *a, **k):
        self.defined.append((a, k))

    def save(self, path, base_path=None, policy=None):
        self.saved.append(Path(path).name)

    def finish(self, exit_code=0):
        self.finished = exit_code


class FakeWandb:
    def __init__(self, fail_on_log=False):
        self.fail_on_log = fail_on_log
        self.runs, self.generated = [], []
        self.util = SimpleNamespace(generate_id=self._generate_id)

    def _generate_id(self):
        wid = f"fakeid{len(self.generated):03d}"
        self.generated.append(wid)
        return wid

    def init(self, **kw):
        run = FakeRun(self, kw)
        self.runs.append(run)
        return run

    @property
    def logged(self):
        return [d for r in self.runs for d in r.logged]
