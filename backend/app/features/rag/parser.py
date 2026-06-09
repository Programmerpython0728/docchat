"""Document parsing — PDF, DOCX, TXT"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> tuple[str, int]:
    """PDF → (text, page_count)."""
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    return text, len(reader.pages)


def parse_docx(file_path: str) -> tuple[str, int]:
    """DOCX → (text, paragraph_count)."""
    from docx import Document as DocxDocument
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs)
    return text, len(paragraphs)


def parse_txt(file_path: str) -> tuple[str, int]:
    """TXT/MD → (text, line_count)."""
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return text, text.count("\n") + 1


def parse_document(file_path: str) -> tuple[str, int]:
    """Fayl turiga qarab parse (SYNC — to_thread orqali chaqiriladi)."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext in (".txt", ".md"):
        return parse_txt(file_path)
    raise ValueError(f"Qo'llab-quvvatlanmaydi: {ext}")
