from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_SQRT)
class FLOW_Node_SQRT(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SQRT
    op_title = "SQRT"
    content_label_objname = "SQRT"
    display_name = 'Sqrt'
    info = 'This function output the square root value of the input.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()