"""BLACKBOX - Append-only incident recorder with replay."""
from __future__ import annotations
import json, time
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock

@dataclass
class Event:
    ts: float
    kind: str
    payload: dict
    run_id: str = ""
    seq: int = 0

class BlackBox:
    def __init__(self, log_dir):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._seq = 0
        self._current = self._new_id()

    @staticmethod
    def _new_id():
        return time.strftime("%Y%m%d-%H%M%S")

    def _file(self):
        return self.log_dir / f"{self._current}.ndjson"

    def record(self, kind, **payload):
        with self._lock:
            self._seq += 1
            e = Event(time.time(), kind, payload, self._current, self._seq)
            with self._file().open("a") as f:
                f.write(json.dumps(asdict(e)) + "\n")

    def replay(self, run_id=""):
        target = self.log_dir / f"{run_id or self._current}.ndjson"
        if not target.exists():
            return []
        return [Event(**json.loads(l)) for l in target.read_text().splitlines()]

    def list_runs(self):
        return sorted(p.stem for p in self.log_dir.glob("*.ndjson"))

    def rotate(self):
        self._current = self._new_id()
        self._seq = 0
