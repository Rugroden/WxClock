from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap


class SizeData:
    def __init__(self, zoom: int, size: QSize):
        self.zoom = zoom
        self.size = size

class TilePathData:
    def __init__(self, timestamp: int, path: str):
        self.timestamp = timestamp
        self.path = path

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class TileUrlsData:
    def __init__(self, timestamp: int, urls: list[str]):
        self.timestamp = timestamp
        self.urls = urls

    def __lt__(self, other):
        return self.timestamp < other.timestamp

class RadarData:
    def __init__(self, timestamp: int, image: QPixmap):
        self.timestamp = timestamp
        self.image = image

    def __lt__(self, other):
        return self.timestamp < other.timestamp