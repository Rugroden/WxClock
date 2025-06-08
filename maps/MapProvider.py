from abc import abstractmethod

class MapProvider:
    @abstractmethod
    def getMap(self, on_finished_callback):
        print("getMap() not implemented.")