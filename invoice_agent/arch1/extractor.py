import re


def extract(raw: dict) -> dict:
  """Parse structured invoice fields from ingest() output.

  Returns None for any field that cannot be found, rather than raising.
  The validator downstream is responsible for reporting all missing fields
  in a single pass.
  """
  text = raw["text"]
  lines = [ln for ln in text.splitlines() if ln.strip()]

  return {
    "vendor_name":   lines[0],
    "invoice_no":    _field(text, r"Invoice No:\s+(\S+)",                    "invoice_no"),
    "date":          _field(text, r"^Date:\s+(.+)$",                         "date"),
    "due_date":      _field(text, r"^Due Date:\s+(.+)$",                     "due_date"),
    "po_number":     _field(text, r"^PO Number:\s+(\S+)",                    "po_number"),
    "customer_name": _after_label(lines, "Bill To:"),
    "line_items":    _line_items(text),
    "subtotal":      _amount(text, r"Subtotal:\s+GBP\s+([\d,]+\.\d{2})",    "subtotal"),
    "vat_amount":    _amount(text, r"VAT\s*\(\d+%\):\s+GBP\s+([\d,]+\.\d{2})", "vat_amount"),
    "total":         _amount(text, r"^Total:\s+GBP\s+([\d,]+\.\d{2})",      "total"),
  }


# ── helpers ──────────────────────────────────────────────────────────────────

def _field(text: str, pattern: str, name: str) -> str | None:
  m = re.search(pattern, text, re.MULTILINE)
  return m.group(1).strip() if m else None


def _amount(text: str, pattern: str, name: str) -> float | None:
  value = _field(text, pattern, name)
  return float(value.replace(",", "")) if value is not None else None


def _after_label(lines: list[str], label: str) -> str | None:
  for i, line in enumerate(lines):
    if line.strip() == label and i + 1 < len(lines):
      return lines[i + 1].strip()
  return None


def _line_items(text: str) -> list[dict]:
  # Matches: <row#> <description> <qty> GBP <unit_price> GBP <line_total>
  # Non-greedy description handles names with embedded digits (e.g. "27-inch Monitor")
  pattern = r"^(\d+)\s+(.+?)\s+(\d+)\s+GBP\s+([\d,]+\.\d{2})\s+GBP\s+([\d,]+\.\d{2})$"
  return [
    {
      "line_no":     int(m.group(1)),
      "description": m.group(2).strip(),
      "qty":         int(m.group(3)),
      "unit_price":  float(m.group(4).replace(",", "")),
      "line_total":  float(m.group(5).replace(",", "")),
    }
    for m in re.finditer(pattern, text, re.MULTILINE)
  ]
