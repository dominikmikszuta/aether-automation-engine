import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.sentinel import Sentinel
from aether.airgap import authorize, flow_check, pad_to_block, set_compartments

def test_sentinel_clean():
    with tempfile.TemporaryDirectory() as t:
        Path(t, "f.txt").write_text("x")
        s = Sentinel(Path(t)); s.snapshot()
        d = s.detect()
        assert d == {"added": [], "removed": [], "modified": []}

def test_sentinel_modified():
    with tempfile.TemporaryDirectory() as t:
        p = Path(t, "f.txt"); p.write_text("x")
        s = Sentinel(Path(t)); s.snapshot()
        p.write_text("y")
        d = s.detect()
        assert str(p) in d["modified"]

def test_mls_flow():
    assert flow_check("SECRET", "CONFIDENTIAL")
    assert not flow_check("CONFIDENTIAL", "SECRET")

def test_mls_authorize():
    set_compartments(["AETHER", "RED"])
    assert authorize("SECRET", ["AETHER"])
    assert not authorize("SECRET", ["BLUE"])

def test_pad():
    assert len(pad_to_block(b"abc", block=64)) == 64

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_sentinel_airgap: PASS")
