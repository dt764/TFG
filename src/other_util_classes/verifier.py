import csv
import pathlib


script_dir = pathlib.Path(__file__).parent.absolute()
csv_file = script_dir / '../../detections.csv'
img_dir = script_dir / '../../detections_img'

ALLOWED_PLATES = ['3547NXB']

def save_plate_record_n_verify(timestamp, plate):

        
    allowed = verify_plate(plate=plate)

    with open(csv_file, mode='a', newline='') as file:

        writer = csv.writer(file)

        image_path = img_dir / f'{timestamp}_{plate}.jpg'

        writer.writerow([timestamp, plate, allowed, image_path])
    

    return allowed

def verify_plate(plate):
    return plate in ALLOWED_PLATES

def get_history():
    history = None
    return history
