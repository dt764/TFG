# msg_dispatcher_factory.py

from .msg_dispatcher import MsgDispatcher
from .handlers import *

class MsgDispatcherFactory:
    # Definir los nombres de las colas como constantes
    VERIFIER_QUEUE_NAME = 'verifier_queue'
    DETECTOR_QUEUE_NAME = 'detector_queue'
    EXCHANGE_NAME = 'detection_exchange'
    
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
            stop_consumimg_after_received_message=True
        )

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
            stop_consumimg_after_received_message=False
        )

    @staticmethod
    def create_screen_dispatcher(hostname):
        return MsgDispatcher(
            hostname=hostname,
            publish_queue_name='',
            publish_is_fanout=True,
            receive_queue_name='',
            receive_is_fanout=True,
            msg_handler=screen_msg_handler,
            reply_to_received_message=False,
            stop_consumimg_after_received_message=False
        )

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
            stop_consumimg_after_received_message=False
        )
