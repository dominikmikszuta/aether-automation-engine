"""TITAN - Cron-like workload scheduler."""
from __future__ import annotations
import time, threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

@dataclass
class Job:
    name: str
    fn: Callable
    interval: float = 60.0
    last_run: float = 0.0
    runs: int = 0
    errors: int = 0
    enabled: bool = True

class Scheduler:
    def __init__(self):
        self._jobs = {}
        self._stop = threading.Event()
        self._thread = None

    def register(self, name, fn, interval=60.0):
        self._jobs[name] = Job(name=name, fn=fn, interval=interval)
        return self

    def unregister(self, name):
        self._jobs.pop(name, None)

    def _tick(self):
        now = time.time()
        for job in self._jobs.values():
            if not job.enabled:
                continue
            if now - job.last_run < job.interval:
                continue
            try:
                job.fn()
                job.runs += 1
            except Exception:
                job.errors += 1
            finally:
                job.last_run = now

    def _run_loop(self):
        while not self._stop.is_set():
            self._tick()
            self._stop.wait(1.0)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def run_once(self):
        self._tick()

    def status(self):
        return [{
            "name": j.name,
            "interval": j.interval,
            "runs": j.runs,
            "errors": j.errors,
            "enabled": j.enabled,
            "last_run": datetime.fromtimestamp(j.last_run).isoformat() if j.last_run else None,
        } for j in self._jobs.values()]
