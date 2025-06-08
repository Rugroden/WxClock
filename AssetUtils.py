import os

ASSETS_DIR = "assets"
BACKGROUNDS_DIR = "backgrounds"
ICONS_DIR = "icons"

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
    def getColorPath(assets_color):
        return os.path.join(AssetUtils.getAssetsPath(), assets_color)

    @staticmethod
    def getIconsPath(assets_color):
        return os.path.join(AssetUtils.getColorPath(assets_color), ICONS_DIR)

    @staticmethod
    def getIcon(assets_color, icon):
        return os.path.join(AssetUtils.getIconsPath(assets_color), icon)