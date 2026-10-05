"""BLAZER - Parallel task execution with retries."""
from __future__ import annotations
import asyncio, time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

@dataclass
class TaskResult:
    name: str
    success: bool
    result: Any = None
    error: str = ""
    elapsed_ms: float = 0.0
    attempts: int = 1

class Blazer:
    def __init__(self, workers=4, max_retries=3, backoff=0.5):
        self.workers = workers
        self.max_retries = max_retries
        self.backoff = backoff

    def _run_one(self, fn, args, kwargs):
        start = time.perf_counter()
        last_err = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                r = fn(*args, **kwargs)
                return TaskResult(fn.__name__, True, r,
                    elapsed_ms=(time.perf_counter()-start)*1000, attempts=attempt)
            except Exception as e:
                last_err = str(e)
                if attempt < self.max_retries:
                    time.sleep(self.backoff * (2 ** (attempt-1)))
        return TaskResult(fn.__name__, False, error=last_err,
            elapsed_ms=(time.perf_counter()-start)*1000, attempts=self.max_retries)

    def run(self, tasks):
        results = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futures = [ex.submit(self._run_one, fn, a, kw) for fn, a, kw in tasks]
            for f in futures:
                results.append(f.result())
        return results

    async def run_async(self, tasks):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.run, list(tasks))
