import os
import shutil
import yt_dlp
from unidecode import unidecode
from tkinter import messagebox


class VideoDownloader:
    """Handles YouTube video download with progress tracking and validation."""

    def __init__(self, root, progress_var, youtube_url):
        """
        Initialize video downloader.

        Args:
            root: Tkinter root window for UI updates
            progress_var: DoubleVar for progress bar updates
            youtube_url: YouTube URL to download
        """
        self.root = root
        self.progress_var = progress_var
        self.youtube_url = youtube_url
        self.output_dir = "videos"

    def download(self):
        """
        Download YouTube video in MP4 format at 480p resolution.

        Validates disk space and permissions before downloading.
        Skips download if video already exists.

        Returns:
            str or None: Path to downloaded video file, None on failure
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                video_title = info['title']
                clean_title = self.sanitize_filename(video_title)
                video_file = os.path.join(self.output_dir, f"{clean_title}.mp4")

            estimated_size = info.get('filesize_approx', 0)
            if not estimated_size:
                estimated_size = 800 * 1024 * 1024  # 800 MB default estimate

            disk_usage = shutil.disk_usage(self.output_dir)
            if disk_usage.free < estimated_size * 1.1:  # +10% safety margin
                messagebox.showerror("Error",f"Insufficient disk space. Need at least {estimated_size / (1024 * 1024):.0f} MB.")
                return None
            if not os.access(self.output_dir, os.W_OK):
                messagebox.showerror("Error", "No write permissions in videos directory.")
                return None

            if os.path.exists(video_file):
                return video_file

            ydl_opts = {
                'format': 'bestvideo[height<=480][ext=mp4]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.output_dir, f'{clean_title}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,
                'quiet': True
            }

            self.progress_var.set(0)
            print("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.youtube_url])
            return video_file
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            return None

    def sanitize_filename(self, title):
        """
        Convert video title to safe ASCII filename.

        Removes special characters, limits length to 100 chars,
        and ensures result is valid for all operating systems.

        Args:
            title: Original video title
        Returns:
            str: Sanitized filename
        """
        ascii_title = unidecode(title)

        prohibited = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '@', '#', '%']
        for char in prohibited:
            ascii_title = ascii_title.replace(char, '_')

        ascii_title = ' '.join(ascii_title.split())
        ascii_title = ascii_title[:100]

        if not ascii_title or ascii_title.isspace():
            ascii_title = "video_download"

        return ascii_title

    def progress_hook(self, d):
        """
        Update progress bar during download.
        Args:
            d: Progress dictionary from yt-dlp
        """
        if d['status'] == 'downloading':
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(progress)
                self.root.update()
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.root.update()
