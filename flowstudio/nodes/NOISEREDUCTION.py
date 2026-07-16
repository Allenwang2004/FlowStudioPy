from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_NOISEREDUCTION)
class FLOW_Node_NOISEREDCUTION(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_NOISEREDUCTION
    op_title = "NOISEREDUCTION"
    content_label_objname = "NOISEREDUCTION"
    display_name = 'DSP Noise Reduction'
    info = 'DSP approached noise reduction'
    expandable = True
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()