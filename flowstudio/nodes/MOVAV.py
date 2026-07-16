from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MOVAV)
class FLOW_Node_MOVAV(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MOVAV
    op_title = "MOVAV"
    content_label_objname = "MOVAV"
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()