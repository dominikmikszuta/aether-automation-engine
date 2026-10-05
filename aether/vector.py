"""VECTOR - Composable data pipeline (eager evaluation)."""
from __future__ import annotations


class Pipeline:
    def __init__(self, source):
        self._data = list(source)

    def map(self, fn):
        self._data = [fn(x) for x in self._data]
        return self

    def filter(self, fn):
        self._data = [x for x in self._data if fn(x)]
        return self

    def flat_map(self, fn):
        result = []
        for x in self._data:
            result.extend(fn(x))
        self._data = result
        return self

    def tap(self, fn):
        for x in self._data:
            fn(x)
        return self

    def batch(self, size):
        self._data = [self._data[i:i + size] for i in range(0, len(self._data), size)]
        return self

    def collect(self):
        return list(self._data)

    def reduce(self, fn, initial=None):
        if not self._data:
            return initial
        it = iter(self._data)
        acc = next(it) if initial is None else initial
        for x in it:
            acc = fn(acc, x)
        return acc

    def count(self):
        return len(self._data)

    def first(self, default=None):
        return self._data[0] if self._data else default
