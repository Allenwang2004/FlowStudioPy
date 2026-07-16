from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_DELAY_Intp)
class FLOW_Node_DELAY_Intp(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_DELAY_Intp
    op_title = "DELAY_Intp"
    content_label_objname = "DELAY_Intp"
    display_name = 'Fractional Delay'
    info = 'Delay with fractional samples'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()