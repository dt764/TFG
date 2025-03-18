import sys
import os
import json
import requests
import traceback

# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from logging_module.logger_setup import setup_logger
from parking_system.base_config import BaseConfig
from parking_system.communication.amqp_msg import AMQP_Msg_Disp


url = BaseConfig.API_URL

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

    headers = {
        "API-KEY": BaseConfig.API_KEY  # Asegúrate de definir esto en tu config
    }

    response = requests.post(url, json=msg_json, headers=headers)

    # Lanza excepción si el código de estado no indica éxito (2xx)
    if not response.ok:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

    return json.dumps(response.json())


def main():

    try:
        setup_logger()

        verifier_msg_dispatcher = AMQP_Msg_Disp(
            hostname=BaseConfig.AMQP_BROKER_URL,
            port=BaseConfig.AMQP_BROKER_PORT,
            publish_queue_name=BaseConfig.GATE_QUEUE_NAME,
            receive_queue_name=BaseConfig.VERIFIER_QUEUE_NAME,
            msg_handler=verifier_msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
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
