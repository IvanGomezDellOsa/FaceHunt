import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import os
import re
import yt_dlp

class FaceHuntInputSelection:
    def __init__ (self, root):
        self.root = root
        self.root.title("FaceHunt - Image and YouTube Link Selection")
        self.root.geometry("600x300")

        self.image_path = tk.StringVar()
        self.youtube_url = tk.StringVar()

        # --- Imagen ---
        tk.Label(root, text = "Select an image (JPG/PNG/WebP)").pack(pady = 5)
        tk.Entry(root, textvariable = self.image_path, width=40).pack(pady = 10)
        tk.Button(root, text = "Browse Image", command = self.select_image).pack(pady=5)
        tk.Button(root, text = "Validate Image", command = self.validate_image).pack(pady = 15)

        # --- YouTube ---
        tk.Label(root, text="Enter YouTube link:").pack(pady=5)
        tk.Entry(root, textvariable=self.youtube_url, width=50).pack(pady=5)
        tk.Button(root, text="Validate YouTube URL", command=self.validate_yt_url).pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.webp")])
        if file_path:
            self.image_path.set(file_path)

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
        messagebox.showinfo("Success", f"Valid image: {file_test}")

    def validate_yt_url(self):
        yt_url = self.youtube_url.get()
        if not yt_url:
            messagebox.showerror("Error", "Please enter a YouTube link.")
            return
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(yt_url, download=False)

            messagebox.showinfo("Success", f"Valid YouTube video: {yt_url.title}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid YouTube link or video not accessible.\nDetails: {e}")
            return

    def clear_window(self):
        """Destroys all widgets in the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def download_ui(self):
        """Sets up the download interface."""
        self.root.title("FaceHunt - Video Download")
        tk.Label(self.root, text="Download YouTube video").pack(pady=5)
        tk.Button(self.root, text="Start Download", command=self.start_download).pack(pady=10)
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress, maximum=100)
        self.progress_bar.pack(pady=5, fill="x", padx=10)

    def next_step(self):
        if not self.validate_image:
            self.validate_image()
        if not self.validate_yt_url:
            self.validate_yt_url()
        if not (self.image_validated and self.url_validated):
            messagebox.showerror("Error", "Please validate both image and YouTube link.")
            return
        self.clear_window()
        self.download_ui()

    def start_download:
        """Starts the download using VideoDownloader."""
        downloader = VideoDownloader(self.root, self.progress, self.youtube_url.get)
        self.video_path = downloader.download()
        if self.video_path:
            messagebox.showinfo("Success", f"Video downloaded successfully: {self.video_path}")
        else:
            messagebox.showerror("Error", "Download failed. Check previous errors.")
