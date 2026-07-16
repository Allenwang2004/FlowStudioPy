import math
import os
import time

from PyQt5 import QtCore, QtWidgets
from control.flow_widget_meter import QMeter
from control.flow_widget_slider import QDoubleSlider
from control.flow_widget_button import QTactileButton, QToggleSwitch
from control.flow_widget_spinbox import IntNumberBox, DoubleNumberBox, PreviewSpinBox, PreviewDoubleSpinBox
from control.flow_widget_combo_box import PreviewComboBox
from control.flow_widget_knob import *
from flowstudio.flow_window_connection import FLOW_Window_Connection
from nodeeditor.utils import dumpException
from template.button_edit_name import Ui_button_name_edit_dialog
from utilities.utils import extract_coefficients_from_excel, getFileDialogDirectory, getFileDialogFilter, getWavFilter, getCoefficientFilter
from flowstudio.flow_conf import *


class widgetCompomentBase(object):

    def __init__(self, info = None):
        self.info = info
        self.initGraphicAssets()
        self.initFontAssets()

    def initFontAssets(self):
        self.grFont = QFont("Arial", 8)
        # self.grFont.setFamily()

    def initGraphicAssets(self):
        self.row_width = [50, 90, 50, 140]
        self.row_spacing = 5
        self.row_height = 30
        self.width_between_label_and_widget = 20

    def trigger_preview_click_logic(self):
        tuning_param_name = None
        for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
            if widget == self and hasattr(widget, 'frame'):
                widget.frame.setFrameShape(QFrame.Box)
                widget.frame.setStyleSheet("""
                                                QFrame {
                                                    border: 1.5px solid #f39c12;
                                                }
                                                QFrame > * {
                                                    border: none;
                                                }
                                            """)
                tuning_param_name = param_name
            else:
                if hasattr(widget, 'frame'):
                    widget.frame.setFrameShape(QFrame.NoFrame)
                    widget.frame.setStyleSheet("")
        if self.parent_widget.node.is_temp_node:
            current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
            for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                       current_selected_custom_ao_index]['tuning_parameters']):
                if tuning_param['name'] == tuning_param_name:
                    self.parent_widget.node.flow_window.custom_ao_builder_ui.tuning_parameters_table.selectRow(
                        row_num)
                    break

class LabelAndSwitch(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget, parameter: dict, is_preview=False):
        super(LabelAndSwitch, self).__init__(widget, info=parameter)
        self.parent_widget = widget
        self.main_layout = QHBoxLayout(self)
        if is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()

        self.label.setFont(self.grFont)
        self.label.setText(parameter['label_text'])
        if parameter is not None and 'pRowWidth' in parameter:
            self.row_width = parameter['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        if is_preview:
            self.frame.setFixedWidth(self.row_width[0] + self.row_width[1])

        self.toggle = QToggleSwitch()
        self.toggle.setFont(self.grFont)
        self.toggle.setCheckable(True)
        if is_preview:
            # self.toggle.blockSignals(True)
            self.toggle.toggled.connect(self.handle_switch_val_change_in_preview)
        if parameter is None:
            self.toggle.setChecked(True)
        else:
            if parameter['pValue'] == 'on':
                self.toggle.setChecked(True)
            elif parameter['pValue'] == 'off':
                self.toggle.setChecked(False)
            else:
                raise Exception('The value of pValue parameter should be "on" or "off".')
            if parameter['pMax'] == parameter['pMin']:
                raise Exception('The value of pMax parameter and the value of pMin parameter should be different.')
            if parameter['pMax'] != 'on' and parameter['pMax'] != 'off':
                raise Exception('The value of pMax parameter should be "on" or "off".')
            if parameter['pMin'] != 'on' and parameter['pMin'] != 'off':
                raise Exception('The value of pMin parameter should be "on" or "off".')
            self.p_max = parameter['pMax']

        if is_preview:
            self.frame_layout.addWidget(self.label)
            self.frame_layout.addWidget(self.toggle)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.toggle)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.valueStored = self.toggle.clicked
        self.valueChanged = self.toggle.toggled

        if is_preview:
            self.frame.installEventFilter(self)

    @property
    def widget_value(self) -> list:
        if self.toggle.isChecked():
            return ["on", 1 if self.p_max == 'on' else 0]
        else:
            return ["off", 0 if self.p_max == 'on' else 1]

    @widget_value.setter
    def widget_value(self, data):
        if data[0] == "on":
            self.toggle.setChecked(True)
        else:
            self.toggle.setChecked(False)

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def eventFilter(self, obj, event):
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        return super().eventFilter(obj, event)

    def handle_switch_val_change_in_preview(self):
        if hasattr(self.parent_widget.node, 'flow_window'):
            self.parent_widget.node.flow_window.trigger_from_preview = True
        self.trigger_preview_click_logic()
        if self.parent_widget.node.is_temp_node:
            tuning_param_name = None
            for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                if widget == self and hasattr(widget, 'frame'):
                    tuning_param_name = param_name
            current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
            tuning_param_index = None
            for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                       current_selected_custom_ao_index]['tuning_parameters']):
                found = False
                if tuning_param['name'] == tuning_param_name:
                    tuning_param_index = row_num
                    params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                        current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                    for param in params:
                        if param['key'] == 'pValue':
                            param['value'] = 'on' if self.toggle.isChecked() else 'off'
                            break
                if found:
                    break
            if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                    params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                    for row in range(params_table.rowCount()):
                        key_name = params_table.cellWidget(row, 0).text()
                        if key_name == 'pValue':
                            params_table.cellWidget(row, 1).setCurrentText('on' if self.toggle.isChecked() else 'off')
                            break
        if hasattr(self.parent_widget.node, 'flow_window'):
            self.parent_widget.node.flow_window.trigger_from_preview = False




