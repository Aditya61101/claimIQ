import pdfplumber
import pytesseract
import cv2
import numpy as np
from .base import BaseExtractor
from .image_preprocessing import preprocess_image_for_ocr

class PDFExtractor(BaseExtractor):

    def _needs_ocr(self, page, text:str):
        if len(text) < 50 or (page.images and len(text) < 200):
            return True
        return False

    def extract(self, file_path: str) -> str:
        extracted_pages = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                page_text = page_text.strip()

                needs_ocr = self._needs_ocr(page, page_text)

                if needs_ocr:
                    page_image = page.to_image(resolution=300).original
                    ## opencv preprocessing
                    open_cv_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
                    processed = preprocess_image_for_ocr(open_cv_image)

                    ocr_text = pytesseract.image_to_string(processed)
                    combined = f"{page_text}\n{ocr_text}".strip()

                    extracted_pages.append(combined or f"[PAGE {page_num}]: NO TEXT")

                else:
                    extracted_pages.append(page_text)

        final_text = "\n\n".join(extracted_pages)

        if not final_text.strip():
            raise ValueError("No text could be extracted from PDF")
        
        return final_text

