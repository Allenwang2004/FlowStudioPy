from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from PyQt5.QtWidgets import QApplication
import time
import numpy as np


def test_tone_gen_set_switch_to_off(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['onoff'].widget_value = [tone_gen.manager.config['onoff'].parameters['pMin']]
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['onoff'].widget_value[0] == tone_gen.manager.config['onoff'].parameters['pMin']


def test_tone_gen_set_switch_to_on(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['onoff'].widget_value = [tone_gen.manager.config['onoff'].parameters['pMax']]
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['onoff'].widget_value[0] == tone_gen.manager.config['onoff'].parameters['pMax']


def test_tone_gen_set_freq_to_max(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['freq'].widget_value = tone_gen.manager.config['freq'].parameters['pMax']
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['freq'].widget_value == tone_gen.manager.config['freq'].parameters['pMax']


def test_tone_gen_set_freq_to_min(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['freq'].widget_value = tone_gen.manager.config['freq'].parameters['pMin']
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['freq'].widget_value == tone_gen.manager.config['freq'].parameters['pMin']


def test_tone_gen_set_gain_to_max(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMax']
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['gain'].widget_value == tone_gen.manager.config['gain'].parameters['pMax']


def test_tone_gen_set_gain_to_min(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
    tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMin']
    make_all_sub_window_not_modified(window)
    assert tone_gen.manager.widgetSet['gain'].widget_value == tone_gen.manager.config['gain'].parameters['pMin']


def test_tone_gen_meter_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        meter_val = float(meter_node.widget.dBLabels[0].text())
        tone_gen_gain_val = float(tone_gen.manager.widgetSet['gain'].widget_value)
        assert tone_gen_gain_val - 0.3 <= meter_val <= tone_gen_gain_val + 0.3
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_off_meter_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen.manager.widgetSet['onoff'].widget_value = [tone_gen.manager.config['onoff'].parameters['pMin']]
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        meter_val = float(meter_node.widget.dBLabels[0].text())
        assert meter_val == -120.0
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_adjust_gain_from_min_to_max_meter_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMin']
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        meter_val_one = float(meter_node.widget.dBLabels[0].text())
        tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        meter_val_two = float(meter_node.widget.dBLabels[0].text())
        assert meter_val_two > meter_val_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_adjust_gain_from_max_to_min_meter_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMax']
        window.settingDialog.onSocketConnection(True)
        meter_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        meter_val_one = float(meter_node.widget.dBLabels[0].text())
        tone_gen.manager.widgetSet['gain'].widget_value = tone_gen.manager.config['gain'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        meter_val_two = float(meter_node.widget.dBLabels[0].text())
        assert meter_val_two < meter_val_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node):
    """
        Validates whether the given tone generator frequency value falls within the x-axis range
        of the bar with the highest y-value in the given RTA node.

        Args:
            tone_gen_freq_val (float): The frequency value of the tone gen audio object.
            rta_node (FLOW_Node_RTA): The RTA node.

        Returns:
            bool: True if the given tone generator frequency value falls within the x-axis range of the
                  highest y-value bar in the given RTA node, False otherwise.
    """
    frequency_ticks = []
    for index, val in rta_node.widget.plotWidget.frequency_ticks[0]:
        if 'k' in val:
            val = float(val.split('k')[0]) * 1000
        frequency_ticks.append(float(val))
    interval_index = 0
    for i in range(len(frequency_ticks)):
        if i == 0:
            if tone_gen_freq_val < frequency_ticks[i]:
                interval_index = i
                break
        elif i == len(frequency_ticks) - 1:
            if tone_gen_freq_val >= frequency_ticks[i]:
                interval_index = i
                break
        if frequency_ticks[i] <= tone_gen_freq_val < frequency_ticks[i + 1]:
            interval_index = i
            break
    highest_val_index = np.where(rta_node.widget.bar.getData()[1] == max(rta_node.widget.bar.getData()[1]))[0][0]
    return interval_index == highest_val_index


def test_tone_gen_rta_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        rta_node = main_sub_window.add_ao(OP_NODE_RTA)
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        rta_ao_input_socket = rta_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=rta_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        rta_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        tone_gen_freq_val = float(tone_gen.manager.widgetSet['freq'].widget_value)
        assert validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node)
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_off_rta_val(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        rta_node = main_sub_window.add_ao(OP_NODE_RTA)
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        rta_ao_input_socket = rta_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=rta_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        tone_gen.manager.widgetSet['onoff'].widget_value = [tone_gen.manager.config['onoff'].parameters['pMin']]
        window.settingDialog.onSocketConnection(True)
        rta_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        for val in rta_node.widget.bar.getData()[1]:
            assert val < 0.2
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_rta_val_change_freq_to_max(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        rta_node = main_sub_window.add_ao(OP_NODE_RTA)
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        rta_ao_input_socket = rta_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=rta_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        rta_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        tone_gen_freq_val = float(tone_gen.manager.widgetSet['freq'].widget_value)
        assert validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node)
        tone_gen.manager.widgetSet['freq'].widget_value = tone_gen.manager.config['freq'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        tone_gen_freq_val = float(tone_gen.manager.widgetSet['freq'].widget_value)
        assert validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node)
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_tone_gen_rta_val_change_freq_to_min(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        tone_gen = main_sub_window.add_ao(OP_NODE_TONEGEN)
        rta_node = main_sub_window.add_ao(OP_NODE_RTA)
        tone_gen_ao_output_socket = tone_gen.outputs[0]
        rta_ao_input_socket = rta_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=tone_gen_ao_output_socket,
                                               end_socket=rta_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        rta_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        tone_gen_freq_val = float(tone_gen.manager.widgetSet['freq'].widget_value)
        assert validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node)
        tone_gen.manager.widgetSet['freq'].widget_value = tone_gen.manager.config['freq'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        tone_gen_freq_val = float(tone_gen.manager.widgetSet['freq'].widget_value)
        assert validate_freq_in_max_bar_range(tone_gen_freq_val, rta_node)
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)
