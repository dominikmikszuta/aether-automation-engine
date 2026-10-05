"""ORACLE - DAG workflow engine with dependency resolution."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Task:
    name: str
    fn: Callable
    deps: list = field(default_factory=list)
    result: Any = None
    status: str = "pending"  # pending | running | done | failed
    error: str = ""


class Oracle:
    def __init__(self):
        self.tasks = {}

    def task(self, name, deps=None):
        def decorator(fn):
            self.tasks[name] = Task(name=name, fn=fn, deps=deps or [])
            return fn
        return decorator

    def add(self, name, fn, deps=None):
        self.tasks[name] = Task(name=name, fn=fn, deps=deps or [])
        return self

    def _topo(self):
        visited, order = set(), []
        def visit(name, stack):
            if name in stack:
                raise ValueError(f"Cycle detected: {name}")
            if name in visited:
                return
            stack.add(name)
            for d in self.tasks[name].deps:
                if d not in self.tasks:
                    raise KeyError(f"Missing dependency: {d}")
                visit(d, stack)
            stack.remove(name)
            visited.add(name)
            order.append(name)
        for n in self.tasks:
            visit(n, set())
        return order

    def run(self, context=None):
        context = context or {}
        order = self._topo()
        results = {}
        for name in order:
            task = self.tasks[name]
            task.status = "running"
            try:
                args = {d: results[d] for d in task.deps}
                task.result = task.fn(**args, **context)
                task.status = "done"
                results[name] = task.result
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                results[name] = None
        return results

    def status(self):
        return {n: {"status": t.status, "error": t.error, "deps": t.deps}
                for n, t in self.tasks.items()}
