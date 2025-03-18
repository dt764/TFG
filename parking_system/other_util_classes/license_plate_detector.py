import tflite_runtime.interpreter as tflite
import numpy as np
import cv2

class LicensePlateDetector:
    """
    A class for detecting license plates in an image using a TensorFlow Lite model.

    This class uses a pre-trained TFLite model with Edge TPU acceleration for real-time license 
    plate detection. It handles image preprocessing, model inference, and extraction of the 
    detected region of interest (ROI) where the license plate is located.

    Attributes:
        interpreter (tflite.Interpreter): The TFLite interpreter used for running the model.
        input_details (list): Details about the model's input tensor.
        output_details (list): Details about the model's output tensor.
        height (int): The height of the model's expected input image size.
        width (int): The width of the model's expected input image size.
        float_input (bool): Indicates whether the model's input tensor is of type float32.
        input_mean (float): The mean value used for input normalization.
        input_std (float): The standard deviation value used for input normalization.
        min_detection_confidence (float): The minimum confidence threshold for valid detections.

    Methods:
        preprocess_image(frame): Preprocesses the input frame for model inference.
        detect_license_plate(frame): Detects license plates in the given frame.
    """

    def __init__(self, model_path, min_detection_confidence):
        """
        Initializes the LicensePlateDetector with a model path and detection confidence.

        Args:
            model_path (str): Path to the TFLite model file.
            min_detection_confidence (float): Minimum confidence threshold for a detection to be 
                                              considered valid.
        """
        self.interpreter = tflite.Interpreter(
            model_path=model_path,
            experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
        )
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        self.float_input = (self.input_details[0]['dtype'] == np.float32)
        self.input_mean = 127.5
        self.input_std = 127.5
        self.min_detection_confidence = min_detection_confidence

    def preprocess_image(self, frame):
        """
        Preprocesses the input frame for model inference by resizing and normalizing.

        Args:
            frame (numpy.ndarray): The input image frame in BGR format.

        Returns:
            numpy.ndarray: The preprocessed image tensor, ready for model inference.
        """
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (self.width, self.height))
        input_data = np.expand_dims(image_resized, axis=0)
        return input_data

    def detect_license_plate(self, frame):
        """
        Detects license plates in the given image frame using the TFLite model.

        Args:
            frame (numpy.ndarray): The input image frame in BGR format.

        Returns:
            tuple: A tuple containing:
                - roi (numpy.ndarray or None): The region of interest containing the detected license plate, 
                  or None if no license plate is detected.
                - ymin (int): The top boundary of the detected bounding box.
                - xmin (int): The left boundary of the detected bounding box.
                - ymax (int): The bottom boundary of the detected bounding box.
                - xmax (int): The right boundary of the detected bounding box.
                - confidence (float): The confidence score of the detection.
        """
        roi = None
        ymin = 0
        xmin = 0
        xmax = 0
        ymax = 0
        confidence = 0.0

        imH, imW, _ = frame.shape

        input_data = self.preprocess_image(frame)

        if self.float_input:
            input_data = (np.float32(input_data) - self.input_mean) / self.input_std

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        boxes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        for i in range(len(scores)):
            if scores[i] > self.min_detection_confidence:
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))
                roi = frame[ymin:ymax, xmin:xmax]
                confidence = scores[i]

        return roi, ymin, xmin, ymax, xmax, confidence
