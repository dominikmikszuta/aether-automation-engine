from fpdf import FPDF
from .utils import sanitize_unicode, find_unicode_font
class PDFEngine:
    def __init__(self, title="", author=""):
        self._font = find_unicode_font()
        self._title = title; self._author = author
    @property
    def has_unicode(self): return self._font is not None
    def _safe(self, v): return v if self.has_unicode else sanitize_unicode(v)
    def _new(self):
        p = FPDF(); p.set_auto_page_break(auto=True, margin=15)
        p.set_title(self._title); p.set_author(self._author)
        if self.has_unicode:
            p.add_font("QM","",self._font); p.add_font("QM","B",self._font)
        return p
    def _f(self, p, style, size):
        p.set_font("QM" if self.has_unicode else "Helvetica", style, size)
    def write_simple(self, path, title, paras):
        p = self._new(); p.add_page(); self._f(p,"B",20)
        p.cell(0,12,self._safe(title),align="C",new_x="LMARGIN",new_y="NEXT"); p.ln(8)
        for para in paras:
            self._f(p,"",11); p.multi_cell(0,6,self._safe(para)); p.ln(3)
        p.output(path); return path
