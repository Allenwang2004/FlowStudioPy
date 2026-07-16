from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_EXP, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_EXP)
class FLOW_Node_EXP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_EXP
    op_title = "EXP"
    content_label_objname = "EXP"
    display_name = 'Exp'
    node_type = 'CO'
    info = "Calculate the exponential in BASE of the input value"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inputs = []
        self.outputs = []
        for i in range(int(num)):
            self.inputs.append(socket_type)
            self.outputs.append(socket_type)
        super().__init__(scene, inctrls=self.inputs, outctrls=self.outputs)
        self.eval()