import json
import random
from typing import Any, Callable

from datetime import datetime, timedelta
from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from assets.AssetUtils import Icons
from configs.ConfigUtils import Config
from weather.WeatherProvider import WeatherProvider
from weather.WeatherData import CurrentConditionsData, DEGREE_SYM, ForecastData, WeatherDataUtils

# NOTES:
# Could add air quality
#   - https://openweathermap.org/api/air-pollution

class OpenWeatherProvider(WeatherProvider):
    def __init__(self, config: Config):
        super().__init__()
        self.location = config.app_settings.location
        self.wx_settings = config.wx_settings
        self.curr_cond_callback = None
        self.forecast_callback = None
        self.net_man = QNetworkAccessManager(self)
        self.curr_cond_reply = None
        self.forecast_reply = None

    @staticmethod
    def getIconType(owm_icon: str) -> str:
        if owm_icon == "01d":
            return Icons.CLEAR_DAY
        elif owm_icon == "01n":
            return Icons.CLEAR_NIGHT
        elif owm_icon == "02d":
            return Icons.PARTLY_CLOUDY_DAY
        elif owm_icon == "02n":
            return Icons.PARTLY_CLOUDY_NIGHT
        elif owm_icon == "03d" or owm_icon == "03n" or owm_icon == "04d" or owm_icon == "04n":
            return Icons.CLOUDY
        elif owm_icon == "09d" or owm_icon == "09n" or owm_icon == "10d" or owm_icon == "10n":
            return Icons.RAIN
        elif owm_icon == "11d" or owm_icon == "11n":
            return Icons.THUNDERSTORM
        elif owm_icon == "13d" or owm_icon == "13n":
            return Icons.SNOW
        elif owm_icon == "50d" or owm_icon == "50n":
            return Icons.FOG
        else:
            print(f"Unknown Open Weather Icon: {owm_icon}.png")
            return ""

    def getWeather(self, on_finished_callback: Callable[[list[Any]], None]):
        units = "metric" if self.wx_settings.is_metric else "imperial"

        wx_url = f"https://api.openweathermap.org/data/2.5/onecall?appid={self.wx_settings.forecast_api_key}"
        wx_url += f"&lat={self.location.latitude}&lon={self.location.longitude}"
        wx_url += f"&units={units}"
        wx_url += "&lang=en"
        wx_url += f"&r={random.random()}"
        print(f"OpenWeatherProvider.getWeather(): url: {wx_url}")
        print(f"OpenWeatherProvider.getWeather(): NOT IMPLEMENTED")


    def getForecast(self, on_finished_callback: Callable[[list[ForecastData]], None]):
        # API Doc: https://openweathermap.org/forecast5
        self.forecast_callback = on_finished_callback
        units = "metric" if self.wx_settings.is_metric else "imperial"

        wx_url = f"https://api.openweathermap.org/data/2.5/forecast?appid={self.wx_settings.forecast_api_key}"
        wx_url += f"&lat={self.location.latitude}&lon={self.location.longitude}"
        wx_url += f"&units={units}"
        wx_url += "&lang=en"
        wx_url += f"&r={random.random()}"

        # DEBUGGING
        #print(f"OpenWeatherProvider.getForecast(): url: {wx_url}")

        request = QNetworkRequest(QUrl(wx_url))
        self.forecast_reply = self.net_man.get(request)
        self.forecast_reply.finished.connect(self.forecastCallback)

    def forecastCallback(self):
        data_list = []
        if self.forecast_reply.error() != QNetworkReply.NetworkError.NoError:
            for _ in range(9):
                data_list.append(ForecastData.getErrorData(self.forecast_reply.errorString()))

        else:
            json_bytes = self.forecast_reply.readAll()
            json_string = json_bytes.data().decode("utf-8")
            if json_string == "":
                error_string = "OpenWeatherProvider.forecastCallback: Received empty JSON string for forecast."
                for _ in range(9):
                    data_list.append(ForecastData.getErrorData(error_string))
            else:
                json_obj = json.loads(json_string)

                # Fill in the next three 3-hour blocks.
                for i in range(0, 3):
                    data_list.append(self.buildHourlyDataFromJson(json_obj["list"][i]))

                # Days run 6am to 6am. Grab today.
                today = datetime.now()
                day_start = datetime(today.year, today.month, today.day, 6, 0, 0)
                # We want to butt up against tomorrow, not be tomorrow, so we do a day minus a second.
                today_seconds = (60 * 60 * 24) - 1
                day_end = day_start + timedelta(0, today_seconds)

                # Separate the entries by day.
                json_list = []
                for item in json_obj["list"]:

                    item_timestamp = datetime.fromtimestamp(item["dt"])
                    if day_start <= item_timestamp <= day_end:
                        json_list.append(item)
                    else:
                        data_list.append(self.buildDayDataFromJson(json_list))
                        json_list = []
                        json_list.append(item)
                        day_start += timedelta(1)
                        day_end += timedelta(1)

                    # If this was the last item and we haven't built a day for our list, do that.
                    if item == json_obj["list"][len(json_obj["list"]) - 1] and len(json_list) > 0:
                        data_list.append(self.buildDayDataFromJson(json_list))

        if callable(self.forecast_callback):
            self.forecast_callback(data_list)
            self.forecast_callback = None
            self.forecast_reply.close()
            self.forecast_reply = None

        else:
            print(f"OpenWeatherProvider.forecastCallback(): Missing callback.")

    def buildHourlyDataFromJson(self, json_object) -> ForecastData:
        # Grab the icon and description.
        weather = json_object["weather"][0]
        icon_type = OpenWeatherProvider.getIconType(weather["icon"])
        icon_description = weather["description"].title()

        # Build the precip string.
        precip_string = ""
        # "pop" = Probability Of Precipitation
        if "pop" in json_object:
            probability = json_object["pop"] * 100.0

            if probability > 0.0:
                precip_type = ""
                precip_accum = 0

                if "snow" in json_object:
                    precip_type = "Snow"
                    precip_accum = json_object["snow"]["3h"]
                elif "rain" in json_object:
                    precip_type = "Rain"
                    precip_accum = json_object["rain"]["3h"]

                # Precip always comes as millimeters, no matter what.
                precip_unit = "mm" if self.wx_settings.is_metric else "in"
                precip_accum = precip_accum if self.wx_settings.is_metric else WeatherDataUtils.millimetersToInches(precip_accum)
                precip_string = f"{probability:.0f}% {precip_type} {precip_accum:.2f}{precip_unit}"

        # Build the temp string.
        main = json_object["main"]
        temp = main["temp"]
        temp_unit = "C" if self.wx_settings.is_metric else "F"
        temp_string = f"{temp:.1f}{DEGREE_SYM}{temp_unit}"

        # Build the timestamp string.
        timestamp = json_object['dt']
        timestamp_string = "{0:%a %I:%M%p}".format(datetime.fromtimestamp(timestamp))

        return ForecastData(
            icon_type,
            icon_description,
            precip_string,
            temp_string,
            timestamp_string
        )

    def buildDayDataFromJson(self, json_object_list) -> ForecastData:
        if len(json_object_list) == 0:
            return ForecastData.getErrorData("Error: Empty JSON list.")

        else:
            icon_types = []
            icon_descriptions = []
            precip_prob = 0
            rain_accum = 0
            snow_accum = 0
            temp_high = -999
            temp_low = 999
            timestamp_string = ""

            for json_object in json_object_list:
                icon_types.append(json_object["weather"][0]["icon"])
                icon_descriptions.append(json_object["weather"][0]["description"].title())

                if "pop" in json_object:
                    probability = json_object["pop"] * 100.0

                    if probability > 0.0:
                        precip_prob += probability

                        if "snow" in json_object:
                            snow_accum += json_object["snow"]["3h"]
                        if "rain" in json_object:
                            rain_accum += json_object["rain"]["3h"]

                temp = json_object["main"]["temp"]
                if temp > temp_high:
                    temp_high = temp
                if temp < temp_low:
                    temp_low = temp

                if timestamp_string == "":
                    timestamp_string = "{0:%A}".format(datetime.fromtimestamp(json_object["dt"]))

            icon_type = self.getIconType(WeatherDataUtils.getMostFrequentItem(icon_types))
            icon_description = WeatherDataUtils.getMostFrequentItem(icon_descriptions)


            precip_string = ""
            precip_prob = precip_prob / len(json_object_list)
            if precip_prob > 0.0:
                precip_type = "Rain" if rain_accum > snow_accum else "Snow"
                precip_accum = rain_accum if rain_accum > snow_accum else snow_accum
                precip_unit = "mm"
                if not self.wx_settings.is_metric:
                    precip_unit = "in"
                    precip_accum = WeatherDataUtils.millimetersToInches(precip_accum)

                precip_string = f"{precip_prob:.0f}% {precip_type} {precip_accum:.2f}{precip_unit}"

            temp_unit = "C" if self.wx_settings.is_metric else "F"
            temp_string = f"{temp_high:.1f}{DEGREE_SYM}{temp_unit}/{temp_low:.1f}{DEGREE_SYM}{temp_unit}"

            return ForecastData(
                icon_type,
                icon_description,
                precip_string,
                temp_string,
                timestamp_string
            )

    def getCurrentConditions(self, on_finished_callback: Callable[[list[CurrentConditionsData]], None]):
        # API Doc: https://openweathermap.org/current
        self.curr_cond_callback = on_finished_callback
        units = "metric" if self.wx_settings.is_metric else "imperial"

        wx_url = f"http://api.openweathermap.org/data/2.5/weather?appid={self.wx_settings.forecast_api_key}"
        wx_url += f"&lat={self.location.latitude}&lon={self.location.longitude}"
        wx_url += f"&units={units}"
        wx_url += "&lang=en"
        wx_url += f"&r={str(random.random())}"
        # DEBUGGING
        #print(f"OpenWeatherProvider.getCurrentConditions(): url: {wx_url}")

        request = QNetworkRequest(QUrl(wx_url))
        self.curr_cond_reply = self.net_man.get(request)
        self.curr_cond_reply.finished.connect(self.currentConditionsCallback)

    def currentConditionsCallback(self):
        data = ""
        if self.curr_cond_reply.error() != QNetworkReply.NetworkError.NoError:
            data = CurrentConditionsData.getErrorData(self.curr_cond_reply.errorString())

        else:
            json_bytes = self.curr_cond_reply.readAll()
            json_string = json_bytes.data().decode("utf-8")
            if json_string == "":
                error_string = "OpenWeatherProvider.currentConditionsCallback: Received empty JSON string for current conditions."
                data = CurrentConditionsData.getErrorData(error_string)

            else:
                json_obj = json.loads(json_string)

                # Grab all our values from the weather JSON.
                weather = json_obj["weather"][0]
                icon_type = OpenWeatherProvider.getIconType(weather["icon"])
                icon_description = weather["description"].title()

                main = json_obj["main"]
                temp = main["temp"]
                temp_unit = "C" if self.wx_settings.is_metric else "F"
                humidity = main["humidity"]
                feels_like = main["feels_like"]

                timestamp = json_obj["dt"]
                timestamp_string = "{0:%H:%M}".format(datetime.fromtimestamp(timestamp))

                wind = json_obj["wind"]
                speed = wind["speed"]
                wind_degrees = wind["deg"]
                cardinal_dir = WeatherDataUtils.getCardinalDirectionName(wind_degrees)
                gust = wind["gust"] if "gust" in wind else None
                wind_unit = "mph"

                # Convert what we need to to metric.
                if self.wx_settings.is_metric:
                    speed = WeatherDataUtils.mphToKmh(speed)
                    wind_unit = "km/h"

                gust_string = "" if gust is None else f" gusting {gust:.1f}{wind_unit}"

                # Create the strings needed for the view.
                data = CurrentConditionsData(
                    icon_type,
                    icon_description,
                    f"{temp:.1f}{DEGREE_SYM}{temp_unit}",
                    f"Humidity {humidity}%",
                    f"Wind {cardinal_dir} {speed:.1f}{wind_unit}{gust_string}",
                    f"Feels like {feels_like:.1f}{DEGREE_SYM}{temp_unit}",
                    f"Updated at {timestamp_string} from openweathermap.org",
                    ""
                )

        if callable(self.curr_cond_callback):
            self.curr_cond_callback(data)
            self.curr_cond_callback = None
            self.curr_cond_reply.close()
            self.curr_cond_reply = None

        else:
            print("OpenWeatherProvider.currentConditionsCallback(): Missing callback.")