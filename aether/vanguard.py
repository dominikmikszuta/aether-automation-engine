"""VANGUARD - Unified command-line interface for AETHER-QM."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .ironsight import Metrics
from .blackbox import BlackBox
from .phoenix import Phoenix
from .eagle import Eagle
from .utils import log
from . import __version__

def cmd_metrics(a):
    m = Metrics()
    if a.export:
        m.export(a.export); log(f"Exported: {a.export}")
    else:
        print(json.dumps(m.snapshot(), indent=2))

def cmd_replay(a):
    bb = BlackBox(a.log_dir)
    if a.list:
        for r in bb.list_runs(): print(r)
        return
    for e in bb.replay(a.run_id):
        print(f"[{e.ts:.3f}] {e.kind}: {json.dumps(e.payload)}")

def cmd_restore(a):
    ph = Phoenix(a.backup_dir, a.restore_dir)
    r = ph.restore_latest() if a.latest else ph.restore(Path(a.snapshot))
    log(f"Restored: {r}")

def cmd_search(a):
    e = Eagle(a.db)
    if a.index:
        c = Path(a.index).read_text()
        e.index(title=Path(a.index).name, content=c, source=a.index)
        log(f"Indexed: {a.index} (total: {e.count()})"); return
    for r in e.search(a.query):
        print(f"{r['title']} [{r['source']}]\n  {r['snippet']}\n")

def main(argv=None):
    p = argparse.ArgumentParser(prog="vanguard",
        description=f"AETHER-QM VANGUARD v{__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("metrics"); m.add_argument("--export"); m.set_defaults(func=cmd_metrics)
    r = sub.add_parser("replay"); r.add_argument("--log-dir", default="~/.aether/blackbox"); r.add_argument("--run-id", default=""); r.add_argument("--list", action="store_true"); r.set_defaults(func=cmd_replay)
    s = sub.add_parser("restore"); s.add_argument("--backup-dir", required=True); s.add_argument("--restore-dir", required=True); s.add_argument("--latest", action="store_true"); s.add_argument("--snapshot", default=""); s.set_defaults(func=cmd_restore)
    e = sub.add_parser("search"); e.add_argument("--db", default="~/.aether/eagle.db"); e.add_argument("--query", default=""); e.add_argument("--index", default=""); e.set_defaults(func=cmd_search)
    a = p.parse_args(argv); a.func(a); return 0

if __name__ == "__main__":
    sys.exit(main())
