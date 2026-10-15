"""
Stub supplier register — stands in for an ERP supplier master.

lookup(name) returns the internal supplier code for a given name,
using case-insensitive matching. Returns None if not found.
"""

_REGISTER: dict[str, str] = {
  "TechSupplies Ltd":   "SUPP-TSL-001",
  "GlobalTech Inc":     "SUPP-GTI-002",
  "EuroOffice GmbH":    "SUPP-EOG-003",
  "NovaTech Solutions": "SUPP-NVT-004",
}

_INDEX = {k.lower(): v for k, v in _REGISTER.items()}


def lookup(name: str) -> str | None:
  """Return the supplier code for name, or None if not found."""
  return _INDEX.get(name.strip().lower())
