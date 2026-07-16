from collections import OrderedDict

from flowstudio.flow_conf import ControlType, CONTROLS_MAPPING
from flowstudio.flow_conf_list import AUDIO_OBJECT


class AOTuningParameterImporter:
    def import_ao_tuning_parameters(self, ao: dict):
        tuning_parameters = OrderedDict()
        for tuning_parameter in ao['tuning_parameters']:
            gui_type_no = tuning_parameter['gui_type_no']
            parameters = tuning_parameter['parameters']
            tuning_parameter_name = tuning_parameter['name']
            if gui_type_no == ControlType.SWITCH.value:
                tuning_parameters[tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=self.get_parameter_value_by_key(parameters, 'label_text'),
                    initial_val=self.get_parameter_value_by_key(parameters, 'pValue'))
            elif gui_type_no == ControlType.LABEL.value:
                tuning_parameters[tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    initial_val=self.get_parameter_value_by_key(parameters, 'label_text'))
            elif gui_type_no == ControlType.MENU.value:
                tuning_parameters[tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=self.get_parameter_value_by_key(parameters, 'label_text'),
                    items=self.get_parameter_value_by_key(parameters, 'pList'),
                    current_selected_item=self.get_parameter_value_by_key(parameters, 'pList')[self.get_parameter_value_by_key(parameters, 'pValue')])
            elif gui_type_no == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value:
                tuning_parameters[tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=self.get_parameter_value_by_key(parameters, 'label_text'),
                    max_value=self.get_parameter_value_by_key(parameters, 'pMax'),
                    min_value=self.get_parameter_value_by_key(parameters, 'pMin'),
                    initial_value=self.get_parameter_value_by_key(parameters, 'pValue'),
                    is_slider_needed=True if self.get_parameter_value_by_key(parameters, 'is_slider_needed') == 'Yes' else False,
                    num_decimal_places=self.get_parameter_value_by_key(parameters, 'pDecimalPrecision'))
            elif (gui_type_no == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value
                  or gui_type_no == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value
                  or gui_type_no == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value):
                tuning_parameters[tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=self.get_parameter_value_by_key(parameters, 'label_text'),
                    max_value=self.get_parameter_value_by_key(parameters, 'pMax'),
                    min_value=self.get_parameter_value_by_key(parameters, 'pMin'),
                    initial_value=self.get_parameter_value_by_key(parameters, 'pValue'))
        AUDIO_OBJECT[ao['ao_name']] = tuning_parameters

    def get_parameter_value_by_key(self, parameters: list, key: str):
        for parameter in parameters:
            if parameter['key'] == key:
                return parameter['value']
        return None
