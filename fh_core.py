import os
import cv2
import yt_dlp
import tempfile
import shutil
import numpy as np
from deepface import DeepFace
import traceback
from fh_downloader import VideoDownloader
from fh_face_recognizer import FaceRecognizer
from fh_frame_extractor import VideoFrameExtractor

class FaceHuntCore:
    """Handles core validation and processing logic for FaceHunt application."""

    def validate_image_file(self, file_path):
        """
        Validates the reference image and extracts facial embedding.

        Returns:
            tuple: (success: bool, embedding: list or None, message: str)
        """
        if not file_path:
            return False, None, "Please select an image file."

        if not os.path.exists(file_path):
            return False, None, "The image does not exist."

        if not file_path.lower().endswith((".jpg", ".png", ".webp")):
            return False, None, "Only JPG, PNG, or WebP files are accepted."

        return self._extract_face_embedding(file_path)

    @staticmethod
    def _create_temp_image_copy(file_path):
        """
        Create temporary copy of image with ASCII-safe name.

        Required because DeepFace fails with non-ASCII paths.

        Args:
            file_path: Original image path

        Returns:
            str or None: Temporary file path on success, None on failure
        """
        try:
            _, ext = os.path.splitext(file_path)
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
            os.close(temp_fd)
            shutil.copyfile(file_path, temp_path)
            return temp_path
        except Exception as e:
            print(f"Error creating temp image copy: {e}")
            return None

    def _extract_face_embedding(self, file_path):
        """
        Extract facial embedding using DeepFace with FaceNet model.

        Process:
        1. Load and decode image from bytes
        2. Create temporary copy with ASCII-safe name
        3. Extract embedding using DeepFace
        4. Validate exactly one face is detected

        Returns:
            tuple: (success: bool, embedding: list or None, message: str)
        """
        temp_path = None
        try:
            with open(file_path, "rb") as f:
                img_bytes = f.read()
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return (
                    False,
                    None,
                    "The image could not be loaded. Please verify it is not corrupted.",
                )

            temp_path = self._create_temp_image_copy(file_path)
            if temp_path is None:
                return (
                    False,
                    None,
                    "Could not create a temporary file for image processing.",
                )

            result = DeepFace.represent(
                img_path=temp_path,
                model_name="Facenet",
                enforce_detection=True,
                detector_backend="retinaface",
            )

            if len(result) == 0:
                return False, None, "No faces detected in the image."
            if len(result) > 1:
                return (
                    False,
                    None,
                    "Multiple faces detected. Please use an image with exactly one face.",
                )

            embedding = result[0]["embedding"]

            face_confidence = result[0].get("face_confidence", 1.0)
            if face_confidence < 0.9:
                return (
                    False,
                    None,
                    f"Face detection confidence too low ({face_confidence:.2f}). Use a clearer, front-facing photo with good lighting.",
                )

            return (
                True,
                embedding,
                "Valid image with 1 face detected",
            )

        except ValueError:
            return False, None, f"Face detection failed"

        except Exception as e:
            return (
                False,
                None,
                f"Unexpected error during face embedding extraction: {str(e)}",
            )

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def validate_video_source(self, source):
        """
        Validate video source (local file or YouTube URL).

        Returns:
            tuple: (success: bool, source_type: str or None, message: str)
                   source_type is 'local' or 'youtube' only when success=True
        """
        if not source:
            return False, None, "Video source cannot be empty."

        if os.path.exists(source):
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                cap.release()
                return True, "local", "Valid local video file."
            else:
                return False, None, "Invalid or unsupported video format."

        try:
            with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True, "extract_flat": False}) as ydl:
                info = ydl.extract_info(source, download=False)

            if not info or 'id' not in info or info.get('duration') is None or info['duration'] <= 0:
                return False, None, "Invalid YouTube URL: Video not found or not accessible."

            if not info.get('formats') or len(info['formats']) == 0:
                return False, None, "Invalid YouTube URL: No video formats available."

            return (
                True,
                "youtube",
                f"Valid YouTube URL:\n{info.get('title', 'Unknown')} ({info.get('duration', 0)}s)",
            )

        except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError, yt_dlp.utils.UnsupportedError) as e:
            msg = str(e)
            if "Invalid" in msg or "ERROR" in msg or "youtube:" in msg:
                msg = "Invalid YouTube URL"
            return False, None, msg

        except Exception as e:
            return False, None, f"An unexpected error occurred: {e}"

    def execute_workflow(self, image_path, mode, video_source):
        """
        Executes the complete FaceHunt workflow in a headless environment.

        This function orchestrates the entire process: validates the reference
        image and video source, downloads the video if necessary, extracts
        frames, and performs face recognition. It is designed to be called
        from an API or a command-line interface, containing no GUI dependencies.

        Args:
            image_path (str): The file path to the reference image.
            mode (str): The processing mode, either "balanced" or "precision".
            video_source (str): The video source, which can be a local file path
                                or a YouTube URL.

        Returns:
            dict: A dictionary containing the results of the process.
                  {
                      "success": bool,
                      "message": str,
                      "matches": list | None
                  }
        """
        downloaded_video_path = None
        try:
            success, embedding, message = self.validate_image_file(image_path)
            if not success:
                return {"success": False, "message": message, "matches": None}

            success, source_type, message = self.validate_video_source(video_source)
            if not success:
                return {"success": False, "message": message, "matches": None}

            if source_type == "youtube":
                print(f"Starting download from: {video_source}")
                downloader = VideoDownloader(video_source)
                video_path = downloader.download()

                if video_path is None:
                    return {"success": False, "message": "Could not download the YouTube video.", "matches": None}

                downloaded_video_path = video_path
            else:
                video_path = video_source

            extractor = VideoFrameExtractor(video_path)
            success, msg = extractor.open_video()
            if not success:
                return {"success": False, "message": msg, "matches": None}

            processing_mode = "High Precision" if mode == "precision" else "Balanced"
            extractor.determine_interval(processing_mode)

            success, frame_generator_or_error = extractor.process_video()
            if not success:
                return {"success": False, "message": frame_generator_or_error, "matches": None}

            frame_generator = frame_generator_or_error

            detector = "retinaface" if mode == "precision" else "mtcnn"
            recognizer = FaceRecognizer(embedding, detector_backend=detector)
            matches = recognizer.find_matches(
                frame_generator,
                threshold=0.32,
                fps=extractor.fps,
                processable_frames=extractor.total_processable_frames
            )

            return {
                "success": True,
                "message": f"Process completed. {len(matches)} matches found.",
                "matches": matches
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "success": False,
                "message": f"An unexpected internal error occurred: {str(e)}",
                "matches": None
            }

        finally:
            if downloaded_video_path and os.path.exists(downloaded_video_path):
                print(f"Cleaning temporary file: {downloaded_video_path}")
                os.remove(downloaded_video_path)