import pyqtgraph as pg
import numpy as np
from PyQt5.QtGui import *


class base(pg.PlotWidget):

    def __init__(self, widget):
        super().__init__(widget)
        pg.setConfigOptions(antialias=True)
        self.plotItem.hideButtons()
        self.initAssets()

    @property
    def viewbox(self):
        return self.plotItem.getViewBox()

    def initAssets(self):
        self.viewbox.setMenuEnabled(False)
        self.viewbox.setMouseEnabled(False, False)

        font = QFont('Calibri')

        self.btm_axis = self.plotItem.getAxis('bottom')
        self.top_axis = self.plotItem.getAxis('top')
        self.left_axis = self.plotItem.getAxis('left')
        self.right_axis = self.plotItem.getAxis('right')
        self.btm_axis.setTicks([])
        self.top_axis.setTicks([])
        self.left_axis.setTicks([])
        self.right_axis.setTicks([])
        self.btm_axis.show()
        self.top_axis.show()
        self.left_axis.show()
        self.right_axis.show()

        self.btm_axis.setTickFont(font)
        self.left_axis.setTickFont(font)
        self.top_axis.setTickFont(font)
        self.right_axis.setTickFont(font)


class filter(base):
    frequency_ticks = [[(np.log10(20), '20'), (np.log10(40), '40'), (np.log10(80), '80'), (np.log10(150), '150'),
                        (np.log10(300), '300'), (np.log10(600), '600'), (np.log10(1200), '1.2k'),
                        (np.log10(2500), '2.5k'), (np.log10(5000), '5k'), (np.log10(10000), '10k'),
                        (np.log10(22000), '22k')]]
    magnitude_ticks = [[(-40, '-40'), (-20, '-20'), (0, '0'), (20, '20'), (40, '40')]]
    phase_ticks = [[(1, '180'), (0.5, '90'), (0, '0'), (-0.5, '-90'), (-1, '-180')]]

    def __init__(self, widget):
        super().__init__(widget)
        self.initChildAxis()

    def initAssets(self):
        super().initAssets()
        self.plotItem.setLogMode(x=True, y=None)
        self.plotItem.showGrid(True, True, 0.2)

        self.viewbox.setXRange(np.log10(20), np.log10(22000), 0, True)
        self.viewbox.setYRange(-40, 40, 0, True)

        self.btm_axis.setTicks(self.frequency_ticks)
        self.left_axis.setTicks(self.magnitude_ticks)
        self.right_axis.setTicks(self.phase_ticks)

    def initChildAxis(self):
        p2 = pg.ViewBox(self.viewbox)
        self.right_axis.linkToView(p2)
        p2.setMenuEnabled(False)
        p2.setMouseEnabled(False, False)
        p2.setYRange(-1, 1, 0, True)


