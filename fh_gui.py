import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import os
import yt_dlp
from fh_downloader import VideoDownloader

class FaceHuntInputSelection:
    def __init__ (self, root):
        self.root = root
        self.root.title("FaceHunt - Image and YouTube Link Selection")
        self.root.geometry("800x400")

        self.image_path = tk.StringVar(value="")
        self.youtube_url = tk.StringVar(value="")
        self.youtube_url.trace("w", lambda *args: setattr(self, "url_validated", False)) # Reset the URL validation whenever its value changes
        self.image_validated = False
        self.url_validated = False
        self.video_path = None

        # --- Imagen ---
        tk.Label(root, text = "Select an image (JPG/PNG/WebP)").pack(pady = 5)
        tk.Entry(root, textvariable = self.image_path, width=40).pack(pady = 10)
        tk.Button(root, text = "Browse Image", command = self.select_image).pack(pady=5)
        tk.Button(root, text = "Validate Image", command = self.validate_image).pack(pady = 15)
        self.image_status = tk.Label(root, text="✗", fg="red", font=("arial", 14))
        self.image_status.pack(pady=2)

        # --- YouTube ---
        tk.Label(root, text="Enter YouTube link:").pack(pady=5)
        tk.Entry(root, textvariable=self.youtube_url, width=50).pack(pady=5)
        tk.Button(root, text="Validate YouTube URL", command=self.validate_yt_url).pack(pady=10)
        self.url_status = tk.Label(root, text="✗", fg="red", font=("Arial", 14))
        self.url_status.pack(pady=2)

        tk.Button(root, text="Next Step", command=self.next_step).pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.webp")])
        if file_path:
            self.image_path.set(file_path)
            self.image_validated = False
            self.update_status()

    def validate_image(self):
        '''Validates the reference image (JPG/PNG/WebP) by checking path, existence, extension, and loading.
            Uses prior validations to display specific errors instead of a generic message if the image fails to load.'''

        file_test = self.image_path.get()
        if not file_test:
            messagebox.showerror("Error", "Please select an image file.")
            return
        if not os.path.exists(file_test):
            messagebox.showerror("Error", "The image does not exist.")
            return
        if not file_test.lower().endswith(('.jpg', '.png', '.webp')):
            messagebox.showerror("Error", "Only JPG, PNG, or WebP files are accepted.")
            return
        img = cv2.imread(file_test)
        if img is None:
            messagebox.showerror("Error", "The image could not be loaded. Please verify it is not corrupted.")
            return
        self.image_validated = True
        messagebox.showinfo("Success", f"Valid image: {file_test}")
        self.update_status()

    def validate_yt_url(self):
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
        """Starts the download using VideoDownloader."""
        downloader = VideoDownloader(self.root, self.progress, self.youtube_url.get())
        self.video_path = downloader.download()
        if self.video_path:
            messagebox.showinfo("Success", f"Video downloaded successfully: {self.video_path}")
        else:
            messagebox.showerror("Error", "Download failed. Check previous errors.")
