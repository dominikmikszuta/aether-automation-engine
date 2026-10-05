"""KATANA - Regex engine backed by Python stdlib re."""
from __future__ import annotations
import re


class Katana:
    @staticmethod
    def compile(pattern):
        return re.compile(pattern)

    @staticmethod
    def match(compiled, text):
        return compiled.fullmatch(text) is not None

    @staticmethod
    def search(pattern, text):
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        m = compiled.search(text)
        return (m.start(), m.end()) if m else None

    @staticmethod
    def findall(pattern, text):
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        return compiled.findall(text)

    @staticmethod
    def sub(pattern, replacement, text):
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        return compiled.sub(replacement, text)
