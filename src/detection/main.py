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
    model_path = script_dir / '../../models/saved_model/license-detector_edgetpu.tflite'
    csv_file = script_dir / '../../detections.csv'
    img_dir = script_dir / '../../detections_img'
    min_detection_confidence = 0.9
    min_ocr_confidence = 0.9

    # Variables para evitar loggear duplicados
    last_detected_plate = None
    last_detection_time = None
    time_threshold = 5  # Umbral de tiempo en segundos

    detector = LicensePlateDetector(str(model_path), min_detection_confidence)
    webcam = WebcamCapture()
    ocr_processor = OCRProcessor()
    logger = Logger(img_dir, csv_file)

    try:
        while True:
            frame = webcam.get_frame()
            roi, ymin, xmin, ymax, xmax, confidence = detector.detect_license_plate(frame)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            if roi is not None:

                # Draw label
                object_name = 'license' # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(confidence*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                #Aplicar OCR
                detected_plate = ocr_processor.apply_ocr(roi)

                if detected_plate:
                    print(f"Detected Plate: {detected_plate}")
                    
                    current_time = datetime.datetime.now()

                    # Evitar guardar si es la misma matrícula detectada recientemente
                    if (detected_plate != last_detected_plate or 
                        last_detection_time is None or 
                        (current_time - last_detection_time).total_seconds() > time_threshold):

                        print(f"Logging {detected_plate} into csv")

                        # Actualizar última detección
                        last_detected_plate = detected_plate
                        last_detection_time = current_time
                        
                        logger.save_detection_to_csv(detected_plate, current_time, frame)
                    else:
                        print(f"Not Logging {detected_plate} because its too early to do it again")
                        
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        webcam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
