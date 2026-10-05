import os, sys, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.eagle import Eagle

def test_eagle_index_count():
    with tempfile.TemporaryDirectory() as t:
        e = Eagle(f"{t}/eagle.db")
        e.index("Doc A", "The quick brown fox jumps over the lazy dog", "a.txt")
        e.index("Doc B", "Military-grade cryptography with AES-256-GCM", "b.txt")
        assert e.count() == 2

def test_eagle_search():
    with tempfile.TemporaryDirectory() as t:
        e = Eagle(f"{t}/eagle.db")
        e.index("Doc A", "The quick brown fox jumps over the lazy dog")
        e.index("Doc B", "Military cryptography advanced")
        results = e.search("cryptography")
        assert len(results) == 1 and results[0]["title"] == "Doc B"

def test_eagle_porter_stemming():
    with tempfile.TemporaryDirectory() as t:
        e = Eagle(f"{t}/eagle.db")
        e.index("Doc", "running runs ran")
        assert len(e.search("run")) >= 1

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f): f()
    print("test_eagle: PASS")
