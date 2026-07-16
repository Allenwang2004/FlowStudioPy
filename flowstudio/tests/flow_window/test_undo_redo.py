from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *


def test_add_in_ao_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0


def test_add_in_ao_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    window.onEditUndo()
    assert len(main_sub_window.scene.nodes) == 0
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1


def test_add_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_add_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 2


def test_add_sub_patch_in_sub_patch_undo_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_add_sub_patch_in_sub_patch_undo_redo_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


def test_add_encrypted_sub_patch_in_sub_patch_undo_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_add_encrypted_sub_patch_in_sub_patch_undo_redo_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


def test_delete_selected_ao_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    in_ao_gr_node = in_ao.grNode
    select_items([in_ao_gr_node])
    window.onEditDelete()
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1


def test_delete_selected_ao_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    in_ao_gr_node = in_ao.grNode
    select_items([in_ao_gr_node])
    window.onEditDelete()
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0


def test_delete_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 2


def test_delete_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_delete_sub_patch_which_contains_encrypted_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


def test_delete_sub_patch_which_contains_encrypted_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_undo_delete_sub_patch_after_add_sub_patch_inside_another_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node_one = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                parameters={'num_in_channels': 1,
                                                            'num_out_channels': 1})
    sub_patch_node_two = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                parameters={'num_in_channels': 1,
                                                            'num_out_channels': 1})
    sub_patch_node_one_gr_node = sub_patch_node_one.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_one_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    sub_patch_two_sub_window = window.mdiArea.subWindowList()[1].widget()
    sub_patch_node_three = sub_patch_two_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                           parameters={'num_in_channels': 1,
                                                                       'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 2
    assert len(window.mdiArea.subWindowList()) == 4


def test_undo_redo_delete_sub_patch_after_add_sub_patch_inside_another_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node_one = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                parameters={'num_in_channels': 1,
                                                            'num_out_channels': 1})
    sub_patch_node_two = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                parameters={'num_in_channels': 1,
                                                            'num_out_channels': 1})
    sub_patch_node_one_gr_node = sub_patch_node_one.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_one_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    sub_patch_two_sub_window = window.mdiArea.subWindowList()[1].widget()
    sub_patch_node_three = sub_patch_two_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                           parameters={'num_in_channels': 1,
                                                                       'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


def test_add_two_sub_patch_undo_add_sub_patch_in_sub_patch_one_redo_in_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1,
                                       'num_out_channels': 1})
    sub_patch_one_sub_window = window.mdiArea.subWindowList()[1].widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1,
                                       'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    sub_patch_one_sub_window.add_ao(OP_NODE_SUBPATCH,
                                    parameters={'num_in_channels': 1,
                                                'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 2
    assert len(window.mdiArea.subWindowList()) == 4


def test_add_two_sub_patch_add_gain_in_sub_patch_two_undo_in_main_add_gain_in_sub_patch_one_redo_in_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1,
                                       'num_out_channels': 1})
    sub_patch_one_sub_window = window.mdiArea.subWindowList()[1].widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1,
                                       'num_out_channels': 1})
    sub_patch_two_sub_window = window.mdiArea.subWindowList()[2].widget()
    sub_patch_two_sub_window.add_ao(OP_NODE_GAIN,
                                    parameters={'num_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditUndo()
    gain_ao_two = sub_patch_one_sub_window.add_ao(OP_NODE_GAIN,
                                                  parameters={'num_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditRedo()
    sub_patch_two_sub_window = window.mdiArea.subWindowList()[2].widget()
    gain_ao_one = None
    for node in sub_patch_two_sub_window.scene.nodes:
        if node.op_code == OP_NODE_GAIN:
            gain_ao_one = node
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 2
    assert len(window.mdiArea.subWindowList()) == 3
    assert gain_ao_one.designator != gain_ao_two.designator
    assert gain_ao_one.title != gain_ao_two.title


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_delete_encrypted_sub_patch_undo(window,
                                         tests_dir_path,
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
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_delete_encrypted_sub_patch_undo_redo(window,
                                              tests_dir_path,
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
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_copy_paste_selected_one_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCopy()
    window.onEditPaste()
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 2


def test_copy_paste_selected_one_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCopy()
    window.onEditPaste()
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 2
    assert len(window.mdiArea.subWindowList()) == 3


def test_copy_paste_selected_one_sub_patch_undo_add_sub_patch_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCopy()
    window.onEditPaste()
    window.onEditUndo()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    sub_patch_node_two = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                     parameters={'num_in_channels': 1,
                                                                 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[1].title != sub_patch_node_two.title
    assert main_sub_window.scene.nodes[1].designator != sub_patch_node_two.designator


def test_copy_paste_selected_one_sub_patch_which_contains_encrypted_sub_patch_undo_in_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCopy()
    window.onEditPaste()
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 3


def test_copy_paste_selected_one_sub_patch_which_contains_encrypted_sub_patch_undo_redo_in_main(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inner_sub_patch_node = sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                                       parameters={'num_in_channels': 1,
                                                                   'num_out_channels': 1})
    inner_sub_patch_node.lock(password='123')
    sub_patch_node_gr_node = sub_patch_node.grNode
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditCopy()
    window.onEditPaste()
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 2
    assert len(window.mdiArea.subWindowList()) == 5


def test_rename_in_ao_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    original_name = in_ao.title
    new_name = 'test'
    in_ao.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == original_name


def test_rename_in_ao_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    original_name = in_ao.title
    new_name = 'test'
    in_ao.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == new_name


def test_rename_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == original_name
    assert window.mdiArea.subWindowList()[1].widget().title == original_name


def test_rename_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == new_name
    assert window.mdiArea.subWindowList()[1].widget().title == new_name


def test_rename_closed_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == original_name
    assert len(window.mdiArea.subWindowList()) == 1


def test_rename_closed_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == new_name
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_rename_saved_sub_patch_undo(window, tests_dir_path, project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.scene.nodes[0]
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == original_name
    assert window.mdiArea.subWindowList()[1].widget().title == original_name + '.json'


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_rename_saved_sub_patch_undo_redo(window, tests_dir_path, project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.scene.nodes[0]
    original_name = sub_patch_node.title
    new_name = 'test'
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.rename(new_name, ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].title == new_name
    assert window.mdiArea.subWindowList()[1].widget().title == new_name


def test_encrypt_sub_patch_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    window.onEditUndo()
    make_all_sub_window_not_modified(window)
    if hasattr(window.mdiArea.subWindowList()[1].widget(), 'encrypted'):
        assert window.mdiArea.subWindowList()[1].widget().encrypted == False


def test_encrypt_sub_patch_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    window.onEditUndo()
    window.onEditRedo()
    make_all_sub_window_not_modified(window)
    if hasattr(window.mdiArea.subWindowList()[1].widget(), 'encrypted'):
        assert window.mdiArea.subWindowList()[1].widget().encrypted == True


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_encrypt_closed_sub_patch_undo(window, tests_dir_path,
                                       project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.lock(password='123')
    window.onEditUndo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    sub_patch_node = main_sub_window.scene.nodes[0]
    window.onEnterGroupFile(sub_patch_node)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_encrypt_closed_sub_patch_undo_redo(window, tests_dir_path,
                                            project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.lock(password='123')
    window.onEditUndo()
    window.onEditRedo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_remove_password_after_encrypt_sub_patch_undo(window, tests_dir_path,
                                                      project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_node.delete_password(input_password='123', ignore_message_box=True)
    window.onEditUndo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_remove_password_after_encrypt_sub_patch_undo_redo(window, tests_dir_path,
                                                           project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_node.delete_password(input_password='123', ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    sub_patch_node = main_sub_window.scene.nodes[0]
    window.onEnterGroupFile(sub_patch_node)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_remove_password_after_encrypt_sub_patch_and_close_undo(window, tests_dir_path,
                                                                project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.delete_password(input_password='123', ignore_message_box=True)
    window.onEditUndo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_remove_password_after_encrypt_sub_patch_and_close_undo_redo(window, tests_dir_path,
                                                                     project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.delete_password(input_password='123', ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    sub_patch_node = main_sub_window.scene.nodes[0]
    window.onEnterGroupFile(sub_patch_node)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_change_password_after_encrypt_sub_patch_and_close_undo(window, tests_dir_path,
                                                                project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.change_password(input_original_password='123',
                                   input_new_password='456',
                                   input_confirm_password='456',
                                   ignore_message_box=True)
    window.onEditUndo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    sub_patch_node = main_sub_window.scene.nodes[0]
    window.decrypt_subpatch(subpatch_to_decrypt=sub_patch_node,
                            input_password='123',
                            ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_change_password_after_encrypt_sub_patch_and_close_undo_redo(window, tests_dir_path,
                                                                     project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node.change_password(input_original_password='123',
                                   input_new_password='456',
                                   input_confirm_password='456',
                                   ignore_message_box=True)
    window.onEditUndo()
    window.onEditRedo()
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    make_all_sub_window_not_modified(window)
    window.onFileOpen(project_file_path=f'{tests_dir_path}\\{project_file_name}.proj')
    sub_patch_node = main_sub_window.scene.nodes[0]
    window.decrypt_subpatch(subpatch_to_decrypt=sub_patch_node,
                            input_password='456',
                            ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


def test_add_inlet_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=True, add_outlet=False)
    window.onEditUndo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 2


def test_add_inlet_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=True, add_outlet=False)
    window.onEditUndo()
    window.onEditRedo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 3


def test_add_inlet_reduce_inlet_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=True, add_outlet=False)
    sub_patch_node = main_sub_window.scene.nodes[0]
    sub_patch_node.reduceChannel(reduce_inlet=True, reduce_outlet=False)
    window.onEditUndo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 3


def test_add_inlet_reduce_inlet_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=True, add_outlet=False)
    sub_patch_node = main_sub_window.scene.nodes[0]
    sub_patch_node.reduceChannel(reduce_inlet=True, reduce_outlet=False)
    window.onEditUndo()
    window.onEditRedo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 2


def test_add_outlet_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=False, add_outlet=True)
    window.onEditUndo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 2


def test_add_outlet_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=False, add_outlet=True)
    window.onEditUndo()
    window.onEditRedo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 3


def test_add_outlet_reduce_outlet_undo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=False, add_outlet=True)
    sub_patch_node = main_sub_window.scene.nodes[0]
    sub_patch_node.reduceChannel(reduce_inlet=False, reduce_outlet=True)
    window.onEditUndo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 3


def test_add_outlet_reduce_outlet_undo_redo(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    sub_patch_node.addChannel(add_inlet=False, add_outlet=True)
    sub_patch_node = main_sub_window.scene.nodes[0]
    sub_patch_node.reduceChannel(reduce_inlet=False, reduce_outlet=True)
    window.onEditUndo()
    window.onEditRedo()
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    make_all_sub_window_not_modified(window)
    assert len(sub_patch_sub_window.scene.nodes) == 2