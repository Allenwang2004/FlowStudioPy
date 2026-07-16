import os
from flowstudio.flow_node_base import FLOW_Node, FlowFixedPointNode
from nodeeditor.node_socket import *
from flowstudio.open_architecture.CustomAOManager import CustomAOManager
from flowstudio.flow_conf import TypeAOAddition


class AOClassGenerator:
    def __init__(self, custom_ao_manager: CustomAOManager):
        self.custom_ao_manager = custom_ao_manager

    def generate_ao_class(self, ao: dict):
        class_name = self.generate_class_name(ao)

        # Determine the base class based on the is_float_point attribute
        base_class = FLOW_Node if ao['is_float_point'] else FlowFixedPointNode

        # Create a new class dynamically
        new_class = type(class_name, (base_class,), {})

        # Add the class attributes
        new_class.op_code = ao['ao_code']
        new_class.op_title = ao['ao_name']
        new_class.content_label_objname = ao['ao_name']
        new_class.display_name = ao['display_name']
        new_class.info = ao['description']
        new_class.type_ao_addition = ao['type_ao_addition']
        new_class.expandable = ao['collapsible']
        new_class.openable = ao['is_popup_allowed']
        new_class.icon = os.path.join(self.custom_ao_manager.custom_folder_path, ao['icon_file_path'])
        __init__ = None
        if new_class.type_ao_addition == TypeAOAddition.FIXED.value:
            # Define the __init__ method
            def __init__(self, scene):
                inputs = [1] * ao['num_input_sockets']
                outputs = [1] * ao['num_output_sockets']
                in_ctrls = [0] * ao['num_inctrl_sockets']
                out_ctrls = [0] * ao['num_outctrl_sockets']
                super(new_class, self).__init__(scene, inputs=inputs, outputs=outputs, inctrls=in_ctrls,
                                                outctrls=out_ctrls)
                self.initControl()
                self.eval()
        elif new_class.type_ao_addition == TypeAOAddition.DYNAMIC_NUM_CHANNELS.value:
            new_class.linkType = 1
            # Define the __init__ method
            def __init__(self, scene, channel):
                self.inputs = [1] * channel
                self.outputs = [1] * channel
                super(new_class, self).__init__(scene, inputs=self.inputs, outputs=self.outputs)
                self.initControl()
                self.eval()
        elif new_class.type_ao_addition == TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value:
            # Define the __init__ method
            def __init__(self, scene, num_input_sockets, num_output_sockets):
                self.inputs = [1] * num_input_sockets
                self.outputs = [1] * num_output_sockets
                super(new_class, self).__init__(scene, inputs=self.inputs, outputs=self.outputs)
                self.initControl()
                self.eval()

        def initSettings(self):
            super(new_class, self).initSettings()
            self.outctrl_socket_position = RIGHT_BOTTOM

        setattr(new_class, '__init__', __init__)
        setattr(new_class, 'initSettings', initSettings)

        return new_class

    def generate_class_name(self, ao: dict):
        return ao['ao_name'].replace(' ', '_')
