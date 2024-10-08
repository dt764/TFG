import csv
import os
import pathlib
import pika
import json


script_dir = pathlib.Path(__file__).parent.absolute()
csv_file = script_dir / '../../detections.csv'
img_dir = script_dir / '../../detections_img'

def save_plate_record(ch, method, properties, body):

    message_object = json.loads(body)

    detected_plate = message_object['matricula']
    timestamp = message_object['timestamp']

    print(f" [x] Received {message_object}")
    print(f"Matricula: {detected_plate}")
    print(f"Matricula: {timestamp}")

        
    with open(csv_file, mode='a', newline='') as file:

        writer = csv.writer(file)

        image_path = img_dir / f'{timestamp}_{detected_plate}.jpg'

        writer.writerow([timestamp, detected_plate, image_path])


def main():

    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'License Plate', 'Image Path'])

    connection_parameters = pika.ConnectionParameters('localhost')

    connection = pika.BlockingConnection(connection_parameters)

    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    queue = channel.queue_declare(queue='', exclusive=True)

    channel.queue_bind(exchange='logs', queue=queue.method.queue)

    channel.basic_consume(queue=queue.method.queue, auto_ack=True,
        on_message_callback=save_plate_record)

    print("Starting Consuming")

    channel.start_consuming()
        

if __name__ == "__main__":
    main()