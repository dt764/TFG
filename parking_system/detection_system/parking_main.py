import argparse
from datetime import datetime, timezone
import pathlib
import cv2
import json
import sys
import os
import pygame
import numpy as np

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from logging_module.logger_setup import setup_logger
from parking_system.communication.amqp_msg import AMQP_Msg_Disp
from parking_system.communication.mqtt_msg import MQTT_Msg_Disp
from parking_system.other_util_classes.license_plate_detector import LicensePlateDetector
from parking_system.other_util_classes.webcam_capture import WebcamCapture
#from parking_system.other_util_classes.pi_webcam_capture import Pi_WebcamCapture
from parking_system.other_util_classes.ocr_processor import OCRProcessor
from parking_system.base_config import BaseConfig

last_screen_message = None

def update_screen_state(message, dispatcher):
    """
    Sends a message to the screen only if it differs from the last sent message.
    """
    global last_screen_message
    if message != last_screen_message:
        dispatcher.send_msg(message)
        print(f"Screen Message: {message}")
        last_screen_message = message


def detect_msg_handler(message):
    """
    Handles messages for detecting if the door should open.

    This function extracts the 'open_door' field from the received message.

    Args:
        message (bytes): The received message as a byte string in JSON format.

    Returns:
        bool: The value of the 'open_door' field, indicating if the door should be opened.
    """
    msg_json = json.loads(message.decode("utf-8"))

    is_allowed = msg_json.get("allowed")
    plate = msg_json.get("plate")

    reply_dict = {
        "plate": plate,
        "allowed": is_allowed
  
    }

    return reply_dict



