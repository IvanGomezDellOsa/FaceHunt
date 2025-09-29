import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import os
import yt_dlp
from fh_downloader import VideoDownloader
from deepface import DeepFace
import numpy as np
import tempfile
import shutil
from fh_frame_extractor import VideoFrameExtractor


class FaceHuntInputSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceHunt - Image and YouTube Link Selection")
        self.root.geometry("800x400")

        self.image_path = tk.StringVar(value="")
        self.youtube_url = tk.StringVar(value="")
        self.youtube_url.trace("w", lambda *args: setattr(self, "url_validated",
                                                          False))  # Reset URL validation when value changes
        self.image_validated = False
        self.url_validated = False
        self.video_path = None
        self.reference_face_embedding = None
        self.frame_extractor = None

        # --- Imagen ---
        tk.Label(root, text="Select an image (JPG/PNG/WebP)").pack(pady=5)
        tk.Entry(root, textvariable=self.image_path, width=40).pack(pady=10)
        tk.Button(root, text="Browse Image", command=self.select_image).pack(pady=5)
        tk.Button(root, text="Validate Image", command=self.validate_image).pack(pady=15)
        self.image_status = tk.Label(root, text="✗", fg="red", font=("Arial", 14))
        self.image_status.pack(pady=2)

        # --- YouTube ---
        tk.Label(root, text="Enter YouTube link:").pack(pady=5)
        tk.Entry(root, textvariable=self.youtube_url, width=50).pack(pady=5)
        tk.Button(root, text="Validate YouTube URL", command=self.validate_yt_url).pack(pady=10)
        self.url_status = tk.Label(root, text="✗", fg="red", font=("Arial", 14))
        self.url_status.pack(pady=2)

        tk.Button(root, text="Next Step", command=self.next_step).pack(pady=10)

    def select_image(self):
        """Open file dialog to select an image file."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.webp")])
        if file_path:
            self.image_path.set(file_path)
            self.image_validated = False
            self.update_status()

    def _create_temp_image_copy(self, file_path):
        """
            Create a temporary copy of the image with a safe name (ASCII).
            Return the temporary path.
        """
        _, ext = os.path.splitext(file_path)
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(temp_fd)
        shutil.copyfile(file_path, temp_path)
        return temp_path

    def extract_face_embedding(self, file_path):
        '''
            Extract the facial embedding from the image using DeepFace with Facenet.
            1. Verify that the image can be opened and decoded from bytes
            2. Create a temporary copy of the image with a safe ASCII name
                (required because DeepFace fail with non-ASCII paths).
            3. Use DeepFace.represent() to compute the facial embedding.
            4. Validate that exactly one face is detected in the image.
            Returns: tuple: (success: bool, embedding: list or None, error_message: str or None)
        '''
        temp_path = None
        try:
            with open(file_path, 'rb') as f:
                img_bytes = f.read()
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return False, None, "The image could not be loaded. Please verify it is not corrupted."

            temp_path = self._create_temp_image_copy(file_path)

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
            return True, embedding, None

        except ValueError as e:
            return False, None, f"Face detection failed: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error during face embedding extraction: {str(e)}"
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def validate_image(self):
        """
        Validates the reference image and extracts facial embedding.

        Performs progressive validation:
        1. File selection check
        2. File existence check
        3. Supported format check (.jpg/.png/.webp)
        4. Delegate to extract_face_embedding() to ensure the image is readable
            and contains exactly one face.

        On success:
        - Stores the extracted embedding in self.reference_face_embedding.
        - Sets self.image_validated = True.
        - Updates the GUI status and shows a success message.
        """
        self.image_validated = False
        file_path = self.image_path.get()

        if not file_path:
            messagebox.showerror("Error", "Please select an image file.")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "The image does not exist.")
            return

        if not file_path.lower().endswith(('.jpg', '.png', '.webp')):
            messagebox.showerror("Error", "Only JPG, PNG, or WebP files are accepted.")
            return

        # Extract facial embedding from the uploaded image
        success, embedding, error_message = self.extract_face_embedding(file_path)
        if not success:
            messagebox.showerror("Error", error_message)
            return

        self.reference_face_embedding = embedding
        self.image_validated = True
        messagebox.showinfo("Success", f"Valid image with 1 face detected: {file_path}")
        self.update_status()

    def validate_yt_url(self):
        """Validate the YouTube URL by checking accessibility and extracting information."""
        yt_url = self.youtube_url.get()
        if not yt_url:
            messagebox.showerror("Error", "Please enter a YouTube link.")
            return
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(yt_url, download=False)
            self.url_validated = True
            messagebox.showinfo("Success", f"Valid YouTube video: {info['title']}")
        except Exception as e:
            self.url_validated = False
            messagebox.showerror("Error", f"Invalid YouTube link or video not accessible.\nDetails: {e}")
            return
        self.update_status()

    def update_status(self):
        """Update the status labels with (✓) or (✗) and colors."""
        if self.image_validated:
            self.image_status.config(text="✓", fg="green")
        else:
            self.image_status.config(text="✗", fg="red")

        if self.url_validated:
            self.url_status.config(text="✓", fg="green")
        else:
            self.url_status.config(text="✗", fg="red")

    def clear_window(self):
        """Destroys all widgets in the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_download_ui(self):
        """Sets up the download interface."""
        self.root.title("FaceHunt - Video Download")
        tk.Label(self.root, text="Download YouTube video").pack(pady=5)
        tk.Button(self.root, text="Start Download", command=self.start_download).pack(pady=10)
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress, maximum=100)
        self.progress_bar.pack(pady=5, fill="x", padx=10)

    def next_step(self):
        """Validates image and URL, clears the window, and shows the download interface."""
        if not (self.image_validated and self.url_validated):
            messagebox.showerror("Error", "Please validate both image and YouTube link.")
            return
        self.clear_window()
        self.setup_download_ui()

    def start_download(self):
        """Starts the download using VideoDownloader"""
        downloader = VideoDownloader(self.root, self.progress, self.youtube_url.get())
        self.video_path = downloader.download()
        if self.video_path:
            messagebox.showinfo("Success", f"Video downloaded successfully: {self.video_path}")
            self.initialize_frame_extractor()
        else:
            messagebox.showerror("Error", "Download failed. Check previous errors.")

    def initialize_frame_extractor(self):
        """Initializes VideoFrameExtractor and sets up extraction."""
        self.frame_extractor = VideoFrameExtractor(self.video_path)
        success, message = self.frame_extractor.open_video()
        if success:
            self.setup_extraction_ui()
        else:
            messagebox.showerror("Error", message)

    def setup_extraction_ui(self):
        """Sets up the UI for video frame extraction process."""
        self.clear_window()
        self.root.title("FaceHunt - Video processor")

        tk.Label(self.root, text="Select extraction mode:").pack(pady=5)

        self.mode_var = tk.StringVar(value="Balanced")
        modes = ["High Precision", "Balanced"]
        self.mode_selector = ttk.Combobox(self.root, textvariable=self.mode_var, values=modes, state="readonly")
        self.mode_selector.pack(pady=5)

        self.extract_button = tk.Button(self.root, text="Start Extraction", command=self.start_extraction)
        self.extract_button.pack(pady=10)

        self.progress_frame = tk.Frame(self.root)

        self.progress_frame.pack(pady=20)
        progress_label = tk.Label(self.progress_frame, text="Extraction Progress:", font=("Arial", 10, "bold"))
        progress_label.pack(pady=2)

        self.step1_label = tk.Label(self.progress_frame, text="⚪ Determine frame interval", font=("Arial", 9))
        self.step1_label.pack(pady=2, anchor="center")

        self.step2_label = tk.Label(self.progress_frame, text="⚪ Extract frames", font=("Arial", 9))
        self.step2_label.pack(pady=2, anchor="center")

        self.step3_label = tk.Label(self.progress_frame, text="⚪ Process for FaceNet", font=("Arial", 9))
        self.step3_label.pack(pady=2, anchor="center") #Vincular cuando haga el paso 3

    def start_extraction(self):
        """Start frame extraction with selected mode."""
        self.extract_button.config(state="disabled")

        mode = self.mode_var.get()

        success_interval = self.frame_extractor.determine_interval(mode)
        if success_interval:
            self.step1_label.config(text="✅ Determine frame interval", fg="green")
            self.root.update()
        else:
            messagebox.showerror("Error", "Failed to determine frame interval")
            return

        success, result = self.frame_extractor.process_video()

        gen = result
        any_frame = False
        try:
            for batch in gen:
                any_frame = True

        except Exception as e:
            messagebox.showerror("Error", f"Extraction failed: {str(e)}")
            return

        if success:
            self.step2_label.config(text="✅ Extract frames", fg="green")
            messagebox.showinfo("Success", "Frames extracted successfully!")
        else:
            messagebox.showerror("Error", result)
            return
