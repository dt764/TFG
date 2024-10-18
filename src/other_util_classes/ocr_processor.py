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
        ocr_results = self.reader.readtext(roi, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')
        
        # Ordenar los resultados por las coordenadas horizontales (xmin)
        ocr_results_sorted = sorted(ocr_results, key=lambda x: x[0][0])

        # Concatenar todos los resultados de OCR detectados en una cadena
        concatenated_plate = ''.join([detection[1].strip().replace(" ", "").upper() for detection in ocr_results_sorted])
        print(f"OCR Concatenated Result: {concatenated_plate}")

        # Validar si el texto concatenado es una matrícula válida
        if self.is_valid_plate(concatenated_plate):
            return concatenated_plate
        
        return None
