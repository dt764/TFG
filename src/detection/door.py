import pika
import random
import time

def on_verification_received(ch, method, properties, body):
    result = body.decode()
    print(f"Received verification result: {result}")
    
    if result == 'true':
        # Simulate opening the gate
        open_time = random.uniform(1, 3)  # Simulate opening delay
        time.sleep(open_time)
        print(f"Gate opened for {open_time} seconds")
        ch.basic_publish('', routing_key=properties.reply_to, 
                         body='opened')
    else:
        print("Gate remained closed")
        ch.basic_publish('', routing_key=properties.reply_to, 
                         body='closed')

        
def on_detector_message_received(ch, method, properties, body):
    message = body.decode()
    if message == 'close_gate':
        print("Received message to close the gate.")
        # Simulate closing the gate
        close_time = random.uniform(1, 3)  # Simulate closing delay
        time.sleep(close_time)
        print(f"Gate closed after {close_time} seconds")
        ch.basic_publish('', routing_key=properties.reply_to, 
                         body='closed')
        print("Notified the detector that the gate is closed.")



connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='verifier-to-gate')
channel.queue_declare(queue='detector-to-gate')

channel.basic_consume(queue='verifier-to-gate', auto_ack=True,
                      on_message_callback=on_verification_received)

# Start consuming messages from the detector to close the gate
channel.basic_consume(queue='detector-to-gate', auto_ack=True,
                      on_message_callback=on_detector_message_received)

print("Gate is waiting for verification results...")
channel.start_consuming()
