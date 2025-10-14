import cv2
import os


class VideoFrameExtractor:
    """Extracts and preprocesses video frames for face recognition."""

    def __init__(self, video_path):
        """
        Initialize frame extractor.

        Args:
            video_path: Path to video file
        """
        self.video_path = video_path
        self.video_capture = None
        self.frame_interval = None
        self.fps = None
        self.total_frames = 0
        self.total_processable_frames = 0

    def open_video(self):
        """
        Open video file and extract metadata (FPS, frame count).
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            if not os.path.exists(self.video_path):
                return False, "Video file not found"

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
        """
        Calculate frame sampling interval based on mode.

        Args:
            mode: "High Precision" (0.25s) or "Balanced" (0.5s)

        Returns:
            int: Frame interval (number of frames to skip)
        """
        if mode == "High Precision":
            seconds_per_sample = 0.35  # 1 frame every 0.35s
        else:  # Mode = Balanced
            seconds_per_sample = 0.8  # 1 frame every 0.8s

        self.frame_interval = int(self.fps * seconds_per_sample)

        return self.frame_interval

    def _is_large_video(self):
        """
        Check if video requires batch processing (>100MB or >30min).

        Returns:
            bool: True if video is large
        """
        try:
            if os.path.getsize(self.video_path) > 100 * 1024 * 1024:  # 100MB
                return True

            if self.total_frames <= 0:
                return False

            duration_minutes = self.total_frames / self.fps / 60
            return duration_minutes > 30

        except (OSError, ZeroDivisionError) as e:
            print(f"Could not determine video size/duration: {e}")
            return False

    def extract_frames(self):
        """
        Extract and preprocess frames for FaceNet model.

        Automatically uses batch mode (100 frames per batch) for large videos,
        or single batch mode for smaller videos. Converts frames to RGB.

        Yields:
            list: Batch of tuples (preprocessed_frame, frame_index)

        Raises:
            RuntimeError: If video or frame interval not initialized
        """
        if self.video_capture is None or self.frame_interval is None:
            raise RuntimeError("Video or frame interval not initialized")
        try:
            use_batch = self._is_large_video()
            batch_size = 100

            if use_batch:
                print("Extracting frames for FaceNet in batch mode...")
            else:
                print("Extracting frames for FaceNet...")

            buffer = []
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
                if processed_count > 0 and processed_count % 200 == 0:
                    print(f"Extracting frames...")

                frame_index += 1
            if buffer:
                yield buffer

            if processed_count == 0:
                raise RuntimeError("No frames extracted")

        finally:
            self.release_video()

    def process_video(self):
        """
        Start frame extraction process with validation.

        Returns:
            tuple: (success: bool, generator or error_message: str)
        """
        try:
            if self.frame_interval is None or self.frame_interval <= 0:
                raise RuntimeError("Frame interval not initialized.")

            gen = self.extract_frames()
            self.total_processable_frames = self.total_frames // self.frame_interval
            return True, gen
        except Exception as e:
            self.release_video()
            return False, f"Error starting extraction: {str(e)}"

    def release_video(self):
        """Release video capture resource."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
