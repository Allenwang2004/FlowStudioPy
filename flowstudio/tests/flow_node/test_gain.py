from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
import time
from PyQt5.QtWidgets import QApplication


def test_add_two_channels_gain_ao_test_num_sockets(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 2})
    make_all_sub_window_not_modified(window)
    assert len(gain_ao.inputs) == 2
    assert len(gain_ao.outputs) == 2


def test_add_two_channels_gain_ao_test_reduce_channel(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 2})
    gain_ao.reduceChannel()
    make_all_sub_window_not_modified(window)
    assert len(gain_ao.inputs) == 1
    assert len(gain_ao.outputs) == 1


def test_add_one_channel_gain_ao_test_add_channel(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    gain_ao.addChannel()
    make_all_sub_window_not_modified(window)
    assert len(gain_ao.inputs) == 2
    assert len(gain_ao.outputs) == 2


def test_gain_set_to_max(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    gain_ao.manager.widgetSet['gain'].widget_value = gain_ao.manager.config['gain'].parameters['pMax']
    make_all_sub_window_not_modified(window)
    assert gain_ao.manager.widgetSet['gain'].widget_value == gain_ao.manager.config['gain'].parameters['pMax']


def test_gain_set_to_min(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    gain_ao.manager.widgetSet['gain'].widget_value = gain_ao.manager.config['gain'].parameters['pMin']
    make_all_sub_window_not_modified(window)
    assert gain_ao.manager.widgetSet['gain'].widget_value == gain_ao.manager.config['gain'].parameters['pMin']


def test_gain_click_increase_btn(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    gain_ao.manager.widgetSet['gain'].widget_value = gain_ao.manager.config['gain'].parameters['pMin']
    value_before = gain_ao.manager.widgetSet['gain'].widget_value
    gain_ao.manager.widgetSet['gain'].add_button.click()
    value_after = gain_ao.manager.widgetSet['gain'].widget_value
    make_all_sub_window_not_modified(window)
    assert value_after > value_before


def test_gain_click_decrease_btn(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    gain_ao = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    gain_ao.manager.widgetSet['gain'].widget_value = gain_ao.manager.config['gain'].parameters['pMax']
    value_before = gain_ao.manager.widgetSet['gain'].widget_value
    gain_ao.manager.widgetSet['gain'].reduce_button.click()
    value_after = gain_ao.manager.widgetSet['gain'].widget_value
    make_all_sub_window_not_modified(window)
    assert value_after < value_before


def test_gain_set_to_max_out_greater_than_in(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        in_node = main_sub_window.add_ao(OP_NODE_ADC)
        gain_node = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        in_node_output_socket = in_node.outputs[0]
        gain_node_input_socket = gain_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                               end_socket=gain_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node_output_socket = gain_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=gain_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMax']
        window.settingDialog.onSocketConnection(True)
        in_node.widget.toggle(True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2:
            QApplication.processEvents()
        in_value = float(in_node.widget.meter.get_current_level())
        out_value = float(out_node.widget.meter.get_current_level())
        assert out_value > in_value
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_gain_set_to_min_out_less_than_in(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        in_node = main_sub_window.add_ao(OP_NODE_ADC)
        gain_node = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        in_node_output_socket = in_node.outputs[0]
        gain_node_input_socket = gain_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                               end_socket=gain_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node_output_socket = gain_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=gain_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMin']
        window.settingDialog.onSocketConnection(True)
        in_node.widget.toggle(True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        in_value = float(in_node.widget.meter.get_current_level())
        out_value = float(out_node.widget.meter.get_current_level())
        assert out_value < in_value
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_gain_max_to_min(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        in_node = main_sub_window.add_ao(OP_NODE_ADC)
        gain_node = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        in_node_output_socket = in_node.outputs[0]
        gain_node_input_socket = gain_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                               end_socket=gain_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node_output_socket = gain_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=gain_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMax']
        window.settingDialog.onSocketConnection(True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        out_value_before = float(out_node.widget.meter.get_current_level())
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        out_value_after = float(out_node.widget.meter.get_current_level())
        assert out_value_after < out_value_before
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_gain_min_to_max(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        in_node = main_sub_window.add_ao(OP_NODE_ADC)
        gain_node = main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
        out_node = main_sub_window.add_ao(OP_NODE_DAC)
        in_node_output_socket = in_node.outputs[0]
        gain_node_input_socket = gain_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                               end_socket=gain_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node_output_socket = gain_node.outputs[0]
        out_node_input_socket = out_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=gain_node_output_socket,
                                               end_socket=out_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMin']
        window.settingDialog.onSocketConnection(True)
        out_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        out_value_before = float(out_node.widget.meter.get_current_level())
        gain_node.manager.widgetSet['gain'].widget_value = gain_node.manager.config['gain'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        out_value_after = float(out_node.widget.meter.get_current_level())
        assert out_value_after > out_value_before
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)
