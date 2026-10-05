# AETHER-QM — Threat Model (STRIDE + MITRE ATT&CK)

## Scope
Filesystem, cryptographic material, network isolation, PDF outputs.

## STRIDE Matrix

| Threat | Vector | Control |
|--------|--------|---------|
| **S**poofing | Forged PDF author | Ed25519 signatures |
| **T**ampering | Modified files on disk | Sentinel hashing + Merkle audit chain |
| **R**epudiation | Denied operation | Append-only signed audit ledger |
| **I**nfo Disclosure | Plaintext on disk | AES-256-GCM + ChaCha20-Poly1305 |
| **D**oS | Resource exhaustion | Argon2id cost tuning + rate limit |
| **E**levation | Key theft | Vault zeroization + Argon2id KDF |

## MITRE ATT&CK Coverage

| Tactic | Technique | Mitigation |
|--------|-----------|------------|
| Credential Access | T1552 Unsecured Credentials | Vault encryption |
| Exfiltration | T1041 C2 Channel | Air-gap mode (socket block) |
| Persistence | T1547 Boot Autostart | Sentinel watchdog |
| Defense Evasion | T1070 Indicator Removal | Merkle audit chain |
| Collection | T1005 Local Data | MLS labels |