class LabelAndLineEditAndBtn(QWidget, widgetCompomentBase):

    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, label_text, filter_str, accept_file_extensions, parameter: dict):
        super(LabelAndLineEditAndBtn, self).__init__(widget, info=parameter)
        self.filter_str = filter_str
        self.accept_file_extensions = accept_file_extensions
        self.private_data = (None, None, None)
        if 'pRowWidth' in parameter:
            self.row_width = parameter['pRowWidth']
        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText(label_text)

        self.textedit = QLineEdit()
        self.textedit.setFixedWidth(self.row_width[1])
        self.textedit.setFont(self.grFont)

        self.open = QTactileButton()
        self.open.setFixedWidth(self.row_width[2])
        self.open.setFont(self.grFont)
        self.open.setText("open")
        self.open.clicked.connect(self.onFileOpen)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.textedit)
        layout.addWidget(self.open)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.previous_textedit_value=self.textedit.text()
        self.open.clicked.connect(self.openClickHandle)

    def openClickHandle(self):
        if self.previous_textedit_value != self.textedit.text():
            self.valueStored.emit()
            self.valueChanged.emit()
        self.previous_textedit_value = self.textedit.text()

    @property
    def widget_value(self):
        ao_no = self.parentWidget().node.op_code
        if ao_no in [OP_NODE_FIR, OP_NODE_FIR_FP, OP_NODE_IIRCOEF, OP_NODE_IIRCOEF_FP]:
            return self.private_data
        return self.textedit.text()

    @widget_value.setter
    def widget_value(self, data: str):
        ao_no = self.parentWidget().node.op_code
        if ao_no in [OP_NODE_FIR, OP_NODE_FIR_FP, OP_NODE_IIRCOEF, OP_NODE_IIRCOEF_FP]:
            if data[0] == None:
                pass
            elif data[0]:
                self.private_data = data
                self.textedit.setText(data[2])
            else:
                self.private_data = (None, None, None)
                self.textedit.setText('Failed, 0 pole')
        else:
            self.textedit.setText(data)

    def onFileOpen(self, file_path=None):
        """
            Handles the file open action for the widget.

            Args:
                file_path (str, optional): The path of the file to be opened. If None, a file dialog will be shown
                    to allow the user to choose a file. Defaults to None.
        """
        if not file_path:
            file_path = None
        from flowstudio.flow_window import FLOW_Window
        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.hide()
        if hasattr(self.parentWidget(), 'node'):
            ao_no = self.parentWidget().node.op_code
            if ao_no == OP_NODE_UPHEAR_VIRT:
                try:
                    folder_path = QFileDialog.getExistingDirectory(self.parentWidget().node.scene.getView().window(),
                                                                   'Choose a directory',
                                                                   self.parentWidget().node.scene.getView().window().getFileDialogDirectory())
                    if folder_path == '':
                        return False
                    files_to_check = ['IsPresetData.sbbs', 'NoPresetData.sbbs', 'UserSpecificData.sbbs']
                    if self.check_files_exist(folder_path, files_to_check):
                        self.textedit.setText(folder_path)
                        self.valueStored.emit()
                    else:
                        statement = "The folder is missing one or more of the following files. Please select again.\n" \
                                    "● IsPresetData.sbbs\n" \
                                    "● NoPresetData.sbbs\n" \
                                    "● UserSpecificData.sbbs"
                        QMessageBox.about(self.parentWidget().node.scene.getView().window(), "Error Tip", "%s" % statement)
                        self.onFileOpen()
                except Exception as e:
                    dumpException(e)
            elif ao_no in [OP_NODE_FIR, OP_NODE_FIR_FP, OP_NODE_IIRCOEF, OP_NODE_IIRCOEF_FP]:
                disable_denominator = True if ao_no == OP_NODE_FIR or ao_no == OP_NODE_FIR_FP else False
                if file_path is not None:
                    selected_file_path = file_path
                else:
                    selected_file_path, selected_filter_str = QFileDialog.getOpenFileName(None,
                                                                                          "Load Coefficient from file",
                                                                                          getFileDialogDirectory(),
                                                                                          self.filter_str)
                    try:
                        if selected_file_path != '' and os.path.isfile(selected_file_path):
                            if os.path.splitext(selected_file_path)[1].split('.')[1] in self.accept_file_extensions:
                                pre_res = extract_coefficients_from_excel(selected_file_path, disable_denominator)
                                res = pre_res + (selected_file_path,)
                            else:
                                res = (False, None, None)
                            if not res[0]:
                                if len(res) > 2 and res[2]:
                                    QMessageBox.about(self.parentWidget().node.scene.getView().window(),
                                                      'Format Error',
                                                      res[2])
                                else:
                                    QMessageBox.about(self.parentWidget().node.scene.getView().window(),
                                                      'Format Error',
                                                      'This file does not comply with the required format.')
                            else:
                                self.widget_value = res
                                self.valueStored.emit()
                                self.valueChanged.emit()
                    except Exception as e:
                        dumpException(e)
            else:
                if file_path is not None:
                    selected_file_path = file_path
                else:
                    selected_file_path, selected_filter_str = QFileDialog.getOpenFileName(None, "Open file from folder",
                                                                                          getFileDialogDirectory(),
                                                                                          self.filter_str)
                try:
                    if selected_file_path != '' and os.path.isfile(selected_file_path):
                        if (len(self.accept_file_extensions) > 0 and self.accept_file_extensions[0] == '*') or \
                                (os.path.splitext(selected_file_path)[1].split('.')[1] in self.accept_file_extensions):
                            self.widget_value = selected_file_path
                            self.valueStored.emit()
                except Exception as e:
                    dumpException(e)

        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.show()

    def check_files_exist(self, path, files):
        """
            Check if specified files exist in the given path.

            Args:
                path (str): The path to check for the existence of files.
                files (list): A list of file names to check.

            Returns:
                bool: True if all files exist, False otherwise.
        """
        file_exists = all(os.path.exists(os.path.join(path, file)) for file in files)
        return file_exists


class Label(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, label_text, parameter: dict):
        super(Label, self).__init__(widget, info=parameter)

        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[3])
        self.label.setFont(self.grFont)
        self.label.setText(label_text)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    @property
    def widget_value(self):
        return self.label.text()

    @widget_value.setter
    def widget_value(self, data: str):
        self.label.setText(data)

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)


class LabelSpinBox(QWidget, widgetCompomentBase):
    def __init__(self, widget: QWidget, parameters: dict):
        super(LabelSpinBox, self).__init__(widget, info=parameters)
        if 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])

        self.slider = QDoubleSlider(2, Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameters["pMax"])
        self.slider.setMinimum(parameters["pMin"])
        self.slider.setValue(parameters["pValue"])

        self.numbox = QDoubleSpinBox()
        self.numbox.setFixedWidth(parameters['spin_box_width'])
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)
        self.numbox.setDecimals(parameters['pDecimalPrecision'])
        # Install the eventFilter method into the QDoubleSpinBox widget
        self.numbox.installEventFilter(self)

        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.numbox)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged

    def eventFilter(self, obj, event):
        """
        To add additional functionality to a widget's event handling,
        override the eventFilter() method of its parent QObject.
        This method intercepts events for any widgets that have installed the event filter.

        Parameters:
            obj (QObject): The object that triggered the event.
            event (QEvent): The intercepted event.

        Returns:
            bool: True if the event has been intercepted and handled, False otherwise.
        """
        # Intercept events in QDoubleSpinBox control
        if obj == self.numbox and event.type() == QEvent.KeyPress:
            # if it is a paste operation
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                # Get the pasted text
                clipboard = QApplication.clipboard()
                text = clipboard.text()
                # Filter and validate the text
                try:
                    value = float(text)
                    decimals = self.numbox.decimals()
                    if len(text) > 0 and text[-1] == '.':
                        # If the last character of the text is a period, do not truncate
                        pass
                    elif len(text.split('.')[-1]) > decimals:
                        # If the number of decimal places exceeds the set value, truncate the text
                        text = '.'.join([text.split('.')[0], text.split('.')[-1][:decimals]])
                except ValueError:
                    # If the text cannot be converted to a float, do not perform the paste operation
                    return True
                # Set the filtered text into the QDoubleSpinBox widget
                self.numbox.lineEdit().insert(text)
                # Prevent the event from being propagated
                return True
        return super().eventFilter(obj, event)

    def isValueChanged(self):
        self.signalFlag = True



    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.slider.setValue(self.numbox.value())
        if self.signalFlag:
            self.valueChanged.emit(self.numbox.value())
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self, bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:white;")


