"""Append-only audit ledger with Merkle chain (tamper detection)."""
from __future__ import annotations
import json, time
from pathlib import Path
from .crypto import sha3
from .crypto_asym import sign, verify

DEFAULT_LEDGER = Path.home() / ".aether" / "audit.log"

class AuditLedger:
    def __init__(self, path: Path = DEFAULT_LEDGER, signing_key=None) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.signing_key = signing_key

    def _last_hash(self) -> str:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return "0" * 64
        lines = self.path.read_text().strip().splitlines()
        if not lines: return "0" * 64
        return json.loads(lines[-1])["hash"]

    def append(self, event: str, payload: dict) -> dict:
        prev = self._last_hash()
        entry = {"ts": time.time(), "event": event, "payload": payload, "prev": prev}
        raw = json.dumps(entry, sort_keys=True).encode()
        entry["hash"] = sha3(raw)
        if self.signing_key is not None:
            entry["sig"] = sign(self.signing_key, raw).hex()
        with self.path.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")
        return entry

    def verify_chain(self) -> bool:
        if not self.path.exists(): return True
        prev = "0" * 64
        for line in self.path.read_text().strip().splitlines():
            e = json.loads(line)
            raw = json.dumps({k: e[k] for k in ("ts","event","payload","prev")},
                             sort_keys=True).encode()
            if sha3(raw) != e["hash"] or e["prev"] != prev:
                return False
            prev = e["hash"]
        return True
