from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MERGER)
class FLOW_Node_MERGER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MERGER
    op_title = "MERGER"
    content_label_objname = "MERGER"
    display_name = 'Merger'
    info = 'Merger is adding all the inputs and divided by the number of input to prevent overflow. This is different from adder which just simply sum up all inputs.'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.eval()