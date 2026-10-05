import os, sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.blackbox import BlackBox
from aether.phoenix import Phoenix

def test_blackbox_record_replay():
    with tempfile.TemporaryDirectory() as t:
        bb = BlackBox(t)
        bb.record("boot", pid=1); bb.record("run", cmd="test")
        events = bb.replay()
        assert len(events) == 2 and events[0].kind == "boot"

def test_blackbox_list_runs():
    with tempfile.TemporaryDirectory() as t:
        bb = BlackBox(t)
        bb.record("x", a=1)
        assert len(bb.list_runs()) >= 1

def test_phoenix_restore():
    with tempfile.TemporaryDirectory() as t:
        src = Path(t, "src"); src.mkdir()
        (src / "file.txt").write_text("hello")
        z = Path(t, "snapshot-test.zip")
        with zipfile.ZipFile(z, "w") as zf:
            zf.write(src / "file.txt", "file.txt")
        ph = Phoenix(t, Path(t, "restore"))
        result = ph.restore(z)
        assert result["files"] == 1 and len(result["hash"]) == 64

def test_phoenix_detects_corruption():
    with tempfile.TemporaryDirectory() as t:
        bad = Path(t, "snapshot-bad.zip")
        bad.write_text("not a zip")
        ph = Phoenix(t, Path(t, "restore"))
        assert not ph.verify(bad)

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_blackbox_phoenix: PASS")
