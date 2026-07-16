from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_REVERB)
class FLOW_Node_REVERB(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_REVERB
    op_title = "REVERB"
    content_label_objname = "REVERB"
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()