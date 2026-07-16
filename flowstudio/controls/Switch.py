from flowstudio.flow_conf import *
from control.flow_control_widget import LabelAndSwitch
from flowstudio.controls.ControlBase import ControlBase


@register_control(ControlType.SWITCH.value)
class Switch(ControlBase):
    gui_type = ControlType.SWITCH.value
    required_parameters = [{'key': 'label_text', 'value': '', 'description': 'The label text'},
                           {'key': 'pValue', 'value': 'on', 'options': ['on', 'off'], 'description': 'Initial value'}]

    def __init__(self, label_text, initial_val, is_preview=False, additional_parameters=None):
        """
        Initialize a Switch object.

        Args:
            label_text (str): The label name of the switch.
            initial_val (str): The initial value of the switch ('on' or 'off').
            is_preview (bool, optional): This parameter indicates whether it is in preview mode.
                                         If it is in preview mode, interacting with the widget will not trigger events.
            additional_parameters (dict, optional): Additional parameters for the switch.

        Raises:
            Exception: If the p_value is neither 'on' nor 'off'.
        """
        if initial_val != 'on' and initial_val != 'off':
            raise Exception("Value of p_value must be 'on' or 'off'.")
        self.label_text = label_text
        self.is_preview = is_preview
        self.parameters = {'pMax': 'on', 'pMin': 'off', 'pValue': initial_val, 'label_text': label_text}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndSwitch(parent_widget, self.parameters,
                              is_preview=self.is_preview)
