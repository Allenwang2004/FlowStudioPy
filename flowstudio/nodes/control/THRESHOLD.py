from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_THRESHOLD, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_THRESHOLD)
class FLOW_Node_THRESHOLD(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_THRESHOLD
    op_title = "THRESHOLD"
    content_label_objname = "THRESHOLD"
    display_name = 'Threshold'
    node_type = 'CO'
    info = "Boolean output when over threshold. Hysteresis mode shall be considered"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene, socket_type):
        super().__init__(scene, inctrls=[socket_type], outctrls=[7])
        self.eval()