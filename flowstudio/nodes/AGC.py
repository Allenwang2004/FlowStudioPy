from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_AGC)
class FLOW_Node_AGC(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_AGC
    op_title = "AGC"
    content_label_objname = "AGC"
    display_name = 'AGC'
    info = 'AGC is the algorithm that automatically controls the amplitude increase of an audio signal from original input to amplified output'
    expandable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    def __init__(self, scene, channel):
        self.inputs = []
        self.outputs = []
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        # super().__init__(scene, inputs=[1], outputs=[1])
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()