# handlers.py

import json
from other_util_classes import door
from other_util_classes import verifier


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

    msg_json = json.loads(message)

    plate = msg_json.get("plate")
    timestamp = msg_json.get("timestamp")
    
    allowed = verifier.save_plate_record_n_verify(timestamp=timestamp, plate=plate)

    reply_dict = {
        "plate": plate,
        "timestamp": timestamp,
        "allowed": allowed
    }

    return json.dumps(reply_dict)



def screen_msg_handler(message):
    # Decodifica el mensaje si está en JSON o string
    decoded_message = message.decode()  # Si el mensaje está en bytes
    print(f"Mensaje para la pantalla recibido: {decoded_message}")
    # Aquí podrías actualizar el estado en la interfaz o loguearlo
    return decoded_message



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

    msg_json = json.loads(message)

    is_allowed = msg_json.get("allowed")

    door.change_door_state(is_allowed)
    

    # Make the reply for the gate

    reply_dict = {
        "open_door": is_allowed
  
    }

    return json.dumps(reply_dict)


def detect_msg_handler(message):
    """
    Handles messages for detecting if the door should open.

    This function extracts the 'open_door' field from the received message.

    Args:
        message (bytes): The received message as a byte string in JSON format.

    Returns:
        bool: The value of the 'open_door' field, indicating if the door should be opened.
    """

    msg_json = json.loads(message)

    #The parking main doesnt reply after receiving the message, it just needs to know if the door is open.

    return msg_json.get("open_door")

