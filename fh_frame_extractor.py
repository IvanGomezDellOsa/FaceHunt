import cv2
from deepface import DeepFace
import os

class VideoFrameExtractor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_capture = None

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

    def extract_frames(self):
        """
         Extract and preprocess frames specifically for FaceNet model.
         Preprocessing steps:
            - Extract frames at self.frame_interval
            - Convert BGR → RGB
            - Resize to 160x160 (FaceNet input requirement)
            - Normalize pixel values to [0,1] range (MachineLearning format)
        """
        if self.video_capture is None or self.frame_interval is None:
            return False, "Video or frame interval not properly initialized"

        frames = []
        frame_index = 0

        print ("Extracting frames for FaceNet...")

        while True:
            ret, frame = self.video_capture.read()

            if not ret or frame is None:
                break

            if frame_index % self.frame_interval == 0:
                try:
                    facenet_frame  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #BGR → RGB
                    facenet_frame  = cv2.resize(facenet_frame , (160, 160)) #Size (160x160)
                    facenet_frame  = facenet_frame .astype("float32") / 255.0
                    frames.append(facenet_frame)

                    if len(frames) % 25 == 0:
                        print(f"Progress: {len(frames)} frames processed")
                except Exception as e:
                    print (f"Error processing frame {frame_index}: {e}")

            frame_index += 1

        if not frames:
            return False, "Error: No frames extracted."

        print(f"Successfully extracted {len(frames)} frames")
        return True, frames

    def process_video(self):
        """Main processing method with proper resource management."""
        try:
            return self.extract_frames()
        except Exception as e:
            return False, f"Unexpected error during processing: {str(e)}"
        finally:
            self.release_video()


    def release_video(self):
        """Release the video capture resource."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
