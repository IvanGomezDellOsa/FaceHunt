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

    def _is_large_video(self):
        """Check if video is considered large (>100MB or >30min)."""
        try:
            if os.path.getsize(self.video_path) > 100 * 1024 * 1024:  # 100MB
                return True

            fps = self.video_capture.get(cv2.CAP_PROP_FPS) or 30
            total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                return False

            duration_minutes = total_frames / fps / 60
            return duration_minutes > 30
        except Exception:
            return False


    def _process_frame(self, frame):
        """
        Preprocessing steps:
            - Extract frames at self.frame_interval
            - Convert BGR → RGB
            - Resize to 160x160 (FaceNet input requirement)
            - Normalize pixel values to [0,1] range (MachineLearning format)
        """
        facenet_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR -> RGB
        facenet_frame = cv2.resize(facenet_frame, (160, 160))  # Size (160x160)
        return facenet_frame.astype("float32") / 255.0

    def extract_frames(self):
        """
         Automatically chooses processing mode based on video size:
            - Normal mode: Returns single batch (videos <30min or <100MB)
            - Batch mode: Yields multiple batches of 100 frames (large videos)
         Extract and preprocess frames specifically for FaceNet model.
         Preprocessing steps
        """
        if self.video_capture is None or self.frame_interval is None:
            raise RuntimeError("Video or frame interval not initialized")
        try:
            use_batch = self._is_large_video()
            if use_batch:
                batch_size = 100
                print("Extracting frames for FaceNet in batch mode")
            else:
                print("Extracting frames for FaceNet in normal mode")

            buffer =[]
            processed_count = 0
            frame_index = 0

            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    break

                if frame_index % self.frame_interval == 0:
                    processed_frame = self._process_frame(frame)
                    buffer.append(processed_frame)
                    processed_count += 1

                    if use_batch and len(buffer) >= batch_size:
                        yield buffer
                        buffer = []

                    if processed_count % 100 == 0:
                        print(f"Progress: {processed_count} frames processed")

                frame_index += 1
            if buffer:
                yield buffer

            if processed_count == 0:
                raise RuntimeError("No frames extracted")

        finally:
            self.release_video()

    def process_video(self):
        """Main processing method with proper resource management."""
        try:
            gen = self.extract_frames()
            return True, gen
        except Exception as e:
            self.release_video()
            return False, f"Error starting extraction: {str(e)}"

    def release_video(self):
        """Release the video capture resource."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None