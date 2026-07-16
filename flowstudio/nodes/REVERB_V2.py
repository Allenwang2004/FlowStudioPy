from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_REVERB_V2)
class FLOW_Node_REVERB_V2(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_REVERB_V2
    op_title = "REVERB_V2"
    content_label_objname = "REVERB_V2"
    display_name = 'Reverb V2'
    info = 'Reverbrator with higher quality compare to legacy REVERB module'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1, 1])
        self.initControl()
        self.eval()
