from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import AppColor, Config
from weather.WeatherUtils import WeatherUtils
from weather.WeatherData import CurrentConditionsData

#                  40%
#       ---------------------------
#       |        |       |        |
#  40%  |        | icon  |        |
#       |        |_______|        |
#  12%  |       Description       |
#  18%  |          Temp           |
#   6%  |        Humidity         |
#   6%  |          Wind           |
#   6%  |     Feels Like Temp     |
#   6%  |       Attribution       |
#   6%  |       (pressure)        |
#       ---------------------------

class CurrentConditions(QFrame):
    def __init__(self, config: Config):
        super().__init__()

        # Store the app color for icons as they change.
        self.app_color = config.app_settings.color
        # Store the weather provider.
        self.weather_provider = WeatherUtils.getWeatherProvider(config)

        # Build a style for our views.
        text_style = f"color: {self.app_color.hash_value};"
        attribution_font_size = "font-size: 20px;\nfont-weight: light;"
        regular_font_size = "font-size: 30px;\nfont-weight: normal;"
        desc_font_size = "font-size: 40px;\nfont-weight: normal;"
        temp_font_size = "font-size: 80px;\nfont-weight: normal;\nfont-family: sans-serif;"

        # Create our child widgets.
        self.icon_frame = QLabel(self)
        self.icon_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_desc_frame = QLabel(self)
        self.icon_desc_frame.setStyleSheet(f"{text_style}\n{desc_font_size}")
        self.icon_desc_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.temp_frame = QLabel(self)
        self.temp_frame.setStyleSheet(f"{text_style}\n{temp_font_size}")
        self.temp_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.humidity_frame = QLabel(self)
        self.humidity_frame.setStyleSheet(f"{text_style}\n{regular_font_size}")
        self.humidity_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.wind_frame = QLabel(self)
        self.wind_frame.setStyleSheet(f"{text_style}\n{regular_font_size}")
        self.wind_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.feels_like_temp_frame = QLabel(self)
        self.feels_like_temp_frame.setStyleSheet(f"{text_style}\n{regular_font_size}")
        self.feels_like_temp_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.extra_frame = QLabel(self)
        self.extra_frame.setStyleSheet(f"{text_style}\n{regular_font_size}")
        self.extra_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.attribution_frame = QLabel(self)
        self.attribution_frame.setStyleSheet(f"{text_style}\n{attribution_font_size}")
        self.attribution_frame.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Build our layout.
        layout = QVBoxLayout()
        layout.addWidget(self.icon_frame)
        layout.addWidget(self.icon_desc_frame)
        layout.addWidget(self.temp_frame)
        layout.addWidget(self.humidity_frame)
        layout.addWidget(self.wind_frame)
        layout.addWidget(self.feels_like_temp_frame)
        layout.addWidget(self.extra_frame)
        layout.addWidget(self.attribution_frame)
        # Adjust the weights.
        layout.setStretch(0, 40)
        layout.setStretch(1, 12)
        layout.setStretch(2, 18)
        layout.setStretch(3, 6)
        layout.setStretch(4, 6)
        layout.setStretch(5, 6)
        layout.setStretch(6, 6)
        layout.setStretch(7, 6)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Fire a fetch once, then set up a timer.
        QTimer.singleShot(0, self.getCurrentConditions)

        self.timer = QTimer()
        self.timer.timeout.connect(self.getCurrentConditions)
        self.timer.start(config.wx_settings.forecast_refresh * 60 * 1000)

    def getCurrentConditions(self):
        self.weather_provider.getCurrentConditions(self.onUpdatedData)

    def onUpdatedData(self, data: CurrentConditionsData):
        icon_asset = AssetUtils.getIcon(self.app_color.asset_folder, data.icon_type)
        icon_pixmap = QPixmap(icon_asset)
        width = self.icon_frame.width()
        height = self.icon_frame.height()
        icon_pixmap = icon_pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.icon_frame.setPixmap(icon_pixmap)
        self.icon_desc_frame.setText(data.icon_description)
        self.temp_frame.setText(data.temp)
        self.humidity_frame.setText(data.humidity)
        self.wind_frame.setText(data.wind)
        self.feels_like_temp_frame.setText(data.feels_like_temp)
        self.extra_frame.setText(data.extra)
        self.attribution_frame.setText(data.attribution)

    def cleanup(self):
        self.timer.stop()