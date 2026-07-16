from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_HW_IN, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_HW_IN)
class FLOW_Node_HW_INPUT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_HW_IN
    op_title = "HW_IN"
    content_label_objname = "HW_IN"
    display_name = 'HW Input'
    node_type = 'CO'
    info = ''
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene, socket_type):
        super().__init__(scene, inctrls=[], outctrls=[socket_type])
        self.eval()