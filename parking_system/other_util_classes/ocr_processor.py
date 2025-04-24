from paddleocr import PaddleOCR
import re
import numpy as np

class OCRProcessor:
    """
    A class to handle OCR (Optical Character Recognition) processing for detecting and validating license plates
    using PaddleOCR.
    
    Attributes:
        ocr (PaddleOCR): An instance of PaddleOCR for text detection.
    """

    def __init__(self, min_confidence=0.9):
        """
        Initializes the OCRProcessorPaddle with English OCR model.
        """
        self.min_confidence = min_confidence
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize with English model

    def is_valid_plate(self, plate):
        """
        Checks whether the given string matches the format of a valid license plate.

        Format: 4 numeric characters followed by 3 uppercase alphabetic characters excluding vowels.

        Args:
            plate (str): The license plate string to validate.

        Returns:
            bool: True if the plate matches the format, False otherwise.
        """
        pattern = re.compile(r'^(C?\d{4}[B-DF-HJ-NP-RSTV-Z]{3})$')
        return pattern.match(plate) is not None

    def apply_ocr(self, roi):
        """
        Applies OCR to the input image and attempts to extract a valid license plate string.

        Args:
            roi (numpy.ndarray): Image region (as numpy array) to apply OCR on.

        Returns:
            str or None: The detected license plate string if valid, otherwise None.
        """
        result = self.ocr.ocr(roi, cls=True)
        
        text_candidates = []

        if not result[0]:
            return None

        for line in result[0]:
            text, confidence = line[1][0], line[1][1]
            if confidence >= self.min_confidence:
                text_candidates.append(text.strip().replace(" ", "").upper())
        

        concatenated_plate = ''.join(text_candidates)

        if self.is_valid_plate(concatenated_plate):
            return concatenated_plate

        return None
