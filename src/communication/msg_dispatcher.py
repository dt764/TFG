import pika
from pika.exchange_type import ExchangeType

class MsgDispatcher:

    """
    Class to manage communication with RabbitMQ, both for sending and receiving messages.

    It allows setting up queues or fanout exchanges and handling received messages with a
    custom handler. It can also be configured to reply to received messages and stop consuming 
    after receiving a message.

    Args:
        hostname (str): The RabbitMQ server's hostname or IP address.
        publish_queue_name (str): The name of the queue or exchange for publishing messages.
        publish_is_fanout (bool): If True, a fanout exchange is set up for publishing.
        receive_queue_name (str): The name of the queue or exchange for receiving messages.
        receive_is_fanout (bool): If True, a fanout exchange is set up for receiving.
        msg_handler (callable): Function to handle received messages.
        stop_consuming_after_received_message (bool): If True, stops consuming (or waiting for messages) after receiving a message. This is used when some other processing needs to be done before waiting for another message
        reply_to_received_message (bool): If True, replies to the received message.

    Attributes:
        connection (pika.BlockingConnection): Connection to RabbitMQ.
        channel (pika.BlockingChannel): Channel for communicating with RabbitMQ.
        publish_queue_name (str): Name of the queue or exchange for publishing messages.
        receive_queue_name (str): Name of the queue or exchange for receiving messages.
        publish_is_fanout (bool): If True, the publish exchange is a fanout type.
        receive_is_fanout (bool): If True, the receive exchange is a fanout type.
        queue (pika.spec.Queue): Queue for receiving messages when using fanout exchange.
        msg_handler (callable): Function to handle received messages.
        stop_consuming_after_received_msg (bool): If True, stops consuming (or waiting for messages) after receiving a message.  
        reply_to_received_msg (bool): If True, replies to the received message.
        last_reply_result (Any): The last result returned by the msg_handler function.
    """


    def __init__(
            self, hostname,
            publish_queue_name, publish_is_fanout,
            receive_queue_name, receive_is_fanout,
            msg_handler, stop_consuming_after_received_message,
            reply_to_received_message
        ):
        
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(hostname)
        )
        
        self.channel = self.connection.channel()

        # This could be the name of the exchange, if it is of type fanout
        self.publish_queue_name = publish_queue_name
        self.receive_queue_name = receive_queue_name

        # It is needed to know if the exchange / queue is fanaout,
        # since the way to declare and create them is different from one another
        self.publish_is_fanout = publish_is_fanout
        self.receive_is_fanout = receive_is_fanout

        if(self.publish_queue_name is not None):
            if(publish_is_fanout):
                # When its fanout, you need to declare the exchange, with the specified name.
                self.channel.exchange_declare(
                    exchange=self.publish_queue_name, exchange_type=ExchangeType.fanout)
            else:
                # When its not, a queue is created
                self.channel.queue_declare(queue=self.publish_queue_name)


        # Its the same thing for the receive exchange / queue.
        if(self.receive_queue_name is not None):
            if(receive_is_fanout):

                # When its fanout, you declare the exchange and bind a temporary queue to the exchange.

                self.channel.exchange_declare(
                    exchange=self.receive_queue_name, exchange_type=ExchangeType.fanout)
        
                self.queue = self.channel.queue_declare(queue='', exclusive=True)

                self.channel.queue_bind(
                    exchange=self.receive_queue_name, queue=self.queue.method.queue)
                
                self.channel.basic_consume(
                    queue=self.queue.method.queue,
                    on_message_callback=self._on_message_received)
            else:

                #If not, a queue is declared with the specified name.
                self.channel.queue_declare(queue=self.receive_queue_name)
                self.channel.basic_consume(
                    queue=self.receive_queue_name,
                    on_message_callback=self._on_message_received)

        self.msg_handler = msg_handler

        # This is used
        self.stop_consuming_after_received_msg = stop_consuming_after_received_message
        self.reply_to_received_msg = reply_to_received_message

        self.last_reply_result = None


    def send_msg(self, message):
        """
        Sends a message to the configured queue or exchange.

        Args:
            message (str): The message to be sent.
        """
        
        if(self.publish_is_fanout):
            self.channel.basic_publish(
                exchange=self.publish_queue_name, routing_key='', body=message)
        else:
            self.channel.basic_publish(
                exchange='', routing_key=self.publish_queue_name, body=message)


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
        
        print(f"Mensaje recibido: {body}")
        

        if self.stop_consuming_after_received_msg:
            # This is needed when the program has to do something else after handling the message.
            # This is the case for the parking main, where it needs to do more more work after receiving and processing the message.
            # Another solution would be to create another thread for this, but this solution hasnt been studied yet.
            ch.stop_consuming() 

        ch.basic_ack(delivery_tag=method.delivery_tag)

        # Every program that uses this type of object may have a different way of handling messages.
        # E.g. The parking waits and handles a different message compared to the gate program.
        # The result is assigned to the atribute, to get it later, and more work with it.

        self.last_reply_result = self.msg_handler(body)

        if self.reply_to_received_msg:
            self.send_msg(self.last_reply_result)

    
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

        Starts wating to receive messages.

        """
        self.channel.start_consuming()

    def close(self):
        """

        Closes the connection to RabbitMQ.

        """
        if self.connection:
            self.connection.close()
