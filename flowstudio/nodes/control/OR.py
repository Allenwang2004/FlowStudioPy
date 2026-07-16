from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_OR, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_OR)
class FLOW_Node_OR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_OR
    op_title = "OR"
    content_label_objname = "OR"
    display_name = 'OR'
    node_type = 'CO'
    info = "OR between N Inputs"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inctrls = []
        self.outctrls = [socket_type]
        self.result = False
        for i in range(int(num)):
            self.inctrls.append(socket_type)
        super().__init__(scene, inctrls=self.inctrls, outctrls=self.outctrls)
        self.eval()

    def onControlChanged(self, socket_type, value):
        value_list = []
        if self.inctrls:
            for socket in self.inctrls:
                if socket.edges:
                    for edge in socket.edges:
                        value_list.append(edge.start_socket.node.manager.widgetSet['constant'].widget_value)
        self.result = any(value_list)

        if self.outctrls:
            for socket in self.outctrls:
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, self.result)