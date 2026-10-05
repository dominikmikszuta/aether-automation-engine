"""CARBON - Unified configuration manager (JSON/YAML/TOML/env)."""
from __future__ import annotations
import json, os
from pathlib import Path

class Config:
    def __init__(self, data=None, env_prefix="AETHER_"):
        self._data = data or {}
        self._env_prefix = env_prefix
        self._apply_env()

    def _apply_env(self):
        for key, value in os.environ.items():
            if not key.startswith(self._env_prefix):
                continue
            path = key[len(self._env_prefix):].lower().split("__")
            self._set_nested(self._data, path, self._coerce(value))

    @staticmethod
    def _coerce(value):
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        if value.lower() in ("null", "none"):
            return None
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    @staticmethod
    def _set_nested(data, path, value):
        cur = data
        for key in path[:-1]:
            cur = cur.setdefault(key, {})
        cur[path[-1]] = value

    def get(self, path, default=None):
        keys = path.split(".") if isinstance(path, str) else path
        cur = self._data
        for key in keys:
            if not isinstance(cur, dict) or key not in cur:
                return default
            cur = cur[key]
        return cur

    def set(self, path, value):
        keys = path.split(".") if isinstance(path, str) else path
        self._set_nested(self._data, keys, value)

    def merge(self, other):
        self._deep_merge(self._data, other._data if isinstance(other, Config) else other)
        return self

    @staticmethod
    def _deep_merge(a, b):
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                Config._deep_merge(a[k], v)
            else:
                a[k] = v

    def to_dict(self):
        return json.loads(json.dumps(self._data))

    @classmethod
    def from_file(cls, path):
        path = Path(path)
        text = path.read_text()
        suffix = path.suffix.lower()
        if suffix == ".json":
            data = json.loads(text)
        elif suffix in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(text)
            except ImportError:
                raise RuntimeError("PyYAML not installed")
        elif suffix == ".toml":
            try:
                import tomllib
                data = tomllib.loads(text)
            except ImportError:
                try:
                    import tomli as tomllib
                    data = tomllib.loads(text)
                except ImportError:
                    raise RuntimeError("tomli/tomllib not available")
        else:
            raise ValueError(f"Unsupported format: {suffix}")
        return cls(data)
