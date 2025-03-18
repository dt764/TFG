import sys
import os
import json

# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from parking_system.base_config import BaseConfig
from parking_system.communication.amqp_msg import AMQP_Msg_Disp
from logging_module.logger_setup import setup_logger



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

    is_allowed = msg_json.get("allowed")
    matricula = msg_json.get("plate")

    change_door_state(is_allowed)
    

    # Make the reply for the gate

    reply_dict = {
        "plate": matricula,
        "allowed": is_allowed
  
    }

    print(json.dumps(reply_dict))

    return json.dumps(reply_dict)

def main():
    try:
        setup_logger()

        gate_msg_dispatcher = AMQP_Msg_Disp(
            hostname=BaseConfig.AMQP_BROKER_URL,
            port=BaseConfig.AMQP_BROKER_PORT,
            publish_queue_name=BaseConfig.DETECTOR_QUEUE_NAME,
            receive_queue_name=BaseConfig.GATE_QUEUE_NAME,
            reply_to_received_message=True,
            msg_handler=gate_msg_handler,
            stop_consuming_after_received_message=False
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
