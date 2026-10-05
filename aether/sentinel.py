"""Integrity watchdog: file hashing, anomaly detection, quarantine.

`detect()` compares the current filesystem state against the stored
baseline WITHOUT overwriting it. Call `snapshot()` only when you want
to re-baseline (e.g. after an approved change).
"""
from __future__ import annotations
import hashlib
import os
import shutil
import time
from pathlib import Path


class Sentinel:
    def __init__(self, watch_dir, quarantine=None) -> None:
        self.watch_dir = Path(watch_dir)
        self.quarantine = Path(quarantine or (Path.home() / ".aether" / "quarantine"))
        self.quarantine.mkdir(parents=True, exist_ok=True)
        self._baseline: dict[str, str] = {}

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha3_256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _scan(self) -> dict[str, str]:
        snap = {}
        for root, _, files in os.walk(self.watch_dir):
            for name in files:
                p = Path(root) / name
                try:
                    snap[str(p)] = self._hash_file(p)
                except OSError:
                    pass
        return snap

    def snapshot(self) -> dict[str, str]:
        """Re-baseline the current state of the watched directory."""
        self._baseline = self._scan()
        return self._baseline

    def detect(self) -> dict[str, list]:
        """Compare current state against baseline. Does NOT modify baseline."""
        current = self._scan()
        added = [p for p in current if p not in self._baseline]
        removed = [p for p in self._baseline if p not in current]
        modified = [
            p for p in current
            if p in self._baseline and current[p] != self._baseline[p]
        ]
        return {"added": added, "removed": removed, "modified": modified}

    def quarantine_file(self, path: str) -> str:
        src = Path(path)
        dst = self.quarantine / f"{int(time.time())}_{src.name}.quarantined"
        shutil.move(str(src), str(dst))
        return str(dst)
