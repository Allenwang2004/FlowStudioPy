from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QMessageBox

from flowstudio.flow_conf import Debug
from flowstudio.flow_conf_co import OP_NODE_CO_CONSTANT
from nodeeditor.node_edge_dragging import EdgeDragging
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_edge import EDGE_TYPE_DEFAULT, EDGE_TYPE_SQUARE
from nodeeditor.utils import dumpException

class FLOW_Edge_Dragging(EdgeDragging):

    def __init__(self, grView: 'QGraphicsView'):
        super().__init__(grView)

    def add_edge(self, start_socket, end_socket, ignore_message_box=False, ignore_drag_edge=False):
        """
            Add an edge to the sub window where the start socket and end socket are located.

            :param start_socket: The starting socket of the edge.
            :param end_socket: The ending socket of the edge.
            :param ignore_message_box: Optional. Default: False.
            A boolean value indicating whether to ignore showing the message box or not.
            :param ignore_drag_edge: Optional. Default: False.
            When the function is directly called by a unit test without the presence of self.drag_edge,
            the ignore_drag_edge parameter should be set to True to bypass any operations related to self.drag_edge.

            :return: Returns True if the edge is successfully added, otherwise returns False.
        """
        if start_socket.is_input and end_socket.is_input:
            if not ignore_message_box:
                QMessageBox.about(self.grView.window(), "invalid",
                                  'You are trying to connect <b>output to output</b>, which is invalid. <br/>Please try connecting <b>input to output</b> instead.')
            return False

        if start_socket.is_output and end_socket.is_output:
            if not ignore_message_box:
                QMessageBox.about(self.grView.window(), "invalid",
                                  'You are trying to connect <b>input to input</b>, which is invalid. <br/>Please try connecting <b>input to output</b> instead.')
            return False

        if start_socket.is_input and end_socket.is_output:
            if not ignore_message_box:
                QMessageBox.about(self.grView.window(), "invalid",
                                  'You are trying to connect <b>output to input</b>, which is invalid. <br/>Please try connecting <b>input to output</b> instead.')
            return False

        # check if edge would be valid
        if not ignore_drag_edge:
            if not self.drag_edge.validateEdge(start_socket, end_socket):
                if Debug.DEBUG_Low_Level.value: print("NOT VALID EDGE")
                return False

        # regular processing of drag edge
        self.grView.resetMode()

        if Debug.DEBUG_Low_Level.value: print('View::edgeDragEnd ~ End dragging edge')
        if not ignore_drag_edge:
            self.drag_edge.remove(silent=True)  # don't notify sockets about removing drag_edge
            self.drag_edge = None

        # Check whether the two socket types are consistent
        if start_socket.socket_type != end_socket.socket_type:
            if not ignore_message_box:
                QMessageBox.about(self.grView.window(), "invalid",
                                  'You are trying to connect sockets of different types, which is invalid. <br/>Please try connecting sockets of same type instead.')
            return False

        try:
            if end_socket != start_socket:
                # if we released dragging on a socket (other then the beginning socket)

                ## First remove old edges / send notifications
                for socket in (end_socket, start_socket):
                    if not socket.is_multi_edges:
                        if socket.is_input:
                            # print("removing SILENTLY edges from input socket (is_input and !is_multi_edges) [DragStart]:", item.socket.edges)
                            socket.removeAllEdges(silent=True)
                        else:
                            socket.removeAllEdges(silent=False)

                ## Create new Edge
                # item.socket = item.socket.node.inputs[item.socket.index]
                # self.drag_start_socket = self.drag_start_socket.node.outputs[self.drag_start_socket.index]

                if start_socket.node.is_feedback == True or end_socket.node.is_feedback == True:
                    edge_type = EDGE_TYPE_SQUARE
                else:
                    edge_type = EDGE_TYPE_DEFAULT

                new_edge = self.getEdgeClass()(end_socket.node.scene, start_socket, end_socket,
                                               edge_type=edge_type)
                if Debug.DEBUG_Low_Level.value: print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting",
                                new_edge.start_socket, "<-->", new_edge.end_socket)

                ## Send notifications for the new edge
                for socket in [start_socket, end_socket]:
                    # @TODO: Add possibility (ie when an input edge was replaced) to be silent and don't trigger change
                    socket.node.onEdgeConnectionChanged(new_edge)
                    if socket.is_input: socket.node.onInputChanged(socket)
                    if socket.is_output: socket.node.onOutputChanged(socket)

                self.control_input_setup()
                self.grView.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                if Debug.DEBUG_Low_Level.value: print('View::edgeDragEnd ~ everything done.')
                return True
            return False
        except Exception as e:
            dumpException(e)
            return False

    def edgeDragEnd(self, item: 'QGraphicsItem'):
        """Code handling the end of dragging an `Edge` operation. In this code return True if skip the
        rest of the mouse event processing. Can be called with ``None`` to cancel the edge dragging mode

        :param item: Item in the `Graphics Scene` where we ended dragging an `Edge`
        :type item: ``QGraphicsItem``
        """

        # early out - clicked on something else than Socket
        if not isinstance(item, QDMGraphicsSocket):
            self.grView.resetMode()
            if Debug.DEBUG_Low_Level.value: print('View::edgeDragEnd ~ End dragging edge early')
            self.drag_edge.remove(silent=True)  # don't notify sockets about removing drag_edge
            self.drag_edge = None
            return False

        # clicked on socket
        if isinstance(item, QDMGraphicsSocket):
            return self.add_edge(start_socket=self.drag_start_socket, end_socket=item.socket)

    def control_input_setup(self):
        for node in self.grView.grScene.scene.nodes:
            if node.op_code in [OP_NODE_CO_CONSTANT]:
                node.value_change()
