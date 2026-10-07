"""
Arch 1 pipeline: ingest -> extract -> validate -> post

Usage:
  python -m invoice_agent.arch1.pipeline <path-to-pdf>
"""

import sys
from pathlib import Path

from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch1.extractor import extract
from invoice_agent.arch1.validator import validate, ValidationError
from invoice_agent.arch1.erp_adapter import post


def run(pdf_path: Path) -> dict:
  """Process a single PDF invoice end-to-end.

  Returns:
    {"status": "ok",    "invoice_no": ..., "erp_reference": ..., "output_file": ...}
    {"status": "error", "invoice_no": ..., "reason": ...}

  ValidationError (bad invoice data) is caught and returned as a structured
  error result. All other exceptions propagate — they are bugs, not bad invoices.
  """
  pdf_path = Path(pdf_path)
  invoice_no = pdf_path.stem  # best-effort identifier before extraction runs

  try:
    raw       = ingest(pdf_path)
    data      = extract(raw)
    invoice_no = data.get("invoice_no") or pdf_path.stem
    validated = validate(data)
    result    = post(validated)
    return {
      "status":        "ok",
      "invoice_no":    invoice_no,
      "erp_reference": result["erp_reference"],
      "output_file":   result["output_file"],
    }

  except ValidationError as e:
    return {
      "status":     "error",
      "invoice_no": invoice_no,
      "reason":     str(e),
    }


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python -m invoice_agent.arch1.pipeline <path-to-pdf>")
    sys.exit(1)

  outcome = run(Path(sys.argv[1]))

  if outcome["status"] == "ok":
    print(f"[OK]    {outcome['invoice_no']}  ->  {outcome['erp_reference']}")
    print(f"        output: {outcome['output_file']}")
  else:
    print(f"[ERROR] {outcome['invoice_no']}")
    print(f"        {outcome['reason']}")
    sys.exit(1)
