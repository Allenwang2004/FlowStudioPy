from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_CLIPFIX)
class FLOW_Node_CLIPFIX(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CLIPFIX
    op_title = "CLIPFIX"
    content_label_objname = "CLIPFIX"
    display_name = 'ClipFix'
    info = 'Provide the mechanism to avoid input audio clipping. (beta)'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        self.inctrls = [0]
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.initControl()
        self.eval()
