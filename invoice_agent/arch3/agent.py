"""
Arch 3 agent: the reasoning loop that drives invoice extraction.

run(pdf_path) → dict
  Opens the PDF, runs the Claude tool-use loop, returns the extracted invoice
  dict once the agent calls finish(). Raises AgentError on failure.

The loop:
  1. Start with a user message describing the task and page count.
  2. Claude responds with one or more tool calls.
  3. Each tool result is fed back; the loop repeats.
  4. When Claude calls finish(), the loop exits with the invoice JSON.
"""

from pathlib import Path

import anthropic

from invoice_agent.arch3.tools import TOOL_DEFINITIONS, PdfContext, dispatch

MAX_ITERATIONS = 10


class AgentError(Exception):
  pass


# ── Prompts ───────────────────────────────────────────────────────────────────

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

_SYSTEM_PROMPT = f"""\
You are an invoice extraction agent. Your job is to extract all fields from a PDF invoice \
and return them as structured JSON.

You have four tools:
- get_full_text()         — full text of the entire invoice
- get_page_text(page_no)  — text from one specific page (1-based)
- get_tables(page_no)     — table data from one specific page as a JSON array
- finish(invoice)         — call this once you have all fields; it ends the session

Suggested strategy:
1. Call get_full_text() first to see the whole invoice.
2. If a field is ambiguous or missing, call get_page_text() or get_tables() on the \
relevant page to look more carefully.
3. Once you are confident you have every required field, call finish() with the complete \
invoice JSON.

Required schema for the invoice argument of finish():
{_SCHEMA}

Rules:
- All monetary values must be plain numbers (no currency symbols), e.g. 1234.56.
- qty and line_no must be integers.
- Assign line_no sequentially (1, 2, 3 ...) if the invoice has no row numbers.
- Return null for any optional field not present in the invoice.
- po_number: capture any purchase/order reference regardless of its label \
(e.g. "PO Number", "Customer Order No", "Purchase Order", etc.).\
"""


# ── Public entry point ────────────────────────────────────────────────────────

def run(pdf_path: Path) -> dict:
  """Run the agent loop on a PDF invoice; return the extracted invoice dict."""
  pdf_path = Path(pdf_path)
  context = PdfContext(pdf_path)
  client = anthropic.Anthropic()

  page_count = context.page_count()
  messages = [
    {
      "role": "user",
      "content": (
        f"The invoice PDF has {page_count} page(s). "
        "Extract all fields and call finish() with the result."
      ),
    }
  ]

  for iteration in range(1, MAX_ITERATIONS + 1):
    response = client.messages.create(
      model="claude-sonnet-4-6",
      max_tokens=4096,
      system=_SYSTEM_PROMPT,
      tools=TOOL_DEFINITIONS,
      messages=messages,
    )

    if response.stop_reason != "tool_use":
      raise AgentError(
        f"Agent stopped without calling finish "
        f"(iteration {iteration}, stop_reason={response.stop_reason!r})"
      )

    # Append the full assistant turn (may include text + tool_use blocks)
    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    finish_invoice = None

    for block in response.content:
      if block.type != "tool_use":
        continue
      result = dispatch(block.name, block.input, context)
      tool_results.append({
        "type":        "tool_result",
        "tool_use_id": block.id,
        "content":     result,
      })
      if block.name == "finish":
        finish_invoice = block.input["invoice"]

    messages.append({"role": "user", "content": tool_results})

    if finish_invoice is not None:
      return finish_invoice

  raise AgentError(f"Agent did not call finish within {MAX_ITERATIONS} iterations")
