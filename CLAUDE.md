# invoice-agent

A learning project: build a supplier-invoice-to-ERP automation flow in three stages, each adding capability deliberately.

## Project goal

Parse supplier PDF invoices and post the extracted data to an ERP system. Built in three stages so each design decision can be understood before the next layer of complexity is added.

## Architectures

### Architecture 1 — no LLM, fixed layout (build first)
A linear, rule-based pipeline for a single known invoice format.
Input: PDF invoice with a fixed, predictable layout.
1. Ingest PDF → extract raw text with `pdfplumber`.
2. Parse fields directly using positional rules or regex (no supplier classification needed yet — one layout only).
3. Validate and normalise the extracted data.
4. Post to ERP via a stub adapter.

Goal: prove the pipeline end-to-end with zero AI cost and full auditability.
No LLM, no classification, no ambiguity.

### Architecture 2 — LLM extraction, multiple layouts (build second)
Extend the same pipeline to handle invoices from multiple suppliers with differing layouts.
Replace the rule-based parser with a Claude API call: pass the extracted text and let the LLM return structured JSON regardless of layout.
The pipeline shape (ingest → extract → validate → post) stays fixed — only the extraction step changes.

Goal: show when and why an LLM earns its place inside a deterministic workflow.

### Architecture 3 — agent (build third)
Replace the fixed extract step with a reasoning agent loop (Claude API with tools).
The agent decides which tool to call, can inspect specific pages or tables, retries uncertain fields, and flags anomalies — iterating until the invoice is fully parsed.
Validation and ERP adapter are reused unchanged from Architecture 1.

Goal: show when a fixed pipeline is no longer enough and an agent loop is the right answer.

## Working conventions

- **Explain design choices.** Before writing any non-trivial module, give a short rationale (2-4 sentences). I'm here to learn, not just ship.
- **Confirm before implementing.** After proposing an approach, wait for approval before writing code.
- **Confirm before any push or repo creation.** Never `git push`, create a GitHub repo, or open a PR without explicit instruction.
- **Incremental builds.** Implement one module at a time. Each increment should be runnable and testable before moving on.
- **Python, Windows.** Use Python 3.11+. Paths must be Windows-compatible (`pathlib.Path` throughout, no hardcoded `/`).
- **2-space indentation** (per global standard).
- **No premature abstractions.** Only add structure the current stage actually needs.

## Environment

- OS: Windows 11
- Shell: PowerShell
- Python: virtual env at `.venv\` (create with `python -m venv .venv`)
- Dependencies tracked in `requirements.txt` (pin versions)

## Out of scope (for now)

- Real ERP integration (use a stub / local JSON file)
- Multi-language invoices
- Cloud deployment
