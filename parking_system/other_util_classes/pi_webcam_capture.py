from picamera2 import Picamera2

class Pi_WebcamCapture:
    def __init__(self):
        """
        Initializes the WebcamCapture object and fetches camera modes.
        """
        self.camera = Picamera2()
        self.camera_modes = self.camera.sensor_modes
        self.active = False

    def show_available_configurations(self):
        """
        Prints and returns the list of supported sensor configurations.

        Returns:
            list of dict: A list of dictionaries representing available sensor modes.
        """
        try:
            print("Available Camera Configurations:")
            for index, mode in enumerate(self.camera_modes):
                print(f"\nConfiguration {index}:")
                for key, value in mode.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error getting configurations: {e}")
            return []

    def start(self, configuration_index=0):
        """
        Starts the camera using the full configuration of the selected sensor mode.

        Args:
            configuration_index (int): Index of the sensor configuration from available options.

        Raises:
            ValueError: If the configuration_index is out of range.
        """
        if not (0 <= configuration_index < len(self.camera_modes)):
            raise ValueError(f"Invalid configuration index {configuration_index}. Valid indices are 0 to {len(self.camera_modes) - 1}.")

        selected_mode = self.camera_modes[configuration_index]
        configuration = self.camera.create_video_configuration(sensor={"mode": selected_mode})

        self.camera.configure(configuration)
        self.camera.start()
        self.active = True
        print(f"\nCamera started with configuration {configuration_index}:")
        for key, value in selected_mode.items():
            print(f"  {key}: {value}")

    def get_frame(self):
        """
        Captures a single frame from the video stream.

        Returns:
            np.ndarray: Captured frame as a NumPy array, or None on error.
        """
        if not self.active:
            raise RuntimeError("Camera is not active.")
        frame = self.camera.capture_array()
        return frame

    def release(self):
        """
        Releases the camera and stops capturing.
        """
        if self.active:
            self.camera.stop()
            self.active = False
            print("Camera stopped.")
