from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_PHASEVOCODER)
class FLOW_Node_PHASEVOCODER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_PHASEVOCODER
    op_title = "PHASEVOCODER"
    content_label_objname = "PHASEVOCODER"
    display_name = 'PHASEVOCODER'
    info = 'DSP PHASEVOCODER'
    expandable = True
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()