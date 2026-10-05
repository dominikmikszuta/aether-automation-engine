"""Ed25519 signatures for authenticity and non-repudiation."""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

def generate_keypair():
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()

def sign(priv, data: bytes) -> bytes:
    return priv.sign(data)

def verify(pub, sig: bytes, data: bytes) -> bool:
    try:
        pub.verify(sig, data); return True
    except Exception:
        return False

def private_to_pem(priv) -> bytes:
    return priv.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption())

def public_to_pem(pub) -> bytes:
    return pub.public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo)
