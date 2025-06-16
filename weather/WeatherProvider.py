from abc import abstractmethod
from typing import Any, Callable

from PyQt6.QtCore import QObject

from weather.WeatherData import CurrentConditionsData, ForecastData

class WeatherProvider(QObject):

    @abstractmethod
    def getWeather(self, on_finished_callback: Callable[[list[Any]], None]):
        print("WeatherProvider.getWeather() not implemented.")

    @abstractmethod
    def getForecast(self, on_finished_callback: Callable[[list[ForecastData]], None]):
        print("WeatherProvider.getForecast() not implemented.")

    @abstractmethod
    def getCurrentConditions(self, on_finished_callback: Callable[[list[CurrentConditionsData]], None]):
        print("WeatherProvider.getCurrentConditions() not implemented.")