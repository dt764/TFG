import tflite_runtime.interpreter as tflite
import numpy as np
import cv2

class LicensePlateDetector:
    def __init__(self, model_path, min_detection_confidence):
        self.interpreter = tflite.Interpreter(model_path=model_path,
                                               experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])
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
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (self.width, self.height))
        input_data = np.expand_dims(image_resized, axis=0)
        return input_data

    def detect_license_plate(self, frame):

        roi = None
        ymin = 0
        xmin = 0
        xmax = 0
        ymax = 0
        
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

        return roi, ymin, xmin, ymax, xmax
