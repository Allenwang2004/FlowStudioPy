from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_TONEGEN)
class FLOW_Node_TONEGEN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_TONEGEN
    op_title = "TONEGEN"
    content_label_objname = "TONEGEN"
    display_name = 'Sine Tone Generator'
    info = 'Sine tone source, with tunable frequency and gain'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.initControl()
        self.eval()