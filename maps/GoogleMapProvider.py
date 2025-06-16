import os
from typing import Callable

from PyQt6.QtCore import QUrl, QSize, QFile
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
        self.net_man = QNetworkAccessManager(self)
        self.on_map_callback = None
        self.reply = None

        # Things that get set when we call for a new map.
        self.latitude = 0
        self.longitude = 0
        self.zoom = 0
        self.size = QSize(0,0)

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
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom
        self.size = size

        cached_map_file = AssetUtils.getCachedMapFile(latitude, longitude, zoom, size)
        if os.path.exists(cached_map_file):
            # DEBUGGING
            print(f"Using cached map file: {cached_map_file}")
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
            print(f"GoogleMapProvider.getMap(): {map_url}")

            if self.reply is not None:
                print("GoogleMapProvider.getMap(): Aborting previous request.")
                self.reply.abort()
                self.reply = None

            request = QNetworkRequest(QUrl(map_url))
            self.reply = self.net_man.get(request)
            self.reply.finished.connect(self.mapCallback)

    def mapCallback(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(self.reply.readAll())

            # Save this to our cache.
            cache_file_name = AssetUtils.getCachedMapFile(self.latitude, self.longitude, self.zoom, self.size)
            print(f"GoogleMapProvider.mapCallback(): saving map cache: {cache_file_name}")
            cache_file = QFile(cache_file_name)
            success = pixmap.save(cache_file)

            if success:
                print(f"GoogleMapProvider.mapCallback(): map cache saved")
            else:
                print(f"GoogleMapProvider.mapCallback(): map cache not saved")

            if callable(self.on_map_callback):
                self.on_map_callback(pixmap)

            else:
                print(f"GoogleMapProvider.mapCallback(): Bad callback = {self.on_map_callback}")
