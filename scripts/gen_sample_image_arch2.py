"""
Generate a PNG invoice sample for Arch 2 with an unusual PO field label.

Layout differences from the PDF samples:
  - Image format (not PDF) — exercises Claude's vision capability
  - PO field labelled "Customer Order No:" (not "PO Number:" or "Bon de commande:")
  - Supplier: TechPro Solutions Ltd, GBP, 20% VAT
  - No row numbers in line-items table

Run: py scripts/gen_sample_image_arch2.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).parent.parent / "data" / "samples" / "arch2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H   = 794, 1123   # A4 at ~96 DPI
M      = 60          # left/right margin
RIGHT  = W - M       # right edge of content area

INVOICE = {
  "invoice_no":  "TP-2024-0055",
  "date":        "15 March 2024",
  "due_date":    "14 April 2024",
  "order_no":    "1234#",
  "supplier": {
    "name":    "TechPro Solutions Ltd",
    "address": "Unit 5, Innovation Park, Cambridge CB1 2AB",
    "vat":     "GB 987 654 321",
  },
  "customer": {
    "name":    "Vertex Analytics Corp",
    "address": "44 Data Street, London EC2A 4AB",
  },
  "lines": [
    ("Data Analytics Platform (annual)", 1, 4500.00),
    ("Cloud Storage Module",             3,  750.00),
    ("Premium Support Package",         12,  125.00),
  ],
  "vat_rate": 0.20,
}


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
  """Load a Windows system font with a plain-font fallback."""
  paths = {
    "bold":   "C:/Windows/Fonts/arialbd.ttf",
    "reg":    "C:/Windows/Fonts/arial.ttf",
    "italic": "C:/Windows/Fonts/ariali.ttf",
  }
  try:
    return ImageFont.truetype(paths.get(name, paths["reg"]), size)
  except OSError:
    return ImageFont.load_default()


def _rtext(draw, x, y, text, font, fill=(0, 0, 0)):
  """Draw text right-aligned so it ends at x."""
  w = int(draw.textlength(text, font=font))
  draw.text((x - w, y), text, fill=fill, font=font)


def build(inv: dict) -> Path:
  img  = Image.new("RGB", (W, H), "white")
  draw = ImageDraw.Draw(img)

  fh1    = _font("bold", 34)
  fh2    = _font("bold", 16)
  fbold  = _font("bold", 13)
  freg   = _font("reg",  13)
  fsmall = _font("reg",  11)

  y = M

  # ── Header ────────────────────────────────────────────────────────────────
  draw.text((M, y), "INVOICE", fill=(25, 25, 112), font=fh1)
  _rtext(draw, RIGHT, y + 4, inv["supplier"]["name"], fh2, fill=(25, 25, 112))
  y += 42
  _rtext(draw, RIGHT, y, inv["supplier"]["address"], fsmall, fill=(110, 110, 110))
  y += 16
  _rtext(draw, RIGHT, y, f'VAT Reg: {inv["supplier"]["vat"]}', fsmall, fill=(110, 110, 110))
  y += 24

  draw.line([(M, y), (RIGHT, y)], fill=(180, 180, 180), width=1)
  y += 16

  # ── Invoice meta ──────────────────────────────────────────────────────────
  label_x  = M
  value_x  = M + 180
  meta = [
    ("Invoice No:",        inv["invoice_no"]),
    ("Date:",              inv["date"]),
    ("Payment Due:",       inv["due_date"]),
    ("Customer Order No:", inv["order_no"]),   # ← unusual label
  ]
  for label, value in meta:
    draw.text((label_x, y), label, fill=(80, 80, 80), font=freg)
    draw.text((value_x, y), value, fill=(0,  0,  0),  font=fbold)
    y += 22
  y += 16

  # ── Bill To ───────────────────────────────────────────────────────────────
  draw.text((M, y), "Bill To:", fill=(80, 80, 80), font=fbold)
  y += 20
  draw.text((M, y), inv["customer"]["name"],    fill=(0,   0,   0),  font=freg)
  y += 18
  draw.text((M, y), inv["customer"]["address"], fill=(110, 110, 110), font=fsmall)
  y += 30

  # ── Line-items table ──────────────────────────────────────────────────────
  # Column right-edges: desc ends at 430, qty at 490, unit at 600, total at RIGHT
  c_desc  = M        # description starts here (left-aligned)
  cr_qty  = M + 370  # qty right-edge
  cr_unit = M + 490  # unit price right-edge
  cr_tot  = RIGHT    # line total right-edge

  # Header row
  draw.rectangle([(M, y), (RIGHT, y + 28)], fill=(25, 25, 112))
  draw.text((M + 5, y + 7), "Description",   fill="white", font=fbold)
  _rtext(draw, cr_qty,  y + 7, "Qty",              fbold, fill="white")
  _rtext(draw, cr_unit, y + 7, "Unit Price (GBP)", fbold, fill="white")
  _rtext(draw, cr_tot,  y + 7, "Line Total (GBP)", fbold, fill="white")
  y += 28

  subtotal = 0.0
  for i, (desc, qty, unit) in enumerate(inv["lines"]):
    line_total = qty * unit
    subtotal  += line_total
    bg = (232, 232, 245) if i % 2 == 0 else "white"
    draw.rectangle([(M, y), (RIGHT, y + 24)], fill=bg)
    draw.text((M + 5, y + 5),      desc,                 fill=(0, 0, 0), font=freg)
    _rtext(draw, cr_qty,  y + 5,   str(qty),             freg)
    _rtext(draw, cr_unit, y + 5,   f"{unit:,.2f}",       freg)
    _rtext(draw, cr_tot,  y + 5,   f"{line_total:,.2f}", freg)
    y += 24
  y += 20

  # ── Totals ────────────────────────────────────────────────────────────────
  vat   = subtotal * inv["vat_rate"]
  total = subtotal + vat
  pct   = int(inv["vat_rate"] * 100)

  totals_label_x = RIGHT - 260
  for label, amount, bold in [
    ("Subtotal:",       subtotal, False),
    (f"VAT ({pct}%):", vat,      False),
    ("Total Due:",      total,    True),
  ]:
    f = fbold if bold else freg
    draw.text((totals_label_x, y), label,                    fill=(0, 0, 0), font=f)
    _rtext(draw, RIGHT, y,         f"GBP {amount:,.2f}",     f)
    y += 22
  y += 16

  draw.line([(M, y), (RIGHT, y)], fill=(180, 180, 180), width=1)
  y += 10
  draw.text(
    (M, y),
    "Payment: BACS transfer within 30 days  |  Sort: 20-00-00  |  Acc: 12345678",
    fill=(130, 130, 130), font=fsmall,
  )

  out = OUT_DIR / f'{inv["invoice_no"]}.png'
  img.save(str(out), dpi=(150, 150))
  print(f"Created: {out}")
  return out


if __name__ == "__main__":
  build(INVOICE)
