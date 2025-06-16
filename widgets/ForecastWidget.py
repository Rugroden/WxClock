from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import AppColor, Config
from weather.WeatherData import ForecastData
from weather.WeatherUtils import WeatherUtils

#           33%         67%
#       -----------------------------
#       |       | DESCRIPTION       |
#       | ICON  | PRECIP%/ TEMP     |
#       |       |          DAY/TIME |
#       -----------------------------

class ForecastEntryWidget(QFrame):
    def __init__(self, config: Config):
        super().__init__()

        # Store the app color for icons as they change.
        self.app_color = config.app_settings.color

        # Build a style for our views.
        font_mult = config.app_settings.font_mult
        text_style = f"color: {self.app_color.hash_value};"
        desc_font_size = f"font-size: {28.0 * font_mult}px;\nfont-weight: normal;"
        precip_font_size = f"font-size: {24.0 * font_mult}px;\nfont-weight: normal;"
        temp_font_size = f"font-size: {24.0 * font_mult}px;\nfont-weight: normal;"
        day_font_size = f"font-size: {20.0 * font_mult}px;\nfont-weight: light;"

        self.icon_frame = QLabel(self)
        self.icon_frame.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.description_frame = QLabel(self)
        self.description_frame.setStyleSheet(f"{text_style}{desc_font_size}")
        self.description_frame.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.precip_frame = QLabel(self)
        self.precip_frame.setStyleSheet(f"{text_style}{precip_font_size}")
        self.precip_frame.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.temp_frame = QLabel(self)
        self.temp_frame.setStyleSheet(f"{text_style}{temp_font_size}")
        self.temp_frame.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.day_frame = QLabel(self)
        self.day_frame.setStyleSheet(f"{text_style}{day_font_size}")
        self.day_frame.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.addWidget(self.icon_frame)

        inner_frame = QFrame(self)
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(self.description_frame)
        inner_layout.addWidget(self.precip_frame)

        temp_day_frame = QFrame(self)
        temp_day_layout = QHBoxLayout()
        temp_day_layout.setContentsMargins(0, 0, 0, 0)
        temp_day_layout.addWidget(self.temp_frame)
        temp_day_layout.addWidget(self.day_frame)
        temp_day_layout.setStretch(0, 2)
        temp_day_layout.setStretch(2, 2)
        temp_day_frame.setLayout(temp_day_layout)

        inner_layout.addWidget(temp_day_frame)

        inner_frame.setLayout(inner_layout)
        layout.addWidget(inner_frame)
        layout.setStretch(0, 1)
        layout.setStretch(1, 2)

        self.setLayout(layout)

    def onUpdatedData(self, data: ForecastData):
        icon_asset = AssetUtils.getIcon(self.app_color.asset_folder, data.icon_type)
        icon_pixmap = QPixmap(icon_asset)
        width = self.icon_frame.width()
        height = self.icon_frame.height()
        icon_pixmap = icon_pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.icon_frame.setPixmap(icon_pixmap)
        self.description_frame.setText(data.icon_description)

        if data.precip == "":
            self.precip_frame.setText(data.temp)
            self.temp_frame.setText("")

        else:
            self.precip_frame.setText(data.precip)
            self.temp_frame.setText(data.temp)

        self.day_frame.setText(data.day_time)


class ForecastWidget(QFrame):
    def __init__(self, config: Config):
        super().__init__()
        # Store the weather provider.
        self.weather_provider = WeatherUtils.getWeatherProvider(config)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for i in range(9):
            layout.addWidget(ForecastEntryWidget(config))

        self.setLayout(layout)

        # Fire a fetch once, then set up a timer.
        QTimer.singleShot(0, self.getForecast)

        self.timer = QTimer()
        self.timer.timeout.connect(self.getForecast)
        self.timer.start(config.wx_settings.forecast_refresh * 60 * 1000)

    def getForecast(self):
        self.weather_provider.getForecast(self.onUpdatedData)

    def onUpdatedData(self, data_list: list[ForecastData]):
        count = min(self.layout().count(), len(data_list))
        for i in range(count):
            forecast_entry_widget = self.layout().itemAt(i).widget()
            data = data_list[i]
            forecast_entry_widget.onUpdatedData(data)

    def cleanup(self):
        self.timer.stop()