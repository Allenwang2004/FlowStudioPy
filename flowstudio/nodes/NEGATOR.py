from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_NEGATOR)
class FLOW_Node_NEGATOR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_NEGATOR
    op_title = "NEGATOR"
    content_label_objname = "NEGATOR"
    display_name = 'Negator'
    info = 'This function inverts the input signal polarity'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()