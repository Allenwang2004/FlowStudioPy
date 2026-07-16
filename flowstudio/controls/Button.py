from flowstudio.flow_conf import *
from control.flow_control_widget import LabelAndButton

@register_control(ControlType.BUTTON.value)
class Button(object):
    gui_type = ControlType.BUTTON.value

    def __init__(self, label_text, value_to_send, button_text, additional_parameters=None):
        self.label_text = label_text
        self.value_to_send = value_to_send
        self.button_text = button_text
        self.parameters = {}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndButton(parent_widget, self.label_text, self.value_to_send, self.button_text, self.parameters)
