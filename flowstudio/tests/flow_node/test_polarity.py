from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from PyQt5.QtWidgets import QApplication
import time


def test_add_two_channels_polarity_ao_test_num_sockets(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    polarity_ao = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 2})
    make_all_sub_window_not_modified(window)
    assert len(polarity_ao.inputs) == 2
    assert len(polarity_ao.outputs) == 2


def test_add_two_channels_polarity_ao_test_reduce_channel(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    polarity_ao = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 2})
    polarity_ao.reduceChannel()
    make_all_sub_window_not_modified(window)
    assert len(polarity_ao.inputs) == 1
    assert len(polarity_ao.outputs) == 1


def test_add_one_channel_polarity_ao_test_add_channel(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    polarity_ao = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
    polarity_ao.addChannel()
    make_all_sub_window_not_modified(window)
    assert len(polarity_ao.inputs) == 2
    assert len(polarity_ao.outputs) == 2


def test_polarity_set_switch_to_off(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    polarity_node = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
    polarity_node.manager.widgetSet['polarity'].widget_value = [
        polarity_node.manager.config['polarity'].parameters['pMin']]
    make_all_sub_window_not_modified(window)
    assert polarity_node.manager.widgetSet['polarity'].widget_value[0] == \
           polarity_node.manager.config['polarity'].parameters['pMin']


def test_polarity_set_switch_to_on(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    polarity_node = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
    polarity_node.manager.widgetSet['polarity'].widget_value = [
        polarity_node.manager.config['polarity'].parameters['pMax']]
    make_all_sub_window_not_modified(window)
    assert polarity_node.manager.widgetSet['polarity'].widget_value[0] == \
           polarity_node.manager.config['polarity'].parameters['pMax']


def test_signal_polarity_and_non_polarity_processing_with_addition(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        tone_gen.manager.widgetSet['onoff'].widget_value = [tone_gen.manager.config['onoff'].parameters['pMax']]
        tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMax']
        polarity_on_node = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
        polarity_on_node.manager.widgetSet['polarity'].widget_value = [
            polarity_on_node.manager.config['polarity'].parameters['pMax']]
        polarity_off_node = main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
        polarity_off_node.manager.widgetSet['polarity'].widget_value = [
            polarity_off_node.manager.config['polarity'].parameters['pMin']]
        adder = main_sub_window.add_ao(OP_NODE_ADDER)
        visualizer = main_sub_window.add_ao(OP_NODE_VISUALIZER)
        tone_gen_output_socket = tone_gen.outputs[0]
        polarity_on_node_input_socket = polarity_on_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_output_socket,
                                               end_socket=polarity_on_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        polarity_off_node_input_socket = polarity_off_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_output_socket,
                                               end_socket=polarity_off_node_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        polarity_on_node_output_socket = polarity_on_node.outputs[0]
        adder_first_input_socket = adder.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=polarity_on_node_output_socket,
                                               end_socket=adder_first_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        polarity_off_node_output_socket = polarity_off_node.outputs[0]
        adder_second_input_socket = adder.inputs[1]
        main_sub_window.view.dragging.add_edge(start_socket=polarity_off_node_output_socket,
                                               end_socket=adder_second_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        adder_output_socket = adder.outputs[0]
        visualizer_input_socket = visualizer.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=adder_output_socket,
                                               end_socket=visualizer_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        visualizer.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        for data in visualizer.widget.plot.getData()[1]:
            assert data == 0
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)
