from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import textwrap


def generate_sktm_pdf_bytes(data: dict) -> bytes:
    """Generate SKTM PDF bytes using ReportLab based on provided data dict.

        Expected keys (example):
            kepala_desa, kecamatan, kabupaten,
            nama, no_ktp, tempat_tanggal_lahir, jenis_kelamin, alamat,
      pernyataan_paragraf (optional), kota_tanggal, kepala_nama
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Margins
    left = 20 * mm
    right = width - 20 * mm
    y = height - 20 * mm

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2.0, y, "SURAT KETERANGAN TIDAK MAMPU")
    y -= 14 * mm

    # NO placeholder
    p.setFont("Helvetica", 10)
    p.drawString(left, y, "NO:")
    y -= 8 * mm

    # Header block (Kepala Desa / Kecamatan / Kabupaten)
    p.setFont("Helvetica", 11)
    p.drawString(left, y, "YANG BERTANDA TANGAN DIBAWAH INI")
    y -= 8 * mm

    label_x = left + 8 * mm
    value_x = left + 60 * mm
    for label, key in (("KEPALA DESA", "kepala_desa"), ("KECAMATAN", "kecamatan"), ("KABUPATEN", "kabupaten")):
        val = data.get(key, "") or ""
        p.drawString(label_x, y, f"{label} :")
        p.drawString(value_x, y, str(val))
        y -= 7 * mm

    y -= 4 * mm

    # Personal data left-aligned in two columns style
    p.setFont("Helvetica-Bold", 12)
    p.drawString(left, y, "NAMA")
    p.drawString(value_x, y, ":")
    p.setFont("Helvetica", 12)
    p.drawString(value_x + 8 * mm, y, data.get('nama', ''))
    y -= 7 * mm

    fields = [
        ("NO KTP", 'no_ktp'),
        ("TEMPAT / TANGGAL LAHIR", 'tempat_tanggal_lahir'),
        ("JENIS KELAMIN", 'jenis_kelamin'),
        ("ALAMAT", 'alamat'),
    ]
    for label, key in fields:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(left, y, f"{label}")
        p.setFont("Helvetica", 11)
        p.drawString(value_x, y, ":")
        p.drawString(value_x + 8 * mm, y, str(data.get(key, '') or ''))
        y -= 6.5 * mm

    y -= 6 * mm

    # Statement paragraph
    p.setFont("Helvetica", 11)
    paragraph = data.get('pernyataan_paragraf') or (
        "Dengan ini menerangkan bahwa nama tersebut benar warga kami yang masuk dalam keluarga kurang mampu/miskin."
    )
    # Wrap paragraph into lines that fit the width
    max_width = right - left
    # Use simple wrap at ~90 chars as fall back
    wrapped = textwrap.fill(paragraph, 100)
    # Use platypus Paragraph for nicer justification
    styles = getSampleStyleSheet()
    ps = styles['Normal']
    ps.fontName = 'Helvetica'
    ps.fontSize = 11
    ps.alignment = TA_JUSTIFY
    para = Paragraph(wrapped.replace('\n', '<br/>'), ps)
    # draw the paragraph with a simple frame
    from reportlab.platypus import Frame
    frame_height = 50 * mm
    f = Frame(left, y - frame_height + 6 * mm, max_width, frame_height, showBoundary=0)
    f.addFromList([para], p)
    y -= frame_height + 6 * mm

    # Closing and signature area
    y -= 6 * mm
    kota = data.get('kota_tanggal') or ''
    p.drawString(right - 80 * mm, y, kota)
    y -= 6 * mm
    p.drawString(right - 80 * mm, y, "KEPALA DESA :")
    y -= 18 * mm
    p.drawString(right - 80 * mm, y, data.get('kepala_nama', ''))

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()
