"""CARVE - Pattern extraction."""
from __future__ import annotations
import re
from pathlib import Path

PATTERNS = {
    "url": re.compile(r"https?://[^\s\"'<>]+"),
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "md5": re.compile(r"\b[a-fA-F0-9]{32}\b"),
    "sha1": re.compile(r"\b[a-fA-F0-9]{40}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "base64": re.compile(r"\b[A-Za-z0-9+/]{20,}={0,2}\b"),
    "uuid": re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
}

class Carver:
    def __init__(self, patterns=None):
        self.patterns = patterns or PATTERNS

    def carve(self, text):
        found = {}
        for name, pat in self.patterns.items():
            matches = list(set(pat.findall(text)))
            if matches: found[name] = matches
        return found

    def carve_file(self, path):
        data = Path(path).read_bytes()
        try:
            text = data.decode("utf-8", "replace")
        except Exception:
            text = data.decode("latin-1", "replace")
        return self.carve(text)
