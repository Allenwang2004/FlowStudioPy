from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from PyQt5.QtWidgets import QApplication
import time


def test_mute_set_switch_to_off(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    mute_node = main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
    mute_node.manager.widgetSet['mute'].widget_value = [mute_node.manager.config['mute'].parameters['pMin']]
    make_all_sub_window_not_modified(window)
    assert mute_node.manager.widgetSet['mute'].widget_value[0] == mute_node.manager.config['mute'].parameters['pMin']


def test_mute_set_switch_to_on(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    mute_node = main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
    mute_node.manager.widgetSet['mute'].widget_value = [mute_node.manager.config['mute'].parameters['pMax']]
    make_all_sub_window_not_modified(window)
    assert mute_node.manager.widgetSet['mute'].widget_value[0] == mute_node.manager.config['mute'].parameters['pMax']


def test_mute_on_tone_gen_out(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen_node = main_sub_window.add_ao(OP_NODE_TONEGEN)
        mute_node = main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        tone_gen_node_output_socket = tone_gen_node.outputs[0]
        mute_node_input_socket = mute_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_node_output_socket,
                                               end_socket=mute_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        mute_node_output_socket = mute_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=mute_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen_node.manager.widgetSet['gain'].widget_value = tone_gen_node.manager.config['gain'].parameters['pMax']
        mute_node.manager.widgetSet['mute'].widget_value = [mute_node.manager.config['mute'].parameters['pMax']]
        window.settingDialog.onSocketConnection(connect=True, ignore_message_box=True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.6:
            QApplication.processEvents()
        out_val = int(float(out_node.widget.dBLabel.text()))
        assert out_val == -120
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(connect=False, ignore_message_box=True)


def test_mute_off_tone_gen_out(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen_node = main_sub_window.add_ao(OP_NODE_TONEGEN)
        mute_node = main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        tone_gen_node_output_socket = tone_gen_node.outputs[0]
        mute_node_input_socket = mute_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_node_output_socket,
                                               end_socket=mute_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        mute_node_output_socket = mute_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=mute_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen_node.manager.widgetSet['gain'].widget_value = tone_gen_node.manager.config['gain'].parameters['pMax']
        mute_node.manager.widgetSet['mute'].widget_value = [mute_node.manager.config['mute'].parameters['pMin']]
        window.settingDialog.onSocketConnection(connect=True, ignore_message_box=True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.6:
            QApplication.processEvents()
        out_val = int(float(out_node.widget.dBLabel.text()))
        assert out_val != -120
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(connect=False, ignore_message_box=True)
