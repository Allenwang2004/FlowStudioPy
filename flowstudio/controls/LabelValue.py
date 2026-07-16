from flowstudio.flow_conf import *
from control.flow_control_widget import LabelAndValue
from flowstudio.controls.ControlBase import ControlBase


@register_control(ControlType.LABEL_VALUE.value)
class LabelValue(ControlBase):
    gui_type = ControlType.LABEL_VALUE.value
    required_parameters = [
        {'key': 'label_text', 'value': '', 'description': 'The label text'},
        {'key': 'pValue', 'value': '', 'description': 'The value to display'}
    ]

    def __init__(self, label_text, pValue, additional_parameters=None, is_preview=False):
        self.label_text = label_text
        self.pValue = pValue
        self.parameters = {'label_text': label_text, 'pValue': pValue}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)
        self.is_preview = is_preview

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndValue(parent_widget, self.label_text, self.pValue, self.parameters)