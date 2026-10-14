"""
Generate two sample PDFs for Arch 2 — deliberately different layouts to the
Arch 1 fixed format, showing the LLM extractor earns its place.

Layout A (GlobalTech Inc): US-style, "Invoice #", "Ship To:", no row numbers
Layout B (EuroOffice GmbH): European-style, "Facture No", date dd.mm.yyyy,
                             totals on the left, no PO field label "Purchase Order:"

Run: py scripts/gen_samples_arch2.py
"""

from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path(__file__).parent.parent / "data" / "samples" / "arch2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Layout A data ─────────────────────────────────────────────────────────────

INVOICES_A = [
  {
    "invoice_no": "GT-2024-0091",
    "date": "March 5, 2024",
    "due_date": "April 4, 2024",
    "po_number": "PO-2024-0110",
    "supplier": {
      "name": "GlobalTech Inc",
      "address": "500 Innovation Drive, Austin TX 78701",
      "tax_id": "US-98-7654321",
    },
    "customer": {
      "name": "Pinnacle Systems",
      "address": "22 Enterprise Blvd, New York NY 10001",
    },
    "lines": [
      ("4K Webcam Pro", 3, 149.99),
      ("Noise-Cancelling Headset", 5, 89.95),
      ("USB-C Docking Station", 2, 199.00),
    ],
    "tax_rate": 0.08,
    "currency": "USD",
  },
]

INVOICES_B = [
  {
    "invoice_no": "EO-2024-0044",
    "date": "12.02.2024",
    "due_date": "13.03.2024",
    "po_number": "BE-2024-0033",
    "supplier": {
      "name": "EuroOffice GmbH",
      "address": "Hauptstraße 7, 10115 Berlin, Germany",
      "vat": "DE 123 456 789",
    },
    "customer": {
      "name": "Meridian Partners",
      "address": "Rue du Commerce 15, 1000 Brussels, Belgium",
    },
    "lines": [
      ("Ergonomic Chair", 4, 320.00),
      ("Standing Desk", 2, 480.00),
      ("Monitor Arm", 6, 65.00),
    ],
    "tax_rate": 0.19,
    "currency": "EUR",
  },
]


# ── Layout A builder ─────────────────────────────────────────────────────────
# Differences from Arch 1 layout:
#   - "Invoice #" label (not "Invoice No:")
#   - "Ship To:" block (not "Bill To:")
#   - No row-number column in line-items table
#   - Tax labelled "Sales Tax" (not "VAT")
#   - Currency symbol before amounts (USD / $)

def build_layout_a(pdf: FPDF, inv: dict) -> None:
  pdf.add_page()
  pdf.set_margins(15, 15, 15)

  # Header: supplier right-aligned, "INVOICE" large left
  pdf.set_font("Helvetica", "B", 22)
  pdf.cell(100, 10, "INVOICE", border=0)
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, inv["supplier"]["name"], ln=True, align="R")
  pdf.set_font("Helvetica", "", 9)
  pdf.set_x(110)
  pdf.cell(0, 5, inv["supplier"]["address"], ln=True, align="R")
  pdf.set_x(110)
  pdf.cell(0, 5, f'Tax ID: {inv["supplier"]["tax_id"]}', ln=True, align="R")
  pdf.ln(4)

  # Invoice meta — "Invoice #" label
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(35, 6, "Invoice #:")
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, inv["invoice_no"], ln=True)

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(35, 6, "Invoice Date:")
  pdf.cell(0, 6, inv["date"], ln=True)

  pdf.cell(35, 6, "Payment Due:")
  pdf.cell(0, 6, inv["due_date"], ln=True)

  pdf.cell(35, 6, "Purchase Order:")
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, inv["po_number"], ln=True)
  pdf.ln(4)

  # "Ship To:" block
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Ship To:", ln=True)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["customer"]["name"], ln=True)
  pdf.cell(0, 6, inv["customer"]["address"], ln=True)
  pdf.ln(6)

  # Line items — no row-number column
  pdf.set_fill_color(50, 50, 120)
  pdf.set_text_color(255, 255, 255)
  pdf.set_font("Helvetica", "B", 9)
  col_w = [100, 20, 32, 32]
  for w, h in zip(col_w, ["Description", "Qty", "Unit Price", "Amount"]):
    pdf.cell(w, 7, h, border=0, fill=True)
  pdf.ln()

  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Helvetica", "", 9)
  subtotal = 0.0
  for i, (desc, qty, unit) in enumerate(inv["lines"], 1):
    line_total = qty * unit
    subtotal += line_total
    fill = i % 2 == 0
    pdf.set_fill_color(235, 235, 245)
    pdf.cell(col_w[0], 6, desc, border=0, fill=fill)
    pdf.cell(col_w[1], 6, str(qty), border=0, fill=fill)
    pdf.cell(col_w[2], 6, f"${unit:,.2f}", border=0, fill=fill)
    pdf.cell(col_w[3], 6, f"${line_total:,.2f}", border=0, fill=fill)
    pdf.ln()

  pdf.ln(4)

  # Totals — "Sales Tax" label
  tax = subtotal * inv["tax_rate"]
  total = subtotal + tax
  rx = 130

  def row(label, value, bold=False):
    pdf.set_font("Helvetica", "B" if bold else "", 9)
    pdf.set_x(rx)
    pdf.cell(35, 6, label)
    pdf.cell(30, 6, value, ln=True)

  row("Subtotal:", f"${subtotal:,.2f}")
  row(f'Sales Tax ({int(inv["tax_rate"]*100)}%):', f"${tax:,.2f}")
  row("Total Due:", f"${total:,.2f}", bold=True)

  pdf.ln(6)
  pdf.set_font("Helvetica", "", 8)
  pdf.set_text_color(120, 120, 120)
  pdf.cell(0, 5, "Terms: Net 30  |  Remit to: GlobalTech Inc", ln=True)


