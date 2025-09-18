import cv2
from deepface import DeepFace
import os

class VideoFrameExtractor:
    def __init__(self, video_path, reference_face_embedding):
        self.video_path = video_path
        self.video_capture = None
        self.reference_face_embedding = reference_face_embedding
        self.frame_interval = None

    def open_video(self):
        """Open the video using cv2.VideoCapture and return the capture or error details."""
        try:
            if not os.path.exists(self.video_path):
                return None, "Video file not found"

            self.video_capture = cv2.VideoCapture(self.video_path)
            if self.video_capture.isOpened():
                return True, None
            else:
                return False, "The downloaded video is not valid"
        except Exception as e:
            print(f"Error opening video: {e}")
            return False, str(e)

    def determine_interval(self, mode="Balanced"):
        """Determine frame interval based on FPS and selected mode."""
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        if fps<=0:
            fps=30

        if mode == "High Precision":
            seconds_per_sample = 0.25 # 1 frame every 0.25s
        else: # Mode = Balanced
            seconds_per_sample = 0.5 # 1 frame every 0.5s

        self.frame_interval = int(fps * seconds_per_sample)
        return self.frame_interval

    def extract_frames(self, ):

    def release_video(self):
        """Release the video capture resource."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
