from flowstudio.flow_conf import *
from control.flow_control_widget import LinearLabelDoubleSliderSpinBox, LabelDoubleNumberBox, \
    VerticalLinearLabelDoubleSliderSpinBoxHasButtons
from flowstudio.controls.ControlBase import ControlBase


@register_control(ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value)
class LinearFloatSliderAndSpinBox(ControlBase):
    gui_type = ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value
    required_parameters = [{'key': 'label_text', 'value': '', 'description': 'The label text'},
                           {'key': 'pMax', 'value': 0.0, 'description': 'The maximum value'},
                           {'key': 'pMin', 'value': 0.0, 'description': 'The minimum value'},
                           {'key': 'pValue', 'value': 0.0, 'description': 'The initial value'},
                           {'key': 'is_slider_needed', 'value': 'Yes', 'options': ['Yes', 'No'], 'description': 'Is slider needed?'},
                           {'key': 'pDecimalPrecision', 'value': 2, 'description': 'Number of decimal places', 'minimum': 2}]

    def __init__(self, label_text, max_value, min_value, initial_value,
                 is_slider_needed=True,
                 num_decimal_places=2,
                 orientation='horizontal',
                 has_buttons=False,
                 additional_parameters=None,
                 is_preview=False):
        if orientation != 'vertical' and orientation != 'horizontal':
            raise Exception("Value of orientation must be 'vertical' or 'horizontal'.")
        self.label_text = label_text
        self.parameters = {'pMax': max_value, 'pMin': min_value, 'pValue': initial_value,
                           'label_text': label_text, 'is_slider_needed': is_slider_needed,
                           'pDecimalPrecision': num_decimal_places}
        self.orientation = orientation
        self.has_buttons = has_buttons
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)
        self.is_preview = is_preview

    def get_widget(self, parent_widget, gui_type):
        from flowstudio.flow_ctrl_manager import GUIType
        if gui_type == GUIType.NODE_GUI.value:
            if self.orientation == 'horizontal' and not self.has_buttons:
                return LinearLabelDoubleSliderSpinBox(parent_widget, self.parameters, is_preview=self.is_preview)
            elif self.orientation == 'vertical' and self.has_buttons:
                return VerticalLinearLabelDoubleSliderSpinBoxHasButtons(parent_widget, self.parameters)
            else:
                raise Exception(f'This parameter combination has not yet been implemented in the corresponding UI.')
        elif gui_type == GUIType.POPUP_GUI.value:
            return LabelDoubleNumberBox(parent_widget, self.parameters)
        else:
            raise Exception(f'The value of gui_type must be one of the values {list(GUIType)}')
