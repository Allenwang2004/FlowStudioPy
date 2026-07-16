from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AEC)
class FLOW_Node_ADDER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AEC
    op_title = "AEC"
    content_label_objname = "AEC"
    display_name = 'AEC'
    info = 'Acoustic Echo Cancellation'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.initControl()
        self.eval()