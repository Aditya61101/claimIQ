import os

from .pdf_extractor import PDFExtractor
from .image_extractor import ImageExtractor
from .docx_extractor import DOCXExtractor
from .txt_extractor import TXTExtractor


EXTRACTORS = {
    ".pdf": PDFExtractor(),
    ".png": ImageExtractor(),
    ".jpg": ImageExtractor(),
    ".jpeg": ImageExtractor(),
    ".docx": DOCXExtractor(),
    ".txt": TXTExtractor(),
}


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    extractor = EXTRACTORS.get(ext)
    if not extractor:
        raise ValueError(f"Unsupported file type: {ext}")

    text = extractor.extract(file_path)

    if not text or not text.strip():
        raise ValueError("No text extracted from document")

    return text.strip()
