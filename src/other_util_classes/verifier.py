import csv
import pathlib

# Define the directory of the current script
script_dir = pathlib.Path(__file__).parent.absolute()

# Paths for the CSV file and the images directory
csv_file = script_dir / '../../detections.csv'
img_dir = script_dir / '../../detections_img'

# List of allowed license plates
ALLOWED_PLATES = ['3547NXB']

def save_plate_record_n_verify(timestamp, plate):
    """
    Verifies the license plate and saves the record in a CSV file.

    Parameters:
        timestamp (str): The timestamp of the detection.
        plate (str): The license plate number detected.

    Returns:
        bool: True if the plate is allowed, False otherwise.
    """
    # Check if the plate is allowed
    allowed = verify_plate(plate=plate)

    # Check if the CSV file exists, if not, create it and add the headers
    file_exists = csv_file.exists()

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            # Write the headers if the file did not exist
            writer.writerow(['Timestamp', 'Plate', 'Allowed', 'Image Path'])

        # Construct the image path using the timestamp and plate
        image_path = img_dir / f'{timestamp}_{plate}.jpg'
        
        # Write the detection record to the CSV file
        writer.writerow([timestamp, plate, allowed, image_path])
    
    # Return whether the plate was allowed
    return allowed

def verify_plate(plate):
    """
    Checks if the given license plate is allowed.

    Parameters:
        plate (str): The license plate number to verify.

    Returns:
        bool: True if the plate is allowed, False otherwise.
    """
    return plate in ALLOWED_PLATES


def get_history():
    """
    Reads the detection history from the CSV file and returns it as a list of dictionaries.

    Returns:
        list: A list of dictionaries, each containing the fields 'Timestamp', 'Plate', 
              'Allowed', and 'Image Path' for each detection.
              If the file does not exist, returns an empty list.
    """
    # Check if the CSV file exists, if not, return an empty list
    if not csv_file.exists():
        return []

    history = []

    # Read the CSV file and populate the history list
    with open(csv_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Append each row as a dictionary to the history list
            history.append({
                'Timestamp': row['Timestamp'],
                'Plate': row['Plate'],
                'Allowed': row['Allowed'] == 'True',  # Convert 'Allowed' to a boolean
                'Image Path': row['Image Path']
            })

    return history
