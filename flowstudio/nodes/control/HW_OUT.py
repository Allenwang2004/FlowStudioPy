from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import register_node_co, OP_NODE_CO_HW_OUT
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_HW_OUT)
class FLOW_Node_HW_OUTPUT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_HW_OUT
    op_title = "HW_OUT"
    content_label_objname = "HW_OUT"
    display_name = 'HW Output'
    node_type = 'CO'
    info = ''
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene, socket_type):
        super().__init__(scene, inctrls=[socket_type], outctrls=[])
        self.eval()