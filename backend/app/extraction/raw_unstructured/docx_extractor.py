from docx import Document
from .base import BaseExtractor

class DOCXExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
