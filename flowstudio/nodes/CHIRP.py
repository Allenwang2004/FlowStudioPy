from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_CHIRP)
class FLOW_Node_CHIRP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CHIRP
    op_title = "CHIRP"
    content_label_objname = "CHIRP"
    display_name = 'Chirp Generator'
    info = 'Tone sweep generator source, with start frequency, end frequency, sweep time, tunable gain, trigger and Log or Linear sweep type'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.initControl()
        self.eval()