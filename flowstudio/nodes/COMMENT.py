from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


class COMMENT_GraphicsNode(FLOW_GraphicsNode):
    """
        Graphics node for COMMENT node.
    """

    def __init__(self, node):
        """
            Initialize COMMENT_GraphicsNode.

            Args:
                node (FLOW_Node_COMMENT): The COMMENT node associated with this graphics node.
        """
        super().__init__(node)
        self.is_moving = False
        self.initial_pos = None
        self.node = node

    def initSizes(self):
        """
            Initialize the size of the graphics node.
        """
        super().initSizes()
        self.width = 180
        self.height = 180

    def initTitle(self):
        """
            Initialize the title of the graphics node.
        """
        self.designator_item = QGraphicsTextItem(self)
        self.designator_item.node = self.node
        self.designator_item.setDefaultTextColor(self._title_color)
        self.designator_item.setFont(self._title_font)
        self.designator_item.setPos(self.title_horizontal_padding, 24)
        self.designator_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def hoverEnterEvent(self, event):
        """
            Event handler for hover enter event.

            Args:
                event (QGraphicsSceneHoverEvent): The hover event object.
        """
        super().hoverEnterEvent(event)
        if not self.node.content.textEdit.editable:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        else:
            QApplication.setOverrideCursor(Qt.IBeamCursor)

    def hoverLeaveEvent(self, event):
        """
            Event handler for hover leave event.

            Args:
                event (QGraphicsSceneHoverEvent): The hover event object.
        """
        super().hoverLeaveEvent(event)
        QApplication.restoreOverrideCursor()


class DoubleClickTextEdit(QTextEdit):
    """
        Custom QTextEdit widget that enables double-click editing and dragging functionality.
    """

    def __init__(self, parent=None):
        """
            Initialize DoubleClickTextEdit.

            Args:
                parent (QWidget): The parent widget.
        """
        super().__init__(parent)
        self.editable = False
        self.parent = parent

    def mouseDoubleClickEvent(self, event):
        """
            Event handler for mouse double-click event.

            Args:
                event (QMouseEvent): The mouse event object.
        """
        if not self.editable:
            self.setReadOnly(False)
            self.editable = True
            QApplication.setOverrideCursor(Qt.IBeamCursor)
            click_event = QMouseEvent(QMouseEvent.MouseButtonPress, event.localPos(), Qt.LeftButton,
                                      Qt.LeftButton, Qt.NoModifier)
            self.mousePressEvent(click_event)
        else:
            super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        """
            Event handler for focus out event.

            Args:
                event (QFocusEvent): The focus event object.
        """
        self.setReadOnly(True)
        self.editable = False
        super().focusOutEvent(event)
        QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        """
            Event handler for mouse press event.

            Args:
                event (QMouseEvent): The mouse event object.
        """
        if not self.editable:
            if event.button() == Qt.LeftButton:
                self.is_selected_including_self = False
                for node in self.parent.node.scene.nodes:
                    if node.grNode.isSelected():
                        if node == self.parent.node:
                            self.is_selected_including_self = True
                self.parent.node.grNode.is_moving = True
                self.parent.node.grNode.initial_pos = event.pos()
                self.parent.node.grNode.setSelected(True)
                for node in self.parent.node.scene.nodes:
                    if node.grNode.isSelected():
                        if not self.is_selected_including_self and node != self.parent.node:
                            node.grNode.doSelect(False)
                            continue
                        if not hasattr(self.parent.node.scene, 'selected_node_positions'):
                            self.parent.node.scene.selected_node_positions = {}
                        self.parent.node.scene.selected_node_positions[node.grNode] = node.grNode.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
            Event handler for mouse move event.

            Args:
                event (QMouseEvent): The mouse event object.
        """
        if not self.editable:
            if self.parent.node.grNode.is_moving:
                offset = event.pos() - self.parent.node.grNode.initial_pos
                for node in self.parent.node.scene.nodes:
                    if node.grNode.isSelected():
                        node.updateConnectedEdges()
                        node.grNode._was_moved = True
                        node.grNode.setPos(self.parent.node.scene.selected_node_positions[node.grNode] + offset)
                        self.parent.node.scene.selected_node_positions[node.grNode] = node.grNode.pos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
            Event handler for mouse release event.

            Args:
                event (QMouseEvent): The mouse event object.
        """
        if not self.editable:
            if self.parent.node.grNode.is_moving:
                self.parent.node.grNode.is_moving = False
                for node in self.parent.node.scene.nodes:
                    if node.grNode.isSelected():
                        node.grNode._was_moved = False
                self.parent.node.scene.history.storeHistory("Node moved", setModified=True)
        else:
            super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """
            Event handler for enter event.

            Args:
                event (QEvent): The event object.
        """
        super().enterEvent(event)
        if not self.editable:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        else:
            QApplication.setOverrideCursor(Qt.IBeamCursor)

    def leaveEvent(self, event):
        """
            Event handler for leave event.

            Args:
                event (QEvent): The event object.
        """
        super().leaveEvent(event)
        QApplication.restoreOverrideCursor()


class COMMENT_Content(QDMNodeContentWidget):
    """
        Content widget for COMMENT node.
    """

    def __init__(self, node: 'Node'):
        """
            Initialize COMMENT_Content.

            Args:
                node (FLOW_Node_COMMENT): The COMMENT node associated with this content widget.
        """
        super().__init__(node)
        self.node = node

    def initUI(self):
        """
            Initialize the user interface of the content widget.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.textEdit = DoubleClickTextEdit(self)
        self.textEdit.setText("Add comments here...")
        self.textEdit.setFont(QFont("Calibri", 12))
        self.textEdit.setStyleSheet("background-color: transparent;")
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(self.textEdit)

    def serialize(self):
        res = super().serialize()
        res['comment'] = self.textEdit.toPlainText()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.textEdit.setText(data['comment'])
            return True & res
        except Exception as e:
            dumpException(e)
        if Debug.DEBUG_SERIALIZE.value: print("Derialized FLOW_Content '%s'" % self.__class__.__name__, "res:", res)
        return res


@register_node(OP_NODE_COMMENT)
class FLOW_Node_COMMENT(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_COMMENT
    op_title = "COMMENT"
    content_label_objname = "COMMENT"
    display_name = 'Comment'
    info = 'Text based block for user comments'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[])
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = COMMENT_Content(self)
        self.grNode = COMMENT_GraphicsNode(self)
