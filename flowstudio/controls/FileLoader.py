from flowstudio.flow_conf import *
from control.flow_control_widget import LabelAndLineEditAndBtn

@register_control(ControlType.LOAD_FILE.value)
class FileLoader(object):
    gui_type = ControlType.LOAD_FILE.value

    def __init__(self, label_text, file_extensions=None, parameters=None):
        self.label_text = label_text
        temp_str = ''
        accept_file_extensions = []
        if file_extensions is not None:
            for file_extension in file_extensions:
                for key, values in file_extension.items():
                    temp_str += key + ' ('
                    for value in values:
                        accept_file_extensions.append(value)
                        temp_str += f'*.{value} '
                    temp_str = temp_str[:-1] + ');;'
            temp_str = temp_str[:-2]
        self.accept_file_extensions = accept_file_extensions if accept_file_extensions else ['*']
        self.filter_str = temp_str if temp_str else 'All files (*)'
        self.parameters = parameters if parameters is not None else {}

    def get_widget(self, parent_widget, gui_type=None):
        return LabelAndLineEditAndBtn(parent_widget, self.label_text, self.filter_str,
                                      self.accept_file_extensions, self.parameters)
