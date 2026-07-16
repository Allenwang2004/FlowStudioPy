from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_LPF_COMB_FILTER)
class FLOW_Node_LPF_COMB_FILTER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_LPF_COMB_FILTER
    op_title = "LPF_COMB_FILTER"
    content_label_objname = "LPF_COMB_FILTER"
    display_name = 'Low Pass Comb Filter'
    info = 'Delay with 1-order low-pass filter on the feedback path'
    expandable = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_TAPS.value

    def __init__(self, scene, tap):
        self.tap = tap
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()