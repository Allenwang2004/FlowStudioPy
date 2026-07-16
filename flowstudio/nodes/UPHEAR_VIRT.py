from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_UPHEAR_VIRT)
class FLOW_Node_UPHEAR_VIRTUALIZER(FLOW_Node):
    icon = '../resources/uphear-virt-ao-icon.png'
    op_code = OP_NODE_UPHEAR_VIRT
    op_title = "upHear Virtualizer"
    content_label_objname = "upHear Virtualizer"
    display_name = 'upHear Virtulizer'
    info = "Codec-agnostic audio post-processing technology that brings authentic and enveloping 3D sound to soundbars and smart speakers<br><a href='https://www.iis.fraunhofer.de/en/ff/amm/consumer-electronics/uphear-virtualizer.html'>https://www.iis.fraunhofer.de/en/ff/amm/consumer-electronics/uphear-virtualizer.html</a>"
    expandable = False
    expand = True

    def __init__(self, scene):
        self.inputs = []
        self.outputs = []
        for i in range(12):
            self.inputs.append(1)
        for i in range(10):
            self.outputs.append(1)
        super().__init__(scene, inputs=self.inputs, outputs=self.outputs)
        self.initControl()
        self.eval()

    def initControl(self):
        for key in self.manager.widgetSet:
            if 'UserEQ' in key:
                key_name = key.split('(')[0].strip()
                key_index = int(key.split('band ')[1].split(')')[0]) - 1
                self.manager.widgetSet[key].valueChanged.connect(partial(self.tweaker, [key_index, key_name, key]))
            else:
                self.manager.widgetSet[key].valueChanged.connect(partial(self.tweaker, key))

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

    def isDirty(self):
        if self._is_dirty:
            if hasattr(self, 'error_msg'):
                del self.error_msg
            return True
        if not self.manager.widgetSet['SBBSDir'].widget_value:
            self.error_msg = f'Value of SBBSDir parameter in {self.title} must not be empty.'
            return True
        return False
