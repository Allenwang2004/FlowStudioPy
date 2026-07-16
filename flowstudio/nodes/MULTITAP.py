from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MULTITAP)
class FLOW_Node_MULTITAP(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MULTITAP
    op_title = "MULTITAP"
    content_label_objname = "MULTITAP"
    display_name = 'Multitap Delay'
    info = 'Mutitap delay with individual tap delay and gain'
    expandable = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_TAPS.value

    def __init__(self, scene, tap):
        self.tap = tap
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()