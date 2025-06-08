import os
import sys
from random import random

from weather.WeatherUtils import ProviderKey
from widgets.MainWindow import MainWindow
from Config import AppColor, Config, Location, Background, AppSettings, ClockSettings, WxSettings

from PyQt6.QtWidgets import QApplication

# Setup the application.
clock_app = QApplication(sys.argv)

# Grab the screen size for background purposes.
screen_size = clock_app.primaryScreen().size()
base_dir = os.path.dirname(__file__)

app_settings = AppSettings(
    Location.ROCHESTER,
    AppColor.RED,
    Background.makePath(
        screen_size.width(),
        screen_size.height(),
        Background.DEFAULT
        )
    )
clock_settings = ClockSettings(is_digital = False)
wx_settings = WxSettings(
    forecast_provider = ProviderKey.OPEN_WEATHER,
    forecast_api_key = Config.weather_api_key,
)
config = Config(app_settings, clock_settings, wx_settings)

# Create a main window.
main_window = MainWindow(config)

# Start the bitch.
clock_app.exec()
