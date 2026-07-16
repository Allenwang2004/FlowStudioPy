from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_CHORUS)
class FLOW_Node_CHORUS(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_CHORUS
    op_title = "CHORUS"
    content_label_objname = "CHORUS"
    display_name = 'Chorus'
    info = 'Chorus  is an audio effect that occurs when individual sounds with approximately the same time, and very similar pitches, converge and are perceived as one.<br>While similar sounds coming from multiple sources can occur naturally, as in the case of a choir or string orchestra, it can also be simulated using an electronic effects unit or signal processing device'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()
