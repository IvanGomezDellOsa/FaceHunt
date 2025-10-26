import os
import shutil
import yt_dlp
from unidecode import unidecode


class VideoDownloader:
    """Handles YouTube video download with validations."""

    def __init__(self, youtube_url):
        """
        Initialize video downloader.

        Args:
        youtube_url (str): YouTube video URL to download.
        """
        self.youtube_url = youtube_url
        self.output_dir = "videos"

    def download(self):
        """
        Download YouTube video in MP4 format at 480p resolution.

        Validates disk space before downloading.
        Skips download if video already exists.

        Returns:
            str or None: Path to downloaded video file, None on failure
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                video_title = info["title"]
                clean_title = self.sanitize_filename(video_title)
                video_file = os.path.join(self.output_dir, f"{clean_title}.mp4")

            disk_usage = shutil.disk_usage(self.output_dir)
            if disk_usage.free < 500 * 1024 * 1024:
                print("[Downloader] Insufficient disk space < 500MB.")
                return None

            if os.path.exists(video_file):
                return video_file

            ydl_opts = {
                "format": "bestvideo[height<=480][ext=mp4]/best[ext=mp4]/best",
                "outtmpl": os.path.join(self.output_dir, f"{clean_title}.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
            }

            print(f"[Downloader] Downloading: {self.youtube_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.youtube_url])

            print(f"[Downloader] Download complete: {video_file}")
            return video_file

        except Exception as e:
            print(f"[Downloader] Download failed: {str(e)}")
            return None

    @staticmethod
    def sanitize_filename(title):
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

        prohibited = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "@", "#", "%"]
        for char in prohibited:
            ascii_title = ascii_title.replace(char, "_")

        ascii_title = " ".join(ascii_title.split())
        ascii_title = ascii_title[:100]

        if not ascii_title or ascii_title.isspace():
            ascii_title = "video_download"

        return ascii_title
