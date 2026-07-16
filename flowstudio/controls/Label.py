from flowstudio.flow_conf import *
from control.flow_control_widget import Label as LabelControl

@register_control(ControlType.LABEL.value)
class Label(object):
    gui_type = ControlType.LABEL.value
    required_parameters = [{'key': 'label_text', 'value': '', 'description': 'The label text'}]

    def __init__(self, initial_val, additional_parameters=None):
        self.text = initial_val
        self.parameters = {}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return LabelControl(parent_widget, self.text, self.parameters)
