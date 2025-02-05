import easyocr
import re

class OCRProcessor:
    """
    A class to handle OCR (Optical Character Recognition) processing for detecting and validating license plates.

    Attributes:
        reader (easyocr.Reader): An EasyOCR reader object used for processing OCR.
    """
    
    def __init__(self):
        """
        Initializes an OCRProcessor object, creating an EasyOCR reader for English language detection.
        """
        self.reader = easyocr.Reader(['en'])

    def is_valid_plate(self, plate):
        """
        Checks whether the given string matches the format of a valid license plate.

        The valid format is defined as four numeric characters followed by three uppercase alphabetic characters,
        excluding vowels to avoid confusion (for example, 'A', 'E', 'I', 'O', and 'U' are excluded).

        Args:
            plate (str): The license plate string to validate.

        Returns:
            bool: True if the plate matches the defined format, otherwise False.
        """
        # Define a regex pattern for the license plate format: 4 numeric characters followed by 3 alphabetic characters
        pattern = re.compile(r'^\d{4}[B-DF-HJ-NP-TV-Z]{3}$')
        return pattern.match(plate) is not None
    

    def apply_ocr(self, roi):
        """
        Performs OCR on the given region of interest (ROI) and attempts to extract a valid license plate.

        The method uses EasyOCR to detect text within the image, sorts the text by the horizontal position (xmin),
        concatenates the detected characters, and validates the resulting string as a license plate.

        Args:
            roi (numpy.ndarray): The image region to apply OCR on.

        Returns:
            str or None: The detected license plate string if it matches the valid format, otherwise None.
        """
        ocr_results = self.reader.readtext(roi, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ', paragraph=True)
        
        # First, sort by vertical position (ymin), then by horizontal position (xmin)
        #ocr_results_sorted = sorted(ocr_results, key=lambda x: (x[0][0][1], x[0][0][0]))

        # Join all detections in one string
        concatenated_plate = ''.join([detection[1].strip().replace(" ", "").upper() for detection in ocr_results])
        print(f"OCR Concatenated Result: {concatenated_plate}")

        # Validate if string is a license plate
        if self.is_valid_plate(concatenated_plate):
            return concatenated_plate
        
        return None
