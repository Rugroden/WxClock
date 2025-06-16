import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QMainWindow

from configs.ConfigUtils import Config
from widgets.ClockWidget import ClockWidget
from widgets.CurrentConditions import CurrentConditions
from widgets.ForecastWidget import ForecastWidget
from widgets.RadarWidget import RadarWidget
from widgets.TextWidget import TextWidget


# The main layout.
#          25%        50%          25%
#       ---------------------------------
#       |       |     HEADER    |       |  10%
#  40%  |  CUR  |---------------|   F   |
#       | COND  |               |   O   |
#       |-------|               |   R   |
#       |       |               |   E   |
#  30%  |RADAR_0|     CLOCK     |   C   |
#       |       |               |   A   |
#       |-------|               |   S   |
#       |       |               |   T   |
#  30%  |RADAR_1|---------------|       |
#       |       |     FOOTER    |       |  10%
#       ---------------------------------

class MainWindow(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()

        # Set the name of the window.
        self.setWindowTitle("WxClock")

        # Build all our widgets.
        self.background_frame = QLabel()
        self.cur_cond_widget = CurrentConditions(config)
        self.radar_0_widget = RadarWidget(config, config.wx_settings.radar_0_zoom)
        self.radar_1_widget = RadarWidget(config, config.wx_settings.radar_1_zoom)
        self.header_widget = TextWidget(TextWidget.Position.HEADER, config)
        self.clock_widget = ClockWidget(config)
        self.footer_widget = TextWidget(TextWidget.Position.FOOTER, config)
        self.forecast_widget = ForecastWidget(config)

        # Left Column.
        left_column = QFrame()
        left_column_grid = QGridLayout()
        left_column_grid.setContentsMargins(0, 0, 0, 0)
        left_column_grid.addWidget(self.cur_cond_widget, 0, 0)
        left_column_grid.addWidget(self.radar_0_widget, 4, 0)
        left_column_grid.addWidget(self.radar_1_widget, 7, 0)
        # Adjust row weights.
        left_column_grid.setRowStretch(0, 4)
        left_column_grid.setRowStretch(4, 3)
        left_column_grid.setRowStretch(7, 3)
        left_column.setLayout(left_column_grid)

        # Center Column.
        center_column = QFrame()
        center_column_grid = QGridLayout()
        center_column_grid.setContentsMargins(0, 0, 0, 0)
        center_column_grid.addWidget(self.header_widget, 0, 0)
        center_column_grid.addWidget(self.clock_widget, 1, 0)
        center_column_grid.addWidget(self.footer_widget, 9, 0)
        # Adjust the row weights.
        center_column_grid.setRowStretch(0, 1)
        center_column_grid.setRowStretch(1, 8)
        center_column_grid.setRowStretch(9, 1)
        center_column.setLayout(center_column_grid)

        # Add columns.
        main_column_grid = QGridLayout()
        main_column_grid.addWidget(left_column, 0, 0)
        main_column_grid.addWidget(center_column, 0, 1)
        # The Right Column is just the Forecast.
        main_column_grid.addWidget(self.forecast_widget, 0, 2)
        # Adjust the column weights.
        main_column_grid.setColumnStretch(0, 1)
        main_column_grid.setColumnStretch(1, 2)
        main_column_grid.setColumnStretch(2, 1)
        self.background_frame.setLayout(main_column_grid)

        # Set up the background image.
        background = os.path.normpath(config.app_settings.background)
        self.background_frame.setPixmap(QPixmap(background))

        self.setCentralWidget(self.background_frame)

        # Make it full screen.
        #self.showFullScreen()
        self.show()

    def cleanup(self):
        self.clock_widget.cleanup()
        self.cur_cond_widget.cleanup()
        self.forecast_widget.cleanup()
        self.radar_0_widget.cleanup()
        self.radar_1_widget.cleanup()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F4:
            self.cleanup()
            QApplication.exit(0)


