"""
Unit tests for invoice_agent.arch2.extractor._parse_response.

_parse_response is pure (no I/O), so these tests run without an API key.
They cover the JSON parsing contract that the rest of the pipeline relies on.
"""

import json
import pytest
from unittest.mock import patch

from invoice_agent.arch2.extractor import _parse_response, extract


# ── _parse_response ───────────────────────────────────────────────────────────

def test_parse_clean_json():
  data = {"vendor_name": "Acme", "invoice_no": "INV-001", "total": 100.0}
  result = _parse_response(json.dumps(data))
  assert result["vendor_name"] == "Acme"
  assert result["total"] == 100.0


def test_parse_json_code_fence():
  data = {"vendor_name": "GlobalTech", "total": 299.50}
  response = f"```json\n{json.dumps(data)}\n```"
  result = _parse_response(response)
  assert result["total"] == 299.50


def test_parse_plain_code_fence():
  data = {"vendor_name": "EuroOffice", "total": 500.0}
  response = f"```\n{json.dumps(data)}\n```"
  result = _parse_response(response)
  assert result["vendor_name"] == "EuroOffice"


def test_parse_surrounding_prose():
  data = {"vendor_name": "Acme", "total": 50.0}
  response = f"Here is the extracted data:\n{json.dumps(data)}\nLet me know if correct."
  result = _parse_response(response)
  assert result["total"] == 50.0


def test_parse_preserves_line_items():
  data = {
    "vendor_name": "Supplier X",
    "invoice_no": "X-001",
    "total": 200.0,
    "line_items": [
      {"line_no": 1, "description": "Widget", "qty": 2, "unit_price": 50.0, "line_total": 100.0},
      {"line_no": 2, "description": "Gadget", "qty": 1, "unit_price": 100.0, "line_total": 100.0},
    ],
  }
  result = _parse_response(json.dumps(data))
  assert len(result["line_items"]) == 2
  assert result["line_items"][0]["qty"] == 2


def test_parse_null_optional_fields():
  data = {"vendor_name": "Acme", "invoice_no": "I-1", "total": 10.0,
          "due_date": None, "po_number": None}
  result = _parse_response(json.dumps(data))
  assert result["due_date"] is None
  assert result["po_number"] is None


def test_parse_malformed_json_raises():
  with pytest.raises(ValueError, match="invalid JSON"):
    _parse_response("{not: valid, json}")


def test_parse_no_json_object_raises():
  with pytest.raises(ValueError, match="No JSON object"):
    _parse_response("Sorry, I cannot process this invoice.")


def test_parse_empty_string_raises():
  with pytest.raises(ValueError, match="No JSON object"):
    _parse_response("")


# ── extract (mocked API call) ─────────────────────────────────────────────────

_SAMPLE_RESPONSE = json.dumps({
  "vendor_name": "GlobalTech Inc",
  "invoice_no": "GT-2024-0091",
  "date": "March 5, 2024",
  "due_date": "April 4, 2024",
  "po_number": "PO-2024-0110",
  "customer_name": "Pinnacle Systems",
  "line_items": [
    {"line_no": 1, "description": "4K Webcam Pro", "qty": 3,
     "unit_price": 149.99, "line_total": 449.97},
    {"line_no": 2, "description": "Noise-Cancelling Headset", "qty": 5,
     "unit_price": 89.95, "line_total": 449.75},
    {"line_no": 3, "description": "USB-C Docking Station", "qty": 2,
     "unit_price": 199.00, "line_total": 398.00},
  ],
  "subtotal": 1297.72,
  "vat_amount": 103.82,
  "total": 1401.54,
})


def test_extract_calls_parse_on_claude_response():
  raw = {"text": "dummy invoice text", "tables": []}
  with patch("invoice_agent.arch2.extractor._call_claude", return_value=_SAMPLE_RESPONSE):
    result = extract(raw)
  assert result["invoice_no"] == "GT-2024-0091"
  assert len(result["line_items"]) == 3


def test_extract_passes_text_to_claude():
  raw = {"text": "the invoice text", "tables": []}
  with patch("invoice_agent.arch2.extractor._call_claude", return_value=_SAMPLE_RESPONSE) as mock:
    extract(raw)
  mock.assert_called_once_with("the invoice text")
