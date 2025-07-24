import fitz  # PyMuPDF
from typing import List

def load_pdf(path: str):
    doc = fitz.open(path)
    return doc

def get_pdf_title(doc) -> str:
    meta = doc.metadata or {}
    title = meta.get("title")
    if title:
        return title.strip()
    # Fallback: First line of first page
    first_page = doc[0]
    lines = first_page.get_text("text").splitlines()
    if lines:
        return lines[0].strip()
    return "Untitled Document"

def get_page_text_blocks(doc) -> List[list]:
    """Returns a list of blocks for each page."""
    pages_blocks = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        pages_blocks.append(blocks)
    return pages_blocks