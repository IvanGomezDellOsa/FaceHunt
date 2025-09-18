import os
import shutil
import yt_dlp
from tkinter import messagebox


class VideoDownloader:
    def __init__(self, root, progress_var, youtube_url):
        self.root = root
        self.progress_var = progress_var
        self.youtube_url = youtube_url
        self.output_dir = "videos"

    def download(self):
        """Downloads the video in MP4/720p with multiple download control."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            # Extract metadata from the video
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                video_title = info['title']
                video_file = f"{self.output_dir}/{video_title}.mp4"

            estimated_size = info.get('filesize_approx', 0)
            if not estimated_size:
                estimated_size = 800 * 1024 * 1024  # 800 MB if info.get fails

            # Check disk space
            disk_usage = shutil.disk_usage(self.output_dir)
            if disk_usage.free < estimated_size * 1.1:  # %10+
                messagebox.showerror("Error",
                                     f"Insufficient disk space. Need at least {estimated_size / (1024 * 1024)} MB.")
                return None
            if not os.access(self.output_dir, os.W_OK):
                messagebox.showerror("Error", "No write permissions in videos directory.")
                return None

            # Avoid multiple downloads
            if os.path.exists(video_file):
                return video_file

            # Download options
            ydl_opts = {
                'format': 'bestvideo[height<=480][ext=mp4]/best[ext=mp4]/best', # DeepFace works well with 480p
                'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
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

    def progress_hook(self, d):
        """Update the progress bar during the download."""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(progress)
                self.root.update()
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.root.update()
