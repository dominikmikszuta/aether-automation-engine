import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.ironsight import Metrics
from aether.blazer import Blazer

def test_ironsight_timer():
    m = Metrics()
    with m.timer("op"):
        time.sleep(0.05)
    snap = m.snapshot()
    assert "op" in snap and snap["op"][0]["unit"] == "ms"

def test_ironsight_counter():
    m = Metrics()
    m.reset()
    m.increment("hits"); m.increment("hits"); m.increment("hits")
    assert m.snapshot()["hits"][-1]["value"] == 3.0

def test_blazer_success():
    def double(x): return x * 2
    results = Blazer(workers=2).run([(double, (5,), {}), (double, (10,), {})])
    assert all(r.success for r in results)
    assert sorted(r.result for r in results) == [10, 20]

def test_blazer_retry():
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] < 3: raise RuntimeError("boom")
        return "ok"
    r = Blazer(max_retries=5, backoff=0.01).run([(flaky, (), {})])[0]
    assert r.success and r.result == "ok"

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_ironsight_blazer: PASS")
