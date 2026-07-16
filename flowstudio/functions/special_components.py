from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QTextEdit


class textEdit_enter(QtWidgets.QTextEdit):
    enterPressed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() == Qt.NoModifier:
            self.onReturnPressed()
        else:
            super().keyPressEvent(event)

    def onReturnPressed(self):
        self.enterPressed.emit(self.toPlainText())

class ClickableLabel(QLabel):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click()
        super().mousePressEvent(event)

    def on_click(self):
        self.clicked.emit(self.text())


class SelectableTextEdit(QTextEdit):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setReadOnly(True)

    def focusOutEvent(self, event):
        # 失去焦点时清除选中
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)