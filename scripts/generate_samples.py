"""
One-off script to generate sample PDF invoices for Arch 1 testing.
All invoices use an identical fixed layout — only the data changes.
Run: python scripts/generate_samples.py
"""

from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path(__file__).parent.parent / "data" / "samples" / "arch1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INVOICES = [
  {
    "invoice_no": "INV-2024-001",
    "date": "15 Jan 2024",
    "due_date": "14 Feb 2024",
    "po_number": "PO-2024-0042",
    "supplier": {
      "name": "TechSupplies Ltd",
      "address": "123 Business Park, London EC1 2AB",
      "vat": "GB123456789",
    },
    "customer": {
      "name": "Acme Corp",
      "address": "456 Customer Street, Manchester M1 3CD",
    },
    "lines": [
      ("Office Laptop Pro", 2, 850.00),
      ("Wireless Mouse", 5, 25.00),
      ("USB-C Hub", 3, 45.00),
    ],
    "vat_rate": 0.20,
  },
  {
    "invoice_no": "INV-2024-002",
    "date": "22 Jan 2024",
    "due_date": "21 Feb 2024",
    "po_number": "PO-2024-0057",
    "supplier": {
      "name": "TechSupplies Ltd",
      "address": "123 Business Park, London EC1 2AB",
      "vat": "GB123456789",
    },
    "customer": {
      "name": "Globex Industries",
      "address": "789 Industrial Road, Birmingham B2 4EF",
    },
    "lines": [
      ("27-inch Monitor", 4, 320.00),
      ("HDMI Cable 2m", 8, 12.50),
      ("Desk Stand Adjustable", 4, 75.00),
    ],
    "vat_rate": 0.20,
  },
  {
    "invoice_no": "INV-2024-003",
    "date": "05 Feb 2024",
    "due_date": "06 Mar 2024",
    "po_number": "PO-2024-0081",
    "supplier": {
      "name": "TechSupplies Ltd",
      "address": "123 Business Park, London EC1 2AB",
      "vat": "GB123456789",
    },
    "customer": {
      "name": "Initech Solutions",
      "address": "321 Tech Avenue, Edinburgh EH1 1AA",
    },
    "lines": [
      ("Mechanical Keyboard", 6, 110.00),
      ("Mouse Pad XL", 6, 18.00),
      ("USB Hub 7-port", 2, 55.00),
      ("Laptop Stand", 3, 40.00),
    ],
    "vat_rate": 0.20,
  },
]


def build_invoice(pdf: FPDF, inv: dict) -> None:
  pdf.add_page()
  pdf.set_margins(15, 15, 15)

  # ── Supplier header ──────────────────────────────────────────────────
  pdf.set_font("Helvetica", "B", 16)
  pdf.cell(0, 8, inv["supplier"]["name"], ln=True)
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(0, 5, inv["supplier"]["address"], ln=True)
  pdf.cell(0, 5, f'VAT: {inv["supplier"]["vat"]}', ln=True)
  pdf.ln(4)

  # ── "INVOICE" title ──────────────────────────────────────────────────
  pdf.set_font("Helvetica", "B", 20)
  pdf.cell(0, 10, "INVOICE", ln=True)
  pdf.ln(2)

  # ── Invoice meta ─────────────────────────────────────────────────────
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(40, 6, "Invoice No:", border=0)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, inv["invoice_no"], ln=True)

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(40, 6, "Date:")
  pdf.cell(0, 6, inv["date"], ln=True)

  pdf.cell(40, 6, "Due Date:")
  pdf.cell(0, 6, inv["due_date"], ln=True)

  pdf.cell(40, 6, "PO Number:")
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, inv["po_number"], ln=True)
  pdf.ln(4)

  # ── Bill To ──────────────────────────────────────────────────────────
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Bill To:", ln=True)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["customer"]["name"], ln=True)
  pdf.cell(0, 6, inv["customer"]["address"], ln=True)
  pdf.ln(6)

  # ── Line items table header ───────────────────────────────────────────
  pdf.set_fill_color(30, 30, 30)
  pdf.set_text_color(255, 255, 255)
  pdf.set_font("Helvetica", "B", 9)
  col_w = [10, 95, 18, 30, 30]
  headers = ["#", "Description", "Qty", "Unit Price", "Total"]
  for w, h in zip(col_w, headers):
    pdf.cell(w, 7, h, border=0, fill=True)
  pdf.ln()

  # ── Line items ────────────────────────────────────────────────────────
  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Helvetica", "", 9)
  subtotal = 0.0
  for i, (desc, qty, unit) in enumerate(inv["lines"], 1):
    line_total = qty * unit
    subtotal += line_total
    fill = i % 2 == 0
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(col_w[0], 6, str(i), border=0, fill=fill)
    pdf.cell(col_w[1], 6, desc, border=0, fill=fill)
    pdf.cell(col_w[2], 6, str(qty), border=0, fill=fill)
    pdf.cell(col_w[3], 6, f"GBP {unit:,.2f}", border=0, fill=fill)
    pdf.cell(col_w[4], 6, f"GBP {line_total:,.2f}", border=0, fill=fill)
    pdf.ln()

  pdf.ln(4)

  # ── Totals ────────────────────────────────────────────────────────────
  vat_amount = subtotal * inv["vat_rate"]
  total = subtotal + vat_amount
  right_x = 130

  def total_row(label: str, value: str, bold: bool = False) -> None:
    pdf.set_font("Helvetica", "B" if bold else "", 9)
    pdf.set_x(right_x)
    pdf.cell(35, 6, label)
    pdf.cell(30, 6, value, ln=True)

  total_row("Subtotal:", f"GBP {subtotal:,.2f}")
  total_row(f'VAT ({int(inv["vat_rate"]*100)}%):', f"GBP {vat_amount:,.2f}")
  total_row("Total:", f"GBP {total:,.2f}", bold=True)

  pdf.ln(6)

  # ── Footer ────────────────────────────────────────────────────────────
  pdf.set_font("Helvetica", "", 8)
  pdf.set_text_color(100, 100, 100)
  pdf.cell(0, 5, "Payment Terms: Net 30", ln=True)
  pdf.cell(0, 5, "Bank: HSBC  |  Sort: 40-12-34  |  Account: 12345678", ln=True)


def main() -> None:
  for inv in INVOICES:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    build_invoice(pdf, inv)
    out_path = OUT_DIR / f'{inv["invoice_no"]}.pdf'
    pdf.output(str(out_path))
    print(f"Created: {out_path}")


if __name__ == "__main__":
  main()
