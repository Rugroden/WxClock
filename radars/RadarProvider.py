from abc import abstractmethod
from typing import Callable

from PyQt6.QtCore import QObject

from radars.RadarData import RadarData, SizeData

class RadarProvider(QObject):

    @abstractmethod
    def getRadar(self, on_finished_callback: Callable[[list[RadarData]], None]):
        raise ValueError("RadarProvider.getRadar() not implemented.")

    @abstractmethod
    def setSize(self, size_data: SizeData):
        raise ValueError("RadarProvider.setSize() not implemented.")