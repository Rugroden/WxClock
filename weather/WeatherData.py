from assets.AssetUtils import Icons

DEGREE_SYM = "°"

class CurrentConditionsData:
    def __init__(
            self,
            icon_type: str,
            icon_description: str,
            temp: str,
            humidity: str,
            wind: str,
            feels_like_temp: str,
            attribution: str,
            extra: str = ""
    ):
        self.icon_type = icon_type
        self.icon_description = icon_description
        self.temp = temp
        self.humidity = humidity
        self.wind = wind
        self.feels_like_temp = feels_like_temp
        self.attribution = attribution
        self.extra = extra

    @staticmethod
    def getErrorData(error: str):
        return CurrentConditionsData(
                    Icons.THUNDERSTORM,
                    error,
                    "Network Error",
                    "",
                    "",
                    "",
                    "",
                    ""
                )

    @staticmethod
    def getDebugData():
        return CurrentConditionsData(
                    Icons.THUNDERSTORM,
                    "Thunderstorm",
                    "55.9°F",
                    "Humidity 94%",
                    "Wind NW 19.6mph",
                    "Feels like 55.6°F",
                    "19:09 weather.site",
                    ""
                )


class ForecastData:
    def __init__(
            self,
            icon_type: str,
            icon_description: str,
            precip: str,
            temp: str,
            day_time: str
    ):
        self.icon_type = icon_type
        self.icon_description = icon_description
        self.precip = precip
        self.temp = temp
        self.day_time = day_time

    @staticmethod
    def getErrorData(error: str):
        return ForecastData(
            Icons.THUNDERSTORM,
            error,
            "Network Error",
            "",
            ""
        )

    @staticmethod
    def getDebugData():
        return ForecastData(
            Icons.THUNDERSTORM,
            "Thunderstorm",
            "100% Rain 1.5in",
            "74/56°F",
            "Sunday 12:34 PM"
        )

class WeatherDataUtils:
    @staticmethod
    def fahrenheitToCelsius(fahrenheit: float | int) -> float:
        return (fahrenheit - 32) / 1.8

    @staticmethod
    def mphToKmh(mph: float | int) -> float:
        return mph * 0.621371192

    @staticmethod
    def mpsToKmh(mps: float | int) -> float:
        """meters per second to kilometers per hour conversion"""
        return mps * 3.6

    @staticmethod
    def pressureToInches(mb: float | int) -> float:
        return mb * 0.029530

    @staticmethod
    def inchesToMillimeters(inches: float | int) -> float:
        return inches * 25.4

    @staticmethod
    def millimetersToInches(millimeters: float | int) -> float:
        return millimeters / 25.4

    @staticmethod
    def barometricToMillimeters(inches: float | int) -> float:
        return inches * 25.4

    @staticmethod
    def getCardinalDirectionName(wind_direction: float | int) -> str:
        cardinal_direction = 'N'
        if wind_direction > 22.5:
            cardinal_direction = 'NE'
        if wind_direction > 67.5:
            cardinal_direction = 'E'
        if wind_direction > 112.5:
            cardinal_direction = 'SE'
        if wind_direction > 157.5:
            cardinal_direction = 'S'
        if wind_direction > 202.5:
            cardinal_direction = 'SW'
        if wind_direction > 247.5:
            cardinal_direction = 'W'
        if wind_direction > 292.5:
            cardinal_direction = 'NW'
        if wind_direction > 337.5:
            cardinal_direction = 'N'
        return cardinal_direction

    @staticmethod
    def getMostFrequentItem(item_list: list[str]) -> str:
        # This function is used for forecasts to get the most common icon and description.
        # List to dict[key, counts].
        item_dict = dict((i, item_list.count(i)) for i in item_list)
        # Sort by counts.
        sorted_dict = sorted(item_dict, key=item_dict.get, reverse=True)
        # Get first (most counted) item.
        if len(sorted_dict):
            return sorted_dict[0]
        else:
            return ""