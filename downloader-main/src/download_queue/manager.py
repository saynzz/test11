from typing import List
from threading import Thread
from src.downloader import VideoDownloader
from core.types import PRESETS

class DownloadQueue:
    def __init__(self):
        self.queue: List[str] = []
        self.downloader = VideoDownloader()
        self.preset = PRESETS["720p"]

    def add_to_queue(self, url: str):
        self.queue.append(url)

    def start_download(self):
        for url in self.queue:
            Thread(target=self.downloader.download, args=(url, self.preset)).start()
        self.queue.clear()