class LabelAndValue(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, label_text, value, parameter: dict):
        super().__init__(widget, info=parameter)
        self.label = QLabel(label_text)
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)

        self.value_box = QDoubleSpinBox()
        self.value_box.setReadOnly(True)
        self.value_box.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.value_box.setFrame(False)
        self.value_box.setFont(self.grFont)
        self.value_box.setFixedWidth(60)
        self.value_box.setValue(value)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.value_box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    @property
    def widget_value(self):
        return self.value_box.value()

    @widget_value.setter
    def widget_value(self, value):
        self.value_box.setValue(value)

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def set_value(self, value):
        self.value_box.setValue(value)


class LabelAndButton(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()


    def __init__(self, widget: QWidget, label_text, value_to_send, button_text, parameter: dict):
        super(LabelAndButton, self).__init__(widget, info=parameter)
        self.value_to_send = value_to_send
        self.private_data = [None, None]

        self.label = QLabel()
        self.label.setFixedWidth(parameter["label_width"])
        self.label.setFont(self.grFont)
        self.label.setText(label_text)

        self.button = QTactileButton()
        self.button.setFixedWidth(parameter["button_width"])
        self.button.setFont(self.grFont)
        self.button.setText(button_text)
        self.button.clicked.connect(self.send_cmd)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    def send_cmd(self):
        self.widget_value = self.value_to_send
        self.valueStored.emit()
        self.valueChanged.emit()

    @property
    def widget_value(self):
        return self.value_to_send

    @widget_value.setter
    def widget_value(self, input_data: list):
        self.private_data = input_data


class Label_TextEdit_Float(QWidget, widgetCompomentBase):
    def __init__(self, widget: QWidget, parameter: dict):
        super(Label_TextEdit_Float, self).__init__(widget, info=parameter)
        self.label = QLabel()
        self.label.setFixedWidth(80)
        self.label.setFont(self.grFont)
        self.label.setText("default")

        self.slider = QDoubleSlider(2, Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameter["pMax"])
        self.slider.setMinimum(parameter["pMin"])
        self.slider.setValue(parameter["pValue"])

        self.numbox = QDoubleSpinBox()
        self.numbox.setFixedWidth(50)
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameter["pMax"])
        self.numbox.setMinimum(parameter["pMin"])
        self.numbox.setValue(parameter["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)
        self.numbox.setDecimals(1)


        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.numbox)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged

    def isValueChanged(self):
        self.signalFlag = True



    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.slider.setValue(self.numbox.value())
        if self.signalFlag:
            self.valueChanged.emit(self.numbox.value())
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self, bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:white;")

class SpecialLabelDoubleSpinBox(QWidget, widgetCompomentBase):
    def __init__(self, widget: QWidget, parameters: dict):
        super(SpecialLabelDoubleSpinBox, self).__init__(widget, info=parameters)
        self.label = QLabel()
        self.label.setFixedWidth(50)
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])

        self.slider = QDoubleSlider(2, Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameters["pMax"])
        self.slider.setMinimum(parameters["pMin"])
        self.slider.setValue(parameters["pValue"])

        self.numbox = QDoubleSpinBox()
        self.numbox.setFixedWidth(50)
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)
        self.numbox.setDecimals(1)
        self.numbox.setEnabled(False)

        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False
        if self.numbox.value() == 1:
            self.numbox.setStyleSheet("background-color:green;")
        else:
            self.numbox.setStyleSheet("background-color:red;")

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.numbox)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged


    def isValueChanged(self):
        self.signalFlag = True
        if self.numbox.value() == 1:
            self.numbox.setStyleSheet("background-color:green;")
        else:
            self.numbox.setStyleSheet("background-color:red;")


    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.slider.setValue(self.numbox.value())
        if self.signalFlag:
            self.valueChanged.emit(self.numbox.value())
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self, bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:white;")


class LinearLabelSliderSpinBox(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super(LinearLabelSliderSpinBox, self).__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.step_value = parameters.get('pStep', 1)  # Store step value
        self.last_emitted_value = None  # Track last emitted value to avoid duplicates
        self.main_layout = QHBoxLayout(self)
        if is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        if is_preview:
            self.frame.setFixedWidth(self.row_width[0] + self.row_width[1] + self.row_width[2] + self.row_spacing + 25)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameters["pMax"])
        self.slider.setMinimum(parameters["pMin"])
        self.slider.setValue(parameters["pValue"])
        
        # Set single step and page step if provided
        if 'pStep' in parameters:
            self.slider.setSingleStep(parameters['pStep'])
            self.slider.setPageStep(parameters['pStep'])
            # Enable tick marks for visual feedback
            self.slider.setTickPosition(QSlider.TicksBelow)
            self.slider.setTickInterval(parameters['pStep'])

        self.numbox = PreviewSpinBox(parent=self) if is_preview else QSpinBox()
        self.numbox.setFixedWidth(self.row_width[2])
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        
        # Set single step for spinbox if provided
        if 'pStep' in parameters:
            self.numbox.setSingleStep(parameters['pStep'])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        self.slider.valueChanged.connect(self.handleSliderValueChange)
        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False

        if is_preview:
            self.frame_layout.addWidget(self.label)
            self.frame_layout.addWidget(self.slider)
            self.frame_layout.addWidget(self.numbox)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.slider)
            self.main_layout.addWidget(self.numbox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.valueChanged

        if is_preview:
            self.frame.installEventFilter(self)

    def isValueChanged(self):
        if Debug.DEBUG_COMMON.value:
            print("isValueChanged")
        self.signalFlag = True
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot(int)
    def handleSliderValueChange(self, value):
        # Snap to step if defined
        if self.step_value > 1:
            min_val = self.slider.minimum()
            snapped_value = min_val + round((value - min_val) / self.step_value) * self.step_value
            
            # Always update numbox display
            self.numbox.setValue(snapped_value)
            
            if snapped_value != value:
                # Block all signals and set snapped value
                self.slider.blockSignals(True)
                self.slider.setValue(snapped_value)
                self.slider.blockSignals(False)
                return  # Don't send command yet, will be called again with snapped value
            
            value = snapped_value
        else:
            self.numbox.setValue(value)
        
        # Only proceed with command if value actually changed from last emitted
        if value == self.last_emitted_value:
            return
        
        self.last_emitted_value = value
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            self.trigger_preview_click_logic()
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = value
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(value)
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot()
    def handleNumboxValueChange(self):
        value = self.numbox.value()
        # Snap to step if defined
        if self.step_value > 1:
            min_val = self.slider.minimum()
            snapped_value = min_val + round((value - min_val) / self.step_value) * self.step_value
            if snapped_value != value:
                self.numbox.setValue(snapped_value)
                value = snapped_value
        
        # Update last emitted value
        self.last_emitted_value = value
        self.slider.setValue(value)
        if self.signalFlag and value != self.slider.value():
            self.valueChanged.emit(value)
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.slider.value()

    @widget_value.setter
    def widget_value(self, value: int):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self,bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:black;")

    def eventFilter(self, obj, event):
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        return super().eventFilter(obj, event)

class LogarithmicLabelSliderSpinBox(QWidget, widgetCompomentBase):

    pyqtSignal()
    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super(LogarithmicLabelSliderSpinBox, self).__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.main_layout = QHBoxLayout(self)
        if is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        if is_preview:
            self.frame.setFixedWidth(self.row_width[0] + self.row_width[1] + self.row_width[2] + self.row_spacing + 25)

        self.scale = parameters["pMax"] - parameters["pMin"]

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(int(math.ceil(math.log(parameters["pMax"], 2) * self.scale)))
        self.slider.setMinimum(int(math.floor(math.log(parameters["pMin"], 2) * self.scale)))
        self.slider.setValue(round(math.log(parameters["pValue"], 2) * self.scale))

        self.numbox = PreviewSpinBox(parent=self) if is_preview else QSpinBox()
        self.numbox.setFixedWidth(self.row_width[2])
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        self.slider.valueChanged.connect(self.handleSliderValueChange)
        if not is_preview:
            self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        if is_preview:
            self.numbox.valueChanged.connect(self.handle_spinbox_value_change)

        if is_preview:
            self.frame_layout.addWidget(self.label)
            self.frame_layout.addWidget(self.slider)
            self.frame_layout.addWidget(self.numbox)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.slider)
            self.main_layout.addWidget(self.numbox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.valueChanged
        self.slider.sliderMoved.connect(self.HandleSliderMoved)
        self.previous_numbox_value = self.numbox.value()
        self.sliderMoveSignalFlag = False
        self.numboxValueChangeSIgnalFlag = False

        if is_preview:
            self.frame.installEventFilter(self)

    def HandleSliderMoved(self):
        self.sliderMoveSignalFlag = True

    @pyqtSlot(int)
    def handleSliderValueChange(self, slider_value):
        if self.sliderMoveSignalFlag or self.numboxValueChangeSIgnalFlag:
            self.numbox.setValue(round(2**(slider_value/self.scale)))
        self.sliderMoveSignalFlag = False
        self.numboxValueChangeSIgnalFlag = False
        self.previous_numbox_value = self.numbox.value()
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            self.trigger_preview_click_logic()
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot()
    def handleNumboxValueChange(self):
        if self.previous_numbox_value != self.numbox.value():
            self.numboxValueChangeSIgnalFlag = True
            self.slider.setValue(round(math.log(self.numbox.value(), 2) * self.scale))
            self.valueStored.emit()
        self.previous_numbox_value = self.numbox.value()

    def handle_spinbox_value_change(self):
        if self.previous_numbox_value != self.numbox.value():
            self.numboxValueChangeSIgnalFlag = True
            value_to_set = round(math.log(self.numbox.value(), 2) * self.scale)
            self.slider.setValue(value_to_set)
            self.valueStored.emit()
            self.parent_widget.node.flow_window.trigger_from_preview = True
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False
        self.previous_numbox_value = self.numbox.value()

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: int):
        self.numbox.setValue(value)
        self.slider.setValue(round(math.log(self.numbox.value(), 2) * self.scale))

    def eventFilter(self, obj, event):
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        return super().eventFilter(obj, event)


