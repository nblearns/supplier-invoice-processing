"""Run the Arch 1 pipeline against every PDF in data/samples/arch1/."""
from pathlib import Path
from invoice_agent.arch1.pipeline import run

pdfs = sorted(Path("data/samples/arch1").glob("*.pdf"))
ok = error = 0

for pdf in pdfs:
  result = run(pdf)
  if result["status"] == "ok":
    print(f"  [OK]    {result['invoice_no']:20s}  ->  {result['erp_reference']}")
    ok += 1
  else:
    print(f"  [ERROR] {result['invoice_no']:20s}  {result['reason'].splitlines()[0]}")
    error += 1

print(f"\n  {ok} posted, {error} failed  (total: {ok + error})")
