from typing import Any

from pyqtgraph import PlotWidget
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SimpleCustomFigure(PlotWidget):
    def __init__(self):
        super().__init__()
        self.setXRange(0,10,padding=0.05)
        self.setYRange(0,10,padding=0.05)
        self.addLegend()
        self.showGrid(x=True,y=True)
        styles={"color":"red","font-size":"20px"}
        self.setLabel("left","vertical axis",**styles)
        self.setLabel("bottom","transverse axis",**styles)
        self.setTitle("Pyqtgraph Chart!",color="b",size="20pt")
        # self.setBackground("w")
        self.setFixedSize(500, 400)
        self.test()
        self.updatePlot()
        # self.clear()

    def test(self):
        pen = pg.mkPen(color=(255, 0, 0),width=15,style=Qt.DashDotLine)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [3, 1, 5, 3, 9, 8, 7, 6, 2]
        self.sample_1=self.plot(x, y,name="sample 1",pen=pen,symbol="o",symbolSize=20,symbolBrush=('b'))
        pen = pg.mkPen(color=(0, 255, 0), width=15, style=Qt.DashDotLine)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sample_2=self.plot(x, y, name="sample 2", pen=pen, symbol="+", symbolSize=10, symbolBrush=('b'))

    def updatePlot(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [3, 1, 5, 3, 9, 8, 7, 6, 2]
        self.sample_2.setData(x,y)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sample_1.setData(x, y)

class ShowFigureMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Turn on mouse movement event
        self.setContentsMargins(10,10,10,10)
        self.setMouseTracking(True)
        self.setWindowTitle('Show Graphical')
        self.graphicview = QGraphicsView()
        self.graphicview.setObjectName("graphicview")
        sc=SimpleCustomFigure()
        graphicscene = QGraphicsScene()
        # graphicscene.setSceneRect(-200 // 2, -200 // 2, 200, 200)
        graphicscene.addWidget(sc)
        spot1=SpotCustom()
        spot1.beganXPosition=0
        spot1.beganYPosition=0
        spot1.centerString="1R"
        graphicscene.addItem(spot1)
        spot2 = SpotCustom()
        spot2.beganXPosition = 100
        spot2.beganYPosition = 100
        spot2.centerString = "2R"
        graphicscene.addItem(spot2)
        spot3 = SpotCustom()
        spot3.beganXPosition = 200
        spot3.beganYPosition = 200
        spot3.centerString = "3R"
        graphicscene.addItem(spot3)
        spot4 = SpotCustom()
        spot4.beganXPosition = 220
        spot4.beganYPosition = 220
        spot4.centerString = "4R"
        graphicscene.addItem(spot4)
        self.graphicview.setScene(graphicscene)
        self.setCentralWidget(self.graphicview)
        # self.graphicview.setFixedSize(sc.get_width_height()[0]+3, sc.get_width_height()[1]+3)

class SpotCustom(QGraphicsItem):
    @property
    def beganXPosition(self):
        return self._beganXPosition

    @beganXPosition.setter
    def beganXPosition(self, beganXPosition):
        self._beganXPosition = beganXPosition+64

    @property
    def beganYPosition(self):
        return self._beganYPosition

    @beganYPosition.setter
    def beganYPosition(self, beganYPosition):
        self._beganYPosition = beganYPosition+49

    @property
    def limitXPosition(self):
        return self._limitXPosition

    @limitXPosition.setter
    def limitXPosition(self, limitXPosition):
        self._limitXPosition = limitXPosition

    @property
    def limitYPosition(self):
        return self._limitYPosition

    @limitYPosition.setter
    def limitYPosition(self, limitYPosition):
        self._limitYPosition = limitYPosition

    @property
    def centerString(self):
        return self._centerString
    @centerString.setter

    def centerString(self,centerString):
        self._centerString=centerString

    def __init__(self,parent:QWidget=None):
        super().__init__(parent)
        self.width=30
        self.height=30
        self.beganXPosition=100
        self.beganYPosition=100
        self.limitXPosition=0
        self.limitYPosition=0
        self.centerString="1R"
        self.hovered=False
        #Set up this ``QGraphicsItem`
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

    def boundingRect(self) -> QRectF:
        return QRectF(
            self.beganXPosition - 2,
            self.beganYPosition - 2,
            self.width + 3.5,
            self.height + 3.5
        ).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painterPath = QPainterPath()
        painterPath.setFillRule(Qt.WindingFill)
        painterPath.addEllipse(self._beganXPosition, self._beganYPosition,
                           self.width,self.height)
        painter.setRenderHint(True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("yellow")))
        painter.drawPath(painterPath.simplified())

        painterPath2 = QPainterPath()
        painterPath2.setFillRule(Qt.WindingFill)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(QColor("black"))
        font = QFont()
        font.setBold(True)
        font.setPixelSize(18)
        painterPath2.addText(QPointF(self._beganXPosition+6,self.height/2+6+self._beganYPosition), font, str(self._centerString))
        painter.setPen(pen)
        painter.drawPath(painterPath2.simplified())

        path_outline = QPainterPath()
        path_outline.arcTo(QRectF(self._beganXPosition, self._beganYPosition,
                           self.width,self.height),0,360)
        painter.setBrush(Qt.NoBrush)
        pen = QPen()
        pen.setWidth(3)
        if self.hovered:
            pen.setColor(QColor("#FFA500"))
            painter.setPen(pen)
            painter.drawPath(path_outline.simplified())
        else:
            if not self.isSelected():
                pen.setWidth(1)
                pen.setColor(QColor("black"))
            else:
                pen.setColor(QColor("#4169E1"))
            painter.setPen(pen)
            painter.drawPath(path_outline.simplified())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value: Any):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            rect = QRectF(64-self._beganXPosition,49-self._beganYPosition,self.scene().width()-144,self.scene().height()-123)
            if not rect.contains(value):
                value.setX(min(rect.right(), max(value.x(), rect.left())))
                value.setY(min(rect.bottom(), max(value.y(), rect.top())))
                return value
        return QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        super().mousePressEvent(event)
        self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setCursor(QCursor(Qt.ArrowCursor))

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def contextMenuEvent(self, event: 'QGraphicsSceneContextMenuEvent'):
        menu=QMenu()
        menu.setFixedSize(50,75)
        a=menu.addAction(self._centerString)
        b=menu.addAction(self._centerString)
        c=menu.addAction(self._centerString)
        action=menu.exec_(event.screenPos())
