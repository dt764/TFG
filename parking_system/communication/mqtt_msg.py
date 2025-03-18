import time
import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)


class MQTT_Msg_Disp:
    def __init__(
        self,
        hostname,
        port,
        publish_topic=None,
        sub_topic=None,
        on_message_callback=None,
        stop_consuming_after_received_message=False
    ):
        self.hostname = hostname
        self.port = port
        self.publish_topic = publish_topic
        self.sub_topic = sub_topic
        self.msg_handler = on_message_callback
        self.stop_consuming_after_received_message = stop_consuming_after_received_message
        self.message_received = False
        self.last_reply_result = None

        self.client = mqtt.Client()

        # Set callbacks
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        if self.msg_handler:
            self.client.on_message = self._on_message_received

        try:
            self.client.connect(self.hostname, self.port, keepalive=60)
            logger.info(f"Connected to MQTT broker at {self.hostname}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

        self.client.loop_start()

        if self.sub_topic:
            self.client.subscribe(self.sub_topic)
            logger.info(f"Subscribed to topic: {self.sub_topic}")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker (code: {rc})")
        else:
            logger.info("Disconnected from MQTT broker.")

    def _on_publish(self, client, userdata, mid):
        logger.debug(f"Message published (mid: {mid})")

    def _on_message_received(self, client, userdata, msg):
        logger.info(f"Message received on topic '{msg.topic}': {msg.payload}")
        if self.msg_handler:
            self.last_reply_result = self.msg_handler(msg.payload)
        if self.stop_consuming_after_received_message:
            self.message_received = True

    def send_msg(self, message):
        """
        Sends a message to the configured publish topic.
        """
        if self.publish_topic:
            result = self.client.publish(self.publish_topic, payload=message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Message sent to topic '{self.publish_topic}': {message}")
            else:
                logger.warning(f"Failed to publish message (code: {result.rc})")
        else:
            logger.warning("No publish topic configured.")

    def wait_and_receive_msg(self):
        """
        Waits until a message is received (if stop_consuming_after_received_message=True).
        """
        if self.sub_topic:
            logger.debug("Waiting for message...")
            while not self.message_received:
                time.sleep(0.1)

    def get_reply_result(self):
        return self.last_reply_result

    def close(self):
        """
        Stops the MQTT client loop and disconnects from the broker.
        """
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT connection closed.")
