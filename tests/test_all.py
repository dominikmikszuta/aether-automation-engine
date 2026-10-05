import os, sys, tempfile, json, zipfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aether.utils import sanitize_unicode, ensure_dir
from aether.pdf_engine import PDFEngine
from aether.portfolio import PortfolioBuilder
from aether.backup import BackupManager
from aether.chat_ingest import ChatIngest
def t_unicode(): assert sanitize_unicode("a\u2014b") == "a-b"
def t_pdf():
    with tempfile.TemporaryDirectory() as t:
        p = PDFEngine(title="T").write_simple(os.path.join(t,"o.pdf"), "Hi", ["A."])
        assert os.path.getsize(p) > 0
def t_port():
    with tempfile.TemporaryDirectory() as t:
        p = PortfolioBuilder(t).build("N","T","S",[{"name":"P","stack":"S","description":"D"}])
        assert os.path.getsize(p) > 0
def t_backup():
    with tempfile.TemporaryDirectory() as t:
        s = os.path.join(t,"s"); os.makedirs(s); open(os.path.join(s,"f"),"w").write("x")
        r = BackupManager(s, os.path.join(t,"d")).run()
        assert "mirror" in r and "zip" in r
def t_ingest():
    with tempfile.TemporaryDirectory() as t:
        z = os.path.join(t,"a.zip")
        with zipfile.ZipFile(z,"w") as f: f.writestr("d.json", json.dumps([{"title":"T","messages":[{"role":"u","content":"h"}]}]))
        ing = ChatIngest(t); j = ing.find_json(ing.extract(z))
        assert os.path.getsize(ing.build_pdf(j)) > 0
if __name__ == "__main__":
    for n,f in list(globals().items()):
        if n.startswith("t_") and callable(f): f()
    print("tests/test_all: PASS")
