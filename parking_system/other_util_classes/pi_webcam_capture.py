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
        Prints and returns the list of supported sensor configurations (Resolution, FPS, and Crop Limits).
        It avoids showing duplicate resolutions.

        Returns:
            list of dict: A list of dictionaries representing available sensor modes.
        """
        seen_resolutions = set()  # Para almacenar resoluciones únicas
        print("Available Camera Configurations (Resolution, FPS, and Crop Limits):")
        
        for index, mode in enumerate(self.camera_modes):
            resolution = mode.get("size", (640, 480))
            fps = mode.get("fps", 0)
            crop_limits = mode.get("crop_limits", "N/A")
            
            # Evitar que se muestren resoluciones duplicadas
            if resolution not in seen_resolutions:
                seen_resolutions.add(resolution)
                print(f"\nConfiguration {index}:")
                print(f"  Resolution: {resolution}")
                print(f"  FPS: {fps}")
                print(f"  Crop Limits: {crop_limits}")

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
        resolution = selected_mode.get("size", (640, 480))

        # Creamos configuración personalizada basada en la resolución seleccionada
        configuration = self.camera.create_video_configuration(
            main={"size": resolution, "format": "RGB888"}
        )

        self.camera.configure(configuration)
        self.camera.start()
        self.active = True

        print(f"\nCamera started with configuration {configuration_index}:")
        print(f"  Resolution: {resolution}")
        print(f"  FPS: {selected_mode.get('fps', 'N/A')}")
        print(f"  Crop Limits: {selected_mode.get('crop_limits', 'N/A')}")

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

