"""Encrypted key vault with Argon2id-derived master key (cryptography-only).

Blob layout: [16-byte salt][12-byte nonce][ciphertext+tag]
Salt is stored in the clear (it is not secret) so the KDF can be re-run.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

from .crypto import SymmetricCrypto, derive_key
from .crypto_asym import generate_keypair, private_to_pem, public_to_pem

DEFAULT_VAULT = Path.home() / ".aether" / "vault"


class Vault:
    def __init__(self, path: Path = DEFAULT_VAULT) -> None:
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def init(self, master_password: str) -> None:
        key, salt = derive_key(master_password)
        priv, pub = generate_keypair()
        payload = {
            "ed25519_priv": private_to_pem(priv).decode(),
            "ed25519_pub": public_to_pem(pub).decode(),
            "created": time.time(),
        }
        blob = SymmetricCrypto.aes_gcm_encrypt(key, json.dumps(payload).encode())
        (self.path / "master.enc").write_bytes(salt + blob)
        # zeroize key
        buf = bytearray(key)
        for i in range(len(buf)):
            buf[i] = 0

    def unlock(self, master_password: str) -> dict:
        raw = (self.path / "master.enc").read_bytes()
        salt, blob = raw[:16], raw[16:]
        key, _ = derive_key(master_password, salt=salt)
        try:
            return json.loads(SymmetricCrypto.aes_gcm_decrypt(key, blob))
        finally:
            buf = bytearray(key)
            for i in range(len(buf)):
                buf[i] = 0

    def rotate(self, master_password: str) -> None:
        self.unlock(master_password)  # verify old password still works
        self.init(master_password)
