import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
from fh_downloader import VideoDownloader
from fh_frame_extractor import VideoFrameExtractor
from fh_face_recognizer import FaceRecognizer
from fh_core import FaceHuntCore


class FaceHuntInputSelection:
    """
    Main GUI for FaceHunt application.

    Handles the complete workflow: image validation, video source selection,
    optional YouTube download, frame extraction, and face recognition.
    """

    def __init__(self, root):
        """
        Initialize the FaceHunt GUI.
        Args:
        root: Tkinter root window
        """
        self.root = root
        self.root.title("FaceHunt - Input Selection")
        self.root.geometry("800x500")

        self.core = FaceHuntCore()

        self.image_path = tk.StringVar(value="")
        self.video_source = tk.StringVar(value="")
        self.image_path.trace_add("write", self.reset_image_validation)
        self.video_source.trace_add("write", self.reset_video_validation)

        self.image_validated = False
        self.source_validated = False

        # Video processing components
        self.video_path = None
        self.reference_face_embedding = None
        self.frame_extractor = None
        self.frame_generator = None
        self.youtube_url_to_download = None
        self.recognize_button = None

        # UI components
        self.progress_container = None
        self.mode_var = None
        self.mode_selector = None
        self.step1_label = None
        self.step2_label = None
        self.step3_label = None

        # Imagen
        tk.Label(root, text="Select an image with a single face (JPG/PNG/WebP)").pack(
            pady=5
        )
        tk.Entry(root, textvariable=self.image_path, width=40).pack(pady=10)
        tk.Button(root, text="Browse Image", command=self.select_image).pack(pady=5)
        tk.Button(root, text="Validate Image", command=self.validate_image).pack(
            pady=15
        )
        self.image_status = tk.Label(root, text="✗", fg="red", font=("Arial", 14))
        self.image_status.pack(pady=2)

        # Video Source
        tk.Label(root, text="Enter YouTube URL or select a local file: ").pack(pady=20)
        tk.Entry(root, textvariable=self.video_source, width=50).pack(pady=5)
        tk.Button(
            root, text="Browse Local Video", command=self.select_local_video
        ).pack(pady=5)

        tk.Button(
            root, text="Validate Video Source", command=self.validate_video_source
        ).pack(pady=10)
        self.video_status = tk.Label(root, text="✗", fg="red", font=("Arial", 14))
        self.video_status.pack(pady=2)

        tk.Button(root, text="Next Step", command=self.proceed_to_next_step).pack(
            pady=10
        )

    def select_image(self):
        """Open file dialog to select a reference image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.webp")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.image_validated = False
            self.update_status()

    def validate_image(self):
        """Validate reference image and extract facial embedding."""
        try:
            self.image_validated = False
            file_path = self.image_path.get()

            success, embedding, message = self.core.validate_image_file(file_path)

            if success:
                self.reference_face_embedding = embedding
                self.image_validated = True
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

        finally:
            self.update_status()

    def select_local_video(self):
        """Open file dialog to select a local video file."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"),
                ("All files", "*.*"),
            ]
        )
        if file_path:
            self.video_source.set(file_path)
            self.video_path = file_path
            self.source_validated = False
            self.video_status.config(text="✗", fg="red")

    def validate_video_source(self):
        """Validate video source (local file or YouTube URL)."""
        try:
            source = self.video_source.get().strip()
            success, source_type, message = self.core.validate_video_source(source)

            if success:
                self.source_validated = True
                messagebox.showinfo("Success", message)
            else:
                self.source_validated = False
                messagebox.showerror("Error", message)
        finally:
            self.update_status()

    def reset_image_validation(self, *_):
        """Reset image validation status when path changes."""
        if self.image_validated:
            self.image_validated = False
            self.update_status()

    def reset_video_validation(self, *_):
        """Reset video validation status when source changes."""
        if self.source_validated:
            self.source_validated = False
            self.update_status()

    def update_status(self):
        """Update validation status indicators (✓/✗)."""
        if self.image_validated:
            self.image_status.config(text="✓", fg="green")
        else:
            self.image_status.config(text="✗", fg="red")

        if self.source_validated:
            self.video_status.config(text="✓", fg="green")
        else:
            self.video_status.config(text="✗", fg="red")

    def proceed_to_next_step(self):
        """Proceed to video download or frame extraction based on source type."""
        if not self.image_validated or not self.source_validated:
            messagebox.showerror(
                "Error", "Please validate both the image and the video source"
            )
            return

        source = self.video_source.get().strip()

        if os.path.exists(source):
            self.video_path = source
            self.initialize_frame_extractor()
        else:
            self.youtube_url_to_download = source
            self.clear_window()
            self.setup_download_ui()

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_download_ui(self):
        """Setup UI for YouTube video download."""
        self.root.title("FaceHunt - Video Download")
        tk.Label(self.root, text="Download YouTube video").pack(pady=5)
        tk.Button(self.root, text="Start Download", command=self.start_download).pack(pady=10)

    def start_download(self):
        """Download YouTube video and proceed to frame extraction."""
        downloader = VideoDownloader(self.youtube_url_to_download)
        self.video_path = downloader.download()
        if self.video_path:
            messagebox.showinfo(
                "Success", f"Video downloaded successfully: {self.video_path}"
            )
            self.initialize_frame_extractor()
        else:
            messagebox.showerror("Error", "Download failed. Check previous errors.")

    def initialize_frame_extractor(self):
        """Initialize video frame extractor and setup extraction UI."""
        self.frame_extractor = VideoFrameExtractor(self.video_path)
        success, message = self.frame_extractor.open_video()
        if success:
            self.setup_extraction_ui()
        else:
            messagebox.showerror("Error", message)

    def setup_extraction_ui(self):
        """Setup UI for frame extraction and recognition process."""
        self.clear_window()
        self.root.title("FaceHunt - Video processor")

        tk.Label(self.root, text="Select extraction mode:").pack(pady=5)

        self.mode_var = tk.StringVar(value="Balanced")
        modes = ["High Precision", "Balanced"]
        self.mode_selector = ttk.Combobox(
            self.root, textvariable=self.mode_var, values=modes, state="readonly"
        )
        self.mode_selector.pack(pady=10)

        self.recognize_button = tk.Button(
            self.root, text="Start Recognition", command=self.start_extraction
        )
        self.recognize_button.pack(pady=15)

        self.progress_container = tk.Frame(self.root)
        self.progress_container.pack(pady=20)

        self.step1_label = tk.Label(
            self.progress_container,
            text="⚪ Determine frame interval",
            font=("Arial", 12),
        )
        self.step1_label.pack(pady=2, anchor="center")

        self.step2_label = tk.Label(
            self.progress_container, text="⚪ Extract frames", font=("Arial", 12)
        )
        self.step2_label.pack(pady=2, anchor="center")

        self.step3_label = tk.Label(
            self.progress_container, text="⚪ Find matches", font=("Arial", 12)
        )
        self.step3_label.pack(pady=2, anchor="center")

    def start_extraction(self):
        """Start frame extraction with selected mode."""
        self.recognize_button.config(state="disabled")
        mode = self.mode_var.get()

        interval = self.frame_extractor.determine_interval(mode)
        if interval <= 0:
            messagebox.showerror("Error", "Failed to determine frame interval")
            return

        self.step1_label.config(text="✅ Determine frame interval", fg="green")
        self.root.update()

        success, result = self.frame_extractor.process_video()

        if success:
            self.frame_generator = result
            self.step2_label.config(text="✅ Extract frames", fg="green")
            self.root.update()
            self.start_recognition()
        else:
            messagebox.showerror("Error", result)
            return

    def start_recognition(self):
        """
        Run face recognition on extracted frames and display results.

        Selects detector backend based on processing mode:
        - High Precision: Uses 'retinaface' for better accuracy
        - Balanced: Uses 'mtcnn' for faster processing
        """
        self.step3_label.config(text="🔵 Find matches", fg="orange")
        self.root.update()

        try:
            mode = self.mode_var.get()
            detector = "retinaface" if mode == "High Precision" else "mtcnn"

            recognizer = FaceRecognizer(
                self.reference_face_embedding, detector_backend=detector
            )
            matches = recognizer.find_matches(
                self.frame_generator,
                threshold=0.32,
                fps=self.frame_extractor.fps,
                processable_frames=self.frame_extractor.total_processable_frames,
                gui_root=self.root,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {e}")
            return

        if not matches:
            messagebox.showinfo("Result", "No matches found.")
        else:
            result_message = f"Recognition complete\nFound {len(matches)} matches:\n"
            match_lines = [
                f"- Match at frame {match['frame_index']} ({match['timestamp']})"
                for match in matches
            ]
            result_message += "\n".join(match_lines)
            messagebox.showinfo("Result", result_message)

        self.step3_label.config(text="✅ Find matches", fg="green")
