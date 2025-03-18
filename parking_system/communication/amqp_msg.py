import pika
import logging
from pika.exchange_type import ExchangeType
import time


class AMQP_Msg_Disp:

    """
    Class to manage communication with RabbitMQ, both for sending and receiving messages.

    It allows setting up queues or fanout exchanges and handling received messages with a
    custom handler. It can also be configured to reply to received messages and stop consuming 
    after receiving a message.

    Args:
        hostname (str): The RabbitMQ server's hostname or IP address.
        publish_queue_name (str): The name of the queue or exchange for publishing messages.
        receive_queue_name (str): The name of the queue or exchange for receiving messages.
        msg_handler (callable): Function to handle received messages.
        stop_consuming_after_received_message (bool): If True, stops consuming (or waiting for messages) after receiving a message. This is used when some other processing needs to be done before waiting for another message
        reply_to_received_message (bool): If True, replies to the received message.

    Attributes:
        connection (pika.BlockingConnection): Connection to RabbitMQ.
        channel (pika.BlockingChannel): Channel for communicating with RabbitMQ.
        publish_queue_name (str): Name of the queue or exchange for publishing messages.
        receive_queue_name (str): Name of the queue or exchange for receiving messages.
        queue (pika.spec.Queue): Queue for receiving messages when using fanout exchange.
        msg_handler (callable): Function to handle received messages.
        stop_consuming_after_received_msg (bool): If True, stops consuming (or waiting for messages) after receiving a message.  
        reply_to_received_msg (bool): If True, replies to the received message.
        last_reply_result (Any): The last result returned by the msg_handler function.
    """


    def __init__(
            self, hostname, port,
            publish_queue_name,
            receive_queue_name,
            msg_handler, stop_consuming_after_received_message,
            reply_to_received_message
        ):

        self.msg_handler = msg_handler

        # This is used
        self.stop_consuming_after_received_msg = stop_consuming_after_received_message
        self.reply_to_received_msg = reply_to_received_message

        self.last_reply_result = None

        self.hostname = hostname
        self.port = port

         # This could be the name of the exchange, if it is of type fanout
        self.publish_queue_name = publish_queue_name
        self.receive_queue_name = receive_queue_name
        
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info("Iniciando MsgDispatcher...")

        # Establish connection
        self.__reconnect()
        


    def __reconnect(self):

        max_retries = 5
        retry_delay = 2
        attempt = 0
        while attempt < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.hostname,
                        port=self.port,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                self.logger.info("Conexión a RabbitMQ establecida con éxito.")
                self.__setup_queues()
                return
            except pika.exceptions.AMQPConnectionError as e:
                attempt += 1
                self.logger.warning(f"Error al intentar reconectar con RabbitMQ: {e}. Intento {attempt} de {max_retries}.")
                time.sleep(retry_delay)
        self.logger.error("No se pudo establecer la conexión después de varios intentos.")
        raise Exception("No se pudo conectar a RabbitMQ después de varios intentos")

    def __setup_queues(self):
        if self.publish_queue_name:
            self.channel.queue_declare(queue=self.publish_queue_name)
        if self.receive_queue_name:
            self.channel.queue_declare(queue=self.receive_queue_name)




    def send_msg(self, message):
        """
        Sends a message to the configured queue or exchange with retries.

        Args:
            message (str): The message to be sent.

        Raises:
            Exception: If the message cannot be sent after retries.
        """
        max_retries = 3
        retry_delay = 1  # Seconds to delay to next try
        attempt = 0
        sent = False

        while not sent and attempt <= max_retries:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.publish_queue_name,
                    body=message)
                
                sent = True
                self.logger.info(f"Mensaje enviado exitosamente: {message}")

            except pika.exceptions.AMQPConnectionError as e:
                attempt += 1
                self.logger.warning(f"Error de conexión al enviar mensaje: {e}. Intento {attempt} de {max_retries}.")

                if attempt <= max_retries:
                    self.logger.info(f"Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                    self.__reconnect()  # Intentar reconectar antes del próximo intento
                else:
                    self.logger.error(f"No se pudo enviar el mensaje después de {max_retries} intentos.")
                    raise Exception("Fallo al enviar el mensaje después de múltiples intentos") from e




    def _on_message_received(
            self, ch, method, properties, body,
            ):
        
        """
        Handles the receipt of a message.

        Args:
            ch (BlockingChannel): The communication channel.
            method (pika.spec.Basic.Deliver): Delivery method.
            properties (pika.spec.BasicProperties): Message properties.
            body (bytes): The body of the received message.
        """
        
        self.logger.info(f"Mensaje recibido: {body}")
        # Every program that uses this type of object may have a different way of handling messages.
        # E.g. The parking waits and handles a different message compared to the gate program.
        # The result is assigned to the atribute, to get it later, and more work with it.

        print("asignando last reply result")
        self.last_reply_result = self.msg_handler(body)

        if self.reply_to_received_msg:
            self.send_msg(self.last_reply_result)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.logger.debug("Mensaje procesado y reconocido.")

        if self.stop_consuming_after_received_msg:
            # This is needed when the program has to do something else after handling the message.
            # This is the case for the parking main, where it needs to do more more work after receiving and processing the message.
            # Another solution would be to create another thread for this, but this solution hasnt been studied yet.
            ch.stop_consuming()
            self.logger.info("Consumo detenido tras procesar el mensaje.")

    
    def get_reply_result(self):
        """
        Retrieves the last result returned by the message handler. This is used when the MsgDispatcher stops consuming,
        to do more processing with the handled message, beforw waiting again for more messages.

        Returns:
            Any: The result from the last execution of the msg_handler.
        """
        return self.last_reply_result

        

    def wait_and_receive_msg(self):
        """
        Starts waiting to receive messages.
        """

        max_retries = 5
        retry_delay = 2  # Retraso en segundos entre reintentos
        attempt = 0
        received = False

        self.channel.basic_consume(
            queue=self.receive_queue_name,
            on_message_callback=self._on_message_received
        )

        while not received and attempt <= max_retries:
            try:
                self.logger.info("Esperando mensajes...")
                self.channel.start_consuming()
                received = True
            except pika.exceptions.AMQPConnectionError as e:
                    attempt += 1
                    self.logger.warning(f"Error de conexión al enviar mensaje: {e}. Intento {attempt} de {max_retries}.")

                    if attempt <= max_retries:
                        self.logger.info(f"Reintentando en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        self.__reconnect()  # Intentar reconectar antes del próximo intento
                    else:
                        self.logger.error(f"No se pudo enviar el mensaje después de {max_retries} intentos.")
                        raise Exception("Fallo al enviar el mensaje después de múltiples intentos") from e
            except pika.exceptions.AMQPChannelError as e:
                    self.logger.error(f"Error en el canal: {e}")


    def close(self):
        """

        Closes the connection to RabbitMQ.

        """
        self.logger.info("Intentando cerrar conexión...")
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.logger.info("Conexion cerrada.")
        else:
            self.logger.info("La conexión ya estaba cerrada o es inválida.")
