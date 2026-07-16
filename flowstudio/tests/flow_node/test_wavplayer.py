import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import time
from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from flowstudio.nodes.WAVPLAYER import FLOW_Node_WAVPLAYER


def test_wav_player_open_wav_file_show_file_path(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    wav = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'taipei_emperor.wav')
    wav.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
    make_all_sub_window_not_modified(window)
    assert wav.manager.widgetSet['Path'].textedit.text() == file_path


def test_wav_player_open_not_wav_file_do_not_show_file_path(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    wav = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'undo.png')
    wav.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
    make_all_sub_window_not_modified(window)
    assert wav.manager.widgetSet['Path'].textedit.text() == ''


def test_wav_player_set_gain_to_max(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    wav = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
    wav.manager.widgetSet['Gain'].widget_value = wav.manager.config['Gain'].parameters['pMax']
    make_all_sub_window_not_modified(window)
    assert wav.manager.widgetSet['Gain'].widget_value == wav.manager.config['Gain'].parameters['pMax']


def test_wav_player_no_file_no_sound(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        wav_node = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        wav_ao_first_output_socket = wav_node.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=wav_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)

        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()

        assert meter_node.widget.dBLabels[0].text() == '-120.0'

    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_wav_player_wav_file_having_sound(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        wav_node = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'taipei_emperor.wav')
        wav_node.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMax']
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        wav_ao_first_output_socket = wav_node.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=wav_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)

        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()

        assert meter_node.widget.dBLabels[0].text() != '-inf' and meter_node.widget.dBLabels[0].text() != '-120'

    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_wav_player_wav_file_adjust_gain_from_max_to_min(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        wav_node = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'taipei_emperor.wav')
        wav_node.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMax']
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        wav_ao_first_output_socket = wav_node.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=wav_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)

        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        meter_val_one = float(meter_node.widget.dBLabels[0].text())
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        meter_val_two = float(meter_node.widget.dBLabels[0].text())
        assert meter_val_two < meter_val_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_wav_player_wav_file_adjust_gain_from_min_to_max(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        wav_node = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'taipei_emperor.wav')
        wav_node.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMin']
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        wav_ao_first_output_socket = wav_node.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=wav_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)

        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        meter_val_one = float(meter_node.widget.dBLabels[0].text())
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        meter_val_two = float(meter_node.widget.dBLabels[0].text())
        assert meter_val_two > meter_val_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_wav_player_socket_exceed_input_channel(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        wav_node = main_sub_window.add_ao(OP_NODE_WAVPLAYER)
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources', 'taipei_emperor.wav')
        wav_node.manager.widgetSet['Path'].onFileOpen(file_path=file_path)
        wav_node.manager.widgetSet['Gain'].widget_value = wav_node.manager.config['Gain'].parameters['pMax']
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=wav_node.outputs[-1],
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        maximum_input_channel = \
            int(window.settingDialog.parse_result_of_info_command(window.settingDialog.cpuClient.hQuery('info/'))[
                    "result"][
                    "Maximum Input Channel"])
        total_num_wav_node_output_sockets = len(wav_node.outputs)
        meter_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        if maximum_input_channel >= total_num_wav_node_output_sockets:
            assert meter_node.widget.dBLabels[0].text() != '-inf' and meter_node.widget.dBLabels[0].text() != '-120'
        else:
            assert meter_node.widget.dBLabels[0].text() == '-120.0'

    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)
