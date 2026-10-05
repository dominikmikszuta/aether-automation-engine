import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.crypto import SymmetricCrypto, derive_key, sha3
from aether.crypto_asym import generate_keypair, sign, verify

def test_aes_roundtrip():
    k = os.urandom(32)
    assert SymmetricCrypto.aes_gcm_decrypt(k, SymmetricCrypto.aes_gcm_encrypt(k, b"hello")) == b"hello"

def test_chacha_roundtrip():
    k = os.urandom(32)
    assert SymmetricCrypto.chacha_decrypt(k, SymmetricCrypto.chacha_encrypt(k, b"world")) == b"world"

def test_argon2():
    k1, s = derive_key("pw", length=32)
    k2, _ = derive_key("pw", salt=s, length=32)
    assert k1 == k2

def test_sha3():
    assert sha3(b"x") == sha3(b"x")

def test_ed25519():
    priv, pub = generate_keypair()
    sig = sign(priv, b"payload")
    assert verify(pub, sig, b"payload")
    assert not verify(pub, sig, b"tampered")

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_crypto: PASS")
