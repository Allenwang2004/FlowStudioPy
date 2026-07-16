from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_LOOKUP_TABLE, register_node_co
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_LOOKUP_TABLE)
class FLOW_Node_LOOKUP_TABLE(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_LOOKUP_TABLE
    op_title = "LOOKUP_TABLE"
    content_label_objname = "LOOKUP_TABLE"
    display_name = 'Lookup Table'
    node_type = 'CO'
    info = "Value mapping between an input and output with linear interpolation between given values"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE.value

    def __init__(self, scene, socket_type):
        super().__init__(scene, inctrls=[socket_type], outctrls=[socket_type])
        self.eval()