from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_ADDER)
class FLOW_Node_ADDER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_ADDER
    op_title = "ADDER"
    content_label_objname = "ADDER"
    display_name = 'Adder'
    info = 'Takes all the current inputs, added together and output the sum.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1], rule_check_mode=-2)
        self.eval()