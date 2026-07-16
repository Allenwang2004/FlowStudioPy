from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_LMS)
class FLOW_Node_LMS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_LMS
    op_title = "LMS"
    content_label_objname = "LMS"
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()

    def initSocketTooltip(self):
        self.inputs[0].grSocket.setToolTip("input")
        self.inputs[1].grSocket.setToolTip("reference")
        self.outputs[0].grSocket.setToolTip("output")
        self.outputs[1].grSocket.setToolTip("error")