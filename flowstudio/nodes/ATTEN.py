from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_ATTEN)
class FLOW_Node_ATTEN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_ATTEN
    op_title = "ATTEN"
    content_label_objname = "ATTEN"
    display_name = 'Attenuator'
    info = 'It attenuates the signal by a gain specified in linear scale. The gain also combines with slew control to prevent unwanted artificial when changing the gain'
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

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

    def serialize(self):
        res = super().serialize()
        res['content']['ch'] = 1
        return res