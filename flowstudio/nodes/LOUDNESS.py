from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_LOUDNESS)
class FLOW_Node_LOUDNESS(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_LOUDNESS
    op_title = "LOUDNESS"
    content_label_objname = "LOUDNESS"
    display_name = 'Loudness Volume'
    info = 'Gain depended equal loudness control, the maxSPL denotes the maximum measured sound pressure level when there is no attenuation (gain = 0dB). Set the precise maxSPL will get the best equal loudness performance.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
