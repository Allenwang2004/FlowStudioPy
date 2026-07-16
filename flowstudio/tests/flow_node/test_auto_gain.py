import time
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from flowstudio.tests.common_functions import make_all_sub_window_not_modified
from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *


# def test_quick_gain_connect_and_open_toggle(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     quick_gain_node = main_sub_window.add_ao(OP_NODE_QUICK_GAIN)
#     in_node = main_sub_window.add_ao(OP_NODE_TONEGEN)
#     out_node = main_sub_window.add_ao(OP_NODE_DAC)
#     in_node_output_socket = in_node.outputs[0]
#     quick_gain_node_input_socket = quick_gain_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
#                                            end_socket=quick_gain_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     quick_gain_node_output_socket = quick_gain_node.outputs[0]
#     out_node_input_socket = out_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=quick_gain_node_output_socket,
#                                            end_socket=out_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     window.settingDialog.onSocketConnection(True)
#     quick_gain_node.widget.toggle(True)
#     start_time = time.time()
#     while time.time() - start_time < 1:
#         QApplication.processEvents()
#     quick_gain_meter = float(quick_gain_node.widget.meter.get_current_level())
#     window.settingDialog.onSocketConnection(False)
#     make_all_sub_window_not_modified(window)
#     assert quick_gain_meter != 0, "Auto Gain Meter should not be zero after connection and toggle on."

# def test_quick_gain_connect_and_click_reset(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     quick_gain_node = main_sub_window.add_ao(OP_NODE_QUICK_GAIN)
#     in_node = main_sub_window.add_ao(OP_NODE_TONEGEN)
#     out_node = main_sub_window.add_ao(OP_NODE_DAC)
#     in_node_output_socket = in_node.outputs[0]
#     quick_gain_node_input_socket = quick_gain_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
#                                            end_socket=quick_gain_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     quick_gain_node_output_socket = quick_gain_node.outputs[0]
#     out_node_input_socket = out_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=quick_gain_node_output_socket,
#                                            end_socket=out_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     window.settingDialog.onSocketConnection(True)
#     quick_gain_node.widget.handle_reset_rec()
#     QTest.qWait(1000)
#     db_value = quick_gain_node.widget.db_display.text()
#     window.settingDialog.onSocketConnection(False)
#     make_all_sub_window_not_modified(window)
#     assert db_value == "0 dB"

# def test_quick_gain_connect_and_click_start_rec(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     quick_gain_node = main_sub_window.add_ao(OP_NODE_QUICK_GAIN)
#     in_node = main_sub_window.add_ao(OP_NODE_TONEGEN)
#     out_node = main_sub_window.add_ao(OP_NODE_DAC)
#     in_node_output_socket = in_node.outputs[0]
#     quick_gain_node_input_socket = quick_gain_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
#                                            end_socket=quick_gain_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     quick_gain_node_output_socket = quick_gain_node.outputs[0]
#     out_node_input_socket = out_node.inputs[0]
#     main_sub_window.view.dragging.add_edge(start_socket=quick_gain_node_output_socket,
#                                            end_socket=out_node_input_socket,
#                                            ignore_message_box=True,
#                                            ignore_drag_edge=True)
#     window.settingDialog.onSocketConnection(True)
#     quick_gain_node.widget.gui_manager.widgetSet["recTime"].widget_value = 2
#     quick_gain_node.widget.handle_start_rec()
#     QTest.qWait(2500)
#     db_value = quick_gain_node.widget.db_display.text()
#     window.settingDialog.onSocketConnection(False)
#     make_all_sub_window_not_modified(window)
#     assert db_value > "1 dB" # default 3.7412 dB
