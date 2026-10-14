"""
Arch 2 pipeline: ingest -> LLM extract -> validate -> post

Identical shape to Arch 1. Only the extractor import changes — everything else
(ingest, validate, post) is reused from arch1 unchanged to make that explicit.

Usage:
  py -m invoice_agent.arch2.pipeline <path-to-pdf>
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

from invoice_agent.arch1.ingest import ingest
from invoice_agent.arch2.extractor import extract        # ← only change vs arch1
from invoice_agent.arch1.validator import validate, ValidationError
from invoice_agent.arch1.erp_adapter import post

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def run(pdf_path: Path) -> dict:
  pdf_path = Path(pdf_path)
  invoice_no = pdf_path.stem

  try:
    if pdf_path.suffix.lower() in _IMAGE_SUFFIXES:
      raw = {"image_path": pdf_path, "tables": []}
    else:
      raw = ingest(pdf_path)
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
  load_dotenv()
  if len(sys.argv) != 2:
    print("Usage: py -m invoice_agent.arch2.pipeline <path-to-pdf>")
    sys.exit(1)

  outcome = run(Path(sys.argv[1]))

  if outcome["status"] == "ok":
    print(f"[OK]    {outcome['invoice_no']}  ->  {outcome['erp_reference']}")
    print(f"        output: {outcome['output_file']}")
  else:
    print(f"[ERROR] {outcome['invoice_no']}")
    print(f"        {outcome['reason']}")
    sys.exit(1)
