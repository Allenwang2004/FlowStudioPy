from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_CTC)
class FLOW_Node_CTC(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CTC
    op_title = "CTC"
    content_label_objname = "CTC"
    display_name = 'CTC'
    info = 'Crosstalk Cancellation technology eliminates interference from the opposite channel, resulting in clearer separation between the left and right audio channels.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)