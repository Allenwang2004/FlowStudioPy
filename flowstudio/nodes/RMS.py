from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_RMS)
class FLOW_Node_RMS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_RMS
    op_title = "RMS"
    content_label_objname = "RMS"
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()