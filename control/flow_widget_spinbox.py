from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class IntNumberBox(QSpinBox):

    def __init__(self):
        super().__init__()

        self.grMaximum = 256
        self.grMinimum = -256
        self.grTravel = self.grMaximum - self.grMinimum

        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setFrame(False)
        editor = self.lineEdit()
        editor.installEventFilter(self)

    def setMaximum(self, max: int) -> None:
        super().setMaximum(max)
        self.valueScale = self.maximum() - self.minimum()

    def setMinimum(self, min: int) -> None:
        super().setMinimum(min)
        self.valueScale = self.maximum() - self.minimum()

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:

        if source is self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                self.pressHandle(event)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.releaseHandle(event)
                return True
            elif event.type() == QEvent.MouseMove:
                self.moveHandle(event)
                return True
            else:
                return False
        else:
            return QWidget.eventFilter(self, source, event)

    def pressHandle(self, event):
        if event.buttons() == Qt.LeftButton:
            self.value_at_press = self.value()
            self.pos_at_press = event.pos()
            self.lineEdit().setCursor(QCursor(Qt.SizeVerCursor))

    def releaseHandle(self, event):
        if event.button() == Qt.LeftButton:
            self.value_at_press = None
            self.pos_at_press = None
            self.lineEdit().setCursor(QCursor(Qt.IBeamCursor))
            return

    def moveHandle(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        if self.pos_at_press is None:
            return

        deltaTraveled = self.pos_at_press.y() - event.pos().y()
        if deltaTraveled >= self.grMaximum: deltaTraveled = self.grMaximum
        elif deltaTraveled <= self.grMinimum: deltaTraveled = self.grMinimum

        val = deltaTraveled * 2 * self.valueScale / self.grTravel

        self.setValue(self.value_at_press + val)


class DoubleNumberBox(QDoubleSpinBox):

    def __init__(self):
        super().__init__()

        self.grMaximum = 256
        self.grMinimum = -256
        self.grTravel = self.grMaximum - self.grMinimum

        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setFrame(False)
        editor = self.lineEdit()
        editor.installEventFilter(self)

    def setMaximum(self, max: float) -> None:
        super().setMaximum(max)
        self.valueScale = self.maximum() - self.minimum()

    def setMinimum(self, min: float) -> None:
        super().setMinimum(min)
        self.valueScale = self.maximum() - self.minimum()

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:

        if source is self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                self.pressHandle(event)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.releaseHandle(event)
                return True
            elif event.type() == QEvent.MouseMove:
                self.moveHandle(event)
                return True
            else:
                return False
        else:
            return QWidget.eventFilter(self, source, event)

    def pressHandle(self, event):
        if event.buttons() == Qt.LeftButton:
            self.value_at_press = self.value()
            self.pos_at_press = event.pos()
            self.lineEdit().setCursor(QCursor(Qt.SizeVerCursor))

    def releaseHandle(self, event):
        if event.button() == Qt.LeftButton:
            self.value_at_press = None
            self.pos_at_press = None
            self.lineEdit().setCursor(QCursor(Qt.IBeamCursor))
            return

    def moveHandle(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        if self.pos_at_press is None:
            return

        deltaTraveled = self.pos_at_press.y() - event.pos().y()
        if deltaTraveled >= self.grMaximum:
            deltaTraveled = self.grMaximum
        elif deltaTraveled <= self.grMinimum:
            deltaTraveled = self.grMinimum

        val = deltaTraveled * 2 * self.valueScale / self.grTravel

        self.setValue(self.value_at_press + val)


class PreviewSpinBox(QSpinBox):

   def focusInEvent(self, event):
       super().focusInEvent(event)
       self.parent().parent().trigger_preview_click_logic()

class PreviewDoubleSpinBox(QDoubleSpinBox):

   def focusInEvent(self, event):
       super().focusInEvent(event)
       self.parent().parent().trigger_preview_click_logic()