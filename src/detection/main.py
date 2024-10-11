import datetime
import pathlib
from license_plate_detector import LicensePlateDetector
from webcam_capture import WebcamCapture
from ocr_processor import OCRProcessor
import cv2
import pika
import json
import uuid
import time

class GateControlSystem:
    def __init__(self):
        # Establecer conexión con RabbitMQ una vez
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Crear una cola exclusiva para respuestas
        self.reply_queue = self.channel.queue_declare(queue='', exclusive=True)

        # Variable para indicar si la puerta está abierta
        self.opened_gate = False
        self.last_no_plate_time = None  # Tiempo cuando no se detecta ninguna matrícula
        self.close_gate_delay = 3  # Retardo en segundos antes de cerrar la puerta

    def send_code_to_verifier(self, code):
        def on_verification_result(ch, method, properties, body):
            result = body.decode()
            print(f"Verification result received: {result}")
            
            if result == 'opened':
                print("Gate is open.")
                self.opened_gate = True  # Solo se cambia el estado si el verificador permite la apertura
            else:
                print("Gate will remain closed (verification failed).")
                self.opened_gate = False  # No abrir si la verificación falla

            ch.stop_consuming()  # Detener el consumo tras recibir la respuesta

        self.channel.basic_consume(queue=self.reply_queue.method.queue, auto_ack=True,
                                   on_message_callback=on_verification_result)

        cor_id = str(uuid.uuid4())
        print(f"Sending detected code: {code}")

        self.channel.basic_publish('', routing_key='detector-to-verifier', 
                                   properties=pika.BasicProperties(
                                       reply_to=self.reply_queue.method.queue,
                                       correlation_id=cor_id
                                   ), 
                                   body=code)

        print("Waiting for verification result...")
        self.channel.start_consuming()  # Bloquea hasta recibir el mensaje de verificación

    def send_close_gate_message(self):
        def on_gate_closed(ch, method, properties, body):
            result = body.decode()
            print(f"Gate status received: {result}")
            
            if result == 'closed':
                print("Gate has been closed.")
                self.opened_gate = False
                ch.stop_consuming()  # Dejar de consumir tras recibir la confirmación de cierre

        self.channel.basic_consume(queue=self.reply_queue.method.queue, auto_ack=True,
                                   on_message_callback=on_gate_closed)

        print("Sending message to close the gate.")
        self.channel.basic_publish('', routing_key='detector-to-gate', 
                                   properties=pika.BasicProperties(
                                       reply_to=self.reply_queue.method.queue
                                   ), 
                                   body='close_gate')

        print("Waiting for gate closed confirmation...")
        self.channel.start_consuming()  # Esperar hasta recibir el mensaje de puerta cerrada

    def close(self):
        # Método para cerrar correctamente la conexión
        if self.connection:
            self.connection.close()


def main():
    script_dir = pathlib.Path(__file__).parent.absolute()
    model_path = script_dir / '../../models/saved_model/license-detector_edgetpu.tflite'
    min_detection_confidence = 0.9

    # Variables para evitar loggear duplicados
    last_detected_plate = None
    last_detection_time = None
    time_last_detect_threshold = 3
    gate_control_system = GateControlSystem()

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
                    if (not gate_control_system.opened_gate):
                        if (detected_plate != last_detected_plate or last_detected_plate is None):

                            # Actualizar última detección
                            last_detected_plate = detected_plate

                            print(f"Logging {detected_plate} into csv")

                            timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')

                            message_object = {
                                "matricula": detected_plate,
                                "timestamp": timestamp_str,
                            }

                            # Convertir el objeto a JSON
                            message = json.dumps(message_object)

                            gate_control_system.send_code_to_verifier(message)
                            gate_control_system.last_no_plate_time = None  # Resetear el tiempo sin matrícula

                        else:
                            time_since_last_detection = (current_time - last_detection_time).total_seconds()
                            if time_since_last_detection < time_last_detect_threshold:
                                print(f"Not logging / verifying {detected_plate} again. Gate will remain in same state (Opened = {gate_control_system.opened_gate})")

                    else:
                        if (detected_plate != last_detected_plate or last_detected_plate is None):
                            print(f"Different license plate detected while gate is opened. Closing the gate.")
                            gate_control_system.send_close_gate_message()
                        else:
                             print(f"Not logging / verifying {detected_plate} again. Gate will remain in same state (Opened = {gate_control_system.opened_gate})")


                    last_detection_time = current_time
                        
            else:
                # No se ha detectado una matrícula
                if gate_control_system.opened_gate:
                    if gate_control_system.last_no_plate_time is None:
                        gate_control_system.last_no_plate_time = time.time()  # Comenzar el temporizador
                    elif (time.time() - gate_control_system.last_no_plate_time) > gate_control_system.close_gate_delay:
                        print(f"No license plate detected for {gate_control_system.close_gate_delay} seconds. Closing the gate.")
                        gate_control_system.send_close_gate_message()
                        gate_control_system.last_no_plate_time = None  # Reiniciar el temporizador
            
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        gate_control_system.close()  # Cerrar la conexión RabbitMQ al finalizar

if __name__ == "__main__":
    main()
