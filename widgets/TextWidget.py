from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QFrame, QLabel

from configs.ConfigUtils import Config

class TextWidget(QFrame):
    class Debug:
        LONG_TEXT = "Wednesday November 28th 2025"

    class Position:
        HEADER = 0
        FOOTER = 1

    def __init__(self, position: int, config: Config):
        super().__init__()

        self.position = position
        self.app_settings = config.app_settings
        self.last_day = -1
        self.text_box = QLabel(self)
        self.text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font_mult = self.app_settings.font_mult
        if position == TextWidget.Position.HEADER:
            style = f"""
                color: {self.app_settings.color.hash_value};
                font-size: {int(64.0 * font_mult)}px;
                font-weight: normal;
            """
            self.text_box.setStyleSheet(style)

            # Setup a timer to refresh the day second.
            self.timer = QTimer()
            self.timer.timeout.connect(self.tick)
            self.timer.start(1000)

            # Call tick() once to initialize our text.
            self.tick()
        else:
            style = f"""
                color: {self.app_settings.color.hash_value};
                font-size: {int(50.0 * font_mult)}px;
                font-weight: normal;
            """
            self.text_box.setStyleSheet(style)

            location_name = self.app_settings.location.human_name
            footer_string = f"Weather for {location_name}"
            self.text_box.setText(footer_string)

    def resizeEvent(self, event: QResizeEvent):
        self.text_box.setGeometry(0, 0, event.size().width(), event.size().height())

    def tick(self):
        now = datetime.now()
        if now.day != self.last_day:
            # Grab a superscript for the day number.
            sup = 'th'
            if now.day == 1 or now.day == 21 or now.day == 31:
                sup = 'st'
            if now.day == 2 or now.day == 22:
                sup = 'nd'
            if now.day == 3 or now.day == 23:
                sup = 'rd'

            date_string = self.app_settings.date_format.format(now, sup)
            self.text_box.setText(date_string)