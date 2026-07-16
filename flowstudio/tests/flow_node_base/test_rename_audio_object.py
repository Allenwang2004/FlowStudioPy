from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *


def test_rename_in_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    new_name = 'test'
    in_ao.rename(new_name, ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert in_ao.title == new_name


def test_rename_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    new_name = 'test'
    sub_patch_node.rename(new_name, ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert sub_patch_node.title == new_name
    assert window.mdiArea.subWindowList()[1].widget().title == new_name


def test_rename_sub_patch_to_existing_name_fail(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node1 = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                             parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_node2 = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                             parameters={'num_in_channels': 1, 'num_out_channels': 1})
    new_name = 'test'
    assert sub_patch_node1.rename(new_name, ignore_message_box=True)
    assert not sub_patch_node2.rename(new_name, ignore_message_box=True)
    make_all_sub_window_not_modified(window)


def test_rename_closed_sub_patch(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    sub_patch_node = main_sub_window.add_ao(OP_NODE_SUBPATCH,
                                            parameters={'num_in_channels': 1, 'num_out_channels': 1})
    sub_patch_sub_window = window.mdiArea.subWindowList()[1].widget()
    window.setActiveSubWindow(sub_patch_sub_window.parent())
    window.closeMdiAreaActiveSubWindowRecursively()
    new_name = 'test'
    sub_patch_node.rename(new_name, ignore_message_box=True)
    make_all_sub_window_not_modified(window)
    assert sub_patch_node.title == new_name
    assert window.sub_patchs[0].title == new_name
