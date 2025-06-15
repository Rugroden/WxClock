from Config import Config
from maps.GoogleMapProvider import GoogleMapProvider
from maps.MapProvider import MapProvider

class MapData:
    def __init__(self):
        return

class ProviderKey:
    GOOGLE_MAP = 0

class MapUtils:
    @staticmethod
    def getMapProvider(config: Config) -> MapProvider:
        if config.wx_settings.map_provider == ProviderKey.GOOGLE_MAP:
            return GoogleMapProvider(config)
        else:
            return MapProvider()