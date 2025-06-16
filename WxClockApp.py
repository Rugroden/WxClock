import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication

import Config
from assets.AssetUtils import AssetUtils

from widgets.MainWindow import MainWindow


# Setup the application.
clock_app = QApplication(sys.argv)
QApplication.setOverrideCursor(QCursor(Qt.CursorShape.BlankCursor))

# Grab the screen size for background purposes.
screen_size = clock_app.primaryScreen().size()
base_dir = os.path.dirname(__file__)

config = Config.config
backgound_file = config.app_settings.background
config.configureBackground(
    screen_size.width(),
    screen_size.height(),
    backgound_file
)

AssetUtils.clearRadarCache()

# Create a main window.
main_window = MainWindow(config)

# Start the bitch.
clock_app.exec()
