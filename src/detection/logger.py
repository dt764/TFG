import csv
import os
import datetime
import cv2

class Logger:
    def __init__(self, img_dir ,csv_file='detections.csv'):
        self.csv_file = csv_file
        self.img_dir = img_dir
        os.makedirs(self.img_dir, exist_ok=True)

        if not os.path.isfile(csv_file):
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'License Plate', 'Image Path'])

    def save_detection_to_csv(self, timestamp, plate, image_path):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, plate, image_path])

    def save_image(self, frame, path):
        cv2.imwrite(path, frame)
