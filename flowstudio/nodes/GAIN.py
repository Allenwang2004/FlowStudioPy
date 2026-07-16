from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_GAIN)
class FLOW_Node_GAIN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_GAIN
    op_title = "GAIN"
    content_label_objname = "GAIN"
    display_name = 'Gain'
    info = 'It amplifies or attenuates the signal by a gain G specified in logarithm scale(dB). The gain also combine with slew control to prevent unwanted artificial when changing the gain.'
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
        # self.manager.widgetSet['gain'].label.setFont(QFont("Arial", 10+len(self.inputs)/10))
        # self.manager.widgetSet['gain'].label.setFixedWidth(60+len(self.inputs))
        # self.manager.widgetSet['gain'].slider.setFixedWidth(10)
        # self.manager.widgetSet['gain'].slider.setOrientation(Qt.Vertical)
        # self.manager.widgetSet['gain'].slider.setFixedHeight(60+len(self.inputs)*5)
        # self.manager.widgetSet['gain'].numbox.setFixedWidth(50+len(self.inputs))
        # self.manager.widgetSet['gain'].numbox.setFont(QFont("Arial", 10 + len(self.inputs) / 10))
        # width = self.grNode.width
        # height = self.grNode.height-30
        # self.manager.widgetSet['gain'].setGeometry(0,0,width,height)

    def serialize(self):
        res = super().serialize()
        res['content']['ch'] = 1
        return res