import math
import os

from PyQt6.QtCore import QSize, QSizeF, Qt, QTimer
from PyQt6.QtGui import QPixmap, QResizeEvent, QColor, QImage, QRgba64
from PyQt6.QtWidgets import QFrame, QLabel, QStackedLayout, QSizePolicy

import DebugUtils
from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import Config
from maps.MapUtils import MapUtils
from radars.RadarData import RadarData, SizeData
from radars.RadarUtils import RadarUtils


class RadarWidget(QFrame):
    def __init__(self, config: Config, zoom: int):
        super().__init__()

        location = config.app_settings.location
        self.latitude = location.latitude
        self.longitude = location.longitude
        self.show_map = config.wx_settings.show_map
        self.map_provider = MapUtils.getMapProvider(config)
        self.radar_provider = RadarUtils.getRadarProvider(config)
        self.radar_refresh = config.wx_settings.radar_refresh
        self.radar_data_index = 0
        self.radar_data_list = []
        self.zoom = zoom
        self.file_zoom = zoom

        self.map_frame = QLabel()
        self.radar_frame = QLabel()

        self.marker_frame = QLabel()
        self.show_marker = config.wx_settings.show_map and config.wx_settings.show_marker
        if self.show_marker:
            self.marker_image = QImage(AssetUtils.getMarkerFile("teardrop_dot"))
            # Color the stupid marker.
            app_color = config.app_settings.color.rgba
            (acr, acg, acb, aca) = QColor.fromRgb(app_color[0], app_color[1], app_color[2], app_color[3]).getRgbF()
            for x in range (0, self.marker_image.width()):
                for y in range (0, self.marker_image.height()):
                    (r, g, b, a)= self.marker_image.pixelColor(x, y).getRgbF()
                    r = r * acr
                    g = g * acg
                    b = b * acb
                    self.marker_image.setPixel(x, y, QColor.fromRgbF(r, g, b, a).rgba())

            self.marker_frame.setPixmap(QPixmap.fromImage(self.marker_image))
            self.marker_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.current_marker = self.marker_image

        layout = QStackedLayout()
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        layout.addWidget(self.map_frame)
        layout.addWidget(self.radar_frame)
        layout.addWidget(self.marker_frame)
        self.setLayout(layout)

        if self.radar_refresh > 0:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.tick)
            self.animation_timer.start(1000)

            self.radar_fetch_timer = QTimer()

    def getShrunkenSize(self, size: QSize) -> QSize:
        temp_size = size
        if size.width() > 640 or size.height() > 640:
            temp_size = QSizeF(size.width() / 2, size.height() / 2).toSize()
            if self.zoom == self.file_zoom:
                self.file_zoom -= 1

        return temp_size

    def setMap(self, map_pixmap: QPixmap):
        cached_map_file = AssetUtils.getCachedMapFile(
            self.latitude,
            self.longitude,
            self.file_zoom,
            map_pixmap.size()
        )
        if not os.path.exists(cached_map_file):
            map_pixmap.save(cached_map_file)

        if map_pixmap.size() != self.size():
            map_pixmap = map_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.map_frame.setPixmap(map_pixmap)

    def resizeEvent(self, event: QResizeEvent):
        # On resize we kick off our map and radar stuff.
        size = self.getShrunkenSize(event.size())

        if self.show_map:
            self.map_provider.getMap(
                self.setMap,
                self.latitude,
                self.longitude,
                self.file_zoom,
                size
            )

        if self.radar_refresh > 0:
            # Now that our sizes are set, we can set up the radar provider.
            size_data = SizeData(self.file_zoom, size)
            self.radar_provider.setSize(size_data)

            # Now that we have everything setup, we can fetch once and setup the timer.
            self.getRadar()
            self.radar_fetch_timer.timeout.connect(self.getRadar)
            self.radar_fetch_timer.start(self.radar_refresh * 60 * 1000)

        if self.show_marker:
            marker_scaled_size = math.ceil(size.height() / 5)
            print(f"marker_scaled_size: {marker_scaled_size}")
            self.current_marker = self.marker_image.scaled(marker_scaled_size, marker_scaled_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.marker_frame.setPixmap(QPixmap.fromImage(self.current_marker))

    def getRadar(self):
        self.radar_provider.getRadar(self.onRadar)

    def onRadar(self, radar_data_list: list[RadarData]):
        self.radar_data_list = radar_data_list

    def tick(self):
        if len(self.radar_data_list) > 0:
            radar_data = self.radar_data_list[self.radar_data_index]
            radar_pixmap = QPixmap()
            radar_pixmap.load(radar_data.file_path)
            self.radar_frame.setPixmap(radar_pixmap)
            self.radar_data_index += 1
            self.radar_data_index %= len(self.radar_data_list)

    def cleanup(self):
        if self.radar_refresh > 0:
            self.animation_timer.stop()
            self.radar_fetch_timer.stop()