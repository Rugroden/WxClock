import os

from PyQt6.QtCore import QSize

ASSETS_DIR = "assets"
BACKGROUNDS_DIR = "backgrounds"
ICONS_DIR = "icons"
MAP_CACHE_DIR = "map_cache"
TILE_CACHE_DIR = "tile_cache"


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
    def getMapCachePath():
        return os.path.join(AssetUtils.getAssetsPath(), MAP_CACHE_DIR)

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
    def getTileCachePath():
        return os.path.join(AssetUtils.getAssetsPath(), TILE_CACHE_DIR)

    @staticmethod
    def getCachedTileFile(
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        base_path = AssetUtils.getTileCachePath()
        file_name = f"{latitude}_{longitude}_{zoom}_{size.width()}x{size.height()}.png"
        return os.path.join(base_path, file_name)

    @staticmethod
    def getColorPath(assets_color):
        return os.path.join(AssetUtils.getAssetsPath(), assets_color)

    @staticmethod
    def getIconsPath(assets_color):
        return os.path.join(AssetUtils.getColorPath(assets_color), ICONS_DIR)

    @staticmethod
    def getIcon(assets_color, icon):
        return os.path.join(AssetUtils.getIconsPath(assets_color), icon)