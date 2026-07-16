from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *

@register_node(OP_NODE_FEEDBACK)
class FLOW_Node_FEEDBACK(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_FEEDBACK
    op_title = "FEEDBACK"
    content_label_objname = "FEEDBACK"
    display_name = 'Feedback'
    info = ''
    is_feedback = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.eval()

        for socket in self.inputs:
            socket.position = RIGHT_TOP
            socket.setSocketPosition()

        for socket in self.outputs:
            socket.position = LEFT_TOP
            socket.setSocketPosition()

