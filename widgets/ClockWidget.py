import os

from datetime import datetime
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QPixmap, QResizeEvent, QTransform
from PyQt6.QtWidgets import QFrame, QLabel

from assets.AssetUtils import AssetUtils
from configs.ConfigUtils import Config


class ClockWidget(QFrame):
    def __init__(self, config: Config):
        super().__init__()

        app_settings = config.app_settings
        self.clock_settings = config.clock_settings
        # last_time_string is for knowing when to update the digital clock.
        self.last_time_string = ""
        # These are for knowing what to update in the analog clock.
        self.last_minute = -1
        self.last_hour = -1

        if self.clock_settings.is_digital:
            # The digital clock is a single text widget
            self.clock_text_frame = QLabel(self)
            style = f"""
                color: {app_settings.color.hash_value};
                font-family: {app_settings.font_family};
                font-size: {self.clock_settings.digital_size * app_settings.font_mult}px;
                font-weight: light;
            """
            self.clock_text_frame.setStyleSheet(style)
            self.clock_text_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        else:
            # Grab the assets, but don't draw them.
            # We resize the assets in resizeEvent().
            # Then we draw them there and on tick().
            assets_folder = AssetUtils.getColorPath(app_settings.color.asset_folder)
            self.clock_face_pixmap =  QPixmap(os.path.normpath(assets_folder + "/clock_face.png"))
            self.hour_hand_pixmap =   QPixmap(os.path.normpath(assets_folder + "/hour_hand.png"))
            self.minute_hand_pixmap = QPixmap(os.path.normpath(assets_folder + "/min_hand.png"))
            self.second_hand_pixmap = QPixmap(os.path.normpath(assets_folder + "/sec_hand.png"))

            # Create the widgets for the assets.
            self.clock_face_frame = QLabel(self)
            self.clock_face_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hour_hand_frame = QLabel(self)
            self.hour_hand_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.minute_hand_frame = QLabel(self)
            self.minute_hand_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.second_hand_frame = QLabel(self)
            self.second_hand_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Setup a timer to refresh the clock every second.
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def resizeEvent(self, event: QResizeEvent):
        # Now that we know how big we are, we can resize and draw our stuff.
        width = event.size().width()
        height = event.size().height()

        if self.clock_settings.is_digital:
            self.clock_text_frame.setGeometry(0, 0, width, height)

        else:
            # Find the narrowest dimension, and that will be our square.
            clock_dims = min(width, height)

            # Resize the clock face.
            self.clock_face_pixmap = self.clock_face_pixmap.scaled(
                QSize(clock_dims, clock_dims),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.clock_face_frame.setPixmap(self.clock_face_pixmap)
            self.clock_face_frame.setGeometry(0, 0, width, height)

            # Resize the second hand.
            self.second_hand_pixmap = self.second_hand_pixmap.scaled(
                QSize(clock_dims, clock_dims),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.second_hand_frame.setPixmap(self.second_hand_pixmap)
            self.second_hand_frame.setGeometry(0, 0, width, height)

            # Resize the minute hand.
            self.minute_hand_pixmap = self.minute_hand_pixmap.scaled(
                QSize(clock_dims, clock_dims),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.minute_hand_frame.setPixmap(self.minute_hand_pixmap)
            self.minute_hand_frame.setGeometry(0, 0, width, height)

            # Resize the hour hand.
            self.hour_hand_pixmap = self.hour_hand_pixmap.scaled(
                QSize(clock_dims, clock_dims),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.hour_hand_frame.setPixmap(self.hour_hand_pixmap)
            self.hour_hand_frame.setGeometry(0, 0, width, height)

    def tick(self):
        now = datetime.now()
        if self.clock_settings.is_digital:
            time_string = self.clock_settings.digital_format.format(now)
            if self.clock_settings.digital_format.find("%I") > -1:
                if time_string[0] == '0':
                    time_string = time_string[1:99]
            if self.last_time_string != time_string:
                self.clock_text_frame.setText(time_string)
            self.last_time_string = time_string

        else:
            # The second hand always gets updated.
            second_angle = now.second * 6
            second_hand_pixmap = self.second_hand_pixmap.transformed(
                QTransform().rotate(second_angle),
                Qt.TransformationMode.SmoothTransformation
            )
            self.second_hand_frame.setPixmap(second_hand_pixmap)

            if self.last_minute != now.minute:
                self.last_minute = now.minute
                minute_angle = now.minute * 6
                minute_hand_pixmap = self.minute_hand_pixmap.transformed(
                    QTransform().rotate(minute_angle),
                    Qt.TransformationMode.SmoothTransformation
                )
                self.minute_hand_frame.setPixmap(minute_hand_pixmap)

                hour_angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
                hour_hand_pixmap = self.hour_hand_pixmap.transformed(
                    QTransform().rotate(hour_angle),
                    Qt.TransformationMode.SmoothTransformation
                )
                self.hour_hand_frame.setPixmap(hour_hand_pixmap)

    def cleanup(self):
        self.timer.stop()