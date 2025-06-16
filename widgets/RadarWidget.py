import os

from PyQt6.QtCore import QSize, QSizeF, Qt, QTimer
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QFrame, QLabel, QStackedLayout

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import Config, Location
from maps.MapUtils import MapUtils
from radars.RadarData import RadarData, SizeData
from radars.RadarUtils import RadarUtils


class RadarWidget(QFrame):
    def __init__(self, config: Config, zoom: int):
        super().__init__()

        location = config.app_settings.location
        self.latitude = location.latitude
        self.longitude = location.longitude
        self.map_provider = MapUtils.getMapProvider(config)
        self.radar_provider = RadarUtils.getRadarProvider(config)
        self.radar_refresh = config.wx_settings.radar_refresh
        self.radar_data_index = 0
        self.radar_data_list = []
        self.zoom = zoom
        self.file_zoom = zoom

        self.map_frame = QLabel(self)
        self.radar_frame = QLabel(self)

        layout = QStackedLayout(self)
        layout.addWidget(self.map_frame)
        layout.addWidget(self.radar_frame)
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        layout.setCurrentWidget(self.radar_frame)
        self.setLayout(layout)

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
        self.map_provider.getMap(
            self.setMap,
            self.latitude,
            self.longitude,
            self.file_zoom,
            size
        )

        # Now that our sizes are set, we can set up the radar provider.
        size_data = SizeData(self.file_zoom, size)
        self.radar_provider.setSize(size_data)

        # Now that we have everything setup, we can fetch once and setup the timer.
        self.getRadar()
        self.radar_fetch_timer.timeout.connect(self.getRadar)
        self.radar_fetch_timer.start(self.radar_refresh * 60 * 1000)

    def getRadar(self):
        self.radar_provider.getRadar(self.onRadar)

    def onRadar(self, radar_data_list: list[RadarData]):
        self.radar_data_list = radar_data_list

    def tick(self):
        if len(self.radar_data_list) > 0:
            radar_data = self.radar_data_list[self.radar_data_index]
            self.radar_frame.setPixmap(radar_data.image)
            self.radar_data_index += 1
            self.radar_data_index %= len(self.radar_data_list)

    def cleanup(self):
        self.animation_timer.stop()
        self.radar_fetch_timer.stop()