from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *


def test_design_rule_check_when_doing_nothing(window):
    assert not window.onDesignRuleCheck()  # when doing nothing, design is invalid


def test_design_rule_check_no_aos_in_main_sub_window(window):
    window.onFileNew()
    assert not window.onDesignRuleCheck()


def test_design_rule_check_ao_not_connected(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    main_sub_window.add_ao(OP_NODE_DAC)
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The nodes IN and OUT are not connected, so the design is invalid


def test_design_rule_check_ao_connected(window):
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
    make_all_sub_window_not_modified(window)
    assert window.onDesignRuleCheck()  # The nodes IN and OUT are connected, so the design is valid

def test_design_rule_check_ao_connected_TONEGEN(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_TONEGEN)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)
    assert window.onDesignRuleCheck()  # The nodes IN and TONEGEN are connected, so the design is valid

def test_design_rule_check_aos_in_sub_patch_not_connected(window):
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
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The nodes in subPatch are not connected, so the design is invalid


def test_design_rule_check_aos_in_subpatch_connected(window):
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
    make_all_sub_window_not_modified(window)
    assert window.onDesignRuleCheck()


def test_design_rule_check_aos_in_closed_sub_patch_connected(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
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
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    make_all_sub_window_not_modified(window)
    assert window.onDesignRuleCheck()


def test_design_rule_check_not_supported_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    node_vep = main_sub_window.add_ao(OP_NODE_CLIPFIX)
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
    vep_ao_input_socket = node_vep.inputs[0]
    vep_ao_output_socket = node_vep.outputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=vep_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=vep_ao_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The design is not valid because the VEP AO is not supported on PC


def test_design_rule_check_not_supported_ao_not_connected(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    main_sub_window.add_ao(OP_NODE_DAC)
    main_sub_window.add_ao(OP_NODE_AI_NR)
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()


def test_design_rule_check_not_supported_ao_in_closed_sub_patch_window(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
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
    node_vep = sub_patch_sub_window.add_ao(OP_NODE_CLIPFIX)
    vep_ao_input_socket = node_vep.inputs[0]
    vep_ao_output_socket = node_vep.outputs[0]
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
                                                    end_socket=vep_ao_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
        sub_patch_sub_window.view.dragging.add_edge(start_socket=vep_ao_output_socket,
                                                    end_socket=outlet_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The design is not valid because the VEP AO is not supported on PC


def test_design_rule_check_not_supported_ao_in_encrypted_sub_patch_window(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
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
    node_vep = sub_patch_sub_window.add_ao(OP_NODE_CLIPFIX)
    vep_ao_input_socket = node_vep.inputs[0]
    vep_ao_output_socket = node_vep.outputs[0]
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
                                                    end_socket=vep_ao_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
        sub_patch_sub_window.view.dragging.add_edge(start_socket=vep_ao_output_socket,
                                                    end_socket=outlet_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
    sub_patch_node.lock(password='123')
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    window.sub_patchs[0].already_input_password = False
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The design is not valid because the VEP AO is not supported on PC


def test_design_rule_check_not_supported_ao_in_encrypted_sub_patch_window_already_inputted_password(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
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
    node_vep = sub_patch_sub_window.add_ao(OP_NODE_CLIPFIX)
    vep_ao_input_socket = node_vep.inputs[0]
    vep_ao_output_socket = node_vep.outputs[0]
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
                                                    end_socket=vep_ao_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
        sub_patch_sub_window.view.dragging.add_edge(start_socket=vep_ao_output_socket,
                                                    end_socket=outlet_input_socket,
                                                    ignore_message_box=True,
                                                    ignore_drag_edge=True)
    sub_patch_node.lock(password='123')
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()  # The design is not valid because the VEP AO is not supported on PC


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_design_rule_check_encrypted_multiple_level_sub_patch_not_supported_ao(window, tests_dir_path,
                                                                               project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    node_in = main_sub_window.add_ao(OP_NODE_ADC)
    node_out = main_sub_window.add_ao(OP_NODE_DAC)
    sub_patch_node1 = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                             parameters={'num_in_channels': 1, 'num_out_channels': 1})
    in_ao_output_socket = node_in.outputs[0]
    out_ao_input_socket = node_out.inputs[0]
    sub_patch_node1_input_socket = sub_patch_node1.inputs[0]
    sub_patch_node1_output_socket = sub_patch_node1.outputs[0]
    main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                           end_socket=sub_patch_node1_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    main_sub_window.view.dragging.add_edge(start_socket=sub_patch_node1_output_socket,
                                           end_socket=out_ao_input_socket,
                                           ignore_message_box=True,
                                           ignore_drag_edge=True)
    sub_patch_sub_window1 = window.mdiArea.subWindowList()[1].widget()
    sub_patch_node2 = sub_patch_sub_window1.add_ao(OP_NODE_SUBPATCH,
                                                   parameters={'num_in_channels': 1,
                                                               'num_out_channels': 1})
    sub_patch_node2_input_socket = sub_patch_node2.inputs[0]
    sub_patch_node2_output_socket = sub_patch_node2.outputs[0]
    inlet = outlet = None
    for node in sub_patch_sub_window1.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    if inlet and outlet:
        inlet_output_socket = inlet.outputs[0]
        outlet_input_socket = outlet.inputs[0]
        sub_patch_sub_window1.view.dragging.add_edge(start_socket=inlet_output_socket,
                                                     end_socket=sub_patch_node2_input_socket,
                                                     ignore_message_box=True,
                                                     ignore_drag_edge=True)
        sub_patch_sub_window1.view.dragging.add_edge(start_socket=sub_patch_node2_output_socket,
                                                     end_socket=outlet_input_socket,
                                                     ignore_message_box=True,
                                                     ignore_drag_edge=True)
    sub_patch_sub_window2 = window.mdiArea.subWindowList()[2].widget()
    sub_patch_node3 = sub_patch_sub_window2.add_ao(OP_NODE_SUBPATCH,
                                                   parameters={'num_in_channels': 1,
                                                               'num_out_channels': 1})
    sub_patch_node3_input_socket = sub_patch_node3.inputs[0]
    sub_patch_node3_output_socket = sub_patch_node3.outputs[0]
    inlet = outlet = None
    for node in sub_patch_sub_window2.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    if inlet and outlet:
        inlet_output_socket = inlet.outputs[0]
        outlet_input_socket = outlet.inputs[0]
        sub_patch_sub_window2.view.dragging.add_edge(start_socket=inlet_output_socket,
                                                     end_socket=sub_patch_node3_input_socket,
                                                     ignore_message_box=True,
                                                     ignore_drag_edge=True)
        sub_patch_sub_window2.view.dragging.add_edge(start_socket=sub_patch_node3_output_socket,
                                                     end_socket=outlet_input_socket,
                                                     ignore_message_box=True,
                                                     ignore_drag_edge=True)
    sub_patch_sub_window3 = window.mdiArea.subWindowList()[3].widget()
    sub_patch_sub_window3.add_ao(OP_NODE_AI_NR)
    # encrypt sub_patch_node2
    sub_patch_node2.lock(password='123')
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    make_all_sub_window_not_modified(window)
    assert not window.onDesignRuleCheck()
