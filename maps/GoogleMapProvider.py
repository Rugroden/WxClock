import os
from typing import Callable

from PyQt6.QtCore import QUrl, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import Config
from maps.MapProvider import MapProvider

class GoogleMapProvider(MapProvider):
    def __init__(self, config: Config):
        super().__init__()
        self.api_key = config.wx_settings.map_api_key
        self.app_color = config.app_settings.color.hex_value
        self.show_marker = config.wx_settings.show_marker
        self.marker_size = config.wx_settings.marker_size
        self.on_map_callback = None
        self.net_man = QNetworkAccessManager(self)

    def getMap(
            self,
            callback: Callable[[QPixmap], None],
            latitude: float,
            longitude: float,
            zoom: int,
            size: QSize
    ):
        # API Docs: https://developers.google.com/maps/documentation/maps-static/start.
        self.on_map_callback = callback

        cached_map_file = AssetUtils.getCachedMapFile(latitude, longitude, zoom, size)
        if os.path.exists(cached_map_file):
            # DEBUGGING
            #print(f"Using cached map file: {cached_map_file}")
            callback(QPixmap(cached_map_file))

        else:
            map_url = f"http://maps.googleapis.com/maps/api/staticmap?key={self.api_key}"
            map_url += f"&center={latitude},{longitude}"
            map_url += f"&zoom={zoom}"
            map_url += f"&size={size.width()}x{size.height()}"
            map_url += f"&maptype=hybrid"
            if self.show_marker:
                map_url += f"&markers=size:{self.marker_size}|color:{self.app_color}|{latitude},{longitude}"
            # DEBUGGING
            #print(f"GoogleMapProvider.getMap(): {map_url}")

            self.net_man.finished.connect(self.mapCallback)
            request = QNetworkRequest(QUrl(map_url))
            self.net_man.get(request)

    def mapCallback(self, reply: QNetworkReply):
        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())

        if callable(self.on_map_callback):
            self.on_map_callback(pixmap)
            self.on_map_callback = None

        else:
            print(f"GoogleMapProvider.mapCallback(): Bad callback = {self.on_map_callback}")
