import sys
import os
import logging
import logging.config
import yaml
import pathlib
import json
import pathlib
import requests
import traceback


# Agrega el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.msg_disp_factory import MsgDispatcherFactory

url = "http://localhost:5000/verificar_matricula"

def verifier_msg_handler(message):

    """
    Handles messages for the verifier, checking if the license plate is allowed.

    This function processes the received message, extracts the license plate and 
    timestamp, verifies if the plate is allowed, and returns a JSON-formatted response 
    containing the original data along with the verification result.

    Args:
        message (bytes): The received message as a byte string in JSON format.

    Returns:
        str: A JSON-formatted string containing the plate, timestamp, and allowed status.
    """


    msg_json = json.loads(message.decode("utf-8"))
    print(msg_json)

    response = requests.post(url, json=msg_json)
    
    return json.dumps(response.json())




def main():

    script_dir = pathlib.Path(__file__).parent.absolute()
    logger_path = script_dir / './logger_config.yaml'

    # Cargar la configuración del archivo YAML
    with open(logger_path, "r") as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    # API URL


    try:

        verifier_msg_dispatcher = MsgDispatcherFactory.create_verifier_dispatcher(
            hostname='localhost',
            msg_handler=verifier_msg_handler
        )
        
        verifier_msg_dispatcher.wait_and_receive_msg()


    except KeyboardInterrupt:
        print("\nInterrupción manual detectada. Cerrando el programa...")
    except Exception as e:
         print(f"Error inesperado durante el programa: {e}")  
         print(traceback.format_exc())    

    finally:
        # Release resources and close the application
        verifier_msg_dispatcher.close()  # Close the RabbitMQ connection when finished

if __name__ == "__main__":
    main()
