import os
import pathlib
from xml.etree import ElementTree
from flowstudio.tests.test_base import window
from flowstudio.flow_conf import OP_NODE_ADC, OP_NODE_DAC, OP_NODE_SUBPATCH, OP_NODE_INLET, OP_NODE_OUTLET
from flowstudio.tests.common_functions import make_all_sub_window_not_modified


def parse_xml_string_to_dict(xml_string):
    # Parse XML string
    root = ElementTree.fromstring(xml_string)

    # Initialize result dictionary
    result = {}

    # Process each AO element
    for ao in root.findall('AO'):
        ao_id = ao.get('id')
        ao_data = {}

        # Process 'to' connections
        to_list = []
        elements = ao.findall('to')
        sorted_elements = sorted(elements, key=lambda x: int(x.attrib['index']))
        for to in sorted_elements:
            port = to.get('port')
            index = int(to.get('dir'))
            to_list.append([port, index])
        if to_list:
            ao_data['to'] = to_list

        # Process 'from' connections
        from_list = []
        elements = ao.findall('from')
        sorted_elements = sorted(elements, key=lambda x: int(x.attrib['index']))
        for from_elem in sorted_elements:
            port = from_elem.get('port')
            index = int(from_elem.get('index'))
            from_list.append([port, index])
        if from_list:
            ao_data['from'] = from_list

        # Process parameters
        params = {}
        for param in ao.findall('param'):
            name = param.get('name')
            val = param.get('val')
            params[name] = val
        if params:
            ao_data['param'] = params

        # Add to result if we have data
        if ao_data:
            result[ao_id] = ao_data

    return result


def compare_dicts(dict1, dict2):
    if dict1.keys() != dict2.keys():
        return False

    for key in dict1:
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            if not compare_dicts(dict1[key], dict2[key]):
                return False
        elif isinstance(dict1[key], list) and isinstance(dict2[key], list):
            if dict1[key] != dict2[key]:
                return False
        else:
            if dict1[key] != dict2[key]:
                return False

    return True


def test_identical_flw_content_for_one_in_out_subpatch(window):
    """
        1. An IN connected to an OUT,
        2. An IN connected to an OUT, with a subpatch in between;
        The exported flw file content from these two signal flows must be identical.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_node = main_sub_window.add_ao(OP_NODE_ADC)
    out_node = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = in_node.outputs[0]
    out_ao_input_socket = out_node.inputs[0]
    sub_patch_node_input_socket = sub_patch_node.inputs[0]
    sub_patch_node_output_socket = sub_patch_node.outputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=sub_patch_node_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=sub_patch_node_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inlet = outlet = None
    for node in sub_patch_sub_window.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    if inlet and outlet:
        inlet_output_socket = inlet.outputs[0]
        outlet_input_socket = outlet.inputs[0]
        sub_patch_sub_window.view.dragging.add_edge(start_socket=inlet_output_socket,
                                                    end_socket=outlet_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))


def test_identical_flw_content_for_one_in_out_two_subpatch(window):
    """
        1. An IN connected to an OUT,
        2. An IN connected to an OUT, with two sub patches in between;
        The exported flw file content from these two signal flows must be identical.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_node = main_sub_window.add_ao(OP_NODE_ADC)
    out_node = main_sub_window.add_ao(OP_NODE_DAC)
    first_sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                  parameters={'num_in_channels': 1, 'num_out_channels': 1})
    second_sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                   parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = in_node.outputs[0]
    out_ao_input_socket = out_node.inputs[0]
    first_sub_patch_node_input_socket = first_sub_patch_node.inputs[0]
    first_sub_patch_node_output_socket = first_sub_patch_node.outputs[0]
    second_sub_patch_node_input_socket = second_sub_patch_node.inputs[0]
    second_sub_patch_node_output_socket = second_sub_patch_node.outputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=first_sub_patch_node_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=first_sub_patch_node_output_socket,
                                           end_socket=second_sub_patch_node_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=second_sub_patch_node_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    first_sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inlet = outlet = None
    for node in first_sub_patch_sub_window.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    if inlet and outlet:
        inlet_output_socket = inlet.outputs[0]
        outlet_input_socket = outlet.inputs[0]
        first_sub_patch_sub_window.view.dragging.add_edge(start_socket=inlet_output_socket,
                                                          end_socket=outlet_input_socket,
                                                          ignore_message_box=True,
                                                          ignore_drag_edge=True)
    second_sub_patch_sub_window = window.mdiArea.subWindowList()[2].widget()
    inlet = outlet = None
    for node in second_sub_patch_sub_window.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    if inlet and outlet:
        inlet_output_socket = inlet.outputs[0]
        outlet_input_socket = outlet.inputs[0]
        second_sub_patch_sub_window.view.dragging.add_edge(start_socket=inlet_output_socket,
                                                           end_socket=outlet_input_socket,
                                                           ignore_message_box=True,
                                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))


