import pika
from pika.exchange_type import ExchangeType

class MsgDispatcher:
    def __init__(
            self, hostname,
            publish_queue_name, publish_is_fanout,
            receive_queue_name, receive_is_fanout,
            msg_handler, stop_consumimg_after_received_message,
            reply_to_received_message
        ):
        
        # Establecer conexión con RabbitMQ una vez
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(hostname)
        )
        
        self.channel = self.connection.channel()

        self.publish_queue_name = publish_queue_name
        self.receive_queue_name = receive_queue_name

        self.publish_is_fanout = publish_is_fanout
        self.receive_is_fanout = receive_is_fanout

        if(publish_is_fanout):
            self.channel.exchange_declare(
                exchange=self.publish_queue_name, exchange_type=ExchangeType.fanout)
        else:
            self.channel.queue_declare(queue=self.publish_queue_name)

        if(receive_is_fanout):

            self.channel.exchange_declare(
                exchange=self.receive_queue_name, exchange_type=ExchangeType.fanout)
    
            self.queue = self.channel.queue_declare(queue='', exclusive=True)

            self.channel.queue_bind(
                exchange=self.receive_queue_name, queue=self.queue.method.queue)
            
            self.channel.basic_consume(
                queue=self.queue.method.queue,
                on_message_callback=self._on_message_received)
        else:
            self.channel.queue_declare(queue=self.receive_queue_name)
            self.channel.basic_consume(
                queue=self.receive_queue_name,
                on_message_callback=self._on_message_received)

        self.msg_handler = msg_handler
        self.stop_consuming_after_received_msg = stop_consumimg_after_received_message
        self.reply_to_received_msg = reply_to_received_message

        self.last_reply_result = None


    def send_msg(self, message):
        if(self.publish_is_fanout):
            self.channel.basic_publish(
                exchange=self.publish_queue_name, routing_key='', body=message)
        else:
            self.channel.basic_publish(
                exchange='', routing_key=self.publish_queue_name, body=message)


    def _on_message_received(
            self, ch, method, properties, body,
            ):
        
        print(f"Mensaje recibido: {body}")
        
        if self.stop_consuming_after_received_msg:
            ch.stop_consuming()  # Detener el consumo tras recibir la respuesta

        ch.basic_ack(delivery_tag=method.delivery_tag)

        self.last_reply_result = self.msg_handler(body)

        if self.reply_to_received_msg:
            self.send_msg(self.last_reply_result)

    
    def get_reply_result(self):
        return self.last_reply_result
        

    def wait_and_receive_msg(self):
        self.channel.start_consuming()

    def close(self):
        if self.connection:
            self.connection.close()
