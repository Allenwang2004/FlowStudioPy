from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from flowstudio.flow_conf import Debug


class QDoubleDial(QDial):

    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals: int):
        super(QDoubleDial, self).__init__()
        self._multi = 10 ** decimals
        self._angleSpan = 0
        self.valueChanged.connect(self.emitDoubleValueChanged)
        self.setWrapping(False)
        self.initAssets()

    def emitDoubleValueChanged(self):
        value = float(super(QDoubleDial, self).value()) / self._multi
        self.doubleValueChanged.emit(value)
        ratio =  (self.value()*self._multi-self.minimum()) / (self.maximum()-self.minimum())
        self._angleSpan = ratio * self._maximumAngleSpan

    def initAssets(self):
        self.startAngle = 225
        self.maximumAngleSpan = -270
        self.borderOffset = 0.05
        self.dialSize = 50
        self.setMinimumSize(self.dialSize, self.dialSize)
        self.setFixedSize(self.dialSize, self.dialSize)

    def value(self):
        return float(super(QDoubleDial, self).value()) / self._multi

    def setMinimum(self, value):
        return super(QDoubleDial, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(QDoubleDial, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(QDoubleDial, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(QDoubleDial, self).singleStep()) / self._multi

    def setValue(self, value):
        super(QDoubleDial, self).setValue(int(value * self._multi))
        ratio = (self.value() * self._multi - self.minimum()) / (self.maximum() - self.minimum())
        self._angleSpan = ratio * self._maximumAngleSpan

    @property
    def startAngle(self):
        return self._startAngle / 16

    @startAngle.setter
    def startAngle(self, angle):
        self._startAngle = angle * 16

    @property
    def maximumAngleSpan(self):
        return self._maximumAngleSpan / 16

    @maximumAngleSpan.setter
    def maximumAngleSpan(self, angle):
        self._maximumAngleSpan = angle * 16

    def paintEvent(self, pe: QPaintEvent):
        # init QPainter
        painter = QPainter(self)

        # draw backgound
        painter.setBackgroundMode(Qt.OpaqueMode)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        # draw rect
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # init QPen
        arcPen = QPen()
        arcPen.setColor(QColor('gray'))
        arcPen.setWidth(3)

        comp = lambda m: (1 - 2 * m) if m < 1 else m
        self.arcRect = QRectF(self.width() * self.borderOffset, self.height() * self.borderOffset, self.width() * comp(self.borderOffset), self.height() * comp(self.borderOffset))

        # draw arc
        painter.setPen(arcPen)
        painter.drawArc(self.arcRect, self._startAngle, self._angleSpan)
        painter.end()

class QIntegerDial(QDial):

    def __init__(self):
        super().__init__()
        self.startAngle = 225
        self.maximumAngleSpan = -270
        self.borderOffset = 0.05
        self.valueChanged.connect(self.updateValue)
        self.updateValue()
        self.setWrapping(False)
        self.initAssets()

    @property
    def startAngle(self):
        return self._startAngle / 16

    @startAngle.setter
    def startAngle(self, angle):
        self._startAngle = angle * 16

    @property
    def maximumAngleSpan(self):
        return self._maximumAngleSpan / 16

    @maximumAngleSpan.setter
    def maximumAngleSpan(self, angle):
        self._maximumAngleSpan = angle * 16

    def initAssets(self):
        self.dialSize = 50
        self.setMinimumSize(self.dialSize, self.dialSize)
        self.setFixedSize(self.dialSize, self.dialSize)

    def paintEvent(self, pe: QPaintEvent):
        if Debug.DEBUG_Low_Level.value: print("paint Event")
        # init QPainter
        painter = QPainter(self)

        # draw backgound
        painter.setBackgroundMode(Qt.OpaqueMode)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        # draw rect
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # init QPen
        arcPen = QPen()
        arcPen.setColor(QColor('gray'))
        arcPen.setWidth(3)

        comp = lambda m: (1 - 2 * m) if m < 1 else m
        self.arcRect = QRectF(self.width() * self.borderOffset, self.height() * self.borderOffset, self.width() * comp(self.borderOffset), self.height() * comp(self.borderOffset))

        # draw arc
        painter.setPen(arcPen)
        painter.drawArc(self.arcRect, self._startAngle, self._angleSpan)
        painter.end()

    def updateValue(self):
        ratio =  (self.value()-self.minimum()) / (self.maximum()-self.minimum())
        self._angleSpan = ratio * self._maximumAngleSpan

    def setMinimum(self, a0: int) -> None:
        super().setMinimum(a0)
        self.updateValue()

    def setMaximum(self, a0: int) -> None:
        super().setMaximum(a0)
        self.updateValue()
