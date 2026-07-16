from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AI_NR_UC)
class FlowNodeAINRUC(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AI_NR_UC
    op_title = "AI_NR_UC"
    content_label_objname = "AI_NR_UC"
    display_name = 'AI Noise Reduction UC(16k)'
    info = 'Deep learning based noise reduction, especially robust to lower SNR rates and has abilities to remove non-stationary noises.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()
        