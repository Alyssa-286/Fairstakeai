from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Placeholder PDF text extraction.
    In MVP we assume PDFs are text-based and simply decode bytes.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1; production version would invoke pdfplumber/tesseract.
        return file_path.read_text(encoding="latin-1")


def extract_text_from_bytes(filename: str, content: bytes) -> str:
    temp_path = Path(filename)
    temp_path.write_bytes(content)
    text = extract_text_from_pdf(temp_path)
    temp_path.unlink(missing_ok=True)
    return text

