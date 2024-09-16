import datetime
import os
import pathlib
from license_plate_detector import LicensePlateDetector
from webcam_capture import WebcamCapture
from ocr_processor import OCRProcessor
from logger import Logger
import cv2

def main():

    script_dir = pathlib.Path(__file__).parent.absolute()
    model_path = os.path.join(script_dir, '../models/saved_model/license-detector_edgetpu.tflite')
    label_file = os.path.join(script_dir, '../models/saved_model/labels.txt')
    csv_file = os.path.join(script_dir, '../detections.csv')
    img_dir = os.path.join(script_dir, '../detections_img')
    min_detection_confidence = 0.85
    min_ocr_confidence = 0.85

    detector = LicensePlateDetector(model_path, min_detection_confidence)
    webcam = WebcamCapture()
    ocr_processor = OCRProcessor()
    logger = Logger(img_dir, csv_file)

    while True:
        frame = webcam.get_frame()
        roi, ymin, xmin, ymax, xmax = detector.detect_license_plate(frame)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

        if roi is not None:

            detected_plate = ocr_processor.apply_ocr(roi)

            if detected_plate:

                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                image_path = os.path.join(img_dir, f'{timestamp}.jpg') 

                logger.save_image(frame, image_path)
                logger.save_detection_to_csv(timestamp, detected_plate, image_path)

                print(f"Detected Plate: {detected_plate}")

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    webcam.release()

if __name__ == "__main__":
    main()
