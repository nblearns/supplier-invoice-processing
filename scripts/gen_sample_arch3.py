"""
Generate a sample invoice for Arch 3 testing.

The invoice deliberately includes only the supplier NAME ("NovaTech Solutions")
and omits any supplier code — forcing the agent to call lookup_supplier_code()
to retrieve it from the ERP supplier register.

Run: py scripts/gen_sample_arch3.py
"""

from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path(__file__).parent.parent / "data" / "samples" / "arch3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INVOICE = {
  "invoice_no":  "NVT-2024-0012",
  "date":        "18 Sep 2024",
  "due_date":    "18 Oct 2024",
  "po_number":   "PO-2024-0555",
  "supplier": {
    "name":    "NovaTech Solutions",          # name only — no supplier code printed
    "address": "14 Quantum Park, Bristol BS1 4QT",
    "vat":     "GB987654321",
  },
  "customer": {
    "name":    "Apex Industries",
    "address": "9 Enterprise Way, Leeds LS1 2AB",
  },
  "lines": [
    ("Cloud Storage Appliance", 2, 1_200.00),
    ("Network Switch 48-port",  3,   540.00),
    ("Rack Mount Kit",          5,    85.00),
  ],
  "vat_rate": 0.20,
}


def build(pdf: FPDF, inv: dict) -> None:
  pdf.add_page()
  pdf.set_margins(15, 15, 15)

  # ── Header ────────────────────────────────────────────────────────────────
  pdf.set_font("Helvetica", "B", 20)
  pdf.cell(0, 10, "TAX INVOICE", ln=True, align="C")
  pdf.ln(2)

  # Supplier block (left) | Invoice meta (right)
  y = pdf.get_y()

  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 6, inv["supplier"]["name"], ln=True)   # ← name only, no code
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(0, 5, inv["supplier"]["address"], ln=True)
  pdf.cell(0, 5, f'VAT: {inv["supplier"]["vat"]}', ln=True)

  # Right column: invoice meta
  pdf.set_xy(120, y)
  pdf.set_font("Helvetica", "", 9)
  for label, value in [
    ("Invoice No:",   inv["invoice_no"]),
    ("Invoice Date:", inv["date"]),
    ("Due Date:",     inv["due_date"]),
    ("PO Number:",    inv["po_number"]),
  ]:
    pdf.set_x(120)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(32, 5, label)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, value, ln=True)

  pdf.ln(6)

  # ── Bill To ───────────────────────────────────────────────────────────────
  pdf.set_font("Helvetica", "B", 9)
  pdf.cell(0, 5, "Bill To:", ln=True)
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(0, 5, inv["customer"]["name"], ln=True)
  pdf.cell(0, 5, inv["customer"]["address"], ln=True)
  pdf.ln(6)

  # ── Line items ────────────────────────────────────────────────────────────
  col_w = [15, 95, 20, 28, 28]
  headers = ["#", "Description", "Qty", "Unit Price", "Total"]

  pdf.set_fill_color(30, 80, 160)
  pdf.set_text_color(255, 255, 255)
  pdf.set_font("Helvetica", "B", 9)
  for w, h in zip(col_w, headers):
    pdf.cell(w, 7, h, border=0, fill=True)
  pdf.ln()

  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Helvetica", "", 9)
  subtotal = 0.0
  for i, (desc, qty, unit) in enumerate(inv["lines"], 1):
    line_total = qty * unit
    subtotal += line_total
    fill = i % 2 == 0
    pdf.set_fill_color(230, 238, 255)
    pdf.cell(col_w[0], 6, str(i),               border=0, fill=fill)
    pdf.cell(col_w[1], 6, desc,                  border=0, fill=fill)
    pdf.cell(col_w[2], 6, str(qty),              border=0, fill=fill)
    pdf.cell(col_w[3], 6, f"GBP {unit:,.2f}",   border=0, fill=fill)
    pdf.cell(col_w[4], 6, f"GBP {line_total:,.2f}", border=0, fill=fill)
    pdf.ln()

  pdf.ln(4)

  # ── Totals ────────────────────────────────────────────────────────────────
  vat   = round(subtotal * inv["vat_rate"], 2)
  total = round(subtotal + vat, 2)
  rx    = 130

  def row(label, value, bold=False):
    pdf.set_font("Helvetica", "B" if bold else "", 9)
    pdf.set_x(rx)
    pdf.cell(32, 6, label)
    pdf.cell(0,  6, value, ln=True)

  row("Subtotal:",         f"GBP {subtotal:,.2f}")
  row(f"VAT ({int(inv['vat_rate']*100)}%):", f"GBP {vat:,.2f}")
  row("Total Due:",        f"GBP {total:,.2f}", bold=True)

  pdf.ln(8)
  pdf.set_font("Helvetica", "", 8)
  pdf.set_text_color(130, 130, 130)
  pdf.cell(0, 5, "Payment terms: 30 days  |  BACS: Sort 20-00-00 / Acc 12345678", ln=True)


def main() -> None:
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  build(pdf, INVOICE)
  out_path = OUT_DIR / f'{INVOICE["invoice_no"]}.pdf'
  pdf.output(str(out_path))
  print(f"Created: {out_path}")


if __name__ == "__main__":
  main()
