import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.vault import Vault
from aether.audit import AuditLedger

def test_vault():
    with tempfile.TemporaryDirectory() as t:
        v = Vault(Path(t)); v.init("pw")
        assert "ed25519_pub" in v.unlock("pw")

def test_audit_chain():
    with tempfile.TemporaryDirectory() as t:
        lg = AuditLedger(Path(t) / "a.log")
        lg.append("boot", {"pid": 1}); lg.append("run", {"cmd": "x"})
        assert lg.verify_chain()

def test_audit_tamper():
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "a.log"; lg = AuditLedger(p)
        lg.append("x", {"a": 1})
        p.write_text(p.read_text().replace('"a": 1', '"a": 2'))
        assert not lg.verify_chain()

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_vault_audit: PASS")
