from pathlib import Path
from invoice_agent.arch1.ingest import ingest

samples = sorted(Path("data/samples/arch1").glob("*.pdf"))
for pdf_path in samples:
  result = ingest(pdf_path)
  table_count = len(result["tables"])
  print(f"=== {pdf_path.name} ===")
  print("-- TEXT --")
  print(result["text"])
  print(f"-- TABLES ({table_count} found) --")
  for i, table in enumerate(result["tables"]):
    print(f"  Table {i}:")
    for row in table:
      print(f"    {row}")
  print()
