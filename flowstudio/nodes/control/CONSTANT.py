from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_CONSTANT, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_CONSTANT)
class FLOW_Node_CONSTANT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_CONSTANT
    op_title = "CONSTANT"
    content_label_objname = "CONSTANT"
    display_name = 'Constant'
    node_type = 'CO'
    info = "Generate a constant value"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene, socket_type):
        self.socket_type = socket_type
        super().__init__(scene, inctrls=[], outctrls=[socket_type])
        self.eval()

        self.manager.widgetSet['constant'].valueChanged.connect(self.value_change)

    def value_change(self):
        if self.outctrls and self.outctrls[0].edges:
            for edge in self.outctrls[0].edges:
                edge.end_socket.node.onControlChanged(self.socket_type, self.manager.widgetSet['constant'].widget_value)