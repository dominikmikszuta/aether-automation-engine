"""Military CLI extensions: encrypt, decrypt, sign, verify, audit, vault, sentinel, airgap."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .crypto import SymmetricCrypto, derive_key
from .crypto_asym import sign as ed_sign, verify as ed_verify, generate_keypair
from .vault import Vault
from .audit import AuditLedger
from .sentinel import Sentinel
from .airgap import enable_airgap, MLS_LEVELS
from .utils import log

def _encrypt(a):
    key, salt = derive_key(a.password)
    blob = SymmetricCrypto.aes_gcm_encrypt(key, Path(a.input).read_bytes())
    Path(a.output).write_bytes(salt + blob)
    log(f"Encrypted: {a.output}")

def _decrypt(a):
    raw = Path(a.input).read_bytes()
    key, _ = derive_key(a.password, salt=raw[:16])
    Path(a.output).write_bytes(SymmetricCrypto.aes_gcm_decrypt(key, raw[16:]))
    log(f"Decrypted: {a.output}")

def _sign(a):
    priv, _ = generate_keypair()
    Path(a.output).write_bytes(ed_sign(priv, Path(a.input).read_bytes()))
    log(f"Signature: {a.output}")

def _verify(a):
    from cryptography.hazmat.primitives import serialization
    pub = serialization.load_pem_public_key(Path(a.key).read_bytes())
    ok = ed_verify(pub, Path(a.signature).read_bytes(), Path(a.input).read_bytes())
    log(f"Signature valid: {ok}")

def _audit(a):
    lg = AuditLedger()
    if a.verify: log(f"Chain valid: {lg.verify_chain()}")
    else: lg.append("cli.audit", {"tail": a.tail})

def _vault(a):
    v = Vault()
    if a.action == "init": v.init(a.password)
    elif a.action == "rotate": v.rotate(a.password)
    log(f"Vault: {a.action} done")

def _sentinel(a):
    s = Sentinel(Path(a.watch))
    s.snapshot(); s.snapshot()
    log(f"Sentinel: clean={s.detect() == {'added':[],'removed':[],'modified':[]}}")

def _airgap(a):
    enable_airgap()
    log(f"Air-gap enabled at level {a.level}")

def register_military(sub):
    p = sub.add_parser("encrypt"); p.add_argument("--input", required=True); p.add_argument("--output", required=True); p.add_argument("--password", required=True); p.set_defaults(func=_encrypt)
    p = sub.add_parser("decrypt"); p.add_argument("--input", required=True); p.add_argument("--output", required=True); p.add_argument("--password", required=True); p.set_defaults(func=_decrypt)
    p = sub.add_parser("sign"); p.add_argument("--input", required=True); p.add_argument("--output", required=True); p.set_defaults(func=_sign)
    p = sub.add_parser("verify"); p.add_argument("--input", required=True); p.add_argument("--signature", required=True); p.add_argument("--key", required=True); p.set_defaults(func=_verify)
    p = sub.add_parser("audit"); p.add_argument("--tail", type=int, default=10); p.add_argument("--verify", action="store_true"); p.set_defaults(func=_audit)
    p = sub.add_parser("vault"); p.add_argument("action", choices=["init","rotate"]); p.add_argument("--password", required=True); p.set_defaults(func=_vault)
    p = sub.add_parser("sentinel"); p.add_argument("--watch", required=True); p.set_defaults(func=_sentinel)
    p = sub.add_parser("airgap"); p.add_argument("--level", choices=list(MLS_LEVELS), default="SECRET"); p.set_defaults(func=_airgap)
