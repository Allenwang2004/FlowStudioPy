from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_ABS)
class FLOW_Node_ABS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_ABS
    op_title = "ABS"
    content_label_objname = "ABS"
    display_name = 'Abs'
    info = 'This function output the absolute value of the input.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()