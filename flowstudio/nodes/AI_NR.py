from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AI_NR)
class FLOW_Node_AI_NR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AI_NR
    op_title = "AI_NR"
    content_label_objname = "AI_NR"
    display_name = 'AI Noise Reduction(16k)'
    info = 'Deep learning based noise reduction, especially robust to lower SNR rates and has abilities to remove non-stationary noises.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()
        