class spectrum(base):
    frequency_ticks = [[(np.log10(20), '20'), (np.log10(40), '40'), (np.log10(80), '80'), (np.log10(150), '150'),
                        (np.log10(300), '300'), (np.log10(600), '600'), (np.log10(1200), '1.2k'),
                        (np.log10(2500), '2.5k'), (np.log10(5000), '5k'), (np.log10(10000), '10k'),
                        (np.log10(22000), '22k')]]
    magnitude_ticks = [
        [(-160, '-160'), (-140, '-140'), (-120, '-120'), (-100, '-100'), (-80, '-80'), (-60, '-60'), (-40, '-40'),
         (-20, '-20'), (0, '0'), (20, '20')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.plotItem.showGrid(True, True, 0.2)
        self.plotItem.setLogMode(x=True, y=None)
        self.viewbox.setXRange(np.log10(20), np.log10(22000), 0, True)
        self.viewbox.setYRange(-160, 20, 0, True)
        self.btm_axis.setTicks(self.frequency_ticks)
        self.left_axis.setTicks(self.magnitude_ticks)


class octaveBandAnalyzer(base):
    frequency_ticks = [
        [(1, '20'), (2, '25'), (3, '31.5'), (4, '40'), (5, '50'), (6, '63'), (7, '80'), (8, '100'), (9, '125'),
         (10, '160'), (11, '200'), (12, '250'), (13, '315'), (14, '400'), (15, '500'), (16, '630'), (17, '800'),
         (18, '1k'), (19, '1.2k'), (20, '1.6k'), (21, '2k'), (22, '2.5k'), (23, '3.1k'), (24, '4k'), (25, '5k'),
         (26, '6.3k'), (27, '8k'), (28, '10k'), (29, '12.5k'), (30, '16k'), (31, '20k')]]
    magnitude_ticks = [
        [(0, '-120'), (20, '-100'), (40, '-80'), (60, '-60'), (80, '-40'), (100, '-20'), (120, '0'), (140, '20')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.viewbox.setXRange(0, 32, 0, True)
        self.viewbox.setYRange(0, 140, 0, True)
        self.btm_axis.setTicks(self.frequency_ticks)
        self.left_axis.setTicks(self.magnitude_ticks)


class waveform(base):
    amplitude_ticks = [[(-1, '-1'), (-0.5, '-0.5'), (0, '0'), (0.5, '0.5'), (1, '1')]]
    sample_ticks = [[
        (48000 * 0, '0'),
        (48000 * 1, '1'),
        (48000 * 2, '2'),
        (48000 * 3, '3'),
        (48000 * 4, '4'),
        (48000 * 5, '5'),
        (48000 * 6, '6'),
        (48000 * 7, '7'),
        (48000 * 8, '8'),
        (48000 * 9, '9'),
        (48000 * 10, '10'),
    ]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.viewbox.setMenuEnabled(True)
        self.viewbox.setMouseEnabled(True, True)
        self.viewbox.setXRange(0, 480000, 0, True)
        self.viewbox.setYRange(-1, 1, 0, True)
        self.btm_axis.setTicks(self.sample_ticks)
        self.left_axis.setTicks(self.amplitude_ticks)


class drc_computer(base):
    input_ticks = [
        [(-120, '-120'), (-100, '-100'), (-80, '-80'), (-60, '-60'), (-40, '-40'), (-20, '-20'), (0, '0'), (20, '20'),  (40, '40')]]
    output_ticks = [
        [(-120, '-120'), (-100, '-100'), (-80, '-80'), (-60, '-60'), (-40, '-40'), (-20, '-20'), (0, '0'), (20, '20'),  (40, '40')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.plotItem.showGrid(True, True, 0.1)
        self.viewbox.setXRange(-120, 40, 0, True)
        self.viewbox.setYRange(-120, 40, 0, True)

        self.btm_axis.setTicks(self.input_ticks)
        self.left_axis.setTicks(self.output_ticks)

        self.right_axis.setStyle(tickTextOffset=-25)

    def setXYRange(self, x_min, x_max, y_min, y_max):
        self.viewbox.setXRange(x_min, x_max, 0, True)
        self.viewbox.setYRange(y_min, y_max, 0, True)


class gain_reduction(base):
    output_ticks = [[(120, '-120'), (100, '-100'), (80, '-80'), (60, '-60'), (40, '-40'), (20, '-20'), (0, '0')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.viewbox.invertY(True)

        self.viewbox.setXRange(0.5, 1.5, 0, True)
        self.viewbox.setYRange(0, 120, 0, True)

        self.right_axis.setTicks(self.output_ticks)

        self.left_axis.setStyle(tickTextOffset=-25)

    def setViewBoxMinimum(self, y_min):
        self.viewbox.setYRange(0, -y_min, 0, True)

    def setMoreTicks(self):
        output_ticks = [[(120, '-120'), (110, '-110'), (100, '-100'), (90, '-90'), (80, '-80'),
                         (70, '-70'), (60, '-60'), (50, '-50'), (40, '-40'), (30, '-30'), (20, '-20'),
                         (10, '-10'), (0, '0')]]
        self.right_axis.setTicks(output_ticks)

class meter(base):
    magnitude_ticks = [
        [(0, '-120'), (10, '-100'), (23, '-80'), (39, '-60'), (58, '-40'), (80, '-20'), (105, '0'), (133, '20')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.viewbox.setXRange(0.5, 1.5, 0, True)
        self.viewbox.setYRange(0, 133, 0, True)
        self.right_axis.setTicks(self.magnitude_ticks)
        self.right_axis.setTickFont(QFont("Arial", 8))
        self.left_axis.setStyle(tickTextOffset=-10)


class In_Out_Meter(base):
    magnitude_ticks = [
        [(0, '-120'), (10, '-100'), (23, '-80'), (39, '-60'), (58, '-40'), (80, '-20'), (105, '0'), (133, '20')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.viewbox.setXRange(0.5, 1.5, 0, True)
        self.viewbox.setYRange(0, 133, 0, True)
        self.right_axis.setTicks(self.magnitude_ticks)
        self.right_axis.setTickFont(QFont("Arial", 8))
        self.left_axis.setStyle(tickTextOffset=0)


class signal_filter(base):
    x_axis = [
        [(0, '0.0'), (1, '1.0'), (2, '2.0'), (3, '3.0'), (4, '4.0'), (5, '5.0'), (6, '6.0'), (7, '7.0'), (8, '8.0')]]
    y_axis = [[(-2, '-2.0'), (-1, '-1.0'), (0, '0.0'), (1, '1.0'), (2, '2.0')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        font = QFont("Times", 12)
        self.viewbox.setXRange(-0.2, 8.2, 0, True)
        self.viewbox.setYRange(-2.2, 2.2, 0, True)
        self.btm_axis.setTicks(self.x_axis)
        self.left_axis.setTicks(self.y_axis)
        self.btm_axis.setLabel('Millisecond')
        self.left_axis.setLabel('Linear')
        self.left_axis.label.setFont(font)
        self.btm_axis.label.setFont(font)


class boost_level(base):
    y_axis = [[(0, '0.0')]]
    x_axis = [[(0, '0'), (10, '10'), (20, '20'), (30, '30'), (40, '40'), (50, '50'), (60, '60')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.plotItem.showGrid(True, True, 0.2)
        self.viewbox.setXRange(0, 60, 0, True)
        self.viewbox.setYRange(0, 0, 0, True)
        self.btm_axis.setTicks(self.x_axis)
        self.left_axis.setTicks(self.y_axis)


class VBassFilter(base):
    magnitude_ticks = [[(-80, '-80'), (-60, '-60'), (-40, '-40'), (-20, '-20'), (0, '0'), (20, '20'), (40, '40')]]
    frequency_ticks = [[(np.log10(20), '20'), (np.log10(40), '40'), (np.log10(80), '80'), (np.log10(150), '150'),
                        (np.log10(300), '300'), (np.log10(600), '600'), (np.log10(1200), '1.2k'),
                        (np.log10(2500), '2.5k'), (np.log10(5000), '5k'), (np.log10(10000), '10k'),
                        (np.log10(22000), '22k')]]

    def __init__(self, widget):
        super().__init__(widget)

    def initAssets(self):
        super().initAssets()
        self.plotItem.showGrid(True, True, 0.2)
        self.plotItem.setLogMode(x=True, y=None)
        self.viewbox.setXRange(np.log10(20), np.log10(22000), 0, True)
        self.viewbox.setYRange(-80, 40, 0, True)
        self.btm_axis.setTicks(self.frequency_ticks)
        self.left_axis.setTicks(self.magnitude_ticks)
