"""KATANA - Regex engine backed by Python stdlib re."""
from __future__ import annotations
import re


class Katana:
    @staticmethod
    def compile(pattern):
        """Compile a pattern to a matcher object."""
        return re.compile(pattern)

    @staticmethod
    def match(compiled, text):
        """Full-string match."""
        return compiled.fullmatch(text) is not None

    @staticmethod
    def search(pattern, text):
        """Return (start, end) of first match, or None."""
        if isinstance(pattern, str):
            compiled = re.compile(pattern)
        else:
            compiled = pattern
        m = compiled.search(text)
        if not m:
            return None
        return (m.start(), m.end())

    @staticmethod
    def findall(pattern, text):
        if isinstance(pattern, str):
            compiled = re.compile(pattern)
        else:
            compiled = pattern
        return compiled.findall(text)

    @staticmethod
    def sub(pattern, replacement, text):
        if isinstance(pattern, str):
            compiled = re.compile(pattern)
        else:
            compiled = pattern
        return compiled.sub(replacement, text)
