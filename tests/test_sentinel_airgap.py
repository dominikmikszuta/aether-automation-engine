import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.sentinel import Sentinel
from aether.airgap import authorize, flow_check, pad_to_block, set_compartments

def test_clean():
    with tempfile.TemporaryDirectory() as t:
        Path(t, "f.txt").write_text("x")
        s = Sentinel(Path(t)); s.snapshot()
        assert s.detect() == {"added": [], "removed": [], "modified": []}

def test_modified():
    with tempfile.TemporaryDirectory() as t:
        p = Path(t, "f.txt"); p.write_text("x")
        s = Sentinel(Path(t)); s.snapshot()
        p.write_text("y")
        assert str(p) in s.detect()["modified"]

def test_flow():
    assert flow_check("SECRET", "CONFIDENTIAL")
    assert not flow_check("CONFIDENTIAL", "SECRET")

def test_authorize():
    set_compartments(["AETHER"])
    assert authorize("SECRET", ["AETHER"])
    assert not authorize("SECRET", ["BLUE"])

def test_pad():
    assert len(pad_to_block(b"abc", block=64)) == 64

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_sentinel_airgap: PASS")
