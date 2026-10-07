from pathlib import Path
from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch1.extractor import extract
from invoice_agent.arch1.validator import validate, ValidationError
from invoice_agent.arch1.erp_adapter import post

print("=== Good invoices (should all PASS) ===")
for pdf in sorted(Path("data/samples/arch1").glob("INV-2024-00[123].pdf")):
  result = post(validate(extract(ingest(pdf))))
  print(f"  PASS  {pdf.name}")

print()
print("=== Bad invoice - no PO number (should reach validator) ===")
pdf = Path("data/samples/arch1/INV-2024-099-NO-PO.pdf")
data = extract(ingest(pdf))
print(f"  extractor returned po_number = {data['po_number']!r}")
print(f"  extractor completed without raising")
try:
  validate(data)
except ValidationError as e:
  print(f"  ValidationError raised at validator:")
  print(f"  {e}")
