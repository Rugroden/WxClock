from assets.AssetUtils import AssetUtils

class AppColor:
    def __init__(self, rgba: list[int], hex_value: str, hash_value: str, asset_folder: str):
        self.rgba = rgba
        self.hex_value = hex_value
        self.hash_value = hash_value
        self.asset_folder = asset_folder

    def __str__(self):
        return f"AppColor: rgba: {self.rgba}, hex: {self.hex_value}, hash: {self.hash_value}, asset_folder: {self.asset_folder}"

class AppColorUtils:
    DARK_BLUE = AppColor([17, 34, 124, 255], "0x11227C", "#11227C", "dark_blue")
    DARK_GREEN = AppColor([0, 170, 34, 255], "0x00AA22", "#00AA22", "dark_green")
    LIGHT_BLUE = AppColor([187, 238, 255, 255], "0xBBEEFF", "#BBEEFF", "light_blue")
    RED = AppColor([205, 0, 4, 255], "0xCD0004", "#CD0004", "red")
    YELLOW = AppColor([255, 166, 0, 255], "0xFFA600", "#FFA600", "yellow")


class Location:
    def __init__(self, latitude, longitude, human_name):
        self.latitude = latitude
        self.longitude = longitude
        self.human_name = human_name

    def __str__(self):
        return f"Location: {self.human_name}, ({self.latitude}, {self.longitude})"


class LocationUtils:
    ALBERT_LEA = Location(43.647801, -93.368655, "Albert Lea")
    ROCHESTER = Location(44.049846, -92.506949, "Rochester")
    WALDEN_WEST = Location(43.780689, -93.271209, "Walden West")


class AppSettings:
    def __init__(
            self,
            location: Location,
            color: AppColor,
            background_path: str,
            date_format: str = "{0:%A %B} {0.day}<sup>{1}</sup> {0.year}",
            font_family: str = "sans-serif"
    ):
        self.location = location
        self.color = color
        self.background = background_path
        self.date_format = date_format
        self.font_family = font_family


class ClockSettings:
    def __init__(
            self,
            is_digital: bool = False,              # Analog Face = False, Digital Face = True.
            digital_format: str = "{0:%I:%M %p}",  # Format for the digital clock face.
            digital_size: int = 250                # Font size for the digital clock face.
    ):
        self.is_digital = is_digital
        self.digital_format = digital_format
        self.digital_size = digital_size

class WxSettings:
    def __init__(
            self,
            is_metric: bool = False,               # Imperial = False, Metric = True.
            is_wind_degrees: bool = False,         # Cardinal = False, Degrees = True.
            forecast_provider: int = None,         # WeatherUtils.ProviderKey value.
            forecast_api_key: str = "",            # API key for that provider.
            forecast_refresh: int = 30,            # Forecast refresh time in minutes.

            radar_provider: int = None,            # RadarUtils.ProviderKey value.
            radar_api_key: str = "",               # API key for that provider
            radar_color: int = 4,                  # Rainviewer radar color style: https://www.rainviewer.com/api/color-schemes.html
            radar_refresh: int = 15,               # Radar refresh time in minutes.
            radar_smoothing: bool = False,         # Rainviewer radar smoothing.
            radar_snow: bool = False,              # Rainviewer radar shows snow as different color.
            radar_0_zoom: int = 10,                # The zoom level for the top radar.
            radar_1_zoom: int = 6,                 # The zoom level for the bottom radar.

            map_provider: int = None,              # MapUtils.ProviderKey value.
            map_api_key:str = "",                  # API key for that provider.
            marker_icon:str = "teardrop_dot.png",  # Icon for marker.
            marker_size:str = "mid",               # Size of the marker.
            show_marker:bool = False               # Show a marker on the map.
    ):
        self.is_metric = is_metric
        self.is_wind_degrees = is_wind_degrees
        self.forecast_provider = forecast_provider
        self.forecast_api_key = forecast_api_key
        self.forecast_refresh = forecast_refresh

        self.radar_provider = radar_provider
        self.radar_api_key = radar_api_key
        self.radar_refresh = radar_refresh
        self.radar_color = radar_color
        self.radar_0_zoom = radar_0_zoom
        self.radar_1_zoom = radar_1_zoom
        self.radar_smoothing = radar_smoothing
        self.radar_snow = radar_snow

        self.map_provider = map_provider
        self.map_api_key = map_api_key
        self.marker_icon = marker_icon
        self.marker_size = marker_size
        self.show_marker = show_marker

class Config:
    def __init__(
            self,
            app_settings: AppSettings,
            clock_settings: ClockSettings = ClockSettings(),
            wx_settings: WxSettings = WxSettings()
    ):
        self.app_settings = app_settings
        self.clock_settings = clock_settings
        self.wx_settings = wx_settings

    def configureBackground(self, screen_width: int, screen_height: int, background_file: str):
        self.app_settings.background = AssetUtils.getBackgroundFile(screen_width, screen_height, background_file)