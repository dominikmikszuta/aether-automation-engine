import json, os, tempfile, zipfile
from fpdf import FPDF
from .utils import sanitize_unicode, find_unicode_font, ensure_dir
class ChatIngest:
    def __init__(self, out):
        self.out = ensure_dir(out); self._font = find_unicode_font()
    @property
    def has_unicode(self): return self._font is not None
    def _safe(self, v): return v if self.has_unicode else sanitize_unicode(v)
    def extract(self, archive):
        d = tempfile.mkdtemp(prefix="qm-")
        with zipfile.ZipFile(archive) as z: z.extractall(d)
        return d
    def find_json(self, d):
        for r,_,fs in os.walk(d):
            for n in fs:
                if n.lower().endswith(".json"): return os.path.join(r,n)
        return None
    def build_pdf(self, jp, name="conversations.pdf"):
        with open(jp, encoding="utf-8") as fh: data = json.load(fh)
        p = FPDF(); p.set_auto_page_break(auto=True, margin=15)
        if self.has_unicode:
            p.add_font("QM","",self._font); p.add_font("QM","B",self._font)
        p.add_page(); fam = "QM" if self.has_unicode else "Helvetica"
        p.set_font(fam,"B",16)
        p.cell(0,10,self._safe("Conversation Archive"),align="C",new_x="LMARGIN",new_y="NEXT"); p.ln(8)
        items = data if isinstance(data,list) else list(data.values())
        for i, c in enumerate(items, 1):
            p.set_font(fam,"B",12)
            t = c.get("title",f"Chat {i}") if isinstance(c,dict) else f"Chat {i}"
            p.cell(0,8,self._safe(t),new_x="LMARGIN",new_y="NEXT")
            if isinstance(c, dict):
                for m in c.get("messages", []):
                    p.set_font(fam,"B",10)
                    p.multi_cell(0,6,self._safe(str(m.get("role","user")).upper()+":"))
                    p.set_font(fam,"",10)
                    p.multi_cell(0,6,self._safe(str(m.get("content","")))); p.ln(2)
            p.ln(4)
        path = os.path.join(self.out, name); p.output(path); return path
