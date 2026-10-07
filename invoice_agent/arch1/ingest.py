from pathlib import Path

import pdfplumber

# Each table is a list of rows; each row is a list of cell strings (or None for empty cells).
PageTable = list[list[str | None]]


def ingest(path: Path) -> dict:
  """Open a PDF invoice and return its raw text and detected tables.

  Returns:
    {
      "text":   full text of all pages joined by newline,
      "tables": list of tables found across all pages,
                each table is a list of rows, each row a list of cell strings
    }

  Raises:
    FileNotFoundError: if the PDF path does not exist
    ValueError:        if the PDF contains no pages
  """
  path = Path(path)
  if not path.exists():
    raise FileNotFoundError(f"Invoice not found: {path}")

  text_parts: list[str] = []
  tables: list[PageTable] = []

  with pdfplumber.open(path) as pdf:
    if not pdf.pages:
      raise ValueError(f"PDF has no pages: {path}")

    for page in pdf.pages:
      page_text = page.extract_text()
      if page_text:
        text_parts.append(page_text)

      page_tables = page.extract_tables()
      if page_tables:
        tables.extend(page_tables)

  return {
    "text": "\n".join(text_parts),
    "tables": tables,
  }
