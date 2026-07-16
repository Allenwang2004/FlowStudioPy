from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


class AIBFGUI(FLOW_GUI):
    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(130, 50)


@register_node(OP_NODE_AI_BF)
class FlowNodeAIBF(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AI_BF
    op_title = "AI_BF"
    content_label_objname = "AI_BF"
    display_name = 'AI Beamforming(16k)'
    info = '4-mic AI based beamforming'
    expandable = True
    openable = True
    linkType = 1
    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1, 1, 1], outputs=[1])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        super().initInnerClasses()
        self.widget = AIBFGUI(self)
