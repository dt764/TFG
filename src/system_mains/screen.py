from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sys
import threading
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.msg_disp_factory import MsgDispatcherFactory

class StatusScreen(QMainWindow):
    def __init__(self, hostname):
        super().__init__()
        self.setWindowTitle("Pantalla de Estado del Parking")
        self.status_label = QLabel("Esperando estado...", self)
        self.status_label.setGeometry(50, 50, 300, 50)
        
        # Crear el dispatcher
        self.msg_dispatcher = MsgDispatcherFactory.create_screen_dispatcher(hostname)
        
        # Hilo para esperar mensajes en el background
        threading.Thread(target=self.msg_dispatcher.wait_and_receive_msg, daemon=True).start()

    def update_status(self, status):
        self.status_label.setText(status)

# Código principal de la aplicación
def main():
    app = QApplication(sys.argv)
    hostname = "localhost"  # o el hostname de tu RabbitMQ
    screen = StatusScreen(hostname)

    # Configura la actualización en el callback de mensajes
    def handle_message_update(message):
        decoded_message = message.decode()  # Decodificar si es necesario
        screen.update_status(decoded_message)

    screen.msg_dispatcher.msg_handler = handle_message_update

    screen.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
