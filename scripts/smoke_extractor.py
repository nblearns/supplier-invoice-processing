import json
from pathlib import Path
from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch1.extractor import extract

samples = sorted(Path("data/samples/arch1").glob("*.pdf"))
for pdf_path in samples:
  result = extract(ingest(pdf_path))
  print(f"=== {pdf_path.name} ===")
  print(json.dumps(result, indent=2))
  print()
