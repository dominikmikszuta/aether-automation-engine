"""LYNX - Plugin loader with hook system and hot reload."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any, Callable


class Plugin:
    def __init__(self, name, module, path):
        self.name = name
        self.module = module
        self.path = path
        self.hooks = {}
        self.enabled = True

    def register(self, hook_name, fn):
        self.hooks.setdefault(hook_name, []).append(fn)

    def fire(self, hook_name, *args, **kwargs):
        results = []
        for fn in self.hooks.get(hook_name, []):
            try:
                results.append(fn(*args, **kwargs))
            except Exception as e:
                results.append(f"error: {e}")
        return results


class Lynx:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._plugins = {}

    def _load_module(self, path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load(self, path):
        path = Path(path)
        name = path.stem
        try:
            module = self._load_module(path, f"plugin_{name}")
            plugin = Plugin(name=name, module=module, path=path)
            if hasattr(module, "register"):
                module.register(plugin)
            self._plugins[name] = plugin
            return plugin
        except Exception as e:
            raise RuntimeError(f"Failed to load {path}: {e}")

    def load_all(self):
        loaded = []
        for f in self.plugin_dir.glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                loaded.append(self.load(f))
            except Exception:
                pass
        return loaded

    def reload(self, name):
        plugin = self._plugins.get(name)
        if not plugin:
            raise KeyError(name)
        return self.load(plugin.path)

    def fire(self, hook_name, *args, **kwargs):
        results = {}
        for name, plugin in self._plugins.items():
            if plugin.enabled:
                results[name] = plugin.fire(hook_name, *args, **kwargs)
        return results

    def list(self):
        return [{"name": p.name, "enabled": p.enabled, "hooks": list(p.hooks.keys())}
                for p in self._plugins.values()]
