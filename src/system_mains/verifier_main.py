import sys
import os

# Agrega el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.msg_disp_factory import MsgDispatcherFactory

def main():

    verifier_msg_dispatcher = MsgDispatcherFactory.create_verifier_dispatcher(
        hostname='localhost'
    )
     
    verifier_msg_dispatcher.wait_and_receive_msg()

if __name__ == "__main__":
    main()
