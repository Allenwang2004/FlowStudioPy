from flowstudio.flow_conf import *
from control.flow_control_widget import LabelAndDisableComboBox
from flowstudio.controls.ControlBase import ControlBase


@register_control(ControlType.DISABLE_MENU.value)
class DisableMenu(ControlBase):
    gui_type = ControlType.DISABLE_MENU.value
    required_parameters = [{'key': 'label_text', 'value': '', 'description': 'The label text'},
                           {'key': 'pList', 'value': [], 'description': 'Selectable values'},
                           {'key': 'pValue', 'value': -1, 'options': [], 'type': 'index',
                            'description': 'Initial value'}]

    def __init__(self, label_text, items: list, current_selected_item,
                 is_preview=False,
                 additional_parameters=None):
        self.label_text = label_text
        if not is_preview and current_selected_item not in items:
            raise Exception('current_selected_item does not exist in items.')
        self.is_preview = is_preview
        self.parameters = {'pMax': len(items) - 1, 'pMin': 0, 'pList': items,
                           'pValue': items.index(current_selected_item) if current_selected_item is not None else -1,
                           'label_text': label_text}
        if additional_parameters is not None:
            self.parameters.update(additional_parameters)

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndDisableComboBox(parent_widget, self.parameters,
                                       is_preview=self.is_preview)
