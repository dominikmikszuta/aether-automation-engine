"""VECTOR - Composable data pipeline (map/filter/reduce/batch)."""
from __future__ import annotations
from typing import Any, Callable, Iterable

class Pipeline:
    def __init__(self, source):
        self._source = source
        self._ops = []

    def map(self, fn):
        self._ops.append(("map", fn)); return self

    def filter(self, fn):
        self._ops.append(("filter", fn)); return self

    def batch(self, size):
        self._ops.append(("batch", size)); return self

    def flat_map(self, fn):
        self._ops.append(("flat_map", fn)); return self

    def tap(self, fn):
        self._ops.append(("tap", fn)); return self

    def _iterate(self):
        data = self._source
        for kind, fn in self._ops:
            if kind == "map":
                data = (fn(x) for x in data)
            elif kind == "filter":
                data = (x for x in data if fn(x))
            elif kind == "flat_map":
                data = (y for x in data for y in fn(x))
            elif kind == "tap":
                data = (self._tap(fn, x) for x in data)
            elif kind == "batch":
                data = self._batcher(data, fn)
        return data

    @staticmethod
    def _tap(fn, x):
        fn(x); return x

    @staticmethod
    def _batcher(data, size):
        batch = []
        for x in data:
            batch.append(x)
            if len(batch) >= size:
                yield batch; batch = []
        if batch:
            yield batch

    def collect(self):
        return list(self._iterate())

    def reduce(self, fn, initial=None):
        it = iter(self._iterate())
        if initial is None:
            try:
                acc = next(it)
            except StopIteration:
                return None
        else:
            acc = initial
        for x in it:
            acc = fn(acc, x)
        return acc

    def count(self):
        return sum(1 for _ in self._iterate())

    def first(self, default=None):
        for x in self._iterate():
            return x
        return default
