from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_NOISEGEN)
class FLOW_Node_NOISEGEN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_NOISEGEN
    op_title = "NOISEGEN"
    content_label_objname = "NOISEGEN"
    display_name = 'Noise Generator'
    info = 'Noise generator source, with tunable gain, and pink or white noise type'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.initControl()
        self.eval()