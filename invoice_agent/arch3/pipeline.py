"""
Arch 3 pipeline: ingest -> agent loop -> validate -> post

The agent replaces the single-shot extractor from Arch 2. Everything else
(validate, post) is reused from Arch 1 unchanged.

Usage:
  py -m invoice_agent.arch3.pipeline <path-to-pdf>
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

from invoice_agent.arch3.agent import run as agent_run, AgentError
from invoice_agent.arch1.validator import validate, ValidationError
from invoice_agent.arch1.erp_adapter import post


def run(pdf_path: Path) -> dict:
  pdf_path = Path(pdf_path)
  invoice_no = pdf_path.stem

  try:
    data       = agent_run(pdf_path)
    invoice_no = data.get("invoice_no") or pdf_path.stem
    validated  = validate(data)
    result     = post(validated)
    return {
      "status":        "ok",
      "invoice_no":    invoice_no,
      "erp_reference": result["erp_reference"],
      "output_file":   result["output_file"],
    }

  except (ValidationError, AgentError) as e:
    return {
      "status":     "error",
      "invoice_no": invoice_no,
      "reason":     str(e),
    }


if __name__ == "__main__":
  load_dotenv()
  if len(sys.argv) != 2:
    print("Usage: py -m invoice_agent.arch3.pipeline <path-to-pdf>")
    sys.exit(1)

  outcome = run(Path(sys.argv[1]))

  if outcome["status"] == "ok":
    print(f"[OK]    {outcome['invoice_no']}  ->  {outcome['erp_reference']}")
    print(f"        output: {outcome['output_file']}")
  else:
    print(f"[ERROR] {outcome['invoice_no']}")
    print(f"        {outcome['reason']}")
    sys.exit(1)
