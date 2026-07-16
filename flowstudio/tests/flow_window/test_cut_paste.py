from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *


def test_cut_paste_selected_one_in_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    in_ao_gr_node = in_ao.grNode
    select_items([in_ao_gr_node])
    window.onEditCut()
    window.onEditPaste()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1


def test_cut_paste_selected_one_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditCut()
    window.onEditPaste()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 2


def test_cut_paste_selected_one_closed_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCut()
    window.onEditPaste()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 2


def test_cut_paste_selected_one_sub_patch_which_contains_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCut()
    window.onEditPaste()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_cut_paste_selected_one_sub_patch_which_has_not_inputted_password(window, tests_dir_path,
                                                                          project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.scene.nodes[0]
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditCut()
    window.onEditPaste()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 1