def main():
    """
    The main function for license plate detection and verification.

    This script captures frames from a webcam, detects license plates using a pre-trained model, 
    performs OCR to recognize the detected plates, and sends the recognized plates to a verifier 
    via message dispatching for further processing (e.g., checking if the vehicle is allowed to enter).

    It includes mechanisms to avoid logging the same plate multiple times within a short period, 
    updates the gate state based on the verifier's response, and displays the detection results in real-time.

    Attributes:
        script_dir (Path): The directory where the script is located.
        model_path (Path): Path to the license plate detector model.
        min_detection_confidence (float): Minimum confidence threshold for detecting a license plate.
        last_detected_plate (str or None): The last detected plate string.
        last_detection_time (datetime or None): The time when the last plate detection occurred.
        time_last_detect_threshold (int): Time threshold in seconds for considering a plate as a duplicate detection.
        parking_msg_dispatcher (MsgDispatcher): The dispatcher for sending and receiving messages for verification.
        opened_gate (bool): Indicates if the gate is open based on the last verification result.
    """

    # Set up argument parser
    parser = argparse.ArgumentParser(description='License plate detection system')
    parser.add_argument('--show-camera-config', action='store_true',
                help='Muestra configuraciones de la Picamea2 disponibles')
    parser.add_argument('--camera-config-index', type=int, default=0,
                help='Index of the Picamera2 configuration to use (must be a positive integer)')
    
    args = parser.parse_args()
    

    # Validate camera config index is positive
    if args.camera_config_index < 0:
        print("Camera configuration index must be a positive integer")
        sys.exit(1)

    '''
    if BaseConfig.USE_PI_CAMERA:

        webcam = Pi_WebcamCapture()

        if args.show_camera_config:
            webcam.show_available_configurations()
            sys.exit(0)
    
        webcam.set_camera_configuration(args.camera_config_index)

    else:
        webcam = WebcamCapture()
        print("Parametros de configuración no disponibles para otras camaras distintas a Picamera2. Continuando con ejecución normal")
        
    '''
    webcam = WebcamCapture()
    script_dir = pathlib.Path(__file__).parent.absolute()
    model_path = script_dir / '../../models/saved_model/license-detector_edgetpu.tflite'
    min_detection_confidence = 0.9

    # Variables to avoid logging duplicates
    last_detected_plate = None
    last_detection_time = None
    time_last_detect_threshold = 3

    setup_logger()

    # Create the message dispatcher for communication
    parking_msg_dispatcher = AMQP_Msg_Disp(
            hostname=BaseConfig.AMQP_BROKER_URL,
            port=BaseConfig.AMQP_BROKER_PORT,
            publish_queue_name=BaseConfig.VERIFIER_QUEUE_NAME,
            receive_queue_name=BaseConfig.DETECTOR_QUEUE_NAME,
            msg_handler=detect_msg_handler,
            reply_to_received_message=False,
            stop_consuming_after_received_message=True
        )

    # Create the message dispatcher for communication with screen
    parking_to_screen_msg_dispatcher = MQTT_Msg_Disp(
            hostname=BaseConfig.MQTT_BROKER_URL,
            port=BaseConfig.MQTT_BROKER_PORT,
            publish_topic=BaseConfig.SCREEN_QUEUE_NAME,
            sub_topic=None,
            on_message_callback=None,
            stop_consuming_after_received_message=True
        )

    opened_gate = False

    # Initialize the license plate detector, webcam, and OCR processor
    detector = LicensePlateDetector(str(model_path), min_detection_confidence)
    ocr_processor = OCRProcessor()

    # Initialize pygame for displaying the frames
    pygame.init()
    webcam_feed_window = None

    try:
        while True:
            # Capture a frame from the webcam
            frame = webcam.get_frame()
            
            # Perform license plate detection
            roi, ymin, xmin, ymax, xmax, confidence = detector.detect_license_plate(frame)


            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            if roi is not None:

                #Send message that a plate has been detected
                #update_screen_state("Matrícula detectada, aplicando la lectura", parking_to_screen_msg_dispatcher)

                # Draw the detection label
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

                # Apply OCR to the detected region of interest (ROI)
                detected_plate = ocr_processor.apply_ocr(roi)

                if detected_plate:
                    print(f"Detected Plate: {detected_plate}")

                    current_time = datetime.now(timezone.utc)

                    # Avoid logging the same plate if it was recently detected
                    if ((detected_plate != last_detected_plate or last_detected_plate is None)
                        or ((current_time - last_detection_time).total_seconds() >  time_last_detect_threshold)):
                        
                        #Send message that license has been read
                        update_screen_state(f"Verificando matrícula {detected_plate}", parking_to_screen_msg_dispatcher)

                        # Update the last detected plate
                        last_detected_plate = detected_plate
                        print(f"{detected_plate} will be sent to verifier")

                        timestamp_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

                        # Create the message payload
                        msg_dict = {
                            "plate": detected_plate,
                            "date": timestamp_str
                        }

                        # Convert the message to JSON
                        message = json.dumps(msg_dict)

                        # Send the message to the verifier and wait for a response
                        parking_msg_dispatcher.send_msg(message=message)

                        good_response = False

                        while not good_response:
                            parking_msg_dispatcher.wait_and_receive_msg()
                            response_dict = parking_msg_dispatcher.get_reply_result()
                            print(response_dict["plate"])
                            print(response_dict["allowed"])
                            print(detected_plate)

                            if response_dict["plate"] == detected_plate:
                                opened_gate = response_dict["allowed"]
                                good_response = True

                            
                    else:
                        print(f"Not logging / verifying {detected_plate} again." +
                                f" Gate will remain in same state (Opened = {opened_gate})")
                        
                    if opened_gate:
                            #Send message that car is allowed
                        update_screen_state(f"Matricula {detected_plate} permitida", parking_to_screen_msg_dispatcher)
                        print("Allowed to enter")
                    else:
                        print("Denied to enter")
                        #Send message that car is not allowed
                        update_screen_state(f"Matricula {detected_plate} denegada", parking_to_screen_msg_dispatcher)

                    # Update the last detection time
                    last_detection_time = current_time
                    last_detected_plate = detected_plate
            else:
                #Send message to screen that is waiting for license plate
               update_screen_state("Esperando matricula", parking_to_screen_msg_dispatcher)

            # Convert frame to RGB for pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))

            # Initialize screen if not already initialized
            if webcam_feed_window is None:
                height, width = frame.shape[:2]
                webcam_feed_window = pygame.display.set_mode((width, height))
                pygame.display.set_caption("Detección de Matrículas")

            # Display the frame
            webcam_feed_window.blit(frame_surface, (0, 0))
            pygame.display.flip()

            # Handle events and allow exiting with the 'q' key
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            # Display the frame with the drawn detection
            #cv2.imshow('Frame', frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #break

    except KeyboardInterrupt:
        print("Interrupción manual detectada. Cerrando el programa...")
    except Exception as e:
         print(f"Error inesperado durante el programa: {e}")      

    finally:
        # Release resources and close the application
        webcam.release()
        #cv2.destroyAllWindows()
        pygame.quit()
        parking_msg_dispatcher.close()  # Close the RabbitMQ connection when finished
        parking_to_screen_msg_dispatcher.close()

if __name__ == "__main__":
    main()
