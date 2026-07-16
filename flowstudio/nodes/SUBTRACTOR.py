from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_SUBTRACTOR)
class FLOW_Node_SUBTRACTOR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SUBTRACTOR
    op_title = "SUBTRACTOR"
    content_label_objname = "SUBTRACTOR"
    display_name = 'Subtractor'
    info = 'This function calculates the subtraction of the input signals.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1], rule_check_mode=-2)
        self.eval()