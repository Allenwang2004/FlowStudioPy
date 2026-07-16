from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *


def test_delete_selected_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    in_ao_gr_node = in_ao.grNode
    select_items([in_ao_gr_node])
    window.onEditDelete()
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0


def test_delete_selected_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_delete_inlet_and_outlet_fail(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH,
                           parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    inlet = outlet = None
    for node in sub_patch_sub_window.scene.nodes:
        if node.op_code == OP_NODE_INLET:
            inlet = node
        if node.op_code == OP_NODE_OUTLET:
            outlet = node
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    if inlet and outlet:
        inlet_gr_node = inlet.grNode
        outlet_gr_node = outlet.grNode
        select_items([inlet_gr_node, outlet_gr_node])
        window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
        assert len(sub_patch_sub_window.scene.nodes) == 2
    make_all_sub_window_not_modified(window)


def test_delete_selected_sub_patch_which_contains_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node_gr_node = sub_patch_node.grNode
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    sub_patch_sub_window.add_ao(OP_NODE_SUBPATCH,
                                parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.setActiveSubWindow(main_sub_window.parent())
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_delete_selected_encrypted_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node.lock(password='123')
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


@pytest.mark.usefixtures('delete_project_file_after_test')
def test_delete_selected_sub_patch_of_saved_file(window, tests_dir_path, project_file_name):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    window.onFileSaveAs(dir_path=tests_dir_path, project_file_name=project_file_name)
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_delete_selected_closed_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': True})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 0
    assert len(window.mdiArea.subWindowList()) == 1


def test_delete_selected_closed_sub_patch_cancel(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    sub_patch_node_gr_node = sub_patch_node.grNode
    select_items([sub_patch_node_gr_node])
    window.onEditDelete(unit_test_parameters={'delete_sub_patch': False})
    make_all_sub_window_not_modified(window)
    assert len(main_sub_window.scene.nodes) == 1
    assert len(window.mdiArea.subWindowList()) == 1
