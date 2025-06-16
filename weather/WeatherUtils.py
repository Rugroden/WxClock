from configs.ConfigUtils import Config
from weather.OpenWeatherProvider import OpenWeatherProvider
from weather.WeatherProvider import WeatherProvider

class ProviderKey:
    OPEN_WEATHER = 0

class WeatherUtils:

    @staticmethod
    def getWeatherProvider(config: Config) -> WeatherProvider:
        if config.wx_settings.forecast_provider == ProviderKey.OPEN_WEATHER:
            return OpenWeatherProvider(config)
        else:
            return WeatherProvider()

