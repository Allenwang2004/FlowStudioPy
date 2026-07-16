from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_NTTS_IML)
class FLOW_Node_VCP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_NTTS_IML
    op_title = "NTTS_IML"
    content_label_objname = "NTTS_IML"
    display_name = 'Intelligent Microphone Voice'
    info = 'Intelligent microphone voice pick-up of headphone product. It includes technologies such as beamforming and AEC.'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        # self.inctrls = [0]
        super().__init__(scene, inputs=[1, 1, 1], outputs=[1])
        self.initControl()
        self.eval()
