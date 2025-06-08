from radars.RadarProvider import RadarProvider

class RadarData:
    def __init__(self):
        return

class ProviderKey:
    RAIN_VIEWER = 0

class RadarUtils:
    @staticmethod
    def getRadarProvider(config):
        if config.wx_settings.radar_provider == ProviderKey.RAIN_VIEWER:
            return RainViewerProvider(config)
        else:
            return RadarProvider()
