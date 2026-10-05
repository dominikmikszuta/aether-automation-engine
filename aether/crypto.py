"""Military-grade crypto: AES-256-GCM, ChaCha20-Poly1305, Argon2id, SHA-3.

Uses only the `cryptography` package (v42+). No external bindings required.
"""
from __future__ import annotations
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


class SymmetricCrypto:
    @staticmethod
    def aes_gcm_encrypt(key: bytes, data: bytes, aad: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        return nonce + AESGCM(key).encrypt(nonce, data, aad)

    @staticmethod
    def aes_gcm_decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
        return AESGCM(key).decrypt(blob[:12], blob[12:], aad)

    @staticmethod
    def chacha_encrypt(key: bytes, data: bytes, aad: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        return nonce + ChaCha20Poly1305(key).encrypt(nonce, data, aad)

    @staticmethod
    def chacha_decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
        return ChaCha20Poly1305(key).decrypt(blob[:12], blob[12:], aad)


def derive_key(password: str, salt: bytes | None = None, length: int = 32) -> tuple[bytes, bytes]:
    salt = salt or os.urandom(16)
    kdf = Argon2id(
        salt=salt,
        length=length,
        iterations=3,
        lanes=4,
        memory_cost=65536,
    )
    return kdf.derive(password.encode()), salt


def sha3(data: bytes) -> str:
    return hashlib.sha3_256(data).hexdigest()
