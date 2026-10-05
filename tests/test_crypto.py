import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.crypto import SymmetricCrypto, derive_key, sha3
from aether.crypto_asym import generate_keypair, sign, verify

def test_aes_roundtrip():
    key = os.urandom(32)
    ct = SymmetricCrypto.aes_gcm_encrypt(key, b"hello")
    assert SymmetricCrypto.aes_gcm_decrypt(key, ct) == b"hello"

def test_chacha_roundtrip():
    key = os.urandom(32)
    ct = SymmetricCrypto.chacha_encrypt(key, b"world")
    assert SymmetricCrypto.chacha_decrypt(key, ct) == b"world"

def test_argon2():
    k1, s = derive_key("pw", length=32)
    k2, _ = derive_key("pw", salt=s, length=32)
    assert k1 == k2 and len(k1) == 32

def test_sha3_deterministic():
    assert sha3(b"x") == sha3(b"x")

def test_ed25519_sign_verify():
    priv, pub = generate_keypair()
    sig = sign(priv, b"payload")
    assert verify(pub, sig, b"payload")
    assert not verify(pub, sig, b"tampered")

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_crypto: PASS")
