import time
import paho.mqtt.client as mqtt


class MQTT_Msg_Disp:

    def __init__(
            self,
            hostname,
            port,
            publish_topic,
            sub_topic,
            on_message_callback,
            stop_consuming_after_received_message
        ):
        
        self.client = mqtt.Client()
        self.client.connect(hostname, port, 60)

        if(sub_topic is not None):
            self.client.subscribe(sub_topic)
            self.sub_topic = sub_topic

        self.publish_topic = publish_topic
        self.msg_handler = on_message_callback
        self.stop_consuming_after_received_message = stop_consuming_after_received_message


    def send_msg(self, message):
        """
        Sends a message to the configured publish topic.

        Args:
            message (str): The message to be sent.
        """
        if(self.publish_topic is not None):
            self.client.publish(self.publish_topic, payload=message)
        

    def wait_and_receive_msg(self):
        if(self.sub_topic is not None):
            def _on_message_received(client, userdata, msg):
                self.last_reply_result = self.msg_handler(msg.payload)
                if self.stop_consuming_after_received_message:
                    self.message_received = True

            self.client.on_message = _on_message_received
            self.message_received = False
            self.client.loop_start()  # Iniciar el bucle en segundo plano
            
            # Mantener en bucle hasta que se reciba un mensaje
            while not self.message_received:
                time.sleep(0.1)  # Pausa breve para evitar consumir demasiados recursos
            
            self.client.loop_stop()

    def get_reply_result(self):
        """
        Retrieves the last result returned by the message handler. This is used when the MsgDispatcher stops consuming,
        to do more processing with the handled message, before waiting again for more messages.

        Returns:
            Any: The result from the last execution of the msg_handler.
        """
        return self.last_reply_result

    def close(self):
        """

        Closes the connection to broker.

        """
        self.client.disconnect()
