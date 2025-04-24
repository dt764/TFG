import cv2
import threading
import time

class WebcamCapture:
    """
    A class for capturing video frames from a webcam with buffering to ensure
    that frames are captured only when needed.
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
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open video source")
        
        # Buffer to store the most recent frame
        self.frame = None
        self.lock = threading.Lock()
        self.running = True

        # Start the capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.start()

    def _capture_frames(self):
        """
        Captures frames from the webcam continuously in a separate thread to ensure
        that the latest frame is always available for processing.
        """
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            time.sleep(0.01)  # Adjust this sleep time to control capture rate

    def get_frame(self, process_frame=None):
        """
        Returns the most recent frame from the webcam. If a frame is being processed,
        waits for the frame to be available.

        Args:
            process_frame (function, optional): A function to process the captured frame (e.g., convert to grayscale).

        Returns:
            frame (numpy.ndarray): The captured (and optionally processed) frame from the webcam.
        """
        with self.lock:
            frame = self.frame

        if frame is None:
            raise RuntimeError("No frame captured yet")

        if process_frame:
            frame = process_frame(frame)

        return frame

    def release(self):
        """
        Releases the webcam resource and closes any OpenCV windows.
        """
        self.running = False
        self.capture_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()
