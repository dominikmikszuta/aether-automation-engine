"""IRONSIGHT - Thread-safe observability and metrics."""
from __future__ import annotations
import json, time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from threading import Lock

@dataclass
class Metric:
    name: str
    value: float
    unit: str = ""
    tags: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class Metrics:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._metrics = defaultdict(list)
                cls._instance._counters = defaultdict(float)
        return cls._instance

    def record(self, name, value, unit="", **tags):
        self._metrics[name].append(Metric(name=name, value=value, unit=unit, tags=tags))

    def increment(self, name, delta=1.0, **tags):
        self._counters[name] += delta
        self.record(name, self._counters[name], unit="count", **tags)

    @contextmanager
    def timer(self, name, **tags):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.record(name, (time.perf_counter() - start) * 1000, unit="ms", **tags)

    def snapshot(self):
        return {n: [asdict(m) for m in ms] for n, ms in self._metrics.items()}

    def export(self, path):
        Path(path).write_text(json.dumps(self.snapshot(), indent=2))

    def reset(self):
        self._metrics.clear()
        self._counters.clear()
