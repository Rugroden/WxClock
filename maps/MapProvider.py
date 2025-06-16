from abc import abstractmethod
from typing import Callable

from PyQt6.QtCore import QObject, QSize
from PyQt6.QtGui import QPixmap


class MapProvider(QObject):

    @abstractmethod
    def getMap(
            self,
            callback: Callable[[QPixmap], None],
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        print("MapProvider.getMap() not implemented.")