import os
import pytest
from collections import defaultdict
from flowstudio.tests.test_base import window
from flowstudio.tests.common_functions import delete_project_file_after_test, make_all_sub_window_not_modified, \
    tests_dir_path, project_file_name
from flowstudio.flow_conf import OP_NODE_ADC, OP_NODE_DAC, OP_NODE_SUBPATCH


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_one_in_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test save and open project with one IN AO in the scene.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    assert main_sub_window.scene.nodes[0].op_code == OP_NODE_ADC


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_one_in_save_add_one_out_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test project save/open functionality by:
    1. Add IN AO & save
    2. Add OUT AO & save again
    3. Reopen project & verify both AOs exist
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    main_sub_window.add_ao(OP_NODE_DAC)
    window.onFileSave()
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    all_nodes = defaultdict(int)
    for node in main_sub_window.scene.nodes:
        all_nodes[node.op_code] += 1
    assert len(main_sub_window.scene.nodes) == 2
    assert all_nodes[OP_NODE_ADC] == 1
    assert all_nodes[OP_NODE_DAC] == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_one_subpatch_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test save and open project with one subpatch in the scene.
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    assert main_sub_window.scene.nodes[0].op_code == OP_NODE_SUBPATCH


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_one_subpatch_save_add_one_subpatch_inside_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test project save/open functionality by:
    1. Add subpatch & save
    2. Add subpatch inside the subpatch & save again
    3. Reopen project & verify both sub patches exist
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    first_sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    first_sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                      parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSave()
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    all_nodes_in_first_sub_patch_sub_window = defaultdict(int)
    for node in first_sub_patch_sub_window.scene.nodes:
        all_nodes_in_first_sub_patch_sub_window[node.op_code] += 1
    assert main_sub_window.scene.nodes[0].op_code == OP_NODE_SUBPATCH
    assert all_nodes_in_first_sub_patch_sub_window[OP_NODE_SUBPATCH] == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_one_in_one_out_connected_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test save and open project with one IN AO connected to one OUT AO.
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
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    all_nodes = defaultdict(int)
    for node in main_sub_window.scene.nodes:
        all_nodes[node.op_code] += 1
    assert all_nodes[OP_NODE_ADC] == 1
    assert all_nodes[OP_NODE_DAC] == 1
    assert main_sub_window.scene.edges[0].start_socket.id == in_ao_output_socket.id
    assert main_sub_window.scene.edges[0].end_socket.id == out_ao_input_socket.id


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_rename_subpatch_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test save and open project with renaming a subpatch
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    new_name = 'test'
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onFileSave()
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    assert main_sub_window.scene.nodes[0].title == new_name


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_enter_incorrect_password_of_sub_patch(window, tests_dir_path, project_file_name):
    """
    Test save and open project with entering incorrect password of a subpatch
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    window.decrypt_subpatch(subpatch_to_decrypt=sub_patch_node,
                            input_password='456',
                            ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_enter_correct_password_of_sub_patch(window, tests_dir_path, project_file_name):
    """
    Test save and open project with entering correct password of a subpatch
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    password = '123'
    sub_patch_node.lock(password=password)
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    window.decrypt_subpatch(subpatch_to_decrypt=sub_patch_node,
                            input_password=password,
                            ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_rename_in_save_and_open(window, tests_dir_path, project_file_name):
    """
    Test save and open project with renaming an IN AO
    """
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    in_ao.rename('test input AO', ignore_message_box=True)
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=os.path.join(tests_dir_path, f'{project_file_name}.proj'))
    assert main_sub_window.scene.nodes[0].title == 'test input AO'
