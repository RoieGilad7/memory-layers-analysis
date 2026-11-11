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


class FakeServerRun:
    def __init__(self, rows):
        self._rows = rows

    def scan_history(self):
        return iter(self._rows)


class FakeApi:
    """The public API: what the 'server' holds. With `lose_unfinished`, rows
    of a session that never called finish() were never uploaded (a kill -9)."""

    default_entity = "fake-entity"

    def __init__(self, owner):
        self.owner = owner

    def run(self, path):
        wid = path.rsplit("/", 1)[-1]
        mine = [r for r in self.owner.runs if r.kw.get("id") == wid]
        if not mine:
            raise ValueError(f"run {path} not found")
        rows = []
        for r in mine:
            if r.finished is None and self.owner.lose_unfinished:
                continue
            rows += r.logged
        return FakeServerRun(rows)


class FakeWandb:
    def __init__(self, fail_on_log=False, lose_unfinished=False):
        self.fail_on_log = fail_on_log
        self.lose_unfinished = lose_unfinished
        self.runs, self.generated = [], []
        self.util = SimpleNamespace(generate_id=self._generate_id)

    def Api(self, timeout=None):  # noqa: N802 - wandb's own name
        return FakeApi(self)

    def server_steps(self, wid):
        """train steps on the 'server' for run id `wid`, with repeats."""
        rows = self.Api().run(f"x/y/{wid}")._rows
        return [int(h["step"]) for h in rows if "train/loss" in h]

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
