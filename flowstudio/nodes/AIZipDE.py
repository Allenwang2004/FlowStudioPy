from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AI_ZIP_DE)
class FLOW_Node_AI_ZIP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AI_ZIP_DE
    op_title = "AIZip_DialogEnhance"
    content_label_objname = "AIZip_DialogEnhance"
    display_name = 'Dialog Enhancement'
    info = 'High performance AI Based Dialog Enhancement Algorithm'
    expandable = False
    linkType = 1
    type_ao_addition = TypeAOAddition.FIXED.value

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()