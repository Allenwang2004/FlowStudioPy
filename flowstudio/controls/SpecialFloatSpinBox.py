from flowstudio.flow_conf import *
from control.flow_control_widget import SpecialLabelDoubleSpinBox

@register_control(ControlType.SPECIAL_FLOAT_SPINBOX.value)
class SpecialFloatSpinBox(object):
    gui_type = ControlType.SPECIAL_FLOAT_SPINBOX.value

    def __init__(self, label_text, max_value, min_value, initial_value, additional_parameters=None):
        self.label_text = label_text
        self.parameters = {'pMax': max_value, 'pMin': min_value, 'pValue': initial_value,
                           'label_text': label_text}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return SpecialLabelDoubleSpinBox(parent_widget, self.parameters)
