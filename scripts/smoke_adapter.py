import json
from pathlib import Path
from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch1.extractor import extract
from invoice_agent.arch1.validator import validate
from invoice_agent.arch1.erp_adapter import post

for pdf_path in sorted(Path("data/samples/arch1").glob("*.pdf")):
  result = post(validate(extract(ingest(pdf_path))))
  print(f"  {result['status'].upper()}  {result['erp_reference']}  ->  {result['output_file']}")

print("\n--- Sample output file ---")
sample = Path("data/outputs/INV-2024-001.json")
print(json.dumps(json.loads(sample.read_text(encoding="utf-8")), indent=2))
