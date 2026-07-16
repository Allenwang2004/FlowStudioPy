from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush


class SwitchButton(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._circle_position = 3  # 圆圈位置

        self.setFixedSize(40, 22)
        self.setCursor(Qt.PointingHandCursor)

        # 动画
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)

    @pyqtProperty(int)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景轨道
        if self._checked:
            # 开启状态 - 蓝色
            track_color = QColor("#2196F3")  # 你界面的蓝色
        else:
            # 关闭状态 - 灰色
            track_color = QColor("#4A4A4A")

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(),
                                self.height() / 2, self.height() / 2)

        # 绘制圆圈
        circle_color = QColor("#FFFFFF")
        painter.setBrush(QBrush(circle_color))

        circle_size = self.height() - 6
        painter.drawEllipse(self._circle_position, 3, circle_size, circle_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()

    def toggle(self):
        self._checked = not self._checked

        # 设置动画
        if self._checked:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(self.width() - self.height() + 3)
        else:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(3)

        self.animation.start()
        self.toggled.emit(self._checked)

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            # 不使用动画直接设置位置
            if checked:
                self._circle_position = self.width() - self.height() + 3
            else:
                self._circle_position = 3
            self.update()

    def isChecked(self):
        return self._checked
