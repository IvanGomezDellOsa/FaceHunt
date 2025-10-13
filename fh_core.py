import os
import cv2
import yt_dlp
import tempfile
import shutil
import numpy as np
from deepface import DeepFace


class FaceHuntCore:
    """    Handles all non-GUI logic for the FaceHunt application """

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

        if not file_path.lower().endswith(('.jpg', '.png', '.webp')):
            return False, None, "Only JPG, PNG, or WebP files are accepted."

        return self._extract_face_embedding(file_path)

    @staticmethod
    def _create_temp_image_copy(file_path):
        """
        Create a temporary copy of the image with a safe name (ASCII).
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
        Extract the facial embedding from the image using DeepFace with Facenet.

        Process:
        1. Verify that the image can be opened and decoded from bytes
        2. Create a temporary copy of the image with a safe ASCII name
           (required because DeepFace fails with non-ASCII paths)
        3. Use DeepFace.represent() to compute the facial embedding
        4. Validate that exactly one face is detected in the image

        Returns:
            tuple: (success: bool, embedding: list or None, message: str)
        """
        temp_path = None
        try:
            with open(file_path, 'rb') as f:
                img_bytes = f.read()
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return False, None, "The image could not be loaded. Please verify it is not corrupted."

            temp_path = self._create_temp_image_copy(file_path)
            if temp_path is None:
                return False, None, "Could not create a temporary file for image processing."

            result = DeepFace.represent(
                img_path=temp_path,
                model_name="Facenet",
                enforce_detection=True
            )

            if len(result) == 0:
                return False, None, "No faces detected in the image."
            if len(result) > 1:
                return False, None, "Multiple faces detected. Please use an image with exactly one face."

            embedding = result[0]["embedding"]
            return True, embedding, f"Valid image with 1 face detected: {os.path.basename(file_path)}"
        except ValueError as e:
            return False, None, f"Face detection failed: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error during face embedding extraction: {str(e)}"
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def validate_video_source(self, source):
        """
        Verify that the video source (local or YouTube) is real and accessible.

        Returns:
            tuple: (success: bool, source_type: str ('local' or 'YouTube'), message: str)
        """
        if not source:
            return False, None, "Video source cannot be empty."

        if os.path.exists(source):
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                cap.release()
                return True, 'local', "Valid local video file."
            else:
                return False, 'local', "Invalid or unsupported video format."

        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
                info = ydl.extract_info(source, download=False)
            return True, 'youtube', f"Valid YouTube URL:\n{info.get('title', 'Unknown')}"

        except yt_dlp.utils.DownloadError:
            return False, 'youtube', "The path is not a valid local file or a YouTube URL."
        except Exception as e:
            return False, 'youtube', f"An unexpected error occurred: {e}"
