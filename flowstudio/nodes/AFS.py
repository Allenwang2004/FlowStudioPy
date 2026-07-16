from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AFS)
class FLOW_Node_AFS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AFS
    op_title = "AFS"
    content_label_objname = "AFS"
    display_name = 'Acoustic Feedback Suppression'
    info = 'AFS is an audio signal processing device which is used in the signal path in a live sound reinforcement system to prevent or suppress audio feedback.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()
        