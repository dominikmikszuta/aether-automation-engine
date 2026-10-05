import argparse, sys
from .portfolio import PortfolioBuilder
from .chat_ingest import ChatIngest
from .backup import BackupManager
from .utils import log
from . import __version__
def _p(a): log("PDF: "+PortfolioBuilder(a.output).build(name="Dominik Mikszuta", title="Systems Architect | C++ / Python", summary="Systems Architect specializing in C++ (23/26), Python, and Linux.", projects=[{"name":"AETHER-QM","stack":"Python,FPDF2,Termux,ARM64","description":"Offline-first automation with Unicode-safe PDFs."}]))
def _i(a):
    ing = ChatIngest(a.output); j = ing.find_json(ing.extract(a.archive))
    if not j: log("no json","ERROR"); sys.exit(1)
    log("PDF: "+ing.build_pdf(j))
def _b(a): log("Backup: "+str(BackupManager(a.source, a.destination).run()))
def main(argv=None):
    p = argparse.ArgumentParser(prog="aether", description=f"AETHER-QM v{__version__}")
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("portfolio"); x.add_argument("--output",default="output"); x.set_defaults(func=_p)
    x = s.add_parser("ingest"); x.add_argument("--archive",required=True); x.add_argument("--output",default="output"); x.set_defaults(func=_i)
    x = s.add_parser("backup"); x.add_argument("--source",required=True); x.add_argument("--destination",required=True); x.set_defaults(func=_b)
    a = p.parse_args(argv); a.func(a); return 0
if __name__ == "__main__": sys.exit(main())
