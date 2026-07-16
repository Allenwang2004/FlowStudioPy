from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_MULTIPLY, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_MULTIPLY)
class FLOW_Node_MULTIPLY(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_MULTIPLY
    op_title = "MULTIPLY"
    content_label_objname = "MULTIPLY"
    display_name = 'Multiply'
    node_type = 'CO'
    info = "Product of inputs"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inctrls = []
        self.outctrls = [socket_type]
        for i in range(int(num)):
            self.inctrls.append(socket_type)
        super().__init__(scene, inctrls=self.inctrls, outctrls=self.outctrls)
        self.eval()

    def onControlChanged(self, socket_type, value):
        self.multiply_value = 1
        if self.inctrls:
            for socket in self.inctrls:
                if socket.edges:
                    for edge in socket.edges:
                        self.multiply_value *= edge.start_socket.node.manager.widgetSet['constant'].widget_value

        if self.outctrls:
            for socket in self.outctrls:
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, self.multiply_value)