import os, sys
from typing import Optional
R = {"\u2014":"-","\u2013":"-","\u2018":"'","\u2019":"'",
     "\u201c":'"',"\u201d":'"',"\u2026":"...","\u2022":"-"}
def sanitize_unicode(t):
    s = t if isinstance(t,str) else str(t)
    for k,v in R.items(): s = s.replace(k,v)
    return s.encode("latin-1","replace").decode("latin-1")
def find_unicode_font():
    for p in ("/system/fonts/NotoSans-Regular.ttf",
              "/system/fonts/Roboto-Regular.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p): return p
    return None
def ensure_dir(p):
    os.makedirs(p, exist_ok=True); return p
def log(m, lvl="INFO"):
    print(f"[QM] {m}", file=sys.stderr if lvl=="ERROR" else sys.stdout)
