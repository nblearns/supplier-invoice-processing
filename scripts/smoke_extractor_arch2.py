"""
Smoke test: run the Arch 2 LLM extractor against each arch2 sample PDF
and pretty-print what Claude returns.  Makes a real API call.

Run: py scripts/smoke_extractor_arch2.py
"""

import json
from pathlib import Path
from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch2.extractor import extract

samples = sorted(Path("data/samples/arch2").glob("*.pdf"))
if not samples:
  print("No samples found — run: py scripts/gen_samples_arch2.py")
else:
  for pdf_path in samples:
    print(f"=== {pdf_path.name} ===")
    result = extract(ingest(pdf_path))
    print(json.dumps(result, indent=2))
    print()
