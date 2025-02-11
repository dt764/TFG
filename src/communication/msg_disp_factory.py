# msg_dispatcher_factory.py

from .amqp_msg import AMQP_Msg_Disp
from .mqtt_msg import MQTT_Msg_Disp

class MsgDispatcherFactory:
 
    """

    This class if for creating the messsage dispatcher objects necessary
    for each program. Having this factory ensure consitency with the
    queue / exchange names, and their types.

    """

    VERIFIER_QUEUE_NAME = 'verifier_queue' # The queue between the parking main and the verifier
    DETECTOR_QUEUE_NAME = 'detector_queue' # The queue which the parking main will use to receive messages from the gate main.
    GATE_QUEUE_NAME = 'gate_queue' # The queue which will receive the verification results.
    SCREEN_QUEUE_NAME = 'parking_status'

    """
    Creates the AMQP_Msg_Disp object for the parking main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The AMQP_Msg_Disp object for the parking main.
    """

    @staticmethod
    def create_detector_dispatcher(hostname, port, msg_handler):
        return AMQP_Msg_Disp(
            hostname=hostname,
            port=port,
            publish_queue_name=MsgDispatcherFactory.VERIFIER_QUEUE_NAME,
            receive_queue_name=MsgDispatcherFactory.DETECTOR_QUEUE_NAME,
            msg_handler=msg_handler,
            reply_to_received_message=False,
            stop_consuming_after_received_message=True
        )
    
    """

    Creates the AMQP_Msg_Disp object for the verifier main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The AMQP_Msg_Disp object for the verifier main.

    """

    @staticmethod
    def create_verifier_dispatcher(hostname, port, msg_handler):
        return AMQP_Msg_Disp(
            hostname=hostname,
            port=port,
            publish_queue_name=MsgDispatcherFactory.GATE_QUEUE_NAME,
            receive_queue_name=MsgDispatcherFactory.VERIFIER_QUEUE_NAME,
            msg_handler=msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
        )
    
    """

    Creates the AMQP_Msg_Disp object for the screen main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The AMQP_Msg_Disp object for the screen main.

    """

    @staticmethod
    def create_screen_dispatcher(hostname, port, msg_handler):
        return MQTT_Msg_Disp(
            hostname=hostname,
            port=port,
            publish_topic=None,
            sub_topic=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            on_message_callback=msg_handler,
            stop_consuming_after_received_message=False
        )

        '''
        return AMQP_Msg_Disp(
            hostname=hostname,
            publish_queue_name=None,
            receive_queue_name=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            msg_handler=screen_msg_handler,
            reply_to_received_message=False,
            stop_consuming_after_received_message=False
        )
        '''
    
    """

    Creates the AMQP_Msg_Disp object for the gate main.

    Args:
        hostname (String): The URL / domain name of the message broker.

    Returns:
        The AMQP_Msg_Disp object for the gate main.

    """

    @staticmethod
    def create_gate_dispatcher(hostname, port, msg_handler):
        return AMQP_Msg_Disp(
            hostname=hostname,
            port=port,
            publish_queue_name=MsgDispatcherFactory.DETECTOR_QUEUE_NAME,
            receive_queue_name=MsgDispatcherFactory.GATE_QUEUE_NAME,
            msg_handler=msg_handler,
            stop_consuming_after_received_message=False
        )
    
    @staticmethod
    def create_parking_to_screen_msg_dispatcher(hostname, port, msg_handler):

        return MQTT_Msg_Disp(
            hostname=hostname,
            port=1883,
            publish_topic=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            sub_topic=None,
            on_message_callback=None,
            stop_consuming_after_received_message=True
        )
        '''
        return AMQP_Msg_Disp(
            hostname=hostname,
            publish_queue_name=MsgDispatcherFactory.SCREEN_QUEUE_NAME,
            receive_queue_name=None,
            msg_handler=gate_msg_handler,
            reply_to_received_message=True,
            stop_consuming_after_received_message=False
        )
        '''
