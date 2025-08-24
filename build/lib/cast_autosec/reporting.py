
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import json, os

def _json_to_pdf(json_path: Path, out_pdf: Path, title: str):
    c = canvas.Canvas(str(out_pdf), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, title)
    c.setFont("Helvetica", 9)
    y = height - 3*cm
    try:
        data = json.loads(Path(json_path).read_text())
        lines = json.dumps(data, indent=2).splitlines()
    except Exception as e:
        lines = [f"Failed to load {json_path}: {e}"]
    for line in lines:
        if y < 2*cm:
            c.showPage(); y = height - 2*cm
            c.setFont("Helvetica", 9)
        c.drawString(2*cm, y, line[:115])
        y -= 12
    c.showPage()
    c.save()

def combine_reports(reports_dir: Path, out_pdf: Path):
    # convert known JSON to PDFs then merge any PDFs and add cover
    temp = out_pdf.with_suffix(".tmpdir")
    temp.mkdir(exist_ok=True)
    parts = []

    # cover page
    cover = temp/"cover.pdf"
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    c = canvas.Canvas(str(cover), pagesize=A4)
    w,h = A4
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h-3*cm, "CAST AutoSec Report")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h-4*cm, f"Source: {reports_dir}")
    c.showPage(); c.save()
    parts.append(cover)

    # known reports
    trivy_json = reports_dir/"trivy.json"
    if trivy_json.exists():
        p = temp/"trivy.pdf"
        _json_to_pdf(trivy_json, p, "Trivy Report")
        parts.append(p)

    # include any existing pdfs
    for p in reports_dir.glob("**/*.pdf"):
        parts.append(p)

    writer = PdfWriter()
    for p in parts:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    writer.write(str(out_pdf))
    writer.close()
