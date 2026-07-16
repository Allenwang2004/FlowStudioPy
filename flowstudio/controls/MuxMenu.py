from flowstudio.flow_conf import *
from flowstudio.controls.Menu import Menu
from control.flow_control_widget import LabelAndComboBoxForMux

@register_control(ControlType.MUX_MENU.value)
class MuxMenu(Menu):
    gui_type = ControlType.MUX_MENU.value

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndComboBoxForMux(parent_widget, self.parameters)