class LinearLabelDoubleSliderSpinBox(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super(LinearLabelDoubleSliderSpinBox, self).__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.main_layout = QHBoxLayout(self)
        if is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        self.slider = QDoubleSlider(2, Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameters["pMax"])
        self.slider.setMinimum(parameters["pMin"])
        self.slider.setValue(parameters["pValue"])

        self.numbox = PreviewDoubleSpinBox() if is_preview else QDoubleSpinBox()
        if 'pDecimalPrecision' in parameters:
            self.numbox.setDecimals(int(parameters['pDecimalPrecision']))
        p_max_integer_part = abs(int(parameters["pMax"]))
        p_min_integer_part = abs(int(parameters["pMin"]))
        p_max_integer_digit_count = len(str(p_max_integer_part))
        p_min_integer_digit_count = len(str(p_min_integer_part))
        integer_digit_count = max(p_max_integer_digit_count, p_min_integer_digit_count)

        self.row_width[2] = integer_digit_count * 8 + parameters['pDecimalPrecision'] * 8 + 10
        self.numbox.setFixedWidth(self.row_width[2])
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)
        self.numbox.setDecimals(parameters['pDecimalPrecision'])

        self.slider.doubleValueChanged.connect(self.handleSliderValueChange)
        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False

        if is_preview:
            if parameters['is_slider_needed']:
                self.frame.setFixedWidth(self.row_width[0] + self.row_width[1] + self.row_width[2] + self.row_spacing + 25)
            else:
                self.frame.setFixedWidth(self.row_width[0] + self.row_width[2] + self.row_spacing + 25)

        if is_preview:
            self.frame_layout.addWidget(self.label)
            if parameters['is_slider_needed']:
                self.frame_layout.addWidget(self.slider)
            self.frame_layout.addWidget(self.numbox)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            if parameters['is_slider_needed']:
                self.main_layout.addWidget(self.slider)
            self.main_layout.addWidget(self.numbox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged

        if is_preview:
            self.frame.installEventFilter(self)

    def isValueChanged(self):
        self.signalFlag = True
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot(float)
    def handleSliderValueChange(self, value):
        self.numbox.setValue(value)
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            self.trigger_preview_click_logic()
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = value
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(value)
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.slider.setValue(self.numbox.value())
        if self.signalFlag and self.numbox.value() != self.slider.value():
            self.valueChanged.emit(self.numbox.value())
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self,bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:white;")

    def eventFilter(self, obj, event):
        """
        To add additional functionality to a widget's event handling,
        override the eventFilter() method of its parent QObject.
        This method intercepts events for any widgets that have installed the event filter.

        Parameters:
            obj (QObject): The object that triggered the event.
            event (QEvent): The intercepted event.

        Returns:
            bool: True if the event has been intercepted and handled, False otherwise.
        """
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        # Intercept events in QDoubleSpinBox control
        elif obj == self.numbox and event.type() == QEvent.KeyPress:
            # if it is a paste operation
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                # Get the pasted text
                clipboard = QApplication.clipboard()
                text = clipboard.text()
                # Filter and validate the text
                try:
                    value = float(text)
                    decimals = self.numbox.decimals()
                    if len(text) > 0 and text[-1] == '.':
                        # If the last character of the text is a period, do not truncate
                        pass
                    elif len(text.split('.')[-1]) > decimals:
                        # If the number of decimal places exceeds the set value, truncate the text
                        text = '.'.join([text.split('.')[0], text.split('.')[-1][:decimals]])
                except ValueError:
                    # If the text cannot be converted to a float, do not perform the paste operation
                    return True
                # Set the filtered text into the QDoubleSpinBox widget
                self.numbox.lineEdit().insert(text)
                # Prevent the event from being propagated
                return True
        return super().eventFilter(obj, event)


class VerticalLinearLabelDoubleSliderSpinBoxHasButtons(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget, parameters: dict):
        super(VerticalLinearLabelDoubleSliderSpinBoxHasButtons, self).__init__(widget, info=parameters)

        self.timer = None

        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText(parameters["label_text"])

        self.slider = QDoubleSlider(2, Qt.Vertical)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(parameters["pMax"])
        self.slider.setMinimum(parameters["pMin"])
        self.slider.setValue(parameters["pValue"])

        self.numbox = QDoubleSpinBox()
        self.numbox.setFixedWidth(70)
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        self.reduce_button = QPushButton('-')
        self.reduce_button.setFixedWidth(35)
        self.reduce_button.setFont(self.grFont)

        self.add_button = QPushButton('+')
        self.add_button.setFixedWidth(35)
        self.add_button.setFont(self.grFont)

        self.reduce_button.clicked.connect(self.handleReduceButtonValueChange)
        self.reduce_button.pressed.connect(self.handleReduceButtonPressed)
        self.reduce_button.released.connect(self.handleBtnReleased)

        self.add_button.clicked.connect(self.handleAddButtonValueChange)
        self.add_button.pressed.connect(self.handleAddButtonPressed)
        self.add_button.released.connect(self.handleBtnReleased)

        self.slider.doubleValueChanged.connect(self.handleSliderValueChange)
        self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        self.numbox.valueChanged.connect(self.isValueChanged)
        self.signalFlag = False

        layout = QVBoxLayout(self)
        layout.addStretch()

        layout1 = QHBoxLayout(self)
        layout1.addWidget(self.label)
        layout.addLayout(layout1)

        layout2 = QHBoxLayout(self)
        layout2.addWidget(self.slider)
        layout.addLayout(layout2)

        layout4 = QHBoxLayout(self)
        layout4.addWidget(self.reduce_button)
        layout4.addWidget(self.add_button)
        layout.addLayout(layout4)

        layout3 = QHBoxLayout(self)
        layout3.addWidget(self.numbox)
        layout.addLayout(layout3)

        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged

    def isValueChanged(self):
        self.signalFlag = True

    @pyqtSlot(float)
    def handleSliderValueChange(self, value):
        self.numbox.setValue(value)

    @pyqtSlot()
    def handleAddButtonValueChange(self):
        self.slider.setValue(self.numbox.value() + 0.5)

    @pyqtSlot()
    def handleAddButtonPressed(self):
        if self.timer is not None:
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.handleAddButtonValueChange)
        self.timer.start(50)

    @pyqtSlot()
    def handleReduceButtonValueChange(self):
        self.slider.setValue(self.numbox.value() - 0.5)

    @pyqtSlot()
    def handleReduceButtonPressed(self):
        if self.timer is not None:
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.handleReduceButtonValueChange)
        self.timer.start(50)

    @pyqtSlot()
    def handleBtnReleased(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer = None

    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.slider.setValue(self.numbox.value())
        if self.signalFlag:
            self.valueChanged.emit(self.numbox.value())
            self.signalFlag = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(value)

    def disableWidget(self,bool=False):
        self.label.setDisabled(bool)
        self.slider.setDisabled(bool)
        self.numbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.slider.setStyleSheet("color:grey;")
            self.numbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.slider.setStyleSheet("color:white;")
            self.numbox.setStyleSheet("color:white;")

class LogarithmicLabelDoubleSliderSpinBox(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super(LogarithmicLabelDoubleSliderSpinBox, self).__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.main_layout = QHBoxLayout(self)
        if is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        if is_preview:
            self.frame.setFixedWidth(self.row_width[0] + self.row_width[1] + self.row_width[2] + self.row_spacing + 25)

        self.scale = parameters["pMax"] - parameters["pMin"]

        self.slider = QDoubleSlider(2, Qt.Horizontal)
        self.slider.setFixedWidth(self.row_width[1])
        self.slider.setMaximum(int(math.ceil(math.log(parameters["pMax"], 2) * self.scale)))
        self.slider.setMinimum(int(math.floor(math.log(parameters["pMin"], 2) * self.scale)))
        self.slider.setValue(round(math.log(parameters["pValue"], 2) * self.scale))

        self.numbox = PreviewDoubleSpinBox() if is_preview else QDoubleSpinBox()
        self.numbox.setFixedWidth(self.row_width[2])
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameters["pMax"])
        self.numbox.setMinimum(parameters["pMin"])
        self.numbox.setValue(parameters["pValue"])
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        self.slider.doubleValueChanged.connect(self.handleSliderValueChange)
        if not is_preview:
            self.numbox.editingFinished.connect(self.handleNumboxValueChange)
        if is_preview:
            self.numbox.valueChanged.connect(self.handle_spinbox_value_change)

        if is_preview:
            self.frame_layout.addWidget(self.label)
            self.frame_layout.addWidget(self.slider)
            self.frame_layout.addWidget(self.numbox)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.slider)
            self.main_layout.addWidget(self.numbox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.valueStored = self.slider.sliderReleased
        self.valueChanged = self.slider.doubleValueChanged

        if is_preview:
            self.frame.installEventFilter(self)

    @pyqtSlot(float)
    def handleSliderValueChange(self, slider_value):
        if hasattr(self, 'trigger_from_num_box_value_change') and self.trigger_from_num_box_value_change:
            return
        if self.is_preview:
            if hasattr(self.parent_widget.node.flow_window, 'trigger_from_preview') and self.parent_widget.node.flow_window.trigger_from_preview:
                return
        self.numbox.setValue(2**(slider_value/self.scale))
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            self.trigger_preview_click_logic()
            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.trigger_from_num_box_value_change = True
        self.slider.setValue(round(math.log(self.numbox.value(), 2) * self.scale))
        self.valueStored.emit()
        self.trigger_from_num_box_value_change = False

    def handle_spinbox_value_change(self):
        if self.is_preview:
            self.parent_widget.node.flow_window.trigger_from_preview = True
            self.slider.setValue(round(math.log(self.numbox.value(), 2) * self.scale))
            self.valueStored.emit()

            if self.parent_widget.node.is_temp_node:
                tuning_param_name = None
                for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                    if widget == self and hasattr(widget, 'frame'):
                        tuning_param_name = param_name
                current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                tuning_param_index = None
                for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                           current_selected_custom_ao_index]['tuning_parameters']):
                    found = False
                    if tuning_param['name'] == tuning_param_name:
                        tuning_param_index = row_num
                        params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                            current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                        for param in params:
                            if param['key'] == 'pValue':
                                param['value'] = self.numbox.value()
                                break
                    if found:
                        break
                if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                    if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                        params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                        for row in range(params_table.rowCount()):
                            key_name = params_table.cellWidget(row, 0).text()
                            if key_name == 'pValue':
                                params_table.cellWidget(row, 1).setValue(self.numbox.value())
                                break
            self.parent_widget.node.flow_window.trigger_from_preview = False

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.slider.setValue(round(math.log(self.numbox.value(), 2) * self.scale))

    def eventFilter(self, obj, event):
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        return super().eventFilter(obj, event)


