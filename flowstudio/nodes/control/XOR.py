from functools import reduce
import operator
from flowstudio.flow_conf_co import OP_NODE_CO_XOR, register_node_co, SocketType
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_XOR)
class FLOW_Node_XOR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_XOR
    op_title = "XOR"
    content_label_objname = "XOR"
    display_name = 'XOR'
    node_type = 'CO'
    info = "XOR between 2 Inputs"
    # type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene):
        super().__init__(scene, inctrls=[SocketType.BOOL.value]*2, outctrls=[SocketType.BOOL.value])
        self.result = False
        self.eval()

    def onControlChanged(self, socket_type, value):
        value_list = []
        if self.inctrls:
            for socket in self.inctrls:
                if socket.edges:
                    for edge in socket.edges:
                        value_list.append(edge.start_socket.node.manager.widgetSet['constant'].widget_value)
        self.result = bool(reduce(operator.xor, value_list))

        if self.outctrls:
            for socket in self.outctrls:
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, self.result)