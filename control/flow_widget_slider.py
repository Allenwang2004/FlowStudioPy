from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class QDoubleSlider(QSlider):

    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals: int, widget: QWidget):
        super(QDoubleSlider, self).__init__(widget)
        self._multi = 10 ** decimals
        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(QDoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(QDoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(QDoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(QDoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(QDoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(QDoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(QDoubleSlider, self).setValue(int(value * self._multi))