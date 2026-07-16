from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_ABS_FP)
class FLOW_Node_ABS_FP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_ABS_FP
    op_title = "ABS_FP"
    content_label_objname = "ABS_FP"
    display_name = 'Abs (fixed-point)'
    info = 'Fixed-point version of ABS'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()