class LabelAndComboBox(QWidget, widgetCompomentBase):
    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super(LabelAndComboBox, self).__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.main_layout = QHBoxLayout(self)
        if self.is_preview:
            self.frame = QFrame(self)
            # Create layout for frame
            self.frame_layout = QHBoxLayout(self.frame)
            # Add frame to main layout
            self.main_layout.addWidget(self.frame)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        if self.is_preview:
            self.frame.setFixedWidth(self.row_width[0] + self.row_width[1] + self.row_width[2] + self.row_spacing)

        self.comboBox = PreviewComboBox() if is_preview else QComboBox()
        self.comboBox.setFixedWidth(self.row_width[1]+self.row_width[2]+self.row_spacing)
        self.comboBox.setFont(self.grFont)
        self.comboBox.addItems(parameters["pList"])
        self.comboBox.setCurrentIndex(parameters["pValue"])

        if self.is_preview:
            self.frame_layout.addWidget(self.label)
            self.frame_layout.addWidget(self.comboBox)
            self.frame_layout.addStretch()
        else:
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.comboBox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.viewPressedSignalFlag = False
        self.comboBox.view().pressed.connect(self.menuViewPressedHandle)
        self.comboBox.currentIndexChanged.connect(self.menuChangeHandle)
        self.comboBox.activated.connect(self.menuActivatedHandle)

        if self.is_preview:
            self.frame.installEventFilter(self)


    def menuActivatedHandle(self):
        self.viewPressedSignalFlag = False

    def menuViewPressedHandle(self):
        self.viewPressedSignalFlag = True
        if self.is_preview:
            self.trigger_preview_click_logic()

    def menuChangeHandle(self):
        if self.viewPressedSignalFlag:
            self.valueStored.emit()
        self.valueChanged.emit()
        self.viewPressedSignalFlag = False
        if self.is_preview:
            if getattr(self, "is_updating", False):
                return
            self.is_updating = True
            try:
                self.parent_widget.node.flow_window.trigger_from_preview = True
                if self.parent_widget.node.is_temp_node:
                    tuning_param_name = None
                    for param_name, widget in self.parent_widget.node.manager.widgetSet.items():
                        if widget == self and hasattr(widget, 'frame'):
                            tuning_param_name = param_name
                    current_selected_custom_ao_index = self.parent_widget.node.flow_window.get_current_selected_custom_ao_index()
                    tuning_param_index = None
                    for row_num, tuning_param in enumerate(self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                                               current_selected_custom_ao_index]['tuning_parameters']):
                        found = False
                        if tuning_param['name'] == tuning_param_name:
                            tuning_param_index = row_num
                            params = self.parent_widget.node.flow_window.temp_custom_aos_in_builder[
                                current_selected_custom_ao_index]['tuning_parameters'][row_num]['parameters']
                            for param in params:
                                if param['key'] == 'pValue':
                                    param['value'] = self.comboBox.currentIndex()
                                    break
                        if found:
                            break
                    if tuning_param_index == self.parent_widget.node.flow_window.get_current_selected_tuning_param_index():
                        if hasattr(self.parent_widget.node.flow_window.custom_ao_builder_ui, 'params_widget'):
                            params_table = self.parent_widget.node.flow_window.custom_ao_builder_ui.params_widget.table
                            for row in range(params_table.rowCount()):
                                key_name = params_table.cellWidget(row, 0).text()
                                if key_name == 'pValue':
                                    params_table.cellWidget(row, 1).setCurrentIndex(self.comboBox.currentIndex())
                                    break
                self.parent_widget.node.flow_window.trigger_from_preview = False
            finally:
                self.is_updating = False

    @property
    def widget_value(self) -> list:
        return [self.comboBox.itemText(self.comboBox.currentIndex()), self.comboBox.currentIndex()]

    @widget_value.setter
    def widget_value(self, value: list):
        self.comboBox.setCurrentIndex(value[1])

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def set_combo_box_items(self, items):
        self.comboBox.clear()
        self.comboBox.addItems(items)

    def set_combo_box_current_index(self, new_index):
        self.comboBox.setCurrentIndex(new_index)

    def eventFilter(self, obj, event):
        if obj == self.frame:
            if event.type() == QEvent.MouseButtonPress:
                self.trigger_preview_click_logic()
                return True
        return super().eventFilter(obj, event)


