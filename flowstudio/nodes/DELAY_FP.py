from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_DELAY_FP)
class FlowNodeDelayFP(FlowFixedPointNode):
    # icon = "icons/in.png"
    op_code = OP_NODE_DELAY_FP
    op_title = "DELAY_FP"
    content_label_objname = "DELAY_FP"
    display_name = 'Delay (fixed-point)'
    info = 'fixed-point version of DELAY'
    expandable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    def __init__(self, scene, channel):
        self.inputs = []
        self.outputs = []
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()
