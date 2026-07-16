from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_AND, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_AND)
class FLOW_Node_AND(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_AND
    op_title = "AND"
    content_label_objname = "AND"
    display_name = 'AND'
    node_type = 'CO'
    info = "AND between N Inputs"
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
        self.result = all(value_list)

        if self.outctrls:
            for socket in self.outctrls:
                if socket.edges:
                    for edge in socket.edges:
                        edge.end_socket.node.onControlChanged(self.outctrls[0].socket_type, self.result)