from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_CLIPPER)
class FLOW_Node_CLIPPER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CLIPPER
    op_title = "CLIPPER"
    content_label_objname = "CLIPPER"
    display_name = 'Clipper'
    info = 'It’s a hard clipper. It set the output level equals to the threshold if the absolute value of input is over the threshold.'
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
        self.manager.widgetSet['Type'].comboBox.setEnabled(False)