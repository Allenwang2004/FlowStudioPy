from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt


class ClickOnlyComboBox(QComboBox):
    def __init__(self):
        super().__init__()

    def wheelEvent(self, event):
        event.ignore()  # Ignore the scroll wheel events


class PreviewComboBox(QComboBox):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().parent().trigger_preview_click_logic()
        super().mousePressEvent(event)
