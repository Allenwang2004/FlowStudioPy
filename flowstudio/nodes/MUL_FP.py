from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUL_FP)
class FlowNodeMulFP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUL_FP
    op_title = "MUL_FP"
    content_label_objname = "MUL_FP"
    display_name = 'Multiplier (fixed-point)'
    info = 'Fixed-point version of MULTIPLIER'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1], rule_check_mode=-2)
        self.eval()
