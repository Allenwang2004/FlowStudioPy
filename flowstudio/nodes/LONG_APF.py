from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_LONG_APF)
class FLOW_Node_LONG_APF(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_LONG_APF
    op_title = "LONG_APF"
    content_label_objname = "LONG_APF"
    display_name = 'Long All Pass Filter'
    info = 'An allpass filter can be defined as any filter having a gain of 11 at all frequencies (but typically different delays at different frequencies), which create a different phase response.'
    expandable = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_TAPS.value

    def __init__(self, scene, tap):
        self.tap = tap
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()