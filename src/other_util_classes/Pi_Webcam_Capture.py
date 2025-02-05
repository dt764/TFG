from picamera2 import Picamera2
import numpy as np

class WebcamCapture :
    def __init__ ( self ) :
        """
        Initializes the WebcamCapture object and fetches camera modes .
        """
        self.camera = Picamera2()
        self.camera_modes = self.camera.sensor_modes 
        self.active = False

    def get_available_resolutions ( self ) :
        """
        Prints and returns the list of supported resolutions from the stored
        camera modes .

        Returns :
            list of tuple : A list of tuples representing available
            resolutions .
        """
        try :
            resolutions =  [(mode["size"][0] , mode["size"][1]) for mode in self.camera_modes]
            print("Available Resolutions : ")
            for index , resolution in enumerate ( resolutions ) :
                print(f" { index }: { resolution [0]} x { resolution [1]}")
        except Exception as e:
            print()


    def start(self, resolution_index=0) :
        """
        Starts the camera in video mode with the selected resolution by index .

        Args :
            resolution_index ( int ) : Index of the resolution from
            available_resolutions .

        Raises :
            ValueError : If the resolution_index is out of range .
        """
        if not (0 <= resolution_index < len (self.camera_modes)):
            raise ValueError(f"Invalid resolution index { resolution_index }. Valid indices are 0 to  { len(self.camera_modes)- 1}.")
        resolution = self . camera_modes [ resolution_index ][ " size " ]
        configuration = self . camera . create_video_configuration ()
        configuration [ " main " ][ " size " ] = resolution
        self.camera.configure(configuration)
        self.camera.start ()
        self.active = True
        print(f" Camera started in video mode with resolution { resolution}.")

    def get_frame (self) :
        """
        Captures a single frame from the video stream .
        
        Returns :
            np.ndarray : Captured frame as a NumPy array , or None on error .
        """
        if not self.active :
            raise RuntimeError ("Camera is not active.")
        frame = self.camera.capture_array ()
        return frame

    def release (self):
        """
        Releases the camera and stops capturing .
        """
        if self.active :
            self.camera.stop()
            self.active = False
            print("Camera stopped.")
