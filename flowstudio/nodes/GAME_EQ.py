from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_GAME_EQ)
class FLOW_Node_GAME_EQ(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_GAME_EQ
    op_title = "GAME_EQ"
    content_label_objname = "GAME_EQ"
    display_name = 'Game EQ'
    info = 'Enhance your gaming experience with GameEQ — featuring 90 expertly tuned EQ presets tailored for different game genres. Whether you’re playing shooters, RPGs, or racing games, GameEQ optimizes soundscapes to boost immersion, clarity, and impact.'
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
