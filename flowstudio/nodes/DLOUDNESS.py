from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_DLOUDNESS)
class FLOW_Node_DASS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_DLOUDNESS
    op_title = "DLOUDNESS"
    content_label_objname = "DLOUDNESS"
    display_name = 'Dynamic Loudness'
    info = 'Dynamic Loudness utilize equal loudness curve with different input levels'
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