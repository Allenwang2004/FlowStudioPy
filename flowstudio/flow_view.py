from flowstudio.flow_conf import Debug
from flowstudio.flow_node_base import FLOW_GraphicsNode
from nodeeditor.node_graphics_view import *
from nodeeditor.utils import dumpException
from nodeeditor.node_scene import QDMGraphicsScene

from flowstudio.flow_edge_dragging import FLOW_Edge_Dragging

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

DEBUG = False

class FLOW_View(QDMGraphicsView):

    dragStatus = False

    def __init__(self, grScene: 'QDMGraphicsScene', parent: 'QWidget' = None):
        super().__init__(grScene, parent)

        self.dragging = FLOW_Edge_Dragging(self)

    def setViewTopLeft(self, x: float, y: float):
        """
        设置视图左上角的场景坐标

        :param x, y: 要显示在视图左上角的场景坐标
        """
        # 计算视口尺寸的一半
        half_width = self.viewport().width() / 2
        half_height = self.viewport().height() / 2

        # centerOn 需要的目标点 = 左上角坐标 + 半个视口
        target_x = x + half_width
        target_y = y + half_height

        self.centerOn(target_x, target_y)

    def keyPressEvent(self, event):
        """
        Overrides the key press event handler to handle keyboard events.

        Args:
            event: The key event object.

        Returns:
            None
        """
        if DEBUG:
            if event.key() == Qt.Key_H:
                if Debug.DEBUG_Low_Level.value: print("HISTORY:     len(%d)" % len(self.grScene.scene.history.history_stack),
                      " -- current_step", self.grScene.scene.history.history_current_step)
                for ele in self.grScene.scene.history.history_stack:
                    print(ele)
                    print('\n')
            elif event.key() == Qt.Key_S:
                if Debug.DEBUG_Low_Level.value: print(self.grScene.scene.getView().window().sub_patchs)
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    # def mousePressEvent(self, event:QMouseEvent):
    #     super().mousePressEvent(event)
    #
    #     try:
    #         item = self.getItemAtClick(event)
    #         if DEBUG: print(item)
    #
    #         if type(item) == QGraphicsProxyWidget:
    #             item = item.widget()
    #             pass
    #
    #         if hasattr(item, 'node') or hasattr(item, 'socket'):
    #             if hasattr(item, 'node'):
    #                 pass
    #
    #     except Exception as e:
    #         dumpException(e)

    def leftMouseButtonPress(self, event:QMouseEvent):
        """When Left  mouse button was pressed"""

        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))

        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super(QDMGraphicsView, self).mousePressEvent(fakeEvent)
                return

        if hasattr(item, "node") and not self.dragStatus:
            if Debug.DEBUG_Low_Level.value: print('View::leftMouseButtonPress - Start dragging a node')
            if self.mode == MODE_NOOP:
                self.mode = MODE_NODE_DRAG
                self.edgeIntersect.enterState(item.node)
                if Debug.DEBUG_Low_Level.value: print(">> edgeIntersect start:", self.edgeIntersect.draggedNode)
        # support for snapping
        if self.isSnappingEnabled(event):
            item = self.snapping.getSnappedSocketItem(event)

        if isinstance(item, QDMGraphicsSocket) and not self.dragStatus:
            if self.mode == MODE_NOOP and event.modifiers() & Qt.CTRL:
                socket = item.socket
                if socket.hasAnyEdge():
                    self.mode = MODE_EDGES_REROUTING
                    self.rerouting.startRerouting(socket)
                    return

            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.dragging.edgeDragStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.dragging.edgeDragEnd(item)
            if res: return

        if item is None and not self.dragStatus:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super(QDMGraphicsView, self).mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super(QDMGraphicsView, self).mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """When Left  mouse button was released"""

        # get item which we release mouse button on
        item = self.getItemAtClick(event)

        try:
            # logic
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                            Qt.LeftButton, Qt.NoButton,
                                            event.modifiers() | Qt.ControlModifier)
                    super(QDMGraphicsView, self).mouseReleaseEvent(fakeEvent)
                    return

            if self.mode == MODE_EDGE_DRAG:
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    if self.isSnappingEnabled(event):
                        item = self.snapping.getSnappedSocketItem(event)
                    res = self.dragging.edgeDragEnd(item)
                    if res: return

            if self.mode == MODE_EDGES_REROUTING:
                if self.isSnappingEnabled(event):
                    item = self.snapping.getSnappedSocketItem(event)

                if not EDGE_REROUTING_UE:
                    # version 2 -- more consistent with the nodeeditor?
                    if not self.rerouting.first_mb_release:
                        # for confirmation of first MB release
                        self.rerouting.first_mb_release = True
                        # skip any re-routing until first MB was released
                        return

                self.rerouting.stopRerouting(item.socket if isinstance(item, QDMGraphicsSocket) else None)

                # don't forget to end the REROUTING MODE

                self.mode = MODE_NOOP

            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.line_points = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = MODE_NOOP
                return

            if self.mode == MODE_NODE_DRAG:
                scenepos = self.mapToScene(event.pos())
                self.edgeIntersect.leaveState(scenepos.x(), scenepos.y())
                if hasattr(item, "node"):
                    node = item.node
                    for input in node.inputs:
                        node.onInputChanged(input)
                    for output in node.outputs:
                        node.onOutputChanged(output)
                    node.evalChildren()
                    node.evalParents()
                self.mode = MODE_NOOP
                self.update()

            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.grScene.selectedItems()

                if current_selected_items != self.grScene.scene._last_selected_items:
                    if current_selected_items == []:
                        self.grScene.itemsDeselected.emit()
                    else:
                        self.grScene.itemSelected.emit()
                    self.grScene.scene._last_selected_items = current_selected_items

                # the rubber band rectangle don't disappears without handling the event
                super(QDMGraphicsView, self).mouseReleaseEvent(event)
                return

            # otherwise deselect everything
            if item is None:
                self.grScene.itemsDeselected.emit()

        except:
            dumpException()

        super(QDMGraphicsView, self).mouseReleaseEvent(event)
