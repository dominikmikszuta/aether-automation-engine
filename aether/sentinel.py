"""SENTRY/SENTINEL - Integrity watchdog."""
from __future__ import annotations
import hashlib, os, shutil, time
from pathlib import Path


class Sentinel:
    def __init__(self, watch_dir, quarantine=None):
        self.watch_dir = Path(watch_dir)
        self.quarantine = Path(quarantine or (Path.home() / ".aether" / "quarantine"))
        self.quarantine.mkdir(parents=True, exist_ok=True)
        self._baseline = {}

    @staticmethod
    def _hash_file(path):
        h = hashlib.sha3_256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _scan(self):
        snap = {}
        for root, _, files in os.walk(self.watch_dir):
            for name in files:
                p = Path(root) / name
                try: snap[str(p)] = self._hash_file(p)
                except OSError: pass
        return snap

    def snapshot(self):
        self._baseline = self._scan()
        return self._baseline

    def detect(self):
        current = self._scan()
        added = [p for p in current if p not in self._baseline]
        removed = [p for p in self._baseline if p not in current]
        modified = [p for p in current if p in self._baseline
                    and current[p] != self._baseline[p]]
        return {"added": added, "removed": removed, "modified": modified}

    def poll(self):
        """Alias for detect() - returns events since last snapshot."""
        return self.detect()

    def quarantine_file(self, path):
        src = Path(path)
        dst = self.quarantine / f"{int(time.time())}_{src.name}.quarantined"
        shutil.move(str(src), str(dst))
        return str(dst)


# Alias dla kompatybilnosci
Sentry = Sentinel
