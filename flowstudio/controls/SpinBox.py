from flowstudio.flow_conf import *
from control.flow_control_widget import LabelSpinBox

@register_control(ControlType.FLOAT_SPINBOX.value)
class SpinBox(object):
    gui_type = ControlType.FLOAT_SPINBOX.value

    def __init__(self, label_text, max_value, min_value, initial_value, spin_box_width,
                 num_decimal_places=0,
                 additional_parameters=None):
        self.label_text = label_text
        self.parameters = {'pMax': max_value, 'pMin': min_value, 'pValue': initial_value,
                           'label_text': label_text, 'pDecimalPrecision': num_decimal_places,
                           'spin_box_width': spin_box_width}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return LabelSpinBox(parent_widget, self.parameters)
