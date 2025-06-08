
from PyQt6.QtWidgets import QWidget

class RadarWidget(QWidget):
    def __init__(self, url):
        super().__init__()
        self.url = url
