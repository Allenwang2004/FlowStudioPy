import os
import json
from PyQt5.QtWidgets import *
from flowstudio.functions.common import is_valid_json
from flowstudio.flow_conf import *


class ConfigFileValidator(object):
    def __init__(self, window):
        self.parent = window
        self.custom_folder_path = self.parent.userPath + '/custom'
        self.custom_aos_config_file_path = self.custom_folder_path + '/custom-aos-config.json'

    def validate(self):
        gui_type_no_allowed = [ele[1] for ele in CONTROL_TYPES_FOR_OA]
        if not self.check_custom_folder_exists():
            if Debug.DEBUG_COMMON.value:
                print('The custom folder does not exist.')
            return False
        if Debug.DEBUG_COMMON.value:
            print('The custom folder exists.')
        if not self.check_custom_aos_config_file_exists():
            if Debug.DEBUG_COMMON.value:
                print('The custom AOs config file does not exist.')
            return False
        if Debug.DEBUG_COMMON.value:
            print('The custom AOs config file exists.')
        if not is_valid_json(self.custom_aos_config_file_path):
            self.show_config_file_format_incorrect_message_box()
            return False
        is_not_support_platforms_column_exist = False
        with open(self.custom_aos_config_file_path, 'r') as file:
            aos = json.load(file)
            if type(aos) is dict:
                self.show_config_file_format_incorrect_message_box()
                return False
            custom_ao_names = set()
            custom_ao_codes = set()
            for ao in aos:
                if 'ao_name' not in ao:
                    if Debug.DEBUG_COMMON.value:
                        print('There is an AO without an ao_name field.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                ao_name = ao['ao_name']
                if ao_name in FLOW_NODES_TYPES or ao_name in custom_ao_names:
                    if Debug.DEBUG_COMMON.value:
                        print('The ao_name has duplicates.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                custom_ao_names.add(ao_name)
                if 'ao_code' not in ao:
                    if Debug.DEBUG_COMMON.value:
                        print('There is an AO without an ao_code field.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                ao_code = ao['ao_code']
                if ao_code in FLOW_NODES or ao_code in custom_ao_codes:
                    if Debug.DEBUG_COMMON.value:
                        print('The ao_code has duplicates.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                custom_ao_codes.add(ao_code)
                if 'is_float_point' not in ao:
                    if Debug.DEBUG_COMMON.value:
                        print('There is an AO without an is_float_point field.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                if 'type_ao_addition' not in ao:
                    if Debug.DEBUG_COMMON.value:
                        print('There is an AO without a type_ao_addition field.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                type_ao_addition = ao['type_ao_addition']
                types_ao_addition_allowed = []
                for ele in AO_ADDITION_TYPES_FOR_OA:
                    types_ao_addition_allowed.append(ele[1])
                if type_ao_addition not in types_ao_addition_allowed:
                    if Debug.DEBUG_COMMON.value:
                        print(f'Value of type_ao_addition {type_ao_addition} of AO {ao_name} is not allowed.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                if 'collapsible' not in ao:
                    if Debug.DEBUG_COMMON.value:
                        print('There is an AO without a collapsible field.')
                    self.show_config_file_format_incorrect_message_box()
                    return False
                if 'tuning_parameters' in ao:
                    tuning_parameters = ao['tuning_parameters']
                    tuning_parameter_names = set()
                    for tuning_parameter in tuning_parameters:
                        if 'name' not in tuning_parameter:
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there is a tuning parameter without a name field.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        tuning_parameter_name = tuning_parameter['name']
                        if not tuning_parameter_name:
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there is a tuning parameter with an empty name.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        if tuning_parameter_name in tuning_parameter_names:
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there are duplicate tuning parameter names.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        tuning_parameter_names.add(tuning_parameter_name)
                        if 'gui_type_no' not in tuning_parameter:
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there is a tuning parameter without a gui_type_no field.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        gui_type_no = tuning_parameter['gui_type_no']
                        if gui_type_no not in gui_type_no_allowed:
                            if Debug.DEBUG_COMMON.value:
                                print(f'Value of gui_type_no {gui_type_no} of AO {ao_name} is not allowed.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        keys_of_required_parameters = CONTROLS_MAPPING[gui_type_no].get_keys_from_required_parameters()
                        count = {}
                        for key_of_required_parameter in keys_of_required_parameters:
                            count[key_of_required_parameter] = 0
                        for param in tuning_parameter['parameters']:
                            if 'key' not in param:
                                if Debug.DEBUG_COMMON.value:
                                    print(f'In AO {ao_name}, there is a tuning parameter without a key field.')
                                self.show_config_file_format_incorrect_message_box()
                                return False
                            param_key = param['key']
                            if param_key in count:
                                count[param_key] += 1
                            else:
                                if Debug.DEBUG_COMMON.value:
                                    print(f'In AO {ao_name}, there is a parameter with an invalid key within a tuning parameter.')
                                self.show_config_file_format_incorrect_message_box()
                                return False
                        if 0 in count.values():
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there is a tuning parameter without a required parameter.')
                            self.show_config_file_format_incorrect_message_box()
                            return False
                        if any(val >= 2 for val in count.values()):
                            if Debug.DEBUG_COMMON.value:
                                print(f'In AO {ao_name}, there are duplicate required parameters in a tuning parameter.')
                            self.show_config_file_format_incorrect_message_box()
                            return False


                # Add support_platforms column if not_support_platforms column exists
                if 'not_support_platforms' in ao:
                    is_not_support_platforms_column_exist = True
                    all_platforms = set(NOT_SUPPORT_AOS.keys())
                    not_support_platforms = set(ao['not_support_platforms'])
                    support_platforms = list(all_platforms - not_support_platforms)
                    ao['support_platforms'] = support_platforms
                    del ao['not_support_platforms']
        # Save the custom AO configuration file with the support_platforms column
        if is_not_support_platforms_column_exist:
            with open(self.custom_aos_config_file_path, 'w') as file:
                json.dump(aos, file, indent=4)
        return True

    def check_custom_folder_exists(self):
        return os.path.exists(self.custom_folder_path)

    def check_custom_aos_config_file_exists(self):
        return os.path.isfile(self.custom_aos_config_file_path)

    def show_config_file_format_incorrect_message_box(self):
        QMessageBox.warning(self.parent, 'The custom AO configuration file format is incorrect',
                            f'The custom AO configuration file format is incorrect. Please import the correct configuration file.')
