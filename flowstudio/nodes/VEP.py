from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


class VEPGUI(FLOW_GUI):
    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(130, 360)


@register_node(OP_NODE_VEP)
class FlowNodeVEP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_VEP
    op_title = "VEP"
    display_name = "Voice Enhancement Package(VEP)"
    content_label_objname = "VEP"
    info = 'Voice Enhancement Package including 4 mic beamforming , AEC and AI Noise Reduction'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        self.inctrls = [0]
        super().__init__(scene, inputs=[1, 1, 1, 1, 1], outputs=[1], inctrls=self.inctrls)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        super().initInnerClasses()
        self.widget = VEPGUI(self)
