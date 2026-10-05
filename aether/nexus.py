"""NEXUS - Dependency injection and service registry."""
from __future__ import annotations
from typing import Any, Callable

class Container:
    def __init__(self):
        self._services = {}
        self._singletons = {}
        self._factories = {}

    def register(self, name, instance=None, factory=None, singleton=True):
        if factory:
            self._factories[name] = (factory, singleton)
        elif instance is not None:
            self._services[name] = instance

    def resolve(self, name):
        if name in self._singletons:
            return self._singletons[name]
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            factory, singleton = self._factories[name]
            obj = factory(self)
            if singleton:
                self._singletons[name] = obj
            return obj
        raise KeyError(f"Service not registered: {name}")

    def has(self, name):
        return name in self._services or name in self._singletons or name in self._factories

    def list(self):
        return sorted(set(self._services) | set(self._singletons) | set(self._factories))


container = Container()
