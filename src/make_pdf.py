"""Render reports/final/REPORT.md to a print-quality PDF.

Markdown -> self-contained HTML (figures base64-embedded) -> PDF via headless
Edge. Kept in the repo so the PDF is reproducible like every other artifact.

Run:  python -m src.make_pdf
"""
from __future__ import annotations

import base64
import re
import subprocess
import sys
import time
from pathlib import Path

import markdown

from .util import ROOT

SRC = ROOT / "reports" / "final" / "REPORT.md"
HTML = ROOT / "reports" / "final" / "REPORT.html"
PDF = ROOT / "reports" / "final" / "WC2026_Hydration_Break_Report.pdf"

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #1a1a18;
  max-width: 100%; margin: 0;
}
h1 {
  font-size: 21pt; line-height: 1.2; margin: 0 0 4pt; color: #0b0b0b;
  letter-spacing: -0.01em;
}
h1 + p strong { font-size: 12pt; font-weight: 600; color: #2a78d6; }
h2 {
  font-size: 14pt; margin: 22pt 0 7pt; padding-top: 10pt; color: #0b0b0b;
  border-top: 1.5px solid #e1e0d9; break-after: avoid; break-inside: avoid;
}
h3 { font-size: 11.5pt; margin: 14pt 0 5pt; color: #2a2a28; break-after: avoid; }
p { margin: 0 0 8pt; }
strong { color: #0b0b0b; }
a { color: #2a78d6; text-decoration: none; }
code {
  font-family: Consolas, monospace; font-size: 9pt;
  background: #f2f1ec; padding: 1px 4px; border-radius: 3px;
}
pre {
  background: #f7f6f2; border: 1px solid #e1e0d9; border-radius: 5px;
  padding: 9pt 11pt; font-size: 8.6pt; line-height: 1.5; overflow-x: auto;
  break-inside: avoid;
}
pre code { background: none; padding: 0; }
blockquote {
  margin: 12pt 0; padding: 9pt 14pt; border-left: 3px solid #2a78d6;
  background: #f5f8fd; font-size: 10.5pt; break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }
table {
  border-collapse: collapse; width: 100%; margin: 10pt 0 12pt;
  font-size: 9pt; break-inside: avoid;
}
th {
  text-align: left; padding: 5pt 7pt; background: #f2f1ec;
  border-bottom: 1.5px solid #c3c2b7; font-weight: 600;
}
td { padding: 4.5pt 7pt; border-bottom: 1px solid #eceae3; vertical-align: top; }
tr:last-child td { border-bottom: 1px solid #c3c2b7; }
img {
  max-width: 100%; height: auto; display: block; margin: 12pt auto 4pt;
  break-inside: avoid;
}
figure { margin: 0 0 14pt; break-inside: avoid; }
hr { border: none; border-top: 1.5px solid #e1e0d9; margin: 20pt 0; }
ul, ol { margin: 0 0 9pt; padding-left: 18pt; }
li { margin-bottom: 3pt; }
em { color: #52514e; }
"""


def embed_images(md_text: str) -> str:
    """Replace ![alt](../figures/x.png) with base64 data URIs."""
    def repl(m: re.Match) -> str:
        alt, rel = m.group(1), m.group(2)
        p = (SRC.parent / rel).resolve()
        if not p.exists():
            print(f"  WARNING: missing figure {rel}", file=sys.stderr)
            return m.group(0)
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f"![{alt}](data:image/png;base64,{b64})"
    return re.sub(r"!\[([^\]]*)\]\(([^)]+\.png)\)", repl, md_text)


def build_html() -> str:
    md_text = embed_images(SRC.read_text(encoding="utf-8"))
    body = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "attr_list", "sane_lists"]
    )
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f"<title>WC2026 Hydration Break Report</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")


def find_edge() -> Path:
    for c in EDGE_CANDIDATES:
        if c.exists():
            return c
    raise FileNotFoundError("Microsoft Edge not found; cannot render PDF")


def main():
    HTML.write_text(build_html(), encoding="utf-8")
    print(f"wrote {HTML} ({HTML.stat().st_size / 1024:.0f} KB)")

    if PDF.exists():
        PDF.unlink()
    edge = find_edge()
    subprocess.run(
        [str(edge), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={PDF}", HTML.as_uri()],
        check=True, capture_output=True, timeout=180,
    )
    # Edge writes asynchronously; wait for the file to settle
    for _ in range(30):
        if PDF.exists() and PDF.stat().st_size > 0:
            break
        time.sleep(1)
    if not PDF.exists():
        raise RuntimeError("Edge did not produce a PDF")
    print(f"wrote {PDF} ({PDF.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
