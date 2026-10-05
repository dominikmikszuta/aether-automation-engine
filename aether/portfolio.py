import os
from fpdf import FPDF
from .utils import sanitize_unicode, find_unicode_font, ensure_dir
BLUE = (0,120,212); DARK = (51,51,51); MID = (100,100,100)
class PortfolioBuilder:
    def __init__(self, out):
        self.out = ensure_dir(out); self._font = find_unicode_font()
    @property
    def has_unicode(self): return self._font is not None
    def _safe(self, v): return v if self.has_unicode else sanitize_unicode(v)
    def _f(self, p, s, sz): p.set_font("QM" if self.has_unicode else "Helvetica", s, sz)
    def build(self, name, title, summary, projects, out_name="portfolio.pdf"):
        p = FPDF(); p.set_auto_page_break(auto=True, margin=15); p.set_margins(20,20,20)
        if self.has_unicode:
            p.add_font("QM","",self._font); p.add_font("QM","B",self._font); p.add_font("QM","I",self._font)
        p.add_page(); p.set_fill_color(*BLUE); p.rect(0,0,210,8,"F"); p.set_y(15)
        self._f(p,"B",24); p.set_text_color(*DARK)
        p.cell(0,10,self._safe(name),new_x="LMARGIN",new_y="NEXT")
        self._f(p,"",13); p.set_text_color(*BLUE)
        p.cell(0,8,self._safe(title),new_x="LMARGIN",new_y="NEXT")
        p.set_draw_color(*BLUE); p.line(20,p.get_y()+4,190,p.get_y()+4); p.ln(8)
        self._f(p,"B",13); p.set_text_color(*BLUE)
        p.cell(0,8,"PROFESSIONAL SUMMARY",new_x="LMARGIN",new_y="NEXT")
        self._f(p,"",11); p.set_text_color(*DARK)
        p.multi_cell(0,5.5,self._safe(summary)); p.ln(6)
        self._f(p,"B",13); p.set_text_color(*BLUE)
        p.cell(0,8,"FEATURED PROJECTS",new_x="LMARGIN",new_y="NEXT")
        for pr in projects:
            self._f(p,"B",11); p.set_text_color(*DARK)
            p.cell(0,6,self._safe(pr.get("name","")),new_x="LMARGIN",new_y="NEXT")
            self._f(p,"I",10); p.set_text_color(*MID)
            p.cell(0,5,self._safe(pr.get("stack","")),new_x="LMARGIN",new_y="NEXT")
            self._f(p,"",10); p.set_text_color(*DARK)
            p.multi_cell(0,5,self._safe(pr.get("description",""))); p.ln(3)
        path = os.path.join(self.out, out_name); p.output(path); return path
