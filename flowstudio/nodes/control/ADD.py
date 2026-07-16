from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_ADD, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_ADD)
class FLOW_Node_ADD(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_ADD
    op_title = "ADD"
    content_label_objname = "ADD"
    display_name = 'Add'
    node_type = 'CO'
    info = "Sums inputs"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inctrls = []
        self.outctrls = [socket_type]
        self.sum_value = 0
        for i in range(int(num)):
            self.inctrls.append(socket_type)
        super().__init__(scene, inctrls=self.inctrls, outctrls=self.outctrls)
        self.eval()

    def onControlChanged(self, socket_type, value):
        self.sum_value = 0
        if self.inctrls:
            for socket in self.inctrls:
                if socket.edges:
                    for edge in socket.edges:
                        self.sum_value += edge.start_socket.node.manager.widgetSet['constant'].widget_value

        if self.outctrls:
            for socket in self.outctrls:
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, self.sum_value)