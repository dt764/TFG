class BaseConfig:
    AMQP_BROKER_URL="localhost"
    AMQP_BROKER_PORT=5672
    MQTT_BROKER_URL="localhost"
    MQTT_BROKER_PORT=1883
    SCREEN_QUEUE_NAME="screen_queue"
    GATE_QUEUE_NAME="gate_queue"
    DETECTOR_QUEUE_NAME="detector_queue"
    VERIFICATION_QUEUE_NAME="verification_queue"
    API_URL="http://localhost:5000/vefify_plate"
    USE_PI_CAMERA=False