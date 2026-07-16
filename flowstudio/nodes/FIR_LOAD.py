from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_matplotlib_graphical import *
from utilities.iir_designer import *
from control.flow_widget_plot import *

DEBUG = False
DEBUG_Content = False

@register_node(OP_NODE_FIR_LOAD)
class FLOW_Node_FIR_LOAD(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_FIR_LOAD
    op_title = "FIR_LOAD"
    content_label_objname = "FIR_LOAD"
    display_name = 'FIR filter loading simulator'
    info = ''
    expandable = True
    # openable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value

    def __init__(self, scene, band, channel, control):
        self.inputs = []
        self.outputs = []
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()
        self.manager.widgetSet['num'].slider.setMaximum(band)
        self.manager.widgetSet['num'].slider.setMinimum(0)
        self.manager.widgetSet['num'].numbox.setMinimum(band)
        self.manager.widgetSet['num'].numbox.setMinimum(0)
        self.manager.widgetSet['num'].numbox.setValue(1)
        self.manager.widgetSet['maxTap'].widget_value = band
        self.manager.widgetSet['maxTap'].label.setVisible(False)
        self.manager.widgetSet['maxTap'].slider.setVisible(False)
        self.manager.widgetSet['maxTap'].numbox.setVisible(False)
