from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_POLARITY)
class FLOW_Node_POLARITY(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_POLARITY
    op_title = "POLARITY"
    content_label_objname = "POLARITY"
    display_name = 'Polarity'
    info = 'Controllable polarity module, when enable the polarity it would invert the phase with 180'
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