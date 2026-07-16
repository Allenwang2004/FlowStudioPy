from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_DBASS)
class FLOW_Node_DASS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_DBASS
    op_title = "DBASS"
    content_label_objname = "DBASS"
    display_name = 'Dynamic Bass'
    info = 'Dynamic bass increase the low frequency response when the signal level is reduced.'
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