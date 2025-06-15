from abc import abstractmethod

from PyQt6.QtCore import QObject, QSize


class MapProvider(QObject):
    @abstractmethod
    def getMap(
            self,
            callback,
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        print("getMap() not implemented.")