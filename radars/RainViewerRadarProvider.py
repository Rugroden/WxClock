import json
import os

from datetime import datetime
from PyQt6.QtCore import QSize, QUrl, QFile
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from typing import Callable

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import Config
from radars.MercatorProjection import LatLng, Utils
from radars.RadarData import RadarData, TilePathData, TileUrlsData, SizeData
from radars.RadarProvider import RadarProvider

class RainViewerRadarProvider(RadarProvider):
    def __init__(self, config: Config):
        super().__init__()

        # Things we can set now and hold onto.
        location = config.app_settings.location
        self.latitude = location.latitude
        self.longitude = location.longitude
        self.app_color = config.app_settings.color.rgba
        self.radar_color = config.wx_settings.radar_color
        self.radar_snow = 1 if config.wx_settings.radar_snow else 0
        self.radar_smoothing = 1 if config.wx_settings.radar_smoothing else 0
        self.frame_count = 10  # Number of radar images to hold onto.
        self.net_man = QNetworkAccessManager(self)

        # Things we will get or build later.
        self.callback = None
        self.current_timestamp_index = 0
        self.current_url_index = 0
        self.reply = None
        self.rect_size = QSize(0,0)
        self.radar_data_list = []
        self.tile_image_list = []
        self.tile_urls_data_list = []
        self.tile_path_list = []
        self.timestamp_list = []
        self.zoom = 10

        # Stuff for combining the tiles into a single image.
        self.corner_tiles = {}
        self.tiles_width = 0
        self.total_width = 0
        self.x_list = []
        self.tiles_height = 0
        self.total_height = 0
        self.y_list = []

    def setSize(self, size_data: SizeData):
        self.zoom = size_data.zoom
        self.rect_size = size_data.size
        corners = Utils.getCorners(
            LatLng(self.latitude, self.longitude),
            self.zoom,
            self.rect_size.width(),
            self.rect_size.height()
        )
        self.corner_tiles = {
            "NW": Utils.getTileXY(LatLng(corners["N"], corners["W"]), self.zoom),
            "NE": Utils.getTileXY(LatLng(corners["N"], corners["E"]), self.zoom),
            "SE": Utils.getTileXY(LatLng(corners["S"], corners["E"]), self.zoom),
            "SW": Utils.getTileXY(LatLng(corners["S"], corners["W"]), self.zoom)
        }

        for y in range(int(self.corner_tiles["NW"]["Y"]), int(self.corner_tiles["SW"]["Y"]) + 1):
            self.y_list.append(y)
            self.total_height += 256
            self.tiles_height += 1

        for x in range(int(self.corner_tiles["NW"]["X"]), int(self.corner_tiles["NE"]["X"]) + 1):
            self.x_list.append(x)
            self.total_width += 256
            self.tiles_width += 1

    def getRadar(self, callback: Callable[[list[RadarData]], None]):
        """
        For RainVeiwer, we need to kick of a series of things before we can return the radar images.
        So here we will grab a main json file to get valid timestamps.
        Then we kick it to a function that will build all the required tile urls.
        Then we cycle over them and build our radar images.
        Once they are all done we finally can return the radar images.
        We need to cache timestamps though so we don't re pull images every time we refresh.
        """
        self.callback = callback
        url = "https://api.rainviewer.com/public/weather-maps.json"
        request = QNetworkRequest(QUrl(url))
        self.reply = self.net_man.get(request)
        self.reply.finished.connect(self.onTimestamps)

    def onTimestamps(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            json_bytes = self.reply.readAll()
            json_string = json_bytes.data().decode("utf-8")
            if json_string == "":
                print(f"JSON string is empty for Rain Viewer timestamp reply: {self.reply.url()}")
                return
            json_obj = json.loads(json_string)

            host = json_obj["host"]

            # The timestamps in the reply JSON are ordered oldest (0) to newest (len - 1).
            # We want the out data lists to also be ordered oldest (0) to newest (len - 1).
            # That way they can animate in order.
            item_list = json_obj["radar"]["past"]

            # Grab the list length so we know where to start inserting new items to.
            insert_index = len(self.tile_path_list)
            added_item = False
            # We reverse the list, so that we can grab the newest items first.
            for item in reversed(item_list):
                item_timestamp = item["time"]
                item_path = item["path"]

                # We only need to add items to our list if the newest items aren't in the list.
                if item_timestamp not in self.timestamp_list:
                    tile_path_data = TilePathData(item_timestamp, item_path)
                    self.timestamp_list.insert(insert_index, item_timestamp)
                    self.tile_path_list.insert(insert_index, tile_path_data)

                    if insert_index > 0:
                        insert_index -= 1

                else:
                    break

            # Sort the things and then prune off any older entries.
            # We can also prune old cache images.
            self.timestamp_list.sort()
            self.tile_path_list.sort()
            while len(self.timestamp_list) > self.frame_count:
                timestamp = self.timestamp_list.pop(0)
                self.tile_path_list.pop(0)
                radar_file_name = AssetUtils.getCachedRadarFile(timestamp, self.latitude, self.longitude, self.zoom, self.rect_size)
                if os.path.exists(radar_file_name):
                    os.remove(radar_file_name)

            # Now we can build all the actual urls we need.
            for item in self.tile_path_list:
                url_list = []
                for y in self.y_list:
                    for x in self.x_list:
                        url = f"{host}{item.path}/{Utils.MERCATOR_RANGE}/"
                        url += f"{self.zoom}/{x}/{y}/{self.radar_color}/{self.radar_smoothing}_{self.radar_snow}.png"

                        url_list.append(url)

                entry = TileUrlsData(item.timestamp, url_list)
                self.tile_urls_data_list.append(entry)

            # Sort the thing and then prune off any older entries.
            self.tile_urls_data_list.sort()
            while len(self.tile_urls_data_list) > self.frame_count:
                self.tile_urls_data_list.pop(0)

            self.getTilesForTimestamps(0, 0)

    def getTilesForTimestamps(
            self,
            timestamp_index: int,
            tile_url_index: int
    ):
        self.timestamp_index = timestamp_index
        self.tile_url_index = tile_url_index

        # If we are over out timestamp list length, we have all the things, and we can finally kick it back.
        if self.timestamp_index >= len(self.timestamp_list):
            # Sort it because I was too lazy to ensure things were added in order.
            self.radar_data_list.sort()
            while len(self.radar_data_list) > self.frame_count:
                self.radar_data_list.pop(0)

            if callable(self.callback):
                self.callback(self.radar_data_list)
                self.callback = None

            else:
                print(f"OpenWeatherProvider.currentConditionsCallback(): Bad callback = {self.callback}")

        else:
            # Otherwise we walk through our entry list to fetch build the tile images.
            entry = self.tile_urls_data_list[self.timestamp_index]

            # We can skip entries whose timestamps already exist in our radar_data_list.
            skip_entry = False
            for radar_data in self.radar_data_list:
                if radar_data.timestamp == entry.timestamp:
                    skip_entry = True
                    break

            radar_file_name = AssetUtils.getCachedRadarFile(entry.timestamp, self.latitude, self.longitude, self.zoom, self.rect_size)
            if not skip_entry and os.path.exists(radar_file_name):
                radar_data = RadarData(entry.timestamp, radar_file_name)
                self.radar_data_list.append(radar_data)
                skip_entry = True

            if skip_entry:
                # We already have this image, so we don't need to re pull it.
                # DEBUGGING
                print(f"skipping radar pull for {entry.timestamp}")
                self.getTilesForTimestamps(self.timestamp_index + 1, 0)

            else:
                # Otherwise we fetch this tile.
                url = entry.urls[self.tile_url_index]
                #print(f"pulling timestamp {entry.timestamp} : {url}")
                request = QNetworkRequest(QUrl(url))
                self.reply = self.net_man.get(request)
                self.reply.finished.connect(self.onTile)

            #for entry in self.tile_urls_data_list:
            #    print(f"timestamp {entry.timestamp} urls: {len(entry.urls)}")
                #urls = entry["urls"]
                #for url in urls:
                #    print(f"    {url}")



    def onTile(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            tile_image = QImage()
            tile_image.loadFromData(self.reply.readAll())
            self.tile_image_list.append(tile_image)

            self.tile_url_index += 1

            # If we still have tiles to grab, grab em.
            if self.tile_url_index < len(self.tile_urls_data_list[self.timestamp_index].urls):
                self.getTilesForTimestamps(self.timestamp_index, self.tile_url_index)

            else:
                # Otherwise we combine our tiles and move on to the next timestamp.
                self.combineTiles()
                self.getTilesForTimestamps(self.timestamp_index + 1, 0)

    def combineTiles(self):

        radar_image = QImage(self.tiles_width * Utils.MERCATOR_RANGE, self.tiles_height * Utils.MERCATOR_RANGE, QImage.Format.Format_ARGB32)

        painter = QPainter()
        painter.begin(radar_image)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(QFont("Arial", 10))

        tile_index = 0
        x_offset = self.corner_tiles["NW"]["X"]
        x_offset = int((int(x_offset) - x_offset) * Utils.MERCATOR_RANGE)
        y_offset = self.corner_tiles["NW"]["Y"]
        y_offset = int((int(y_offset) - y_offset) * Utils.MERCATOR_RANGE)

        for y in range(0, self.total_height, Utils.MERCATOR_RANGE):
            for x in range(0, self.total_width, Utils.MERCATOR_RANGE):
                if self.tile_image_list[tile_index].format() == QImage.Format.Format_ARGB32:
                    painter.drawImage(x, y, self.tile_image_list[tile_index])

                tile_index += 1

        painter.end()
        self.tile_image_list = []

        radar_image_2 = radar_image.copy(-x_offset, -y_offset, self.rect_size.width(), self.rect_size.height())
        painter = QPainter()
        painter.begin(radar_image_2)
        timestamp = self.timestamp_list[self.timestamp_index]
        timestamp_string = "{0:%H:%M} rainvewer.com".format(datetime.fromtimestamp(timestamp))
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(QFont("Arial", 10))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawText(5, 13, timestamp_string)
        painter.end()

        radar_pixmap = QPixmap(radar_image_2)
        radar_file_name = AssetUtils.getCachedRadarFile(timestamp, self.latitude, self.longitude, self.zoom, self.rect_size)
        cache_file = QFile(radar_file_name)
        radar_pixmap.save(cache_file)

        radar_data = RadarData(timestamp, radar_file_name)
        self.radar_data_list.append(radar_data)