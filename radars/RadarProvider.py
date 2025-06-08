from abc import abstractmethod

class ProviderKey:
    RAIN_VIEWER = 0

class RadarProvider:
    @abstractmethod
    def getRadar(self, on_finished_callback):
        print("getRadar() not implemented.")