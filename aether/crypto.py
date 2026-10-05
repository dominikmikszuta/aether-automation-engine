"""Symmetric crypto: AES-256-GCM, ChaCha20-Poly1305, Argon2id, SHA-3."""
from __future__ import annotations
import hashlib, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


class SymmetricCrypto:
    @staticmethod
    def aes_gcm_encrypt(key, data, aad=b""):
        nonce = os.urandom(12)
        return nonce + AESGCM(key).encrypt(nonce, data, aad)

    @staticmethod
    def aes_gcm_decrypt(key, blob, aad=b""):
        return AESGCM(key).decrypt(blob[:12], blob[12:], aad)

    @staticmethod
    def chacha_encrypt(key, data, aad=b""):
        nonce = os.urandom(12)
        return nonce + ChaCha20Poly1305(key).encrypt(nonce, data, aad)

    @staticmethod
    def chacha_decrypt(key, blob, aad=b""):
        return ChaCha20Poly1305(key).decrypt(blob[:12], blob[12:], aad)


def derive_key(password, salt=None, length=32, fast=False):
    """Argon2id key derivation.

    fast=True: iterations=1, memory=8 MB (for tests/rotation)
    fast=False: iterations=3, memory=64 MB (production)
    """
    salt = salt or os.urandom(16)
    if fast:
        kdf = Argon2id(salt=salt, length=length, iterations=1, lanes=1, memory_cost=8192)
    else:
        kdf = Argon2id(salt=salt, length=length, iterations=3, lanes=4, memory_cost=65536)
    return kdf.derive(password.encode()), salt


def sha3(data: bytes) -> str:
    return hashlib.sha3_256(data).hexdigest()
