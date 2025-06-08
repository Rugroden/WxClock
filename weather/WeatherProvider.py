from abc import abstractmethod

from PyQt6.QtCore import QObject

class WeatherProvider(QObject):
    @abstractmethod
    def getWeather(self, on_finished_callback):
        print("getWeather() not implemented.")
    @abstractmethod
    def getForecast(self, on_finished_callback):
        print("getForecast() not implemented.")
    @abstractmethod
    def getCurrentConditions(self, on_finished_callback):
        print("getCurrentConditions() not implemented.")