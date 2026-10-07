import json
from pathlib import Path

# Stub output directory — replace with real ERP endpoint in production
_OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "outputs"


def post(data: dict) -> dict:
  """Transform validated invoice data into an ERP payload and post it.

  Stub implementation: writes the payload as JSON to data/outputs/.
  Returns a result dict with status and the generated ERP reference.

  The adapter is the only module that knows the ERP schema — all field
  name mapping lives here so upstream modules stay ERP-agnostic.
  """
  payload = _build_payload(data)
  result = _post_to_erp(payload)
  return result


# ── internal ──────────────────────────────────────────────────────────────────

def _build_payload(data: dict) -> dict:
  """Map internal field names to ERP schema."""
  return {
    "purchase_order_number": data["po_number"],
    "supplier_name":         data["vendor_name"],
    "invoice_number":        data["invoice_no"],
    "invoice_date":          data["date"],
    "due_date":              data["due_date"],
    "bill_to":               data["customer_name"],
    "line_items": [
      {
        "position":    item["line_no"],
        "description": item["description"],
        "quantity":    item["qty"],
        "unit_cost":   item["unit_price"],
        "line_total":  item["line_total"],
      }
      for item in data["line_items"]
    ],
    "subtotal":   data["subtotal"],
    "tax_amount": data["vat_amount"],
    "total_due":  data["total"],
  }


def _post_to_erp(payload: dict) -> dict:
  """Stub: write payload to disk and return a mock ERP response."""
  _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

  invoice_no = payload["invoice_number"]
  out_path = _OUTPUT_DIR / f"{invoice_no}.json"

  with out_path.open("w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

  return {
    "status":       "posted",
    "erp_reference": f"ERP-{invoice_no}",
    "output_file":  str(out_path),
  }