class LabelAndDisableComboBox(QWidget, widgetCompomentBase):
    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, parameters: dict, is_preview=False):
        super().__init__(widget, info=parameters)
        self.parent_widget = widget
        self.is_preview = is_preview
        self.main_layout = QHBoxLayout(self)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        self.comboBox = QComboBox()
        self.comboBox.setFixedWidth(self.row_width[1]+self.row_width[2]+self.row_spacing)
        self.comboBox.setFont(self.grFont)
        self.comboBox.addItems(parameters["pList"])
        self.comboBox.setCurrentIndex(parameters["pValue"])

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.comboBox)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.row_spacing)

        self.comboBox.currentIndexChanged.connect(self.menuChangeHandle)
        self.comboBox.activated.connect(self.menuActivatedHandle)

    def set_disabled(self, disabled: bool):
        self.comboBox.setDisabled(disabled)

    def menuActivatedHandle(self):
        self.valueStored.emit()

    def menuChangeHandle(self):
        self.valueChanged.emit()

    @property
    def widget_value(self) -> list:
        return [self.comboBox.itemText(self.comboBox.currentIndex()), self.comboBox.currentIndex()]

    @widget_value.setter
    def widget_value(self, value: list):
        self.comboBox.setCurrentIndex(value[1])

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def set_combo_box_items(self, items):
        self.comboBox.clear()
        self.comboBox.addItems(items)

    def set_combo_box_current_index(self, new_index):
        self.comboBox.setCurrentIndex(new_index)

class LabelAndComboBoxForMux(QWidget, widgetCompomentBase):
    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, parameters: dict):
        super(LabelAndComboBoxForMux, self).__init__(widget, info=parameters)

        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])

        self.comboBox = QComboBox()
        self.comboBox.setFixedWidth(self.row_width[1]+self.row_width[2]+self.row_spacing)
        self.comboBox.setFont(self.grFont)
        self.comboBox.addItems(parameters["pList"])
        self.comboBox.setCurrentIndex(parameters["pValue"])

        self.rename = QPushButton()
        self.rename.setIcon(QIcon("../resources/edit-white.png"))

        button_width = 140
        button_labels = ['default_0', 'default_1', 'default_2', 'default_3']
        self.default_buttons = []
        for label in button_labels:
            button = QPushButton(label)
            button.setFixedWidth(button_width)
            button.setFont(self.grFont)
            button.setFixedHeight(20)
            self.default_buttons.append(button)

        self.default_buttons[0].clicked.connect(lambda: self.clickButton(0))
        self.default_buttons[1].clicked.connect(lambda: self.clickButton(1))
        self.default_buttons[2].clicked.connect(lambda: self.clickButton(2))
        self.default_buttons[3].clicked.connect(lambda: self.clickButton(3))

        layout = QVBoxLayout(self)

        layout_menu = QHBoxLayout(self)
        layout_menu.addWidget(self.label)
        layout_menu.addWidget(self.comboBox)
        layout_menu.addWidget(self.rename)
        layout_menu.setSpacing(self.row_spacing * 2)

        layout_button = QVBoxLayout(self)
        for button in self.default_buttons:
            layout_button.addWidget(button)
        layout_button.setContentsMargins(60, 10, 10, 10)
        layout_button.setSpacing(self.row_spacing*2)

        layout.addLayout(layout_menu)
        layout.addLayout(layout_button)
        layout.setContentsMargins(5, 5, 5, 0)
        layout.setSpacing(self.row_spacing)

        self.viewPressedSignalFlag = False
        self.comboBox.view().pressed.connect(self.menuViewPressedHandle)
        self.comboBox.currentIndexChanged.connect(self.menuChangeHandle)
        self.comboBox.activated.connect(self.menuActivatedHandle)
        self.rename.clicked.connect(self.buttonRename)

        self.parent_widget=widget

    def buttonRename(self):
        self.qdialog = QDialog(self.parent_widget.node.scene.getView().window())
        self.qdialog.setWindowTitle('Rename Button')
        self.renameDialog = Ui_button_name_edit_dialog()
        self.renameDialog.setupUi(self.qdialog)

        buttons = self.parent_widget.node.manager.widgetSet['select'].default_buttons

        lineEdits = [
            self.renameDialog.lineEdit_1,
            self.renameDialog.lineEdit_2,
            self.renameDialog.lineEdit_3,
            self.renameDialog.lineEdit_4
        ]

        for i, button in enumerate(buttons):
            lineEdit = lineEdits[i]
            lineEdit.setText(button.text())

        self.renameDialog.save.clicked.connect(self.onButtonSave)
        self.renameDialog.cancel.clicked.connect(self.onButtonCancel)

        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        self.qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def onButtonSave(self):
        items = []
        items.append(self.renameDialog.lineEdit_1.text())
        items.append(self.renameDialog.lineEdit_2.text())
        items.append(self.renameDialog.lineEdit_3.text())
        items.append(self.renameDialog.lineEdit_4.text())

        self.parent_widget.node.manager.widgetSet['select'].comboBox.clear()
        self.parent_widget.node.manager.widgetSet['select'].comboBox.addItems(items)

        index = 0
        for button in self.parent_widget.node.manager.widgetSet['select'].default_buttons:
            button.setText(items[index])
            index = index + 1

        self.qdialog.close()

    def onButtonCancel(self):
        self.qdialog.close()

    def menuActivatedHandle(self):
        self.viewPressedSignalFlag = False

    def menuViewPressedHandle(self):
        self.viewPressedSignalFlag = True

    def menuChangeHandle(self):
        if self.viewPressedSignalFlag:
            self.valueStored.emit()
        self.valueChanged.emit()
        self.viewPressedSignalFlag = False

    def clickButton(self, index):
        self.comboBox.setCurrentIndex(index)

    @property
    def widget_value(self) -> list:
        return [self.comboBox.itemText(self.comboBox.currentIndex()), self.comboBox.currentIndex()]

    @widget_value.setter
    def widget_value(self, value: list):
        self.comboBox.setCurrentIndex(value[1])

