import os, sys, time, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.nexus import Container
from aether.saber import Saber
from aether.sentry import Sentry
from aether.carbon import Config
from aether.vector import Pipeline
from aether.titan import Scheduler
from aether.prism import Prism
from aether.beacon import Beacon
from aether.forge import Forge
from aether.cipher import Cipher


def test_nexus():
    c = Container()
    c.register("x", instance=42)
    assert c.resolve("x") == 42


def test_saber():
    with tempfile.TemporaryDirectory() as t:
        s = Saber(t)
        p = Path(t, "file.txt")
        p.write_text("hello world")
        s.load_or_create()
        s.sign_file(p)
        assert s.verify_file(p)


def test_sentry():
    with tempfile.TemporaryDirectory() as t:
        Path(t, "f.txt").write_text("a")
        s = Sentry(t)
        s.baseline()
        Path(t, "g.txt").write_text("b")
        events = s.poll()
        assert any(e[0] == "created" for e in events)


def test_carbon():
    c = Config({"a": {"b": 1}})
    assert c.get("a.b") == 1


def test_vector():
    result = Pipeline([1, 2, 3, 4, 5]).filter(lambda x: x % 2 == 0).map(lambda x: x * 10).collect()
    assert result == [20, 40]
    total = Pipeline([1, 2, 3, 4]).reduce(lambda a, b: a + b, 0)
    assert total == 10


def test_titan():
    s = Scheduler()
    state = {"n": 0}
    s.register("job", lambda: state.update(n=state["n"] + 1), interval=0.0)
    time.sleep(0.05)
    s.run_once()
    assert state["n"] >= 1


def test_prism():
    p = Prism()
    html = p.to_html("# Title\nSome text\n- bullet 1", "T")
    assert "<h1>Title</h1>" in html


def test_beacon():
    b = Beacon()
    b.register("ok", lambda: True)
    b.register("fail", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    summary = b.summary()
    assert summary["status"] == "degraded"


def test_forge():
    tpl = Forge.from_string("Hello {{ name|upper }}, n={{ items|len }}")
    out = tpl.render({"name": "world", "items": [1, 2, 3]})
    assert out == "Hello WORLD, n=3"


def test_cipher():
    with tempfile.TemporaryDirectory() as t:
        c = Cipher(t, rotation_days=0, fast_kdf=True)
        key_id = c.auto_rotate()
        assert key_id is not None
        assert c.status()["current_key"] == key_id


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f):
            f()
    print("test_apex: PASS")
