import cv2

class WebcamCapture:
    """
    A class for capturing video frames from a webcam.

    This class provides a simple interface to access the webcam, capture frames, and release
    the camera resource when done. It uses OpenCV's VideoCapture for video stream handling.

    Attributes:
        cap (cv2.VideoCapture): The video capture object used to interface with the webcam.

    Methods:
        get_frame(): Captures a frame from the webcam.
        release(): Releases the webcam resource and closes any OpenCV windows.
    """

    def __init__(self, source=0):
        """
        Initializes the WebcamCapture with the specified video source.

        Args:
            source (int or str): The video source index or path. The default value of 0 corresponds 
                                 to the default system webcam. If a string is provided, it should 
                                 be a path to a video file or stream URL.
        """
        self.cap = cv2.VideoCapture(source)

    def get_frame(self):
        """
        Captures a frame from the webcam.

        Returns:
            frame (numpy.ndarray): The captured frame from the webcam.

        Raises:
            RuntimeError: If a frame could not be grabbed from the webcam.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to grab frame")
        return frame

    def release(self):
        """
        Releases the webcam resource and closes any OpenCV windows.

        This method should be called when the webcam is no longer needed to free up the
        camera and avoid resource leaks.
        """
        self.cap.release()
        cv2.destroyAllWindows()
