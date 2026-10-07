class ValidationError(Exception):
  pass


def validate(data: dict) -> dict:
  """Validate extracted invoice data against ERP posting requirements.

  Checks presence of ERP-required fields, per-line-item integrity, and
  arithmetic consistency. Collects all failures before raising so the
  caller sees every problem in one pass.

  Returns the same dict unchanged if valid.
  Raises ValidationError listing every failed check if not.
  """
  errors: list[str] = []

  # ── 1. ERP required fields ────────────────────────────────────────────
  # Minimum to create an invoice in ERP: PO number, supplier, items, totals
  for field in ("po_number", "vendor_name", "invoice_no", "date",
                "customer_name", "line_items", "total"):
    value = data.get(field)
    if value is None or value == "" or value == []:
      errors.append(f"missing required field '{field}'")

  # ── 2. Per-line-item checks ───────────────────────────────────────────
  for item in data.get("line_items") or []:
    n = item.get("line_no", "?")
    if not item.get("description"):
      errors.append(f"line {n}: missing description")
    if not isinstance(item.get("qty"), int) or item["qty"] <= 0:
      errors.append(f"line {n}: qty must be a positive integer, got {item.get('qty')!r}")
    if not isinstance(item.get("unit_price"), (int, float)) or item["unit_price"] <= 0:
      errors.append(f"line {n}: unit_price must be positive, got {item.get('unit_price')!r}")

  # ── 3. Arithmetic consistency ─────────────────────────────────────────
  # Only run if we have enough data (presence errors already captured above)
  items = data.get("line_items") or []
  items_ok = all(
    isinstance(item.get("qty"), int)
    and isinstance(item.get("unit_price"), (int, float))
    and isinstance(item.get("line_total"), (int, float))
    for item in items
  )

  if items and items_ok:
    for item in items:
      expected = _round(item["qty"] * item["unit_price"])
      actual   = _round(item["line_total"])
      if expected != actual:
        errors.append(
          f"line {item['line_no']}: {item['qty']} × {item['unit_price']} "
          f"= {expected} but line_total is {actual}"
        )

    if data.get("subtotal") is not None:
      computed = _round(sum(item["line_total"] for item in items))
      if computed != _round(data["subtotal"]):
        errors.append(
          f"subtotal mismatch: line totals sum to {computed} "
          f"but subtotal is {data['subtotal']}"
        )

  if (data.get("subtotal") is not None
      and data.get("vat_amount") is not None
      and data.get("total") is not None):
    expected_total = _round(data["subtotal"] + data["vat_amount"])
    if expected_total != _round(data["total"]):
      errors.append(
        f"total mismatch: {data['subtotal']} + {data['vat_amount']} "
        f"= {expected_total} but total is {data['total']}"
      )

  if errors:
    bullet_list = "\n".join(f"  - {e}" for e in errors)
    raise ValidationError(f"Invoice failed validation:\n{bullet_list}")

  return data


def _round(value: float) -> float:
  return round(value, 2)
