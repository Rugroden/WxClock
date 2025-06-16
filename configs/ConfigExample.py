from configs.ConfigUtils import AppColorUtils, AppSettings, ClockSettings, Config, LocationUtils, WxSettings
from maps.MapUtils import ProviderKey as MapProviderKey
from radars.RadarUtils import ProviderKey as RadarProviderKey
from weather.WeatherUtils import ProviderKey as WeatherProviderKey

# Copy this file to the root directory.
# Rename it to Config.py
# Update the settings objects to fit your needs.
# Details on each objects settings can be found in ./ConfigUtils.py

app_settings = AppSettings(
    location = LocationUtils.ROCHESTER,
    color = AppColorUtils.RED,
    background_path = "default.jpg",
    date_format = "{0:%A %B} {0.day}<sup>{1}</sup> {0.year}",
    font_family = "sans-serif"
)

clock_settings = ClockSettings(
    is_digital = False,
    digital_format = "{0:%I:%M %p}",
    digital_size = 250
)

wx_settings = WxSettings(
    is_metric = False,
    is_wind_degrees = False,
    forecast_provider = WeatherProviderKey.OPEN_WEATHER,
    forecast_api_key = "OpenWeatherMapAPIKey",
    forecast_refresh = 30,

    radar_provider = RadarProviderKey.RAIN_VIEWER,
    radar_api_key = "RainViewerAPIKey",
    radar_color = 4,
    radar_refresh = 15,
    radar_smoothing = True,
    radar_snow = True,
    radar_0_zoom = 10,
    radar_1_zoom = 6,

    map_provider = MapProviderKey.GOOGLE_MAP,
    map_api_key = "GoogleMapAPIKey",
    marker_icon = "teardrop_dot.png",
    marker_size = "mid",
    show_marker = True
)

config = Config(
    app_settings,
    clock_settings,
    wx_settings
)
