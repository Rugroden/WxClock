import os
from datetime import datetime, timedelta

from PyQt6.QtCore import QSize

ASSETS_DIR = ""
BACKGROUNDS_DIR = "backgrounds"
ICONS_DIR = "icons"
MAP_CACHE_DIR = "map_cache"
MARKERS_DIR = "markers"
RADAR_CACHE_DIR = "radar_cache"


class Icons:
    CLEAR_DAY = "clear-day"
    CLEAR_NIGHT = "clear-night"
    CLOUDY = "cloudy"
    FOG = "fog"
    PARTLY_CLOUDY_DAY = "partly-cloudy-day"
    PARTLY_CLOUDY_NIGHT = "partly-cloudy-night"
    RAIN = "rain"
    SLEET = "sleet"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    WIND = "wind"

class AssetUtils:
    @staticmethod
    def getAssetsPath():
        return os.path.join(os.path.dirname(__file__), ASSETS_DIR)

    @staticmethod
    def getBackgroundsPath():
        return os.path.join(AssetUtils.getAssetsPath(), BACKGROUNDS_DIR)

    @staticmethod
    def getBackgroundFile(width, height, file_name):
        return f"{AssetUtils.getBackgroundsPath()}/{width}x{height}/{file_name}"

    @staticmethod
    def getMapCachePath():
        path = os.path.join(AssetUtils.getAssetsPath(), MAP_CACHE_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def getCachedMapFile(
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        base_path = AssetUtils.getMapCachePath()
        file_name = f"{latitude}_{longitude}_{zoom}_{size.width()}x{size.height()}.png"
        return os.path.join(base_path, file_name)

    @staticmethod
    def getMarkersPath():
        path = os.path.join(AssetUtils.getAssetsPath(), MARKERS_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def getMarkerFile(name: str):
        base_path = AssetUtils.getMarkersPath()
        file_name = f"{name}.png"
        return os.path.join(base_path, file_name)

    @staticmethod
    def getRadarCachePath():
        path = os.path.join(AssetUtils.getAssetsPath(), RADAR_CACHE_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def getCachedRadarFile(
            timestamp: int,
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        base_path = AssetUtils.getRadarCachePath()
        file_name = f"{timestamp}_{latitude}_{longitude}_{zoom}_{size.width()}x{size.height()}.png"
        return os.path.join(base_path, file_name)

    @staticmethod
    def clearRadarCache():
        cache_path = AssetUtils.getRadarCachePath()
        if os.path.exists(cache_path):
            now = datetime.now()
            for file_name in os.listdir(cache_path):
                file_name_parts = file_name.split("_")
                file_time = datetime.fromtimestamp(int(file_name_parts[0]))
                # We can delete anything that is older than 2 hours.
                if file_time + timedelta(hours = 2) < now:
                    os.remove(os.path.join(cache_path, file_name))

    @staticmethod
    def getColorPath(assets_color):
        return os.path.join(AssetUtils.getAssetsPath(), assets_color)

    @staticmethod
    def getIconsPath(assets_color):
        return os.path.join(AssetUtils.getColorPath(assets_color), ICONS_DIR)

    @staticmethod
    def getIcon(assets_color, icon):
        return os.path.join(AssetUtils.getIconsPath(assets_color), icon)