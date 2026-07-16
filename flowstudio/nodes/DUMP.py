from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *

@register_node(OP_NODE_DUMP)
class FLOW_Node_DUMP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_DUMP
    op_title = "DUMP"
    content_label_objname = "DUMP"
    display_name = 'Audio Dump'
    info = '“DUMP” object can dump the audio to wav file format on whatever point of the signal flow. User can easily understand the issue on that point for whole audio system debug'
    openable = False
    linkType = 1

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)