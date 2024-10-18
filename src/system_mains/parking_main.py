import datetime
import pathlib
import cv2
import json

import sys
import os

# Agrega el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from other_util_classes.license_plate_detector import LicensePlateDetector
from other_util_classes.webcam_capture import WebcamCapture
from other_util_classes.ocr_processor import OCRProcessor

from communication.msg_disp_factory import MsgDispatcherFactory


def main():
    script_dir = pathlib.Path(__file__).parent.absolute()
    model_path = script_dir / '../../models/saved_model/license-detector_edgetpu.tflite'
    min_detection_confidence = 0.9

    # Variables para evitar loggear duplicados
    last_detected_plate = None
    last_detection_time = None
    time_last_detect_threshold = 3


    parking_msg_dispatcher = MsgDispatcherFactory.create_detector_dispatcher(
        hostname='localhost'
    )


    opened_gate = False

    detector = LicensePlateDetector(str(model_path), min_detection_confidence)
    webcam = WebcamCapture()
    ocr_processor = OCRProcessor()

    try:
        while True:
            frame = webcam.get_frame()
            roi, ymin, xmin, ymax, xmax, confidence = detector.detect_license_plate(frame)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            if roi is not None:
                # Dibujar etiqueta
                print("New Frame with detection:")
                object_name = 'license'
                label = '%s: %d%%' % (object_name, int(confidence * 100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, labelSize[1] + 10)

                cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), 
                              (xmin + labelSize[0], label_ymin + baseLine - 10), 
                              (255, 255, 255), cv2.FILLED)

                cv2.putText(frame, label, (xmin, label_ymin - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # Aplicar OCR
                detected_plate = ocr_processor.apply_ocr(roi)

                if detected_plate:

                    print(f"Detected Plate: {detected_plate}")

                    current_time = datetime.datetime.now()

                    # Evitar guardar si es la misma matrícula detectada recientemente
                    if (detected_plate != last_detected_plate or last_detected_plate is None):

                        # Actualizar última detección
                        last_detected_plate = detected_plate

                        print(f"{detected_plate} will be sent to verifier")

                        timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')

                        msg_dict = {
                            "plate": detected_plate,
                            "timestamp": timestamp_str
                        }

                        message = json.dumps(msg_dict)

                        parking_msg_dispatcher.send_msg(message=message)
                        parking_msg_dispatcher.wait_and_receive_msg()
                        opened_gate = parking_msg_dispatcher.get_reply_result()

                        if opened_gate:
                            print("Allowed to enter")
                        else:
                            print("Denied to enter")

                    else:
                        time_since_last_detection = (current_time - last_detection_time).total_seconds()
                        if time_since_last_detection < time_last_detect_threshold:
                            print(f"Not logging / verifying {detected_plate} again." +
                                    "Gate will remain in same state (Opened = {opened_gate})")


                    last_detection_time = current_time
                        
            
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        parking_msg_dispatcher.close()  # Cerrar la conexión RabbitMQ al finalizar

if __name__ == "__main__":
    main()
