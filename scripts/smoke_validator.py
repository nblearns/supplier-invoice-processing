from pathlib import Path
from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch1.extractor import extract
from invoice_agent.arch1.validator import validate, ValidationError

# ── Happy path: all three real invoices ──────────────────────────────────────
print("=== Happy path ===")
for pdf_path in sorted(Path("data/samples/arch1").glob("*.pdf")):
  result = validate(extract(ingest(pdf_path)))
  print(f"  PASS  {pdf_path.name}  |  {result['invoice_no']}  |  total={result['total']}")

# ── Failure cases ─────────────────────────────────────────────────────────────
print("\n=== Failure cases ===")

cases = [
  (
    "missing po_number",
    {
      "vendor_name": "TechSupplies Ltd", "invoice_no": "INV-X", "date": "01 Jan 2024",
      "due_date": "01 Feb 2024", "po_number": "",  "customer_name": "Acme",
      "line_items": [{"line_no": 1, "description": "Widget", "qty": 2, "unit_price": 10.0, "line_total": 20.0}],
      "subtotal": 20.0, "vat_amount": 4.0, "total": 24.0,
    },
  ),
  (
    "line total arithmetic wrong",
    {
      "vendor_name": "TechSupplies Ltd", "invoice_no": "INV-X", "date": "01 Jan 2024",
      "due_date": "01 Feb 2024", "po_number": "PO-001", "customer_name": "Acme",
      "line_items": [{"line_no": 1, "description": "Widget", "qty": 2, "unit_price": 10.0, "line_total": 99.0}],
      "subtotal": 99.0, "vat_amount": 19.8, "total": 118.8,
    },
  ),
  (
    "subtotal does not match line items",
    {
      "vendor_name": "TechSupplies Ltd", "invoice_no": "INV-X", "date": "01 Jan 2024",
      "due_date": "01 Feb 2024", "po_number": "PO-001", "customer_name": "Acme",
      "line_items": [{"line_no": 1, "description": "Widget", "qty": 2, "unit_price": 10.0, "line_total": 20.0}],
      "subtotal": 999.0, "vat_amount": 4.0, "total": 1003.0,
    },
  ),
  (
    "total does not match subtotal + vat",
    {
      "vendor_name": "TechSupplies Ltd", "invoice_no": "INV-X", "date": "01 Jan 2024",
      "due_date": "01 Feb 2024", "po_number": "PO-001", "customer_name": "Acme",
      "line_items": [{"line_no": 1, "description": "Widget", "qty": 2, "unit_price": 10.0, "line_total": 20.0}],
      "subtotal": 20.0, "vat_amount": 4.0, "total": 999.0,
    },
  ),
]

for label, data in cases:
  try:
    validate(data)
    print(f"  UNEXPECTED PASS  {label}")
  except ValidationError as e:
    print(f"  CAUGHT  [{label}]\n{e}\n")
