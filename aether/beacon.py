"""BEACON - Health check registry and heartbeat."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class HealthResult:
    name: str
    status: str
    message: str = ""
    elapsed_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

class Beacon:
    def __init__(self):
        self._checks = {}
        self._history = []

    def register(self, name, fn):
        self._checks[name] = fn
        return self

    def unregister(self, name):
        self._checks.pop(name, None)

    def check(self, name):
        fn = self._checks.get(name)
        if not fn:
            return HealthResult(name, "unknown", "check not registered")
        start = time.perf_counter()
        try:
            result = fn()
            status = "healthy" if result is not False else "unhealthy"
            return HealthResult(name, status,
                message=str(result) if result not in (True, None) else "",
                elapsed_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return HealthResult(name, "unhealthy", message=str(e),
                elapsed_ms=(time.perf_counter() - start) * 1000)

    def check_all(self):
        results = [self.check(n) for n in self._checks]
        self._history.append(results)
        return results

    def summary(self):
        results = self.check_all()
        return {
            "status": "healthy" if all(r.status == "healthy" for r in results) else "degraded",
            "checks": [{"name": r.name, "status": r.status, "message": r.message,
                        "elapsed_ms": round(r.elapsed_ms, 2)} for r in results],
            "timestamp": time.time(),
        }

    def heartbeat(self, interval=30, duration=None):
        start = time.time()
        while True:
            yield self.summary()
            if duration and (time.time() - start) >= duration:
                break
            time.sleep(interval)
