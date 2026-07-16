from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_BD_SOUND)
class FLOW_Node_BD_SOUND(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_BD_SOUND
    op_title = "BdSoundS2C"
    content_label_objname = "BdSoundS2C"
    display_name = 'BdSoundS2C'
    info = ''
    expandable = False
    linkType = 1
    type_ao_addition = TypeAOAddition.FIXED.value

    def __init__(self, scene):
        super().__init__(scene, inputs=[1]*8, outputs=[1]*3)
        self.initControl()
        self.eval()