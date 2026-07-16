from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_DRYWET)
class FLOW_Node_DRYWET(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_DRYWET
    op_title = "DRYWET"
    content_label_objname = "DRYWET"
    display_name = 'Dry wet fader'
    info = 'Mix ratio between input 1 and input 2'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.initControl()
        self.eval()
