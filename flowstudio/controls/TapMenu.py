from flowstudio.flow_conf import *
from control.flow_control_widget import TapMenu as TapMenuUI

@register_control(ControlType.TAP_MENU.value)
class TapMenu(object):
    gui_type = ControlType.TAP_MENU.value

    def __init__(self, parameters_under_tap: dict, use_vertical_tab_bar=False, parameters=None):
        self.parameters_under_tap = parameters_under_tap
        self.use_vertical_tab_bar = use_vertical_tab_bar
        self.parameters = {
            'pSize': 0,
            'cSize': len(parameters_under_tap.keys()),
            'cParameter': self.parameters_under_tap
        }
        if parameters is not None:
            self.parameters.update(parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return TapMenuUI(parent_widget, self.parameters, self.use_vertical_tab_bar)
