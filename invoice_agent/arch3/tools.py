"""
Arch 3 tools: PDF inspection tools exposed to the agent.

PdfContext     — wraps a PDF path; provides per-page text and table access.
TOOL_DEFINITIONS — Anthropic tool schemas passed to the API.
dispatch()     — routes a tool call (name + input) to a PdfContext method.
"""

import json
from pathlib import Path

import pdfplumber


# ── Tool definitions (passed to Anthropic API) ────────────────────────────────

TOOL_DEFINITIONS = [
  {
    "name": "get_full_text",
    "description": (
      "Return the full extracted text of the entire invoice. "
      "Call this first to get an overview before drilling into specific pages."
    ),
    "input_schema": {
      "type": "object",
      "properties": {},
      "required": [],
    },
  },
  {
    "name": "get_page_text",
    "description": "Return the extracted text from a single invoice page.",
    "input_schema": {
      "type": "object",
      "properties": {
        "page_no": {
          "type": "integer",
          "description": "1-based page number.",
        }
      },
      "required": ["page_no"],
    },
  },
  {
    "name": "get_tables",
    "description": (
      "Return structured table data from a single invoice page as a JSON array. "
      "Useful when line items are in a table that plain text extraction loses."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "page_no": {
          "type": "integer",
          "description": "1-based page number.",
        }
      },
      "required": ["page_no"],
    },
  },
  {
    "name": "finish",
    "description": (
      "Signal that extraction is complete. Call this once you have gathered "
      "all invoice fields. The invoice object must match the required schema."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "invoice": {
          "type": "object",
          "description": "Extracted invoice data matching the required schema.",
        }
      },
      "required": ["invoice"],
    },
  },
]


# ── PdfContext ────────────────────────────────────────────────────────────────

class PdfContext:
  """Lazy per-page wrapper around a pdfplumber PDF."""

  def __init__(self, pdf_path: Path) -> None:
    self.pdf_path = Path(pdf_path)
    self._pages: list[dict] | None = None

  def _load(self) -> None:
    if self._pages is not None:
      return
    self._pages = []
    with pdfplumber.open(self.pdf_path) as pdf:
      for page in pdf.pages:
        self._pages.append({
          "text":   page.extract_text() or "",
          "tables": page.extract_tables() or [],
        })

  def page_count(self) -> int:
    self._load()
    return len(self._pages)

  def get_full_text(self) -> str:
    self._load()
    combined = "\n".join(p["text"] for p in self._pages).strip()
    return combined or "(no text extracted from PDF)"

  def get_page_text(self, page_no: int) -> str:
    self._load()
    if page_no < 1 or page_no > len(self._pages):
      return f"Error: page {page_no} does not exist (PDF has {len(self._pages)} pages)"
    text = self._pages[page_no - 1]["text"].strip()
    return text or f"(no text on page {page_no})"

  def get_tables(self, page_no: int) -> str:
    self._load()
    if page_no < 1 or page_no > len(self._pages):
      return f"Error: page {page_no} does not exist (PDF has {len(self._pages)} pages)"
    tables = self._pages[page_no - 1]["tables"]
    if not tables:
      return f"(no tables on page {page_no})"
    return json.dumps(tables, ensure_ascii=False)


# ── Dispatcher ────────────────────────────────────────────────────────────────

def dispatch(name: str, tool_input: dict, context: PdfContext) -> str:
  """Execute a tool call and return a string result for the API."""
  if name == "get_full_text":
    return context.get_full_text()
  if name == "get_page_text":
    return context.get_page_text(tool_input["page_no"])
  if name == "get_tables":
    return context.get_tables(tool_input["page_no"])
  if name == "finish":
    return "acknowledged"
  return f"Error: unknown tool '{name}'"
