from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_NTTS_AGC)
class FlowNodeNTTSAGC(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_NTTS_AGC
    op_title = "NTTS_AGC"
    content_label_objname = "NTTS_AGC"
    display_name = 'Noise Level AGC'
    info = 'Noise level AGC adjust its gain automatically in conjunction with the noise level of the surrounding environment. If the surrounding noise level is louder, it increases gain, and vice versa.'
    expandable = True
    openable = True
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    linkType = 1

    def __init__(self, scene, channel):
        # self.inctrls = [0]
        self.inputs = []
        for i in range(channel):
            self.inputs.append(1)
        super().__init__(scene, self.inputs, outputs=[1])
        self.initControl()
        self.eval()
