"""
Arch 2 extractor: replaces the regex parser with a Claude API call.

The module is split into three layers so each part is independently testable:
  _call_claude(text)      → raw string from the model
  _parse_response(text)   → dict parsed from that string (no I/O, pure logic)
  extract(raw)            → public entry point called by the pipeline
"""

import base64
import json
from pathlib import Path

import anthropic

_CLIENT = None  # lazy-initialised so tests that mock _call_claude don't need a key


def _client() -> anthropic.Anthropic:
  global _CLIENT
  if _CLIENT is None:
    _CLIENT = anthropic.Anthropic()
  return _CLIENT


# ── Prompt ────────────────────────────────────────────────────────────────────

_SCHEMA = """\
{
  "vendor_name":   "string — supplier / company name",
  "invoice_no":    "string — invoice identifier",
  "date":          "string — invoice date as it appears",
  "due_date":      "string or null",
  "po_number":     "string or null — purchase order reference",
  "customer_name": "string — buyer name",
  "line_items": [
    {
      "line_no":     "integer (1-based; assign sequentially if not printed)",
      "description": "string",
      "qty":         "integer",
      "unit_price":  "number — strip any currency symbol",
      "line_total":  "number — strip any currency symbol"
    }
  ],
  "subtotal":   "number or null",
  "vat_amount": "number or null — tax / TVA / sales-tax amount",
  "total":      "number — grand total"
}"""

_PROMPT = """\
Extract all invoice fields from the text below and return them as a single JSON object.

Return ONLY valid JSON — no explanation, no markdown, no code fences.

Schema (field names are fixed; types are hints):
{schema}

Rules:
- All monetary values must be plain numbers, e.g. 1234.56 (no currency symbols).
- qty and line_no must be integers.
- Assign line_no sequentially (1, 2, 3 …) if the invoice has no row numbers.
- Return null for any optional field not present in the invoice.

Invoice text:
---
{text}
---"""


# ── Public entry point ────────────────────────────────────────────────────────

def extract(raw: dict) -> dict:
  """Extract structured invoice fields using Claude.

  Accepts either:
    raw["text"]       — plain text from pdfplumber (PDF path)
    raw["image_path"] — Path to a PNG/JPG invoice (uses Claude vision)
  """
  if "image_path" in raw:
    response_text = _call_claude_image(Path(raw["image_path"]))
  else:
    response_text = _call_claude(raw["text"])
  return _parse_response(response_text)


# ── Internal layers ───────────────────────────────────────────────────────────

def _call_claude(invoice_text: str) -> str:
  """Send invoice text to Claude; return the raw response string."""
  prompt = _PROMPT.format(schema=_SCHEMA, text=invoice_text)
  message = _client().messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
  )
  return message.content[0].text


_PROMPT_IMAGE = """\
Extract all invoice fields from the invoice image and return them as a single JSON object.

Return ONLY valid JSON — no explanation, no markdown, no code fences.

Schema (field names are fixed; types are hints):
{schema}

Rules:
- All monetary values must be plain numbers, e.g. 1234.56 (no currency symbols).
- qty and line_no must be integers.
- Assign line_no sequentially (1, 2, 3 …) if the invoice has no row numbers.
- Return null for any optional field not present in the invoice.
- po_number: capture any purchase/order reference regardless of its label
  (e.g. "PO Number", "Customer Order No", "Bon de commande", "Purchase Order", etc.)"""


def _call_claude_image(image_path: Path) -> str:
  """Send an invoice image to Claude vision; return the raw response string."""
  suffix     = image_path.suffix.lower()
  media_type = "image/png" if suffix == ".png" else "image/jpeg"
  data       = base64.standard_b64encode(image_path.read_bytes()).decode()

  message = _client().messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
      "role": "user",
      "content": [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
        {"type": "text",  "text": _PROMPT_IMAGE.format(schema=_SCHEMA)},
      ],
    }],
  )
  return message.content[0].text


def _parse_response(response_text: str) -> dict:
  """Parse a JSON invoice dict from Claude's response string.

  Tolerates markdown code fences and leading/trailing prose — finds the
  outermost { … } block and parses it.

  Raises ValueError if no valid JSON object is found.
  """
  text = response_text.strip()

  # Strip markdown code fences (```json ... ``` or ``` ... ```)
  if text.startswith("```"):
    first_newline = text.find("\n")
    if first_newline != -1:
      text = text[first_newline + 1:]
    if text.endswith("```"):
      text = text[:-3].strip()

  # Find outermost JSON object
  start = text.find("{")
  end = text.rfind("}") + 1
  if start == -1 or end == 0:
    raise ValueError(f"No JSON object found in response: {response_text!r}")

  json_str = text[start:end]
  try:
    return json.loads(json_str)
  except json.JSONDecodeError as exc:
    raise ValueError(
      f"Claude returned invalid JSON: {exc}\nResponse: {response_text!r}"
    ) from exc
