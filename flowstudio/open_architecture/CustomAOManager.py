import os
import json
import shutil

from open_architecture.AOTuningParameterImporter import AOTuningParameterImporter
from flowstudio.flow_conf import FLOW_NODES, FLOW_NODES_TYPES, FLOW_NODES_DISPLAY_NAMES, NOT_SUPPORT_AOS, \
    CATE_AO_MAPPING, AO_TYPE_NAME
from flowstudio.flow_conf_list import AUDIO_OBJECT


class CustomAOManager:
    def __init__(self, window):
        self.parent = window
        self.custom_folder_path = self.parent.userPath + '/custom'
        self.custom_aos_config_file_path = self.custom_folder_path + '/custom-aos-config.json'
        self.temp_folder_path = self.parent.userPath + '/custom/temp'
        self.is_custom_category_expanded = False

    def clear_custom_aos_from_system(self):
        if not os.path.exists(self.custom_aos_config_file_path):
            return
        with open(self.custom_aos_config_file_path, 'r') as file:
            aos = json.load(file)
        if 'Custom' in CATE_AO_MAPPING:
            CATE_AO_MAPPING['Custom'] = []
        for ao in aos:
            ao_code = ao['ao_code']
            ao_name = ao['ao_name']
            ao_display_name = ao['display_name']
            if ao_code in FLOW_NODES:
                del FLOW_NODES[ao_code]
            if ao_name in FLOW_NODES_TYPES:
                del FLOW_NODES_TYPES[ao_name]
            if ao_display_name in FLOW_NODES_DISPLAY_NAMES:
                del FLOW_NODES_DISPLAY_NAMES[ao_display_name]
            if ao_name in AUDIO_OBJECT:
                del AUDIO_OBJECT[ao_name]
            for key, value in NOT_SUPPORT_AOS.items():
                if ao_code in value:
                    value.remove(ao_code)
            if ao_code in self.parent.license_mechanism.feature_permission_data[AO_TYPE_NAME]:
                self.parent.license_mechanism.feature_permission_data[AO_TYPE_NAME].remove(ao_code)
            if ao_code in self.parent.license_mechanism.ao_info_data:
                del self.parent.license_mechanism.ao_info_data[ao_code]
            if not os.path.exists(self.temp_folder_path):
                os.makedirs(self.temp_folder_path)
            for file_name in os.listdir(self.custom_folder_path):
                if file_name.endswith('.png'):
                    source = os.path.join(self.custom_folder_path, file_name)
                    destination = os.path.join(self.temp_folder_path, file_name)
                    shutil.move(source, destination)

        top_level_count = self.parent.nodesListWidget.topLevelItemCount()
        custom_category_item = None
        custom_category_index = -1
        for i in range(top_level_count):
            top_item = self.parent.nodesListWidget.topLevelItem(i)
            if 'Custom' in top_item.text(0):
                custom_category_item = top_item
                custom_category_index = i
                self.is_custom_category_expanded = top_item.isExpanded()
                break
        if custom_category_index != -1:
            widgets = []
            child_count = custom_category_item.childCount()
            for i in range(child_count):
                child_item = custom_category_item.child(i)
                widgets.append(child_item)
            self.parent.nodesListWidget.takeTopLevelItem(custom_category_index)
            for widget in widgets:
                self.parent.nodesListWidget.items.remove(widget)
    def handle_icon_of_aos(self, aos):
        if not os.path.exists(self.custom_folder_path):
            os.makedirs(self.custom_folder_path)
        for ao in aos:
            icon_path = ao.get('icon_file_path')
            if not icon_path:
                continue

            # Check if the path includes a folder
            if os.path.dirname(icon_path):
                # Move the file to the custom folder
                destination_path = os.path.join(self.custom_folder_path, os.path.basename(icon_path))
                shutil.copy(icon_path, destination_path)
                ao['icon_file_path'] = os.path.basename(icon_path)
                ao['is_icon_file_in_predefined_folder'] = True
            else:
                # Move the file from temp folder to custom folder
                temp_path = os.path.join(self.temp_folder_path, icon_path)
                destination_path = os.path.join(self.custom_folder_path, icon_path)
                if os.path.exists(temp_path):
                    shutil.move(temp_path, destination_path)

        # Remove the temp folder
        if os.path.exists(self.temp_folder_path):
            shutil.rmtree(self.temp_folder_path)


    def add_aos_to_system_from_config_file(self):
        from open_architecture.AOClassGenerator import AOClassGenerator
        with open(self.custom_aos_config_file_path, 'r') as file:
            aos = json.load(file)
        for ao in aos:
            AOTuningParameterImporter().import_ao_tuning_parameters(ao)
            ao_class = AOClassGenerator(self).generate_ao_class(ao)
            FLOW_NODES[ao_class.op_code] = ao_class
            FLOW_NODES_TYPES[ao_class.content_label_objname] = ao_class
            FLOW_NODES_DISPLAY_NAMES[ao_class.display_name] = ao_class
            self.add_ao_support_platforms(ao)
            self.add_ao_to_mapping(ao)
            self.add_ao_to_permission_data(ao)
            self.add_ao_info_data(ao)
            self.add_ao_to_ao_pane(ao)
            self.parent.settingDialog.onTargetSelect()
            self.parent.handle_ao_filter_q_checkbox()
        if len(aos) > 0:
            self.parent.exist_custom_aos = True
        else:
            self.parent.exist_custom_aos = False
        self.parent.update_export_custom_aos_settings_availability()

    def add_ao_support_platforms(self, ao):
        all_platforms = set(NOT_SUPPORT_AOS.keys())
        for platform in all_platforms:
            if platform not in ao['support_platforms']:
                if ao['ao_code'] not in NOT_SUPPORT_AOS[platform]:
                    NOT_SUPPORT_AOS[platform].append(ao['ao_code'])

    def add_ao_to_mapping(self, ao):
        if 'Custom' not in CATE_AO_MAPPING:
            CATE_AO_MAPPING['Custom'] = []
        CATE_AO_MAPPING['Custom'].append(ao['ao_code'])

    def add_ao_to_ao_pane(self, ao):
        top_level_count = self.parent.nodesListWidget.topLevelItemCount()
        custom_category_item = None
        custom_category_index = -1
        for i in range(top_level_count):
            top_item = self.parent.nodesListWidget.topLevelItem(i)
            if 'Custom' in top_item.text(0):
                custom_category_item = top_item
                custom_category_index = i
                break
        if custom_category_item is None:
            self.parent.nodesListWidget.addMyItems(category_name='Custom')
            if self.is_custom_category_expanded:
                top_level_count = self.parent.nodesListWidget.topLevelItemCount()
                for i in range(top_level_count):
                    top_item = self.parent.nodesListWidget.topLevelItem(i)
                    if 'Custom' in top_item.text(0):
                        custom_category_item = top_item
                        break
                custom_category_item.setExpanded(True)
        else:
            widgets = []
            child_count = custom_category_item.childCount()
            for i in range(child_count):
                child_item = custom_category_item.child(i)
                widgets.append(child_item)
            self.parent.nodesListWidget.takeTopLevelItem(custom_category_index)
            for widget in widgets:
                self.parent.nodesListWidget.items.remove(widget)
            self.parent.nodesListWidget.addMyItems(category_name='Custom')
            if self.is_custom_category_expanded:
                self.parent.nodesListWidget.topLevelItem(custom_category_index).setExpanded(True)

    def add_ao_to_permission_data(self, ao):
        self.parent.license_mechanism.feature_permission_data[AO_TYPE_NAME].append(ao['ao_code'])
        self.parent.license_mechanism.custom_ao_list = []
        self.parent.license_mechanism.custom_ao_list.append(ao['ao_code'])

    def add_ao_info_data(self, ao):
        self.parent.license_mechanism.ao_info_data[ao['ao_code']] = ao['description']
