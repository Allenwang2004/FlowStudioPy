from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AI_ZIP)
class FLOW_Node_AI_ZIP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AI_ZIP
    op_title = "AIZip"
    content_label_objname = "AIZip"
    display_name = 'Vocal Removal'
    info = 'High performance AI Based Vocal Removal algorithm'
    expandable = False
    linkType = 1
    type_ao_addition = TypeAOAddition.FIXED.value

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()