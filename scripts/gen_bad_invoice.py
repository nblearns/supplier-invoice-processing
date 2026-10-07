"""Generate a single invoice PDF with no PO number field."""
from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path(__file__).parent.parent / "data" / "samples" / "arch1"

def build(pdf: FPDF) -> None:
  pdf.add_page()
  pdf.set_margins(15, 15, 15)

  pdf.set_font("Helvetica", "B", 16)
  pdf.cell(0, 8, "TechSupplies Ltd", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(0, 5, "123 Business Park, London EC1 2AB", new_x="LMARGIN", new_y="NEXT")
  pdf.cell(0, 5, "VAT: GB123456789", new_x="LMARGIN", new_y="NEXT")
  pdf.ln(4)

  pdf.set_font("Helvetica", "B", 20)
  pdf.cell(0, 10, "INVOICE", new_x="LMARGIN", new_y="NEXT")
  pdf.ln(2)

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(40, 6, "Invoice No:")
  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "INV-2024-099", new_x="LMARGIN", new_y="NEXT")

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(40, 6, "Date:")
  pdf.cell(0, 6, "10 Mar 2024", new_x="LMARGIN", new_y="NEXT")

  pdf.cell(40, 6, "Due Date:")
  pdf.cell(0, 6, "09 Apr 2024", new_x="LMARGIN", new_y="NEXT")
  # PO Number deliberately omitted
  pdf.ln(4)

  pdf.set_font("Helvetica", "B", 10)
  pdf.cell(0, 6, "Bill To:", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, "Umbrella Corp", new_x="LMARGIN", new_y="NEXT")
  pdf.cell(0, 6, "1 Corporate Plaza, London WC2 9ZZ", new_x="LMARGIN", new_y="NEXT")
  pdf.ln(6)

  pdf.set_fill_color(30, 30, 30)
  pdf.set_text_color(255, 255, 255)
  pdf.set_font("Helvetica", "B", 9)
  for w, h in zip([10, 95, 18, 30, 30], ["#", "Description", "Qty", "Unit Price", "Total"]):
    pdf.cell(w, 7, h, fill=True)
  pdf.ln()

  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Helvetica", "", 9)
  pdf.cell(10, 6, "1")
  pdf.cell(95, 6, "Server Rack Unit")
  pdf.cell(18, 6, "1")
  pdf.cell(30, 6, "GBP 1,200.00")
  pdf.cell(30, 6, "GBP 1,200.00")
  pdf.ln()

  pdf.ln(4)
  pdf.set_font("Helvetica", "", 9)
  pdf.set_x(130)
  pdf.cell(35, 6, "Subtotal:")
  pdf.cell(30, 6, "GBP 1,200.00", new_x="LMARGIN", new_y="NEXT")
  pdf.set_x(130)
  pdf.cell(35, 6, "VAT (20%):")
  pdf.cell(30, 6, "GBP 240.00", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "B", 9)
  pdf.set_x(130)
  pdf.cell(35, 6, "Total:")
  pdf.cell(30, 6, "GBP 1,440.00", new_x="LMARGIN", new_y="NEXT")

  pdf.ln(6)
  pdf.set_font("Helvetica", "", 8)
  pdf.set_text_color(100, 100, 100)
  pdf.cell(0, 5, "Payment Terms: Net 30", new_x="LMARGIN", new_y="NEXT")
  pdf.cell(0, 5, "Bank: HSBC  |  Sort: 40-12-34  |  Account: 12345678", new_x="LMARGIN", new_y="NEXT")

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
build(pdf)
out = OUT_DIR / "INV-2024-099-NO-PO.pdf"
pdf.output(str(out))
print(f"Created: {out}")
