# Changelog

All notable changes to AETHER-QM are documented in this file.

## [30.1.0] - IRONCLAD - 2026-10-06

### Highlights
Production-grade release. All test suites green.

### Stability
- Deterministic Argon2id KDF modes (fast for tests, hardened for production)
- Eager evaluation in data pipeline
- Forced execution in scheduler run_once
- Native regex backend
- Clean PEM key loader

### Stack
- **Core:** PDF engine, chat ingest, portfolio, backup
- **Military:** AES-256-GCM, ChaCha20-Poly1305, Ed25519, Argon2id, SHA3-256
- **Security:** vault, Merkle audit ledger, sentinel, MLS airgap
- **OMNI:** metrics, parallel runner, event recorder, backup restore, FTS5 search
- **APEX:** DI container, batch signing, watcher, config, pipeline, scheduler, renderer, health checks, templates, key rotation
- **SPECTRE:** binary recon, ELF/PE parser, strings, entropy, pattern carving, XOR trace
- **OMEGA:** async runtime, plugin loader, bytecode VM, network clients, TLV serialization, compression, dashboard, web framework, NFA search, DAG workflow

### Install
```
pip install aether-automation-engine
```
