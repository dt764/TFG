# msg_dispatcher_factory.py

from .msg_dispatcher import MsgDispatcher
from .handlers import *

class MsgDispatcherFactory:
 
    """

    This class if for creating the MsgDispatcher objects necessary
    for each program. Having this factory ensure consitency with the
    queue / exchange names, and their types.

    """

    VERIFIER_QUEUE_NAME = 'verifier_queue' # The queue between the parking main and the verifier
    DETECTOR_QUEUE_NAME = 'detector_queue' # The queue which the parking main will use to receive messages from the gate main.
    EXCHANGE_NAME = 'detection_exchange' # The exchange which will receive the verification results.
    SCREEN_QUEUE_NAME = 'parking_status'
    

    """
    Creates the MsgDispatcher object for the parking main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The MsgDispatcher object for the parking main.
    """

    @staticmethod
    def create_detector_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name=MsgDispatcherFactory.VERIFIER_QUEUE_NAME,
            publish_is_fanout=False,
            receive_queue_name=MsgDispatcherFactory.DETECTOR_QUEUE_NAME,
            receive_is_fanout=False,
            msg_handler=detect_msg_handler,
            reply_to_received_message=False,
            stop_consuming_after_received_message=True
        )
    
    """

    Creates the MsgDispatcher object for the verifier main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The MsgDispatcher object for the verifier main.

    """

    @staticmethod
    def create_verifier_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name=MsgDispatcherFactory.EXCHANGE_NAME,
            publish_is_fanout=True,
            receive_queue_name=MsgDispatcherFactory.VERIFIER_QUEUE_NAME,
            receive_is_fanout=False,
            msg_handler=verifier_msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
        )
    
    """

    Creates the MsgDispatcher object for the screen main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The MsgDispatcher object for the screen main.

    """

    @staticmethod
    def create_screen_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name=None,
            publish_is_fanout=False,
            receive_queue_name=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            receive_is_fanout=False,
            msg_handler=screen_msg_handler,
            reply_to_received_message=False,
            stop_consuming_after_received_message=False
        )
    
    """

    Creates the MsgDispatcher object for the gate main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The MsgDispatcher object for the gate main.

    """

    @staticmethod
    def create_gate_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name=MsgDispatcherFactory.DETECTOR_QUEUE_NAME,
            publish_is_fanout=False,
            receive_queue_name=MsgDispatcherFactory.EXCHANGE_NAME,
            receive_is_fanout=True,
            msg_handler=gate_msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
        )
    
    @staticmethod
    def create_parking_to_screen_msg_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            publish_is_fanout=False,
            receive_queue_name=None,
            receive_is_fanout=False,
            msg_handler=gate_msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
        )
