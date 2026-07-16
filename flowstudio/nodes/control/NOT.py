from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_NOT, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_NOT)
class FLOW_Node_NOT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_NOT
    op_title = "NOT"
    content_label_objname = "NOT"
    display_name = 'NOT'
    node_type = 'CO'
    info = "Input Negation"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inctrls = []
        self.outctrls = []
        for i in range(int(num)):
            self.inctrls.append(socket_type)
            self.outctrls.append(socket_type)
        super().__init__(scene, inctrls=self.inctrls, outctrls=self.outctrls)
        self.eval()

    def onControlChanged(self, socket_type, value):
        res_list = []
        if self.inctrls:
            for socket in self.inctrls:
                if socket.edges:
                    for edge in socket.edges:
                        res_list.append(not edge.start_socket.node.manager.widgetSet['constant'].widget_value)

        if self.outctrls:
            for i, socket in enumerate(self.outctrls):
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, res_list[i])