from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_DLFQ)
class FLOW_Node_DLFQ(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_DLFQ
    op_title = "DLFQ"
    content_label_objname = "DLFQ"
    display_name = 'DLFQ'
    info = 'info'
    linkType = 1
    type_ao_addition = TypeAOAddition.FIXED.value

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()
