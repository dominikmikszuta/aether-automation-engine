"""FORGE - Lightweight template engine for reports."""
from __future__ import annotations
import re

_TOKEN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")

class Template:
    def __init__(self, text):
        self.text = text

    def render(self, context):
        def replace(match):
            expr = match.group(1).strip()
            return str(self._eval(expr, context))
        return _TOKEN.sub(replace, self.text)

    @staticmethod
    def _eval(expr, context):
        # Support: var, var.attr, var[key], var|filter
        if "|" in expr:
            base, _, filter_name = expr.partition("|")
            value = Template._resolve(base.strip(), context)
            return Template._apply_filter(filter_name.strip(), value)
        return Template._resolve(expr, context)

    @staticmethod
    def _resolve(path, context):
        if path in context:
            return context[path]
        parts = re.split(r"\.|\[|\]", path)
        cur = context
        for p in parts:
            p = p.strip("'\"")
            if not p:
                continue
            if isinstance(cur, dict):
                cur = cur.get(p, "")
            elif isinstance(cur, (list, tuple)):
                try:
                    cur = cur[int(p)]
                except (ValueError, IndexError):
                    return ""
            else:
                cur = getattr(cur, p, "")
        return cur

    @staticmethod
    def _apply_filter(name, value):
        filters = {
            "upper": lambda v: str(v).upper(),
            "lower": lambda v: str(v).lower(),
            "title": lambda v: str(v).title(),
            "trim": lambda v: str(v).strip(),
            "len": lambda v: len(v) if hasattr(v, "__len__") else 0,
            "json": lambda v: __import__("json").dumps(v, default=str),
            "default": lambda v: v if v else "",
        }
        if ":" in name:
            fname, arg = name.split(":", 1)
            if fname == "default" and value:
                return value
            if fname == "default":
                return arg
        return filters.get(name, lambda v: v)(value)

class Forge:
    @staticmethod
    def from_string(text):
        return Template(text)

    @staticmethod
    def from_file(path):
        from pathlib import Path
        return Template(Path(path).read_text())
