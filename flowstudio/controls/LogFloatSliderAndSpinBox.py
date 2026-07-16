from flowstudio.flow_conf import *
from control.flow_control_widget import LogarithmicLabelDoubleSliderSpinBox, LabelDoubleNumberBox
from flowstudio.controls.ControlBase import ControlBase


@register_control(ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value)
class LogFloatSliderAndSpinBox(ControlBase):
    gui_type = ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value
    required_parameters = [{'key': 'label_text', 'value': '', 'description': 'The label text'},
                           {'key': 'pMax', 'value': 2000.0, 'description': 'The maximum value'},
                           {'key': 'pMin', 'value': 10.0, 'description': 'The minimum value'},
                           {'key': 'pValue', 'value': 20.0, 'description': 'The initial value'}]

    def __init__(self, label_text, max_value, min_value, initial_value, additional_parameters=None,
                 is_preview=False):
        self.label_text = label_text
        self.parameters = {'pMax': max_value, 'pMin': min_value, 'pValue': initial_value,
                           'label_text': label_text}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)
        self.is_preview = is_preview

    def get_widget(self, parent_widget, gui_type):
        from flowstudio.flow_ctrl_manager import GUIType
        if gui_type == GUIType.NODE_GUI.value:
            return LogarithmicLabelDoubleSliderSpinBox(parent_widget, self.parameters, is_preview=self.is_preview)
        elif gui_type == GUIType.POPUP_GUI.value:
            return LabelDoubleNumberBox(parent_widget, self.parameters)
        else:
            raise Exception(f'The value of gui_type must be one of the values {list(GUIType)}')
