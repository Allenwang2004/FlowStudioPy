from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from statsmodels.tsa.stattools import adfuller
from PyQt5.QtWidgets import QApplication
import time


def test_noise_gen_set_switch_to_off(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMin']]
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['onoff'].widget_value[0] == noise_gen.manager.config['onoff'].parameters['pMin']


def test_noise_gen_set_switch_to_on(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMax']]
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['onoff'].widget_value[0] == noise_gen.manager.config['onoff'].parameters['pMax']


def test_noise_gen_set_type_to_white_noise(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    val = 'White Noise'
    noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                        noise_gen.manager.config['type'].parameters['pList'].index(val)]
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['type'].widget_value[0] == val


def test_noise_gen_set_type_to_pink_noise(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    val = 'Pink Noise'
    noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                        noise_gen.manager.config['type'].parameters['pList'].index(val)]
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['type'].widget_value[0] == val


def test_noise_gen_set_gain_to_max(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMax']
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['gain'].widget_value == noise_gen.manager.config['gain'].parameters['pMax']


def test_noise_gen_set_gain_to_min(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
    noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMin']
    make_all_sub_window_not_modified(window)
    assert noise_gen.manager.widgetSet['gain'].widget_value == noise_gen.manager.config['gain'].parameters['pMin']


def is_white_noise(data, significance_level=0.05):
    """
        Determine if a given dataset exhibits characteristics of white noise.

        Parameters:
            data (list): The dataset to be tested for white noise characteristics.
            significance_level (float, optional): The significance level for the Augmented Dickey-Fuller test.
                                              Default is 0.05.

        Returns:
            bool: True if the dataset is determined to be white noise, False otherwise.

        Notes:
        This function applies the Augmented Dickey-Fuller test to assess whether the given dataset
        could be considered white noise. The p-value obtained from the test is compared to the
        specified significance level. If the p-value is less than or equal to the significance level,
        the dataset is considered white noise.
    """
    # Perform Augmented Dickey-Fuller test
    result = adfuller(data)

    # Compare p-value with significance level
    return result[1] <= significance_level


def test_noise_gen_determine_white_noise(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'White Noise'
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        spectrum_node = main_sub_window.add_ao(OP_NODE_SPECTRUM)
        noise_gen_ao_output_socket = noise_gen.outputs[0]
        spectrum_ao_input_socket = spectrum_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_output_socket,
                                               end_socket=spectrum_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        spectrum_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            QApplication.processEvents()
        values = spectrum_node.widget.plot.getData()[1]
        assert is_white_noise(values)
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_noise_gen_white_noise_gain_max_to_min(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'White Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMax']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMax']
        spectrum_node = main_sub_window.add_ao(OP_NODE_SPECTRUM)
        noise_gen_ao_output_socket = noise_gen.outputs[0]
        spectrum_ao_input_socket = spectrum_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_output_socket,
                                               end_socket=spectrum_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        spectrum_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        first_y_value_one = spectrum_node.widget.plot.getData()[1][0]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        first_y_value_two = spectrum_node.widget.plot.getData()[1][0]
        assert first_y_value_two < first_y_value_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_noise_gen_white_noise_gain_min_to_max(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'White Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMax']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMin']
        spectrum_node = main_sub_window.add_ao(OP_NODE_SPECTRUM)
        noise_gen_ao_output_socket = noise_gen.outputs[0]
        spectrum_ao_input_socket = spectrum_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_output_socket,
                                               end_socket=spectrum_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        spectrum_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        first_y_value_one = spectrum_node.widget.plot.getData()[1][0]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        first_y_value_two = spectrum_node.widget.plot.getData()[1][0]
        assert first_y_value_two > first_y_value_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_noise_gen_pink_noise_gain_max_to_min(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'Pink Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMax']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMax']
        spectrum_node = main_sub_window.add_ao(OP_NODE_SPECTRUM)
        noise_gen_ao_output_socket = noise_gen.outputs[0]
        spectrum_ao_input_socket = spectrum_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_output_socket,
                                               end_socket=spectrum_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        spectrum_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        first_y_value_one = spectrum_node.widget.plot.getData()[1][0]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMin']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        first_y_value_two = spectrum_node.widget.plot.getData()[1][0]
        assert first_y_value_two < first_y_value_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_noise_gen_pink_noise_gain_min_to_max(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'Pink Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMax']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMin']
        spectrum_node = main_sub_window.add_ao(OP_NODE_SPECTRUM)
        noise_gen_ao_output_socket = noise_gen.outputs[0]
        spectrum_ao_input_socket = spectrum_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_output_socket,
                                               end_socket=spectrum_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
        window.settingDialog.onSocketConnection(True)
        spectrum_node.widget.toggle(True)
        start_time = time.time()
        while time.time() - start_time < 1:
            QApplication.processEvents()
        first_y_value_one = spectrum_node.widget.plot.getData()[1][0]
        noise_gen.manager.widgetSet['gain'].widget_value = noise_gen.manager.config['gain'].parameters['pMax']
        start_time = time.time()
        while time.time() - start_time < 1.5:
            QApplication.processEvents()
        first_y_value_two = spectrum_node.widget.plot.getData()[1][0]
        assert first_y_value_two > first_y_value_one
    finally:
        make_all_sub_window_not_modified(window)
        window.settingDialog.onSocketConnection(False)


def test_noise_gen_white_noise_off(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'White Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMin']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        noise_gen_ao_first_output_socket = noise_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
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


def test_noise_gen_pink_noise_off(window):
    try:
        window.onFileNew()
        main_sub_window = window.findMain().widget()
        noise_gen = main_sub_window.add_ao(OP_NODE_NOISEGEN)
        val = 'Pink Noise'
        noise_gen.manager.widgetSet['onoff'].widget_value = [noise_gen.manager.config['onoff'].parameters['pMin']]
        noise_gen.manager.widgetSet['type'].widget_value = [val,
                                                            noise_gen.manager.config['type'].parameters['pList'].index(val)]
        meter_node = main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
        noise_gen_ao_first_output_socket = noise_gen.outputs[0]
        meter_ao_input_socket = meter_node.inputs[0]
        main_sub_window.view.dragging.add_edge(start_socket=noise_gen_ao_first_output_socket,
                                               end_socket=meter_ao_input_socket,
                                               ignore_message_box=True,
                                               ignore_drag_edge=True)
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
