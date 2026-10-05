"""SENTRY - Real-time filesystem event stream."""
from __future__ import annotations
import time
from pathlib import Path

class Sentry:
    def __init__(self, path):
        self.path = Path(path)
        self._state = {}

    def _scan(self):
        snap = {}
        for f in self.path.rglob("*"):
            if f.is_file():
                try:
                    st = f.stat()
                    snap[str(f)] = (st.st_mtime, st.st_size)
                except OSError:
                    pass
        return snap

    def baseline(self):
        self._state = self._scan()
        return len(self._state)

    def poll(self):
        current = self._scan()
        events = []
        for p in current:
            if p not in self._state:
                events.append(("created", p, current[p]))
            elif current[p] != self._state[p]:
                events.append(("modified", p, current[p]))
        for p in self._state:
            if p not in current:
                events.append(("deleted", p, self._state[p]))
        self._state = current
        return events

    def watch(self, interval=1.0, duration=None, callback=None):
        start = time.time()
        while True:
            for kind, path, meta in self.poll():
                if callback:
                    callback(kind, path, meta)
            if duration and (time.time() - start) >= duration:
                break
            time.sleep(interval)
