import datetime
import pathlib
import cv2
import json
import sys
import os
import pygame
import numpy as np

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from other_util_classes.license_plate_detector import LicensePlateDetector
from other_util_classes.webcam_capture import WebcamCapture
from other_util_classes.ocr_processor import OCRProcessor
from communication.msg_disp_factory import MsgDispatcherFactory

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
        
    script_dir = pathlib.Path(__file__).parent.absolute()
    model_path = script_dir / '../../models/saved_model/license-detector_edgetpu.tflite'
    min_detection_confidence = 0.9

    # Variables to avoid logging duplicates
    last_detected_plate = None
    last_detection_time = None
    time_last_detect_threshold = 3

    # Create the message dispatcher for communication
    parking_msg_dispatcher = MsgDispatcherFactory.create_detector_dispatcher(
        hostname='localhost'
    )

    # Create the message dispatcher for communication with screen
    parking_to_screen_msg_dispatcher =  MsgDispatcherFactory.create_parking_to_screen_msg_dispatcher(
        hostname='localhost'
    )

    opened_gate = False

    # Initialize the license plate detector, webcam, and OCR processor
    detector = LicensePlateDetector(str(model_path), min_detection_confidence)
    webcam = WebcamCapture()
    ocr_processor = OCRProcessor()

    # Initialize pygame for displaying the frames
    pygame.init()
    screen = None

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

                    current_time = datetime.datetime.now()

                    # Avoid logging the same plate if it was recently detected
                    if ((detected_plate != last_detected_plate or last_detected_plate is None)
                        or ((current_time - last_detection_time).total_seconds() >  time_last_detect_threshold)):
                        
                        #Send message that license has been read
                        update_screen_state(f"Verificando matrícula {detected_plate}", parking_to_screen_msg_dispatcher)

                        # Update the last detected plate
                        last_detected_plate = detected_plate
                        print(f"{detected_plate} will be sent to verifier")

                        timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')

                        # Create the message payload
                        msg_dict = {
                            "plate": detected_plate,
                            "timestamp": timestamp_str
                        }

                        # Convert the message to JSON
                        message = json.dumps(msg_dict)

                        # Send the message to the verifier and wait for a response
                        parking_msg_dispatcher.send_msg(message=message)
                        parking_msg_dispatcher.wait_and_receive_msg()
                        opened_gate = parking_msg_dispatcher.get_reply_result()
                            
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
            if screen is None:
                screen = pygame.display.set_mode((frame.shape[1], frame.shape[0]))

            # Display the frame
            screen.blit(frame_surface, (0, 0))
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

if __name__ == "__main__":
    main()
