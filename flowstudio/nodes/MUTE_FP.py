from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUTE_FP)
class FLOW_Node_MUTE_FP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUTE_FP
    op_title = "MUTE_FP"
    content_label_objname = "MUTE_FP"
    display_name = 'Mute (fixed-point)'
    info = 'Fixed-point version of MUTE'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()