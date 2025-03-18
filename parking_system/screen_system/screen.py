from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sys
import threading
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from parking_system.base_config import BaseConfig
from parking_system.communication.mqtt_msg import MQTT_Msg_Disp
from logging_module.logger_setup import setup_logger


class StatusScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pantalla de Estado del Parking")
        self.status_label = QLabel("Esperando estado...", self)
        self.status_label.setGeometry(50, 50, 300, 50)
    
    def update_status(self, message):
        self.status_label.setText(message)



def main():
    app = QApplication(sys.argv)
    screen = StatusScreen()

    setup_logger()

    def handle_message_update(message):
        decoded_message = message.decode()
        screen.update_status(decoded_message)

    msg_dispatcher = MQTT_Msg_Disp(
            hostname=BaseConfig.AMQP_BROKER_URL,
            port=BaseConfig.AMQP_BROKER_PORT,
            publish_topic=None,
            sub_topic=BaseConfig.SCREEN_QUEUE_NAME,
            on_message_callback=handle_message_update,
            stop_consuming_after_received_message=False
        )
    threading.Thread(target=msg_dispatcher.wait_and_receive_msg, daemon=True).start()
    

    screen.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
