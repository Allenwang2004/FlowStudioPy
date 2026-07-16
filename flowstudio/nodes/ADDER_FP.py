from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_ADDER_FP)
class FlowNodeAdderFP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_ADDER_FP
    op_title = "ADDER_FP"
    content_label_objname = "ADDER_FP"
    display_name = 'Adder (fixed-point)'
    info = 'Fixed-point version of ADDER'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1], rule_check_mode=-2)
        self.eval()