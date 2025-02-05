import sys
import os
import logging
import logging.config
import yaml
import pathlib
import json

# Agrega el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from communication.msg_disp_factory import MsgDispatcherFactory

def change_door_state(state):
    print(state)

def gate_msg_handler(message):

    """
    Handles messages for controlling the gate.

    This function processes the received message to determine if the door should be opened 
    or closed based on the 'allowed' field, updates the door's state, and returns a response 
    indicating the door state.

    Args:
        message (bytes): The received message as a byte string in JSON format.

    Returns:
        str: A JSON-formatted string containing the door state.
    """

    msg_json = json.loads(message.decode("utf-8"))

    is_allowed = msg_json.get("pertenece")
    matricula = msg_json.get("matricula")

    change_door_state(is_allowed)
    

    # Make the reply for the gate

    reply_dict = {
        "matricula": matricula,
        "permitido": is_allowed
  
    }

    print(json.dumps(reply_dict))

    return json.dumps(reply_dict)

def main():

    script_dir = pathlib.Path(__file__).parent.absolute()
    logger_path = script_dir / './logger_config.yaml'

    # Cargar la configuración del archivo YAML
    with open(logger_path, "r") as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)


    try:

        gate_msg_dispatcher = MsgDispatcherFactory.create_gate_dispatcher(
            hostname='localhost',
            msg_handler=gate_msg_handler
        )
        
        gate_msg_dispatcher.wait_and_receive_msg()

    except KeyboardInterrupt:
        print("\nInterrupción manual detectada. Cerrando el programa...")
    except Exception as e:
         print(f"Error inesperado durante el programa: {e}")      

    finally:
        # Release resources and close the application
        gate_msg_dispatcher.close()  # Close the RabbitMQ connection when finished

if __name__ == "__main__":
    main()
