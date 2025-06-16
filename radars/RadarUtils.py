from configs.ConfigUtils import Config
from radars.RadarProvider import RadarProvider
from radars.RainViewerRadarProvider import RainViewerRadarProvider

class ProviderKey:
    RAIN_VIEWER = 0

class RadarUtils:

    @staticmethod
    def getRadarProvider(config: Config):
        if config.wx_settings.radar_provider == ProviderKey.RAIN_VIEWER:
            return RainViewerRadarProvider(config)
        else:
            return RadarProvider()
