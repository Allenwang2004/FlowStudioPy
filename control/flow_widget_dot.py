import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

class plotDot(pg.GraphItem):

    posChanged = pyqtSignal(list)

    def __init__(self, pos = [0, 0], texts=None, color=[120, 120, 120, 255]):
        super().__init__()
        self.pos = np.array([pos], dtype=float)
        self.color = color
        self.initAssets()
        self.isDrag = False
        self.initText(texts)

        self.setData(pos=self.pos, size=self.dotSize, symbol=self.dotShape, pxMode=True, symbolBrush=self.dotBrush, symbolPen=self.dotPen)
        self.scatter.sigClicked.connect(self.clicked)

    def initAssets(self):
        self.dotShape = 'o'
        self.dotSize = 16
        self.dotBrush = pg.mkBrush(self.color)
        self.dotPen = pg.mkPen(self.color, width=0)
        self.disableY = False
        self.disableX = False
        self.noDrag = False

    def initText(self, string):
        if string==None:
            self.dotText = None
        else:
            self.dotText = string

            self.font = QFont()
            self.font.setBold(True)
            self.font.setFamily("Calibri")
            self.font.setPixelSize(16)

            obj = pg.TextItem(text = self.dotText, anchor = (0.5, 0.5))
            obj.setPos(self.pos[0][0], self.pos[0][1])
            obj.setColor((60, 60, 60))
            obj.setFont(self.font)
            obj.setParentItem(self)

    def mouseDragEvent(self,event):
        if self.noDrag:
            return

        self.isDrag = True
        self.clicked()

        range = self.scatter.getViewBox().viewRange()

        self.x_minimal = np.math.ceil(range[0][0]*100000)/100000
        self.x_maximum = np.math.floor(range[0][1]*100000)/100000
        self.y_minimal = -24
        self.y_maximum = 24

        pos = np.array([event.pos()], dtype=float)

        if self.x_minimal >= event.pos()[0]:
            pos[0][0] = self.x_minimal

        elif self.x_maximum <= event.pos()[0]:
            pos[0][0] = self.x_maximum

        if self.y_minimal >= event.pos()[1]:
            pos[0][1] = self.y_minimal

        elif self.y_maximum <= event.pos()[1]:
            pos[0][1] = self.y_maximum

        else:
            pass

        if self.disableY:
            pos[0][1] = 0
        elif self.disableX:
            pos[0][0] = 0

        self.posChanged.emit([pos[0][0], pos[0][1]])
        self.setData(pos=pos)

        if self.dotText:
            text = self.childItems()[1]
            text.setPos(pos[0][0], pos[0][1])

        event.accept()

    def clicked(self):
        self.selected()

        children = self.scatter.getViewBox().allChildren()

        for child in children:
            if type(child) == plotDot and not self == child:
                child.notSelected()

        self.posChanged.emit(self.pos[0].tolist())

    def notSelected(self):
        self.dotPen = pg.mkPen(self.color, width=3)
        self.dotBrush = pg.mkBrush(self.color)
        self.setData(pos=self.pos, symbolPen=self.dotPen, symbolBrush=self.dotBrush)

    def selected(self):
        self.dotPen = pg.mkPen(color=(255, 255, 0, 255), width=6)
        self.dotBrush = pg.mkBrush(color=(255, 255, 0, 255))
        self.setData(pos=self.pos, symbolPen=self.dotPen, symbolBrush=self.dotBrush)
