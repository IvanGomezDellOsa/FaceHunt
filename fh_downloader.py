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
            os.makedirs(self.output_dir, exist_ok = True)