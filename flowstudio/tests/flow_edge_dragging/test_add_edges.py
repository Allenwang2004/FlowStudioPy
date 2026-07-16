from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.nodes.IN import FLOW_Node_IN
from flowstudio.tests.common_functions import *


def test_add_edge_in_ao_socket_to_itself_return_false(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_ADC)
    in_ao_output_socket = main_sub_window.scene.nodes[0].outputs[0]
    assert not main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                                      end_socket=in_ao_output_socket,
                                                      ignore_message_box=True,
                                                      ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)


def test_add_edge_out_ao_socket_to_itself_return_false(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    out_ao_input_socket = out_ao.inputs[0]
    assert not main_sub_window.view.dragging.add_edge(start_socket=out_ao_input_socket,
                                                      end_socket=out_ao_input_socket,
                                                      ignore_message_box=True,
                                                      ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)


def test_add_edge_in_ao_socket_to_out_ao_socket_return_true(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    assert main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                                  end_socket=out_ao_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)


def test_add_edge_in_ao_socket_to_smart_gain_ao_inctrls_socket_return_false(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    smart_gain_ao = main_sub_window.add_ao(OP_NODE_SMART_GAIN)
    in_ao_output_socket = in_ao.outputs[0]
    smart_gain_ao_inctrls_socket = smart_gain_ao.inctrls[0]
    assert not main_sub_window.view.dragging.add_edge(start_socket=in_ao_output_socket,
                                                      end_socket=smart_gain_ao_inctrls_socket,
                                                      ignore_message_box=True,
                                                      ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)


def test_add_edge_out_ao_socket_to_in_ao_socket_return_false(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    in_ao = main_sub_window.add_ao(OP_NODE_ADC)
    out_ao = main_sub_window.add_ao(OP_NODE_DAC)
    in_ao_output_socket = in_ao.outputs[0]
    out_ao_input_socket = out_ao.inputs[0]
    assert not main_sub_window.view.dragging.add_edge(start_socket=out_ao_input_socket,
                                                      end_socket=in_ao_output_socket,
                                                      ignore_message_box=True,
                                                      ignore_drag_edge=True)
    make_all_sub_window_not_modified(window)
