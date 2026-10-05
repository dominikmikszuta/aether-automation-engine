"""PHOENIX - Automatic recovery from backups with verification."""
from __future__ import annotations
import hashlib, zipfile
from pathlib import Path
from datetime import datetime

class Phoenix:
    def __init__(self, backup_dir, restore_dir):
        self.backup_dir = Path(backup_dir)
        self.restore_dir = Path(restore_dir)

    @staticmethod
    def _hash_dir(path):
        h = hashlib.sha3_256()
        for f in sorted(path.rglob("*")):
            if f.is_file():
                h.update(str(f.relative_to(path)).encode())
                h.update(f.read_bytes())
        return h.hexdigest()

    def list_backups(self):
        return sorted(self.backup_dir.glob("snapshot-*.zip"), reverse=True)

    def verify(self, snapshot):
        try:
            with zipfile.ZipFile(snapshot) as z:
                return z.testzip() is None
        except Exception:
            return False

    def restore(self, snapshot, verify=True):
        if verify and not self.verify(snapshot):
            raise ValueError(f"Corrupted: {snapshot}")
        target = self.restore_dir / f"restored-{datetime.now():%Y%m%d-%H%M%S}"
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(snapshot) as z:
            z.extractall(target)
        return {
            "snapshot": str(snapshot), "target": str(target),
            "hash": self._hash_dir(target),
            "files": sum(1 for _ in target.rglob("*") if _.is_file()),
        }

    def restore_latest(self):
        backups = self.list_backups()
        if not backups:
            raise FileNotFoundError("No backups available")
        for b in backups:
            if self.verify(b):
                return self.restore(b)
        raise ValueError("All backups corrupted")
