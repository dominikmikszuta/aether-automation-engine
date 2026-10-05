"""SABER - Batch signing and verification service."""
from __future__ import annotations
import json, time
from pathlib import Path
from .crypto_asym import generate_keypair, sign, verify, private_to_pem, public_to_pem

class Saber:
    def __init__(self, key_dir):
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self._priv = None
        self._pub = None

    def load_or_create(self, name="default"):
        priv_path = self.key_dir / f"{name}.key"
        pub_path = self.key_dir / f"{name}.pub"
        if priv_path.exists() and pub_path.exists():
            from cryptography.hazmat.primitives import serialization
            self._priv = serialization.load_pem_private_key(priv_path.read_bytes(), password=None)
            self._pub = serialization.load_pem_public_key(pub_path.read_bytes())
        else:
            self._priv, self._pub = generate_keypair()
            priv_path.write_bytes(private_to_pem(self._priv))
            pub_path.write_bytes(public_to_pem(self._pub))
            priv_path.chmod(0o600)
        return pub_path

    def sign_file(self, path):
        sig = sign(self._priv, Path(path).read_bytes())
        sig_path = Path(str(path) + ".sig")
        sig_path.write_bytes(sig)
        return sig_path

    def sign_batch(self, paths):
        return [self.sign_file(p) for p in paths]

    def verify_file(self, path):
        sig_path = Path(str(path) + ".sig")
        if not sig_path.exists():
            return False
        return verify(self._pub, sig_path.read_bytes(), Path(path).read_bytes())

    def manifest(self, paths):
        entries = []
        for p in paths:
            p = Path(p)
            entries.append({
                "path": str(p),
                "signed": self.verify_file(p),
                "sig_file": str(p) + ".sig",
            })
        return {
            "signed_count": sum(1 for e in entries if e["signed"]),
            "total": len(entries),
            "entries": entries,
            "timestamp": time.time(),
        }
