import cv2
import pytesseract
from .base import BaseExtractor
from .image_preprocessing import preprocess_image_for_ocr

class ImageExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Unable to read image file")
        
        processed = preprocess_image_for_ocr(image)
        text = pytesseract.image_to_string(processed)

        if not text.strip():
            raise ValueError("OCR produced no text.")
        
        return text.strip()