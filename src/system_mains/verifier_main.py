import sys
import os

# Agrega el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.msg_disp_factory import MsgDispatcherFactory

def main():
    try:

        verifier_msg_dispatcher = MsgDispatcherFactory.create_verifier_dispatcher(
            hostname='localhost'
        )
        
        verifier_msg_dispatcher.wait_and_receive_msg()


    except KeyboardInterrupt:
        print("\nInterrupción manual detectada. Cerrando el programa...")
    except Exception as e:
         print(f"Error inesperado durante el programa: {e}")      

    finally:
        # Release resources and close the application
        verifier_msg_dispatcher.close()  # Close the RabbitMQ connection when finished

if __name__ == "__main__":
    main()
