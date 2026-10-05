"""CIPHER - Automatic key rotation service."""
from __future__ import annotations
import json, time
from pathlib import Path

class Cipher:
    def __init__(self, key_dir, rotation_days=90):
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.rotation_seconds = rotation_days * 86400

    def _meta_path(self):
        return self.key_dir / "meta.json"

    def _load_meta(self):
        p = self._meta_path()
        if p.exists():
            return json.loads(p.read_text())
        return {"keys": [], "current": None}

    def _save_meta(self, meta):
        self._meta_path().write_text(json.dumps(meta, indent=2))

    def rotate(self, name="master"):
        from .crypto import derive_key
        from .crypto_asym import generate_keypair, private_to_pem, public_to_pem
        import os

        key_id = time.strftime("%Y%m%d-%H%M%S")
        key_path = self.key_dir / f"{name}-{key_id}"

        # Symmetric key
        sym_key, salt = derive_key(key_id, length=32)
        (self.key_dir / f"{name}-{key_id}.sym").write_bytes(salt + sym_key)

        # Asymmetric
        priv, pub = generate_keypair()
        (self.key_dir / f"{name}-{key_id}.priv").write_bytes(private_to_pem(priv))
        (self.key_dir / f"{name}-{key_id}.pub").write_bytes(public_to_pem(pub))

        # Update meta
        meta = self._load_meta()
        old = meta.get("current")
        if old:
            meta.setdefault("history", []).append({
                "id": old, "rotated_at": time.time(), "reason": "rotation"
            })
        meta["current"] = key_id
        meta.setdefault("keys", []).append({"id": key_id, "created": time.time()})
        self._save_meta(meta)

        # Zeroize
        sym_key = bytearray(sym_key)
        for i in range(len(sym_key)):
            sym_key[i] = 0

        return key_id

    def needs_rotation(self):
        meta = self._load_meta()
        current = meta.get("current")
        if not current:
            return True
        for k in meta.get("keys", []):
            if k["id"] == current:
                return (time.time() - k["created"]) >= self.rotation_seconds
        return True

    def auto_rotate(self, name="master"):
        if self.needs_rotation():
            return self.rotate(name)
        return None

    def status(self):
        meta = self._load_meta()
        return {
            "current_key": meta.get("current"),
            "total_rotations": len(meta.get("history", [])),
            "keys": len(meta.get("keys", [])),
            "needs_rotation": self.needs_rotation(),
        }
