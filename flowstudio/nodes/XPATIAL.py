from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_XPATIAL)
class FLOW_Node_X(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_XPATIAL
    op_title = "XPATIAL"
    content_label_objname = "Xpatial"
    display_name = 'Xpatial'
    info = 'Xpatial'
    linkType = 1
    type_ao_addition = TypeAOAddition.FIXED.value

    def __init__(self, scene):
        super().__init__(scene, [1]*2, [1]*2)
        # self.initControl()
        # self.eval()