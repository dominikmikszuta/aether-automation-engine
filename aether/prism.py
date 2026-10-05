"""PRISM - Render markdown to multiple formats (PDF/HTML)."""
from __future__ import annotations
import re
from pathlib import Path
from .pdf_engine import PDFEngine

class Prism:
    def __init__(self):
        self.engine = PDFEngine()

    @staticmethod
    def _parse_markdown(text):
        """Very small markdown parser: h1-h3, bullets, paragraphs."""
        blocks = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                blocks.append({"type": "break", "text": ""})
            elif stripped.startswith("### "):
                blocks.append({"type": "h3", "text": stripped[4:]})
            elif stripped.startswith("## "):
                blocks.append({"type": "h2", "text": stripped[3:]})
            elif stripped.startswith("# "):
                blocks.append({"type": "h1", "text": stripped[2:]})
            elif stripped.startswith("- ") or stripped.startswith("* "):
                blocks.append({"type": "bullet", "text": stripped[2:]})
            else:
                blocks.append({"type": "p", "text": stripped})
        return blocks

    def to_html(self, text, title="Document"):
        blocks = self._parse_markdown(text)
        parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title></head><body>"]
        for b in blocks:
            t = b["text"]
            if b["type"] == "h1": parts.append(f"<h1>{t}</h1>")
            elif b["type"] == "h2": parts.append(f"<h2>{t}</h2>")
            elif b["type"] == "h3": parts.append(f"<h3>{t}</h3>")
            elif b["type"] == "bullet": parts.append(f"<li>{t}</li>")
            elif b["type"] == "p": parts.append(f"<p>{t}</p>")
            else: parts.append("<br>")
        parts.append("</body></html>")
        return "".join(parts)

    def to_pdf(self, text, output_path, title="Document"):
        blocks = self._parse_markdown(text)
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        if self.engine.has_unicode:
            pdf.add_font("P", "", self.engine._font_path)
            pdf.add_font("P", "B", self.engine._font_path)
            fam = "P"
        else:
            fam = "Helvetica"
        pdf.add_page()
        for b in blocks:
            if b["type"] == "h1":
                pdf.set_font(fam, "B", 20); pdf.ln(4)
            elif b["type"] == "h2":
                pdf.set_font(fam, "B", 16); pdf.ln(3)
            elif b["type"] == "h3":
                pdf.set_font(fam, "B", 13); pdf.ln(2)
            elif b["type"] == "bullet":
                pdf.set_font(fam, "", 11); b = {**b, "text": "- " + b["text"]}
            else:
                pdf.set_font(fam, "", 11)
            pdf.multi_cell(0, 6, b["text"])
        pdf.output(output_path)
        return output_path
