from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_SQRT, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_SQRT)
class FLOW_Node_SQRT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_SQRT
    op_title = "SQRT"
    content_label_objname = "CO_SQRT"
    display_name = 'Sqrt'
    node_type = 'CO'
    info = "Extract the RADIX of input value"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inputs = []
        self.outputs = []
        for i in range(int(num)):
            self.inputs.append(socket_type)
            self.outputs.append(socket_type)
        super().__init__(scene, inctrls=self.inputs, outctrls=self.outputs)
        self.eval()