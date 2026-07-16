from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUX_FP)
class FLOW_Node_MUX_FP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUX_FP
    op_title = "MUX_FP"
    content_label_objname = "MUX_FP"
    display_name = 'Multiplexer (fixed-point)'
    info = 'Fixed-point version of MUX'
    expandable = False
    expand = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_OUTPUTS_AND_FOUR_TIMES_INPUTS.value

    def __init__(self, scene, out):
        self.inputs = []
        self.outputs = []
        for i in range(out*4):
            self.inputs.append(1)
        for i in range(out):
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()

    def initSocketTooltip(self):
        for i in range(len(self.inputs)):
            self.inputs[i].grSocket.setToolTip("input " + str(i + 1))
        self.outputs[0].grSocket.setToolTip("output")

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        items = []

        l = []
        for i in range(1,len(self.inputs)+1,len(self.outputs)):
            l.append(i)
        for i in range(4):
            items.append('Ch %s - %s'%(l[i],l[i]+len(self.outputs)-1))
        self.manager.widgetSet['select'].comboBox.clear()
        self.manager.widgetSet['select'].comboBox.addItems(items)

    def serialize(self):
        res = super().serialize()
        res['content']['ch'] = 1
        return res