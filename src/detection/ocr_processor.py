import easyocr
import re

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def is_valid_plate(self, plate):
        # Define a regex pattern for the license plate format: 4 numeric characters followed by 3 alphabetic characters
        pattern = re.compile(r'^\d{4}[B-DF-HJ-NP-TV-Z]{3}$')
        return pattern.match(plate) is not None

    def apply_ocr(self, roi):
       ocr_results = self.reader.readtext(roi, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
       # Procesar resultados del OCR
       for detection in ocr_results:
         print(f"OCR Result for license: {detection[1]}")
         detected_plate = detection[1].strip().replace(" ", "").upper()

         if self.is_valid_plate(detected_plate):
            return detected_plate

