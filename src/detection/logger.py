import csv
import os
import datetime
import cv2

class Logger:
    def __init__(self, img_dir ,csv_file):
        self.csv_file = csv_file
        self.img_dir = img_dir
        os.makedirs(self.img_dir, exist_ok=True)

        if not os.path.isfile(csv_file):
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'License Plate', 'Image Path'])

    def save_detection_to_csv(self, detected_plate, timestamp, frame):
        with open(self.csv_file, mode='a', newline='') as file:

            writer = csv.writer(file)

            timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
            image_path = self.img_dir / f'{timestamp_str}_{detected_plate}.jpg'

            writer.writerow([timestamp_str, detected_plate, image_path])

            cv2.imwrite(image_path, frame)