class VerticalTabBar(QtWidgets.QTabBar):
    def __init__(self,widget):
        super().__init__(widget)
        self.setFont(QFont("Calibri"))

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class TapMenu(QTabWidget, widgetCompomentBase):

    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, parameter: dict, rotate: bool):
        super().__init__(widget)
        self.pSize = parameter["pSize"]
        self.cSize = parameter["cSize"]
        self.rotate = rotate

        if rotate is False:
            self.tabWidth = 200
            self.tabOffset = 5
            self.tabHeight = self.cSize * 30 + 37
        else:
            self.tabWidth = 180
            self.tabHeight = 280
            self.tabOffset = 0
            tabBar = VerticalTabBar(self)
            self.setTabBar(tabBar)
            self.setTabPosition(QTabWidget.West)

        self.setFont(self.grFont)
        self.setUsesScrollButtons(False)
        for i in range(self.pSize):
            name = 'tab' + str(i)
            self.__setattr__(name, QWidget(widget))
            tab = self.__getattribute__(name)
            tab.setObjectName(name)
            self.addTab(tab, str(i+1))

        self.signalFlag = False
        self.currentChanged.connect(self.menuChangedHandle)
        self.tabBarClicked.connect(self.menuClickedHandle)

    def menuChangedHandle(self):
        if self.signalFlag == True: self.valueStored.emit()
        self.signalFlag = False

    def menuClickedHandle(self):
        self.signalFlag = True

    def resizeEvent(self, event):
        self.setFixedWidth(self.tabWidth + self.tabOffset)
        self.setFixedHeight(self.tabHeight)
        QTabWidget.resizeEvent(self, event)
        if self.rotate:
            self.setVertical()
        else:
            self.setHorizontal()

    def setHorizontal(self):
        self.setStyleSheet(("QTabWidget::pane { \n"
                            "top:-1px; \n"
                            "border: none;\n"
                            "}\n"
                            "QTabBar::tab {\n"
                            "border: 1px solid #7d7d7d; \n"
                            "color: #7d7d7d; \n"
                            "padding: 2px;\n"
                            "width: %dpx;\n"
                            "}\n"
                            "QTabBar::tab:selected { \n"
                            "color: #ffffff;\n"
                            "background: #7d7d7d; \n"
                            "}" % ((self.tabWidth - (self.pSize + 1) - self.pSize * 4) / self.pSize)))

    def setVertical(self):
        self.setStyleSheet(("QTabWidget::pane { \n"
                            "top:-1px; \n"
                            "border: none;\n"
                            "}\n"
                            "QTabBar::tab {\n"
                            "border: 1px solid #7d7d7d; \n"
                            "color: #7d7d7d; \n"
                            "padding: 2px;\n"
                            "height: %dpx;\n"
                            "}\n"
                            "QTabBar::tab:selected { \n"
                            "color: #ffffff;\n"
                            "background: #7d7d7d; \n"
                            "}" % ((self.tabHeight - self.pSize - 1 - self.pSize * 4) / self.pSize)))

    @property
    def widget_value(self):
        return [self.currentIndex(), self.pSize]

    @widget_value.setter
    def widget_value(self, value: list):
        self.signalFlag = False
        self.setCurrentIndex(value[0])
        self.pSize = value[1]

