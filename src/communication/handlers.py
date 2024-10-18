# handlers.py

import json
from other_util_classes import door
from other_util_classes import verifier


def verifier_msg_handler(message):

    msg_json = json.loads(message)

    # Extraer los valores del mensaje recibido
    plate = msg_json.get("plate")
    timestamp = msg_json.get("timestamp")
    
    # Verificar si la placa está permitida
    allowed = verifier.save_plate_record_n_verify(timestamp=timestamp, plate=plate)

    # Responder con la misma información más el campo 'allowed'
    reply_dict = {
        "plate": plate,
        "timestamp": timestamp,
        "allowed": allowed
    }

    # Convertir el diccionario de respuesta a una cadena JSON y luego a bytes
    return json.dumps(reply_dict)



def screen_msg_handler(message):
    return json.loads(message)



def gate_msg_handler(message):

    msg_json = json.loads(message)

    is_allowed = msg_json.get("allowed")

    door.change_door_state(is_allowed)
    
    # Verificar si la placa está permitida

    # Responder con la misma información más el campo 'allowed'
    reply_dict = {
        "open_door": is_allowed
  
    }

    # Convertir el diccionario de respuesta a una cadena JSON y luego a bytes
    return json.dumps(reply_dict)


def detect_msg_handler(message):
    msg_json = json.loads(message)

    return msg_json.get("open_door")

