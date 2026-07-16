from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_DELAY)
class FLOW_Node_DELAY(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_DELAY
    op_title = "DELAY"
    content_label_objname = "DELAY"
    display_name = 'Delay'
    info = 'Delay with integer samples'
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
