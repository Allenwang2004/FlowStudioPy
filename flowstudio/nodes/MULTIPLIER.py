from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MULTIPLIER)
class FLOW_Node_MULTIPLIER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MULTIPLIER
    op_title = "MULTIPLIER"
    content_label_objname = "MULTIPLIER"
    display_name = 'Multiplier'
    info = 'This function calculates the multiplication of the input signals.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1], rule_check_mode=-2)
        self.eval()
