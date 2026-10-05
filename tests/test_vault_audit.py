import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.vault import Vault
from aether.audit import AuditLedger

def test_vault_init_unlock():
    with tempfile.TemporaryDirectory() as t:
        v = Vault(Path(t))
        v.init("supersecret")
        data = v.unlock("supersecret")
        assert "ed25519_pub" in data

def test_audit_chain_valid():
    with tempfile.TemporaryDirectory() as t:
        lg = AuditLedger(Path(t) / "a.log")
        lg.append("boot", {"pid": 1})
        lg.append("run", {"cmd": "portfolio"})
        assert lg.verify_chain()

def test_audit_tamper_detected():
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "a.log"
        lg = AuditLedger(p)
        lg.append("x", {"a": 1})
        raw = p.read_text().replace('"a": 1', '"a": 2')
        p.write_text(raw)
        assert not lg.verify_chain()

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_vault_audit: PASS")
