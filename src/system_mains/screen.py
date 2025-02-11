from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sys
import threading
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.msg_disp_factory import MsgDispatcherFactory

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
    hostname = "localhost"
    port=1883
    screen = StatusScreen()

    def handle_message_update(message):
        decoded_message = message.decode()
        screen.update_status(decoded_message)

    msg_dispatcher = MsgDispatcherFactory.create_screen_dispatcher(hostname, port, msg_handler=handle_message_update)
    threading.Thread(target=msg_dispatcher.wait_and_receive_msg, daemon=True).start()
    

    screen.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
