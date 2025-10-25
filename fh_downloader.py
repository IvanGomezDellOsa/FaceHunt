import os
import shutil
import yt_dlp
from unidecode import unidecode
import tempfile


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
        self.cookie_file = None

    def _setup_cookies(self):
        """
        Set up YouTube cookies from environment variable if available.

        Returns:
            str or None: Path to temporary cookie file, None if no cookies available
        """
        youtube_cookies = os.environ.get("YOUTUBE_COOKIES")

        if youtube_cookies:
            try:
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".txt"
                )
                temp_file.write(youtube_cookies)
                temp_file.close()
                self.cookie_file = temp_file.name
                print("[Downloader] Using YouTube cookies")
                return self.cookie_file
            except Exception as e:
                print(f"[Downloader] Error setting  cookies: {e}")
                return None
        else:
            print(
                "[Downloader] No cookies (YOUTUBE_COOKIES) found, continuing without them"
            )
            return None

    def _cleanup_cookies(self):
        """Remove temporary cookie file if it exists."""
        if self.cookie_file and os.path.exists(self.cookie_file):
            try:
                os.unlink(self.cookie_file)
                self.cookie_file = None
            except Exception as e:
                print(f"[Downloader] Error deleting temporary cookies:{e}")

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

            cookie_file = self._setup_cookies()

            basic_opts = {"quiet": True}
            if cookie_file:
                basic_opts["cookiefile"] = cookie_file

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                video_title = info["title"]
                clean_title = self.sanitize_filename(video_title)
                video_file = os.path.join(self.output_dir, f"{clean_title}.mp4")

            disk_usage = shutil.disk_usage(self.output_dir)
            if disk_usage.free < 500 * 1024 * 1024:
                print("[Downloader] Insufficient disk space < 500MB.")
                self._cleanup_cookies()
                return None

            if os.path.exists(video_file):
                return video_file

            ydl_opts = {
                "format": "bestvideo[height<=480][ext=mp4]/best[ext=mp4]/best",
                "outtmpl": os.path.join(self.output_dir, f"{clean_title}.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
                },
            }

            if cookie_file:
                ydl_opts["cookiefile"] = cookie_file

            print(f"[Downloader] Downloading: {self.youtube_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.youtube_url])

            print(f"[Downloader] Download complete: {video_file}")
            return video_file

        except Exception as e:
            print(f"[Downloader] Download failed: {str(e)}")
            return None
        finally:
            self._cleanup_cookies()

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
