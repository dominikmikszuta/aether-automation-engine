"""STRINGS - ASCII + UTF-16 string extraction."""
from __future__ import annotations
import re
from pathlib import Path

class Strings:
    def __init__(self, min_length=4):
        self.min_length = min_length

    def extract_ascii(self, data):
        pat = re.compile(rb"[\x20-\x7e]{%d,}" % self.min_length)
        for m in pat.finditer(data):
            yield m.group().decode("ascii", "replace")

    def extract_utf16(self, data):
        pat = re.compile(rb"(?:[\x20-\x7e]\x00){%d,}" % self.min_length)
        for m in pat.finditer(data):
            yield m.group().decode("utf-16-le", "replace")

    def extract(self, path, encoding="both"):
        data = Path(path).read_bytes()
        results = []
        if encoding in ("ascii", "both"):
            results.extend(("ascii", s) for s in self.extract_ascii(data))
        if encoding in ("utf16", "both"):
            results.extend(("utf16", s) for s in self.extract_utf16(data))
        return results
