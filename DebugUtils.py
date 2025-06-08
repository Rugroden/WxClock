from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QFrame, QWidget


class ColoredFrame(QFrame):
    def __init__(self, rgba: list | str):
        super().__init__()
        DebugUtils.setWidgetColor(self, rgba)

class DebugUtils:
    @staticmethod
    def setWidgetColor(widget: QWidget, rgba: list | str):
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        if isinstance(rgba, list):
            palette.setColor(QPalette.ColorRole.Window, QColor(rgba[0], rgba[1], rgba[2], rgba[3]))
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(rgba))
        widget.setPalette(palette)
