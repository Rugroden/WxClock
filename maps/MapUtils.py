from maps.MapProvider import MapProvider

class MapData:
    def __init__(self):
        return

class ProviderKey:
    GOOGLE_MAP = 0

class MapUtils:
    @staticmethod
    def getRadarProvider(config):
        if config.wx_settings.radar_provider == ProviderKey.GOOGLE_MAP:
            return GoogleMapProvider(config)
        else:
            return MapProvider()