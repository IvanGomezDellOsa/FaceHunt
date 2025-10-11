import cv2
import os

class VideoFrameExtractor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_capture = None
        self.frame_interval = None
        self.fps = None
        self.total_frames = 0
        self.total_processable_frames = 0

    def open_video(self):
        """Open the video using cv2.VideoCapture and return the capture or error details."""
        try:
            if not os.path.exists(self.video_path):
                return None, "Video file not found"

            self.video_capture = cv2.VideoCapture(self.video_path)
            if not self.video_capture.isOpened():
                return False, "The downloaded video is not valid"

            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            if not self.fps or self.fps <= 0:
                self.fps = 30

            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

            if self.total_frames <= 0:
                print("CAP_PROP_FRAME_COUNT failed, counting frames manually")
                temp_capture = cv2.VideoCapture(self.video_path)
                self.total_frames = 0
                while temp_capture.isOpened():
                    ret, frame = temp_capture.read()
                    if not ret:
                        break
                    self.total_frames += 1
                temp_capture.release()

            print(f"Total frames: {self.total_frames}")
            return True, None

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

            if self.total_frames <= 0:
                return False

            duration_minutes = self.total_frames / self.fps / 60
            return duration_minutes > 30
        except Exception:
            return False

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
                print("Extracting frames for FaceNet in batch mode...")
            else:
                print("Extracting frames for FaceNet in normal mode...")

            buffer =[]
            processed_count = 0
            frame_index = 0

            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    break

                if frame_index % self.frame_interval == 0:
                    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    buffer.append((processed_frame, frame_index))
                    processed_count += 1

                    if use_batch and len(buffer) >= batch_size:
                        yield buffer
                        buffer = []
                if processed_count % 200 == 0:
                    print(f"Extracting frames...")

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
            self.total_processable_frames = (self.total_frames // self.frame_interval)
            return True, gen
        except Exception as e:
            self.release_video()
            return False, f"Error starting extraction: {str(e)}"

    def release_video(self):
        """Release the video capture resource."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None