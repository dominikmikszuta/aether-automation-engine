# AETHER-QM - Compliance Mapping

## NIST SP 800-53 Rev. 5
| Control | Family | AETHER Module |
|---------|--------|---------------|
| AC-3 | Access Enforcement | airgap.authorize |
| AC-4 | Information Flow | airgap.flow_check |
| AU-2 | Event Logging | audit.AuditLedger |
| AU-9 | Protection of Audit Info | audit.verify_chain |
| SC-8 | Transmission Confidentiality | crypto.SymmetricCrypto |
| SC-12 | Cryptographic Key Establishment | vault.Vault |
| SC-13 | Cryptographic Protection | crypto (AES-GCM, ChaCha20) |
| SC-28 | Protection of Info at Rest | vault + AES-256-GCM |
| SI-4 | System Monitoring | sentinel.Sentinel |
| SI-7 | Software Integrity | audit + Ed25519 |

## ISO/IEC 27001:2022
- A.8.24 Cryptography: crypto.py
- A.8.16 Monitoring: sentinel.py
- A.5.15 Access Control: airgap.py
- A.8.15 Logging: audit.py

## Common Criteria EAL2
Target of Evaluation: AETHER-QM runtime and vault subsystem.

## CMMC Level 2
Full coverage of AU, SC, SI, AC domains.

## GDPR Article 32
State-of-the-art encryption (AES-256-GCM), pseudonymization, integrity.
