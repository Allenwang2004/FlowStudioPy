import math
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath


EDGE_CP_ROUNDNESS = 100     #: Bezier control point distance on the line
WEIGHT_SOURCE = 0.2         #: factor for square edge to change the midpoint between start and end socket


class GraphicsEdgePathBase:
    """Base Class for calculating the graphics path to draw for an graphics Edge"""

    def __init__(self, owner: 'QDMGraphicsEdge'):
        # keep the reference to owner GraphicsEdge class
        self.owner = owner

    def calcPath(self):
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the graphics path to draw
        :rtype: ``QPainterPath`` or ``None``
        """
        return None


class GraphicsEdgePathDirect(GraphicsEdgePathBase):
    """Direct line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the direct line
        :rtype: ``QPainterPath``
        """
        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.lineTo(self.owner.posDestination[0], self.owner.posDestination[1])
        return path


class GraphicsEdgePathBezier(GraphicsEdgePathBase):
    """Cubic line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the cubic Bezier line connection with 2 control points

        :returns: ``QPainterPath`` of the cubic Bezier line
        :rtype: ``QPainterPath``
        """
        s = self.owner.posSource
        d = self.owner.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.owner.edge.start_socket is not None:
            ssin = self.owner.edge.start_socket.is_input
            ssout = self.owner.edge.start_socket.is_output

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s[1] - d[1]) / math.fabs(
                        (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                    (d[1] - s[1]) / math.fabs(
                        (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.owner.posDestination[0], self.owner.posDestination[1])

        return path


# class GraphicsEdgePathSquare(GraphicsEdgePathBase):
#     """Square line connection Graphics Edge"""
#     def __init__(self, *args, handle_weight=0.5, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.rand = None
#         self.handle_weight = handle_weight
#
#     def calcPath(self):
#         """Calculate the square edge line connection
#
#         :returns: ``QPainterPath`` of the edge square line
#         :rtype: ``QPainterPath``
#         """
#
#         s = self.owner.posSource
#         d = self.owner.posDestination
#
#         mid_x = s[0] + ((d[0] - s[0]) * self.handle_weight)
#
#         path = QPainterPath(QPointF(s[0], s[1]))
#         path.lineTo(mid_x, s[1])
#         path.lineTo(mid_x, d[1])
#         path.lineTo(d[0], d[1])
#
#         return path


class GraphicsEdgePathSquare(GraphicsEdgePathBase):
    """Square line - 最简洁实用版"""

    def __init__(self, *args, handle_weight=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.handle_weight = handle_weight
        self.min_offset = 50  # 最小外延距离

    def calcPath(self):
        s = self.owner.posSource
        d = self.owner.posDestination
        path = QPainterPath(QPointF(s[0], s[1]))

        if not self.owner.edge.start_socket or not self.owner.edge.end_socket:
            return self.normalPath(path, s, d)

        # 判断是否同侧
        start_pos = self.owner.edge.start_socket.position
        end_pos = self.owner.edge.end_socket.position
        same_side = (start_pos in [3, 4] and end_pos in [3, 4]) or \
                    (start_pos in [1, 2] and end_pos in [1, 2])

        if same_side:
            return self.bypassPath(path, s, d, start_pos in [3, 4])
        return self.normalPath(path, s, d)

    def normalPath(self, path, s, d):
        """正常路径"""
        mid_x = s[0] + ((d[0] - s[0]) * self.handle_weight)
        path.lineTo(mid_x, s[1])
        path.lineTo(mid_x, d[1])
        path.lineTo(d[0], d[1])
        return path

    def bypassPath(self, path, s, d, on_right):
        """绕行路径 - 简化版"""
        dx = d[0] - s[0]
        dy = d[1] - s[1]

        # 外延方向和距离
        offset_x = self.min_offset if on_right else -self.min_offset

        # 绕行高度：向上绕
        offset_y = 60
        bypass_y = min(s[1], d[1]) - offset_y

        # 外延 X 坐标
        out_x = max(s[0], d[0]) + abs(offset_x) if on_right else \
            min(s[0], d[0]) - abs(offset_x)

        # 绘制路径（智能省略重复点）
        path.lineTo(out_x, s[1])  # 向外
        # path.lineTo(out_x, bypass_y)  # 向上

        # 只有当需要水平移动时才画这段
        if abs((out_x) - (out_x)) > 5:  # 这个判断可以去掉，因为总是同一个 out_x
            pass  # 不需要额外的水平线

        path.lineTo(out_x, d[1])  # 向下
        path.lineTo(d[0], d[1])  # 进入

        return path
