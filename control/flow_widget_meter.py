from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class QMeter(QWidget):

    clickedValue = pyqtSignal(int)

    def __init__(self, steps, height = 100, width = 100):
        super().__init__()

        self._height = height
        self._width = width

        self.value = 1

        self.initResolution(steps)
        self.initAssets()


    def initResolution(self, steps):

        if isinstance(steps, list):
            # list of colours.
            self.n_steps = len(steps)
            self.steps = steps

        elif isinstance(steps, int):
            # int number of bars, defaults to yellow.
            self.n_steps = steps
            self.steps = ['red'] * steps

        else:
            raise TypeError('steps must be a list or int')

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_value):
        self._height = new_value
        self.update()

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_value):
        self._width = new_value
        self.update()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value < 0:
            self._value = 0
        elif new_value > 1:
            self._value = 1
        else:
            self._value = new_value

        self.update()

    def initAssets(self):
        self._bar_solid_percent = 0.75
        self._background_color = QColor('black')

        self._meter_padding = 5
        self._disp_padding = 5

        self.step_size = self.height / self.n_steps

        self.bar_width = self.step_size * self._bar_solid_percent
        self.bar_spacer = self.step_size * (1 - self._bar_solid_percent) / 2

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        #painter.begin(self)
        # TODO: this will cause an error flag in macs

        # draw background
        background_brush = QBrush()
        background_brush.setColor(QColor('black'))
        background_brush.setStyle(Qt.SolidPattern)
        background_rect = QRect(0, 0, self.width, self.height)
        #print("parent", (0, 0, self.meter_height, self.meter_width))
        painter.fillRect(background_rect, background_brush)

        self.n_steps_to_draw = int(self.value * self.n_steps)

        # draw meter
        meter_brush = QBrush()
        meter_brush.setStyle(Qt.SolidPattern)
        for n in range(self.n_steps_to_draw):
            meter_brush.setColor(QColor(self.steps[n]))
            # print(0, (self.n_steps - n - 1) * self.step_size, self.meter_width, self.bar_width)
            meter_rect = QRect(0, (self.n_steps - n - 1) * self.step_size + self.bar_spacer, self.width, self.bar_width)
            painter.fillRect(meter_rect, meter_brush)

        painter.end()

    def sizeHint(self):
        return QSize(self.width, self.height)

    def _trigger_refresh(self):
        self.update()

    # def _calculate_clicked_value(self, e):
    #     # print(e.x(), e.y(), ceil(e.x()/self.step_size))
    #     self.value = 1 - (floor(e.y() / self.step_size ) / self.n_steps)
    #     print(self.value)
    #     # print(self.value)
    #     self.update()

    # def mouseMoveEvent(self, e):
    #     self._calculate_clicked_value(e)
    #
    # def mousePressEvent(self, e):
    #     self._calculate_clicked_value(e)

    def setBarPadding(self, i):
        self._disp_padding = int(i)
        self.update()

    def setBarSolidPercent(self, f):
        self._bar_solid_percent = float(f)
        self.update()