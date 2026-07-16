from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUTE)
class FLOW_Node_MUTE(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUTE
    op_title = "MUTE"
    content_label_objname = "MUTE"
    display_name = 'Mute'
    info = 'A simple mute block with soft ramping feature'
    expandable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    def __init__(self, scene, num_channels):
        self.inputs = []
        self.outputs = []
        for i in range(num_channels):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()