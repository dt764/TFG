class ScreenMessageKey:
    DETECTING = "DETECTING"
    READING = "READING"
    VERIFYING = "VERIFYING"
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    OCR_FAIL = "OCR_FAIL"
    WAITING = "WAITING"


class BaseConfig:
    AMQP_BROKER_URL="localhost"
    AMQP_BROKER_PORT=5672

    MQTT_BROKER_URL="localhost"
    MQTT_BROKER_PORT=1883

    SCREEN_QUEUE_NAME="screen_queue"
    GATE_QUEUE_NAME="gate_queue"
    DETECTOR_QUEUE_NAME="detector_queue"
    VERIFIER_QUEUE_NAME="verification_queue"

    DETECTION_MIN_CONFIDENCE=0.9
    OCR_MIN_CONFIDENCE=0.9

    API_URL="http://localhost:5000/verify_plate"
    API_KEY="secret-api-key"

    USE_PI_CAMERA=False

    SCREEN_MESSAGES = {
        ScreenMessageKey.DETECTING: "Esperando matrícula",
        ScreenMessageKey.READING: "Matrícula detectada, aplicando la lectura",
        ScreenMessageKey.VERIFYING: "Verificando matrícula {plate}",
        ScreenMessageKey.ALLOWED: "Matrícula {plate} permitida",
        ScreenMessageKey.DENIED: "Matrícula {plate} denegada",
        ScreenMessageKey.OCR_FAIL: "No se ha podido leer la matrícula, intente ponerse en una posición mejor",
        ScreenMessageKey.WAITING: "Esperando a sistema de detección..."
    }