def test_identical_flw_content_for_one_in_out_two_subpatch_inside(window):
    """
        The necessary parts of the exported flw file content from
        "An IN connected to an OUT" and
        in-out-two-sub-patches-inside.proj must be identical.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    dir_path = str(pathlib.Path(__file__).parent.resolve())
    window.onFileOpen(project_file_path=os.path.join(dir_path, 'in-out-two-sub-patches-inside.proj'))
    main_sub_window = window.findMain().widget()
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.temp_folder_path, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))


def test_identical_flw_content_for_one_in_two_out_one_subpatch(window):
    """
        The necessary parts of the exported flw file content from
        "An IN connected to two OUTs" and
        one-in-sub-patch-two-out.proj must be identical.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    first_out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    second_out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    first_out_ao_input_socket = first_out_ao.inputs[0]
    second_out_ao_input_socket = second_out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=first_out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=second_out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    dir_path = str(pathlib.Path(__file__).parent.resolve())
    window.onFileOpen(project_file_path=os.path.join(dir_path, 'one-in-sub-patch-two-out.proj'))
    main_sub_window = window.findMain().widget()
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.temp_folder_path, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))


def test_identical_flw_content_for_one_in_two_out_one_subpatch_with_two_outputs(window):
    """
        The necessary parts of the exported flw file content from
        "An IN connected to two OUTs" and
        one-in-sub-patch-two-outputs-two-out.proj must be identical.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    first_out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    second_out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    first_out_ao_input_socket = first_out_ao.inputs[0]
    second_out_ao_input_socket = second_out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=first_out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=second_out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.userPath, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    dir_path = str(pathlib.Path(__file__).parent.resolve())
    window.onFileOpen(project_file_path=os.path.join(dir_path, 'one-in-sub-patch-two-outputs-two-out.proj'))
    main_sub_window = window.findMain().widget()
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.temp_folder_path, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))


def test_identical_flw_content_for_soundbar_reference_template_with_without_sub_patches(window):
    """
        The necessary parts of the exported flw file content from
        soundbar-reference-with-subpatch.proj and
        soundbar-reference-without-subpatch.proj must be identical.
    """
    dir_path = str(pathlib.Path(__file__).parent.resolve())
    window.onFileOpen(project_file_path=os.path.join(dir_path, 'soundbar-reference-with-subpatch.proj'))
    main_sub_window = window.findMain().widget()
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.temp_folder_path, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_with_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=os.path.join(dir_path, 'soundbar-reference-without-subpatch.proj'))
    main_sub_window = window.findMain().widget()
    main_sub_window.exportXML(sub_window=main_sub_window, is_to_binary=False)
    with open(os.path.join(window.temp_folder_path, 'default_config.flw'), 'r', encoding='utf-8') as file:
        content_without_subpatch = file.read()
    make_all_sub_window_not_modified(window)
    assert compare_dicts(parse_xml_string_to_dict(content_without_subpatch),
                         parse_xml_string_to_dict(content_with_subpatch))