# ── Layout B builder ─────────────────────────────────────────────────────────
# Differences from Arch 1 layout:
#   - "Facture No" label
#   - Date format dd.mm.yyyy
#   - No row numbers; columns: Description | Quantity | Unit Price | Line Total
#   - Totals on the left side
#   - "TVA" for tax, "Montant Total" for total

def build_layout_b(pdf: FPDF, inv: dict) -> None:
  pdf.add_page()
  pdf.set_margins(15, 15, 15)

  # Centered company name at top
  pdf.set_font("Helvetica", "B", 18)
  pdf.cell(0, 10, inv["supplier"]["name"], ln=True, align="C")
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(0, 5, inv["supplier"]["address"], ln=True, align="C")
  pdf.cell(0, 5, f'VAT-Nr: {inv["supplier"]["vat"]}', ln=True, align="C")
  pdf.ln(5)

  # Horizontal rule
  pdf.set_draw_color(180, 180, 180)
  pdf.line(15, pdf.get_y(), 195, pdf.get_y())
  pdf.ln(4)

  # Two-column meta block: invoice details left, customer right
  y_start = pdf.get_y()
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Facture No:", ln=True)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["invoice_no"], ln=True)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Date:", ln=True)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["date"], ln=True)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Echeance:", ln=True)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["due_date"], ln=True)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Bon de commande:", ln=True)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, inv["po_number"], ln=True)

  # Customer block on the right (go back up)
  pdf.set_xy(110, y_start)
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Facture a:", ln=True)
  pdf.set_xy(110, y_start + 6)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, inv["customer"]["name"], ln=True)
  pdf.set_xy(110, y_start + 12)
  pdf.cell(0, 6, inv["customer"]["address"], ln=True)
  pdf.ln(10)

  # Line items — no row numbers
  pdf.set_fill_color(220, 50, 50)
  pdf.set_text_color(255, 255, 255)
  pdf.set_font("Helvetica", "B", 9)
  col_w = [100, 22, 32, 30]
  for w, h in zip(col_w, ["Description", "Quantity", "Prix unitaire", "Montant"]):
    pdf.cell(w, 7, h, border=0, fill=True)
  pdf.ln()

  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Helvetica", "", 9)
  subtotal = 0.0
  for i, (desc, qty, unit) in enumerate(inv["lines"], 1):
    line_total = qty * unit
    subtotal += line_total
    fill = i % 2 == 0
    pdf.set_fill_color(245, 230, 230)
    pdf.cell(col_w[0], 6, desc, border=0, fill=fill)
    pdf.cell(col_w[1], 6, str(qty), border=0, fill=fill)
    pdf.cell(col_w[2], 6, f"EUR {unit:,.2f}", border=0, fill=fill)
    pdf.cell(col_w[3], 6, f"EUR {line_total:,.2f}", border=0, fill=fill)
    pdf.ln()

  pdf.ln(4)

  # Totals on the LEFT side
  tax = subtotal * inv["tax_rate"]
  total = subtotal + tax

  def row(label, value, bold=False):
    pdf.set_font("Helvetica", "B" if bold else "", 9)
    pdf.cell(40, 6, label)
    pdf.cell(30, 6, value, ln=True)

  row("Sous-total:", f"EUR {subtotal:,.2f}")
  row(f'TVA ({int(inv["tax_rate"]*100)}%):', f"EUR {tax:,.2f}")
  row("Montant Total:", f"EUR {total:,.2f}", bold=True)

  pdf.ln(6)
  pdf.set_font("Helvetica", "", 8)
  pdf.set_text_color(120, 120, 120)
  pdf.cell(0, 5, "Paiement: virement bancaire sous 30 jours", ln=True)
  pdf.cell(0, 5, "IBAN: DE89 3704 0044 0532 0130 00  |  BIC: COBADEFFXXX", ln=True)


def main() -> None:
  for inv in INVOICES_A:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    build_layout_a(pdf, inv)
    out_path = OUT_DIR / f'{inv["invoice_no"]}.pdf'
    pdf.output(str(out_path))
    print(f"Created (layout A): {out_path}")

  for inv in INVOICES_B:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    build_layout_b(pdf, inv)
    out_path = OUT_DIR / f'{inv["invoice_no"]}.pdf'
    pdf.output(str(out_path))
    print(f"Created (layout B): {out_path}")


if __name__ == "__main__":
  main()
