# AETHER-QM - Cryptographic Specification

## Algorithms
| Primitive | Algorithm | Standard | Key/Nonce |
|-----------|-----------|----------|-----------|
| Symmetric AEAD | AES-256-GCM | FIPS 197 / NIST SP 800-38D | 256-bit key, 96-bit nonce |
| Symmetric AEAD | ChaCha20-Poly1305 | RFC 8439 | 256-bit key, 96-bit nonce |
| Password KDF | Argon2id | RFC 9106 | 3 iter, 64 MiB, 4 lanes |
| Signature | Ed25519 | RFC 8032 | 256-bit key |
| Hash | SHA3-256 | FIPS 202 | N/A |

## Key Management
- Master key derived via Argon2id with 16-byte random salt.
- Ed25519 keypair stored encrypted under master key.
- Zeroization on unlock exit (3-pass overwrite in memory).

## Nonce Policy
- Nonces generated via os.urandom(12) - CSPRNG.
- No nonce reuse: single-use per encryption call.
- AAD supported for context binding.

## Compliance
- NIST SP 800-53: SC-12, SC-13, SC-28
- FIPS 140-3 (via cryptography provider)
- Common Criteria EAL2+ target
