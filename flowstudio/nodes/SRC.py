from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from flowstudio.flow_conf_list import SRC

class SRC_GUI(FLOW_GUI):
    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.input_freq_menu = SRC['srin'].get_widget(self)
        self.output_freq_menu = SRC['srout'].get_widget(self)
        self.quality_menu = SRC['Quality'].get_widget(self)
        # self.latency = SRC['Latency'].get_widget(self)
        self.isConnected = False
        self.refresh()

    def set_connected_state(self, connected: bool):
        self.isConnected = connected
        self.update_menu_lock(disabled=connected)

    def refresh(self):
        super().refresh()
        self.update_menu_lock(disabled=self.isConnected)

    def update_menu_lock(self, disabled=True):
        self.input_freq_menu.set_disabled(disabled)
        self.output_freq_menu.set_disabled(disabled)
        self.quality_menu.set_disabled(disabled)
    # TODO: implement latency value


@register_node(OP_NODE_SRC)
class FLOW_Node_SRC(FLOW_Node):
    op_code = OP_NODE_SRC
    op_title = "SRC"
    content_label_objname = "SRC"
    display_name = "Sample Rate Converter"
    info = "Sample Rate Converter (SRC) is a process that converts audio signals from one sample rate to another."
    expandable = True
    linkType = 1

    def __init__(self, scene):
        self.isConnected = False
        self.inputs = [1]
        self.outputs = [1]
        super().__init__(scene, inputs=self.inputs, outputs=self.outputs)
        self.widget = SRC_GUI(self)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

    def is_enable_comboBox(self, mode):
        style = """
        QComboBox:disabled {
                background-color: #f0f0f0;
                color: #888888;
            }
        """

        combo_srin = self.manager.widgetSet['srin'].comboBox
        combo_srout = self.manager.widgetSet['srout'].comboBox
        combo_Quality = self.manager.widgetSet['Quality'].comboBox

        for combo in [combo_srin, combo_srout, combo_Quality]:
            combo.setEnabled(not mode)
            combo.setStyleSheet(style if mode else "")