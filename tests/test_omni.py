import os, sys, time, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.ironsight import Metrics
from aether.blazer import Blazer
from aether.blackbox import BlackBox
from aether.phoenix import Phoenix
from aether.eagle import Eagle

def test_ironsight_timer():
    m = Metrics()
    with m.timer("op"): time.sleep(0.05)
    assert "op" in m.snapshot()

def test_blazer_retry():
    s = {"n": 0}
    def flaky():
        s["n"] += 1
        if s["n"] < 3: raise RuntimeError("boom")
        return "ok"
    r = Blazer(max_retries=5, backoff=0.01).run([(flaky, (), {})])[0]
    assert r.success and r.result == "ok"

def test_blackbox():
    with tempfile.TemporaryDirectory() as t:
        bb = BlackBox(t)
        bb.record("boot", pid=1); bb.record("run", cmd="x")
        assert len(bb.replay()) == 2

def test_phoenix():
    with tempfile.TemporaryDirectory() as t:
        z = Path(t, "snapshot-test.zip")
        with zipfile.ZipFile(z, "w") as zf: zf.writestr("f.txt", "hi")
        r = Phoenix(t, Path(t, "r")).restore(z)
        assert r["files"] == 1 and len(r["hash"]) == 64

def test_eagle():
    with tempfile.TemporaryDirectory() as t:
        e = Eagle(f"{t}/e.db")
        e.index("A", "quick brown fox"); e.index("B", "military cryptography")
        assert e.count() == 2
        assert len(e.search("cryptography")) == 1

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_omni: PASS")