class Meter_Label_Button(QWidget, widgetCompomentBase):

    def __init__(self, widget: QWidget):
        super(Meter_Label_Button, self).__init__(widget)

        steps = ['green'] * 27 + ['yellow'] * 3 + ['red'] * 2

        self.meter = QMeter(steps)

        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText("default")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QToggleSwitch()
        self.button.setCheckable(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.meter, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    @property
    def height(self) -> int:
        return self.meter.height

    @height.setter
    def height(self, new_value):
        self.meter._height = new_value - 90

    @property
    def width(self) -> int:
        return self.meter._width

    @width.setter
    def width(self, new_value):
        self.meter._width = (new_value - 20)/2
        self.label.setFixedWidth(new_value - 20)
        self.button.setFixedWidth((new_value - 20)/2)

class QLiveDialDouble(QWidget, widgetCompomentBase):

    def __init__(self, widget, parameter):
        super().__init__(widget)
        self.row_height = 100

        self.dial = QDoubleDial(2)
        self.dial.setMaximum(parameter["pMax"])
        self.dial.setMinimum(parameter["pMin"])
        self.dial.setValue(parameter["pValue"])

        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText("default")
        self.label.setFixedWidth(50)
        self.label.setFixedHeight(20)
        self.label.setAlignment(Qt.AlignCenter)

        self.numbox = QDoubleSpinBox()
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameter["pMax"])
        self.numbox.setMinimum(parameter["pMin"])
        self.numbox.setValue(parameter["pValue"])
        self.numbox.setFixedWidth(40)
        self.numbox.setFixedHeight(20)
        self.numbox.setAlignment(Qt.AlignCenter)
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.dial, alignment=Qt.AlignHCenter)
        layout.addWidget(self.numbox, alignment=Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.valueStored = self.dial.sliderReleased
        self.valueChanged = self.dial.doubleValueChanged

        self.dial.valueChanged.connect(self.handleDialValueChange)
        self.numbox.editingFinished.connect(self.handleNumboxValueChange)

    @pyqtSlot(int)
    def handleDialValueChange(self):
        self.numbox.setValue(self.dial.value())

    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.dial.setValue(self.numbox.value())
        self.valueStored.emit()

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.dial.setValue(value)

class QLiveDialInteger(QWidget, widgetCompomentBase):

    def __init__(self, widget, parameter):
        super().__init__(widget)
        self.row_height = 100

        self.dial = QIntegerDial()
        self.dial.setMaximum(parameter["pMax"])
        self.dial.setMinimum(parameter["pMin"])
        self.dial.setValue(parameter["pValue"])

        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText("default")
        self.label.setFixedWidth(50)
        self.label.setFixedHeight(20)
        self.label.setAlignment(Qt.AlignCenter)

        self.numbox = QSpinBox()
        self.numbox.setFont(self.grFont)
        self.numbox.setMaximum(parameter["pMax"])
        self.numbox.setMinimum(parameter["pMin"])
        self.numbox.setValue(parameter["pValue"])
        self.numbox.setFixedWidth(40)
        self.numbox.setFixedHeight(20)
        self.numbox.setAlignment(Qt.AlignCenter)
        self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numbox.setFrame(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.dial, alignment=Qt.AlignHCenter)
        layout.addWidget(self.numbox, alignment=Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.valueStored = self.dial.sliderReleased
        self.valueChanged = self.dial.valueChanged

        self.dial.valueChanged.connect(self.handleDialValueChange)
        self.numbox.editingFinished.connect(self.handleNumboxValueChange)

    @pyqtSlot(int)
    def handleDialValueChange(self):
        self.numbox.setValue(self.dial.value())

    @pyqtSlot()
    def handleNumboxValueChange(self):
        self.dial.setValue(self.numbox.value())
        self.valueStored.emit()

    @property
    def widget_value(self):
        return self.numbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.numbox.setValue(value)
        self.dial.setValue(value)


class LabelDoubleNumberBox(QWidget, widgetCompomentBase):
    def __init__(self, widget, parameters):
        super().__init__(widget)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        self.spinbox = DoubleNumberBox()

        self.spinbox.setFont(self.grFont)
        self.spinbox.setMaximum(parameters["pMax"])
        self.spinbox.setMinimum(parameters["pMin"])

        p_max_integer_part = abs(int(parameters["pMax"]))
        p_min_integer_part = abs(int(parameters["pMin"]))
        p_max_integer_digit_count = len(str(p_max_integer_part))
        p_min_integer_digit_count = len(str(p_min_integer_part))
        integer_digit_count = max(p_max_integer_digit_count, p_min_integer_digit_count)

        self.row_width[2] = integer_digit_count * 8 + parameters['pDecimalPrecision'] * 8 + 10
        self.spinbox.setFixedWidth(self.row_width[2])
        self.spinbox.setDecimals(int(parameters['pDecimalPrecision']))
        self.spinbox.setValue(parameters["pValue"])


        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.valueStored = self.spinbox.editingFinished
        self.valueChanged = self.spinbox.valueChanged

    @property
    def widget_value(self):
        return self.spinbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.spinbox.setValue(value)

    def disableWidget(self,bool=False):
        self.label.setDisabled(bool)
        self.spinbox.setDisabled(bool)
        if bool:
            self.label.setStyleSheet("color:grey;")
            self.spinbox.setStyleSheet("color:grey;")
        else:
            self.label.setStyleSheet("color:white;")
            self.spinbox.setStyleSheet("color:white;")

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def set_spinbox_max_value(self, new_value):
        self.spinbox.setMaximum(new_value)

    def set_spinbox_min_value(self, new_value):
        self.spinbox.setMinimum(new_value)

    def set_num_decimal_places(self, new_value):
        self.spinbox.setDecimals(new_value)


class LabelAndIntNumberBox(QWidget, widgetCompomentBase):
    def __init__(self, widget, parameters):
        super().__init__(widget)
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        if parameters is not None and 'pRowWidth' in parameters:
            self.row_width = parameters['pRowWidth']
        else:
            self.row_width[0] = self.width_between_label_and_widget + self.label.sizeHint().width()
        self.label.setFixedWidth(self.row_width[0])

        self.spinbox = IntNumberBox()
        self.spinbox.setFixedWidth(self.row_width[2])
        self.spinbox.setFont(self.grFont)
        self.spinbox.setMaximum(parameters["pMax"])
        self.spinbox.setMinimum(parameters["pMin"])
        self.spinbox.setValue(parameters["pValue"])

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.valueStored = self.spinbox.editingFinished
        self.valueChanged = self.spinbox.valueChanged

    @property
    def widget_value(self):
        return self.spinbox.value()

    @widget_value.setter
    def widget_value(self, value: float):
        self.spinbox.setValue(value)

    def set_label_text(self, new_label_text):
        self.label.setText(new_label_text)

    def set_spinbox_max_value(self, new_value):
        self.spinbox.setMaximum(new_value)

    def set_spinbox_min_value(self, new_value):
        self.spinbox.setMinimum(new_value)


class Label_PushButton_DoubleNumber(QWidget, widgetCompomentBase):
    def __init__(self, widget, parameter):
        super().__init__(widget)

        self.label = QLabel()
        self.label.setFixedWidth(self.row_width[0])
        self.label.setFont(self.grFont)
        self.label.setText("default")

        self.toggle = QToggleSwitch()
        self.toggle.setFont(self.grFont)
        self.toggle.setCheckable(True)
        self.toggle.setChecked(False)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinbox.setFrame(False)
        self.spinbox.setFixedWidth(self.row_width[2])
        self.spinbox.setEnabled(False)
        self.spinbox.setFont(self.grFont)
        self.spinbox.setMaximum(parameter["pMax"])
        self.spinbox.setMinimum(parameter["pMin"])
        self.spinbox.setValue(parameter["pValue"])

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.toggle)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)
     
# class LabelSpinBox(QWidget, widgetCompomentBase):
#     def __init__(self, widget, parameter):
#         super().__init__(widget)
#         if 'pRowWidth' in parameter:
#             self.row_width = parameter['pRowWidth']
#         self.label = QLabel()
#         self.label.setFixedWidth(self.row_width[0])
#         self.label.setFont(self.grFont)
#         self.label.setText("default")
#
#         self.numbox = QDoubleSpinBox()
#         if 'pDecimalPrecision' in parameter:
#             self.numbox.setDecimals(parameter['pDecimalPrecision'])
#         self.numbox.setFixedWidth(self.row_width[2])
#         self.numbox.setFont(self.grFont)
#         self.numbox.setMaximum(parameter["pMax"])
#         self.numbox.setMinimum(parameter["pMin"])
#         self.numbox.setValue(parameter["pValue"])
#         self.numbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
#         self.numbox.setFrame(False)
#
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.label)
#         layout.addWidget(self.numbox)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(self.row_spacing)
#
#         self.valueStored = self.numbox.editingFinished
#         self.valueChanged = self.numbox.valueChanged
#
#     @property
#     def widget_value(self):
#         return self.numbox.value()
#
#     @widget_value.setter
#     def widget_value(self, value: float):
#         self.numbox.setValue(value)
#
#     def disableWidget(self, bool=False):
#         self.label.setDisabled(bool)
#         self.numbox.setDisabled(bool)
#         if bool:
#             self.label.setStyleSheet("color:grey;")
#             self.numbox.setStyleSheet("color:grey;")
#         else:
#             self.label.setStyleSheet("color:white;")
#             self.numbox.setStyleSheet("color:white;")