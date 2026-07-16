from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_SPATIALIZER)
class FLOW_Node_SPATIALIZER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SPATIALIZER
    op_title = "SPATIALIZER"
    content_label_objname = "SPATIALIZER"
    display_name = 'Spatializer'
    info = 'Sound image widening algorithm for stereo signal.'
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()