from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_SQRT_FP)
class FlowNodeSqrtFP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_SQRT_FP
    op_title = "SQRT_FP"
    content_label_objname = "SQRT_FP"
    display_name = 'Sqrt (fixed-point)'
    info = 'Fixed-point version of SQRT'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()