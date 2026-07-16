import re
import shutil
import csv
import time

from flowstudio.functions.common import is_program_installed
from template.usb_runtime_select import Ui_usb_runtime_select_Dialog
from template.dialog_remote_control_selection import Ui_dialog_remote_control_selection
from utilities.configFileTransfer import *
from utilities.utils import isEngineAlive, killEngine
from threading import Timer
import serial
import serial.tools.list_ports
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from template.control_dialog import *
from template.export_command import *
from template.runtime_select import *
from template.project_title_edit import *
from flowstudio.flow_audio_manager import AudioEnviroment
from flowstudio.flow_thread_manager import *
from flowstudio.flow_engine_interface import FLOW_Engine_Interface
import sounddevice as sd
import numpy as np
from flowstudio.flow_window import *
from flowstudio.flow_conf import Target, OP_NODE_ADC, OP_NODE_DAC, AO_TYPE_NAME, Debug
from flowstudio.functions.logger_setup import setup_logger
DEBUG = True
DEBUG_Low_Level = True
DEBUG_Tick_Socket = True

class AudioThread(QThread):

    def __init__(self, engine, instance, inIdx, outIdx, Fs, ins, outs, frameSize):
        super(QThread, self).__init__()
        self.engine = engine
        self.instance = instance
        self.inIdx = inIdx
        self.outIdx = outIdx
        self.Fs = Fs
        self.ins = ins
        self.outs = outs
        self.frameSize = frameSize

    def run(self):
        import sounddevice as sd
        AudioEnviroment.startPaStream(self, self.engine, self.instance,
                           self.inIdx, self.outIdx, self.Fs, self.ins, self.outs, self.frameSize)
        # def deinterleave(input, framesize, channels):
        #     out = np.zeros((channels, framesize)).astype(np.float32)
        #     for ch in range(channels):
        #         for i in range(framesize):
        #             out[ch][i] = input[i][ch]
        #     return out
        #
        # def interleave(input, framesize, channels):
        #     out = np.zeros((framesize, channels)).astype(np.float32)
        #     for ch in range(channels):
        #         for i in range(framesize):
        #             out[i][ch] = input[ch][i]
        #     return out
        #
        # def callback(indata, outdata, frames, time, status):
        #     if status:
        #         print(status)
        #     inDeinterleave = deinterleave(indata, self.frameSize, self.ins)
        #
        #     out = self.engine.process(self.instance, inDeinterleave)
        #
        #     outdata[:] = interleave(out, self.frameSize, self.outs)
        # try:
        #     with sd.Stream(device=(self.inIdx, self.outIdx),
        #                    samplerate=self.Fs, blocksize=self.frameSize,
        #                    dtype='float32', latency='low',
        #                    channels=(self.ins, self.outs), callback=callback):
        #
        #         print(sd.query_devices())
        #         SR = [8000, 16000, 32000, 44100, 48000, 88200, 96000, 192000]
        #         for rate in SR:
        #             print("checking input sample rate: ", rate)
        #             try:
        #                 with sd.check_input_settings(device=self.inIdx, samplerate=rate):
        #                     print("check_input_settings")
        #             except Exception as e:
        #                 print(e)
        #
        #             print("checking output sample rate: ", rate)
        #             try:
        #                 with sd.check_output_settings(device=self.outIdx, samplerate=rate):
        #                     print("check_output_settings")
        #             except Exception as e:
        #                 print(e)
        #
        #     while True:
        #         print("audio thread")
        #         sd.sleep(500)
        # except Exception as e:
        #     exit(type(e).__name__ + ': ' + str(e))



class FLOW_Window_Connection(AudioEnviroment):

    cpuTimer = QTimer()
    client = FLOW_Thread_Manager()
    show_window_objects = list()
    FlowEngineVersion = ''



    def __init__(self, parent, dialog):
        super().__init__()
        self.window = parent
        self.is_debug_mode = True
        current_path = os.getcwd()
        index = current_path.find('flowstudio')
        if index == -1:
            index = current_path.rfind('main')
            target_path = current_path[:index] + 'bin\\'
        else:
            target_path = current_path[:index] + 'bin\\'
        self.default_pc_engine_path = os.path.join(target_path, 'FlowEngine.exe')
        self.pc_engine_path = self.default_pc_engine_path

        self.allow_connect_inconsistent_version = False
        self.currDriver = 0
        self.currSoundCardInput = ''
        self.currSoundCardOutput = ''

        # init from ui template file
        self.controlDialog = Ui_controlDialog()
        self.controlDialog.setupUi(dialog)

        self.behaviorSetUp()
        self.audioInterfaceSetUp(init_signal_slot=True)
        self.IntiUartData()

        # QTimer need start function to emit timeout siganl
        self.cpuTimer.timeout.connect(self.tickSocket)

        self.controlDialog.comboBox_driver_list.clear()
        self.controlDialog.comboBox_driver_list.addItems(self.driverList())


        # setup Input list
        self.controlDialog.comboBox_input_list.clear()
        self.controlDialog.comboBox_input_list.addItems(self.inputList())

        # setup Output list
        self.controlDialog.comboBox_output_list.clear()
        self.controlDialog.comboBox_output_list.addItems(self.outputList())

        # setup sample rate list
        sampleratelist = self.supportedSampleRate(str(self.defaultInput()), str(self.defaultOutput()))
        self.controlDialog.comboBox_sr_list.clear()
        if sampleratelist:
            self.controlDialog.comboBox_sr_list.addItems(sampleratelist)

        # build up driver list
        self.onRefreshSampleRateList()

        # driver/input/output item list signal-slot init

        self.controlDialog.comboBox_driver_list.currentIndexChanged.connect(self.onCombobox_driver_sel)
        self.controlDialog.comboBox_input_list.currentIndexChanged.connect(self.onCombobox_io_sel)
        self.controlDialog.comboBox_output_list.currentIndexChanged.connect(self.onCombobox_io_sel)




    def behaviorSetUp(self):
        """
            Set the parameter values for the control dialog
        """
        # ComboBox_targetdevice history options
        self.comboBox_targetdevice_history = []

        self.controlDialog.pushButton_import.clicked.connect(self.window.onProfileImport)
        self.controlDialog.pushButton_save.clicked.connect(self.window.onProfileSave)
        self.controlDialog.pushButton_update.clicked.connect(self.window.onSoundDeviceUpdate)

        # dsp status check box status connect ui class
        self.controlDialog.checkBox_dsp.setChecked(self.window.dspstatus)

        # dsp status check box status connect to socket class
        self.controlDialog.checkBox_dsp.clicked.connect(self.onSocketConnection)

        self.controlDialog.push_button_browse_engine_path.clicked.connect(self.open_select_engine_dialog)
        # DISABLE THE TARGET DEVICE/REMOTE DEVICE AVAILABLE LIST HERE!!!

        # target index changed connect to
        self.controlDialog.comboBox_targetdevice.currentIndexChanged.connect(self.onTargetSelect)
        self.controlDialog.comboBox_targetdevice.setCurrentIndex(self.window.target)
        # self.controlDialog.comboBox_targetdevice.model().item(0).setEnabled(False)
        # self.controlDialog.comboBox_targetdevice.model().item(1).setEnabled(False)
        self.controlDialog.comboBox_targetdevice.model().item(2).setEnabled(False)
        # self.controlDialog.comboBox_targetdevice.model().item(3).setEnabled(False)
        self.controlDialog.comboBox_targetdevice.model().item(4).setEnabled(False)
        # self.controlDialog.comboBox_targetdevice.model().item(5).setEnabled(False)
        # self.controlDialog.comboBox_targetdevice.model().item(6).setEnabled(False)

        self.controlDialog.debug_mode_check_box.clicked.connect(self.handle_debug_mode_check_box)

    def audioInterfaceSetUp(self, init_signal_slot=False):
        """
            Set the parameter values for the control dialog -> PC
        """
        # clean exisited elements in the list
        # self.controlDialog.comboBox_input_list.clear()
        # self.controlDialog.comboBox_output_list.clear()
        # self.controlDialog.comboBox_sr_list.clear()
        # print('audioInterfaceSetUp')
        # print(self.window.itemIndex)
        self.onCombobox_driver_sel()
        # setup driver list
        self.controlDialog.comboBox_driver_list.clear()
        self.controlDialog.comboBox_driver_list.addItems(self.driverList())

        # setup Input list
        self.controlDialog.comboBox_input_list.clear()
        self.controlDialog.comboBox_input_list.addItems(self.inputList())

        # setup Output list
        self.controlDialog.comboBox_output_list.clear()
        self.controlDialog.comboBox_output_list.addItems(self.outputList())

        # setup sample rate list
        sampleratelist = self.supportedSampleRate(str(self.defaultInput()), str(self.defaultOutput()))
        self.controlDialog.comboBox_sr_list.clear()
        if sampleratelist:
            self.controlDialog.comboBox_sr_list.addItems(sampleratelist)
            self.controlDialog.comboBox_sr_list.setCurrentIndex(self.window.itemIndex[3])

        # driver/input/output item list signal-slot init
        if init_signal_slot:
            self.controlDialog.comboBox_driver_list.currentIndexChanged.connect(self.onCombobox_driver_sel)
            self.controlDialog.comboBox_input_list.currentIndexChanged.connect(self.onCombobox_io_sel)
            self.controlDialog.comboBox_output_list.currentIndexChanged.connect(self.onCombobox_io_sel)
            # self.controlDialog.comboBox_sr_list.currentIndexChanged.connect(self.handle_sample_rate_change)

        # driver/input/output Set last value
        self.controlDialog.comboBox_driver_list.setCurrentIndex(self.window.itemIndex[0])
        self.controlDialog.comboBox_input_list.setCurrentIndex(self.window.itemIndex[1])
        self.controlDialog.comboBox_output_list.setCurrentIndex(self.window.itemIndex[2])

        self.onRefreshSampleRateList()

    def open_select_engine_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self.window, "Select Engine", "", "Engine Files (*.exe)",
                                                   options=options)
        if file_path:
            self.pc_engine_path = file_path
            self.controlDialog.line_edit_engine_path.setText(file_path)
            if os.path.normpath(file_path) != os.path.normpath(self.default_pc_engine_path):
                self.controlDialog.debug_mode_label.setVisible(True)
                self.controlDialog.debug_mode_check_box.setVisible(True)
            else:
                self.controlDialog.debug_mode_check_box.setChecked(False)
                self.controlDialog.debug_mode_label.setVisible(False)
                self.controlDialog.debug_mode_check_box.setVisible(False)

    # def handle_sample_rate_change(self):
    #     from flowstudio.flow_conf import NOT_SUPPORT_AOS, AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR, \
    #         AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR, AOS_ONLY_ALLOW_SIXTEEN_K_AND_FORTY_EIGHT_K_SR
    #
    #     current_sr = self.controlDialog.comboBox_sr_list.currentText()
    #
    #     # Under the PC platform, these AOs only support 16k
    #     if current_sr == '16000':
    #         for ao in AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR:
    #             if ao in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].remove(ao)
    #     else:
    #         for ao in AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR:
    #             if ao not in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].append(ao)
    #
    #     # Under the PC platform, these AOs only support 48k
    #     if current_sr == '48000':
    #         for ao in AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR:
    #             if ao in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].remove(ao)
    #     else:
    #         for ao in AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR:
    #             if ao not in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].append(ao)
    #
    #     # Under the PC platform, these AOs only support 16k and 48k
    #     if current_sr in ['16000', '48000']:
    #         for ao in AOS_ONLY_ALLOW_SIXTEEN_K_AND_FORTY_EIGHT_K_SR:
    #             if ao in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].remove(ao)
    #     else:
    #         for ao in AOS_ONLY_ALLOW_SIXTEEN_K_AND_FORTY_EIGHT_K_SR:
    #             if ao not in NOT_SUPPORT_AOS[Target.PC.value]:
    #                 NOT_SUPPORT_AOS[Target.PC.value].append(ao)
    #
    #     if hasattr(self.window, 'license_mechanism'):
    #         self.disable_not_supported_ao()

    def checkPort(self):
        """
            update the value of COM PORT in UART
        """
        self.port_list = []
        portlist = list(serial.tools.list_ports.comports())
        if len(portlist) <= 0:
            self.port_list = ['None']
        else:
            for i in range(len(portlist)):
                self.port_list.append(portlist[i].name)
        self.window.comport = self.controlDialog.Port_comboBox.currentIndex()
        self.controlDialog.Port_comboBox.clear()
        self.controlDialog.Port_comboBox.addItems(self.port_list)
        self.controlDialog.Port_comboBox.setCurrentIndex(self.window.comport)


    def IntiUartData(self):
        """
            Initialize data for UART(Cortex-M)
        """
        self.checkPort()

        self.connect_list = ['RS232']
        # self.rate_list = ['9600', '14400', '13200', '38400', '57600', '115200', '230400', '460800', '921600']
        self.rate_list = ['115200', "230400" , "460800", "921600"]
        self.parity_list = ['none']
        self.bits_list = ['1']

        if self.window.target == Target.GX8008C_USB.value:
            self.engine_list = ['USB_TX', 'USB_RX']
        else:
            self.engine_list = ['USB_TX', 'USB_RX', 'HFP_TX', 'HFP_RX', 'A2DP', 'BIS RX', 'CIS TX', 'CIS RX']

        self.controlDialog.Connection_comboBox.clear()
        self.controlDialog.Connection_comboBox.addItems(self.connect_list)
        self.controlDialog.Connection_comboBox.setCurrentIndex(self.window.connection)

        self.controlDialog.Rate_comboBox.clear()
        self.controlDialog.Rate_comboBox.addItems(self.rate_list)
        self.controlDialog.Rate_comboBox.setCurrentIndex(self.window.rate)

        self.controlDialog.Parity_comboBox.clear()
        self.controlDialog.Parity_comboBox.addItems(self.parity_list)
        self.controlDialog.Parity_comboBox.setCurrentIndex(self.window.parity)

        self.controlDialog.Bites_comboBox.clear()
        self.controlDialog.Bites_comboBox.addItems(self.bits_list)
        self.controlDialog.Bites_comboBox.setCurrentIndex(self.window.bites)

        engine_index = self.controlDialog.Engine_comboBox.currentIndex()
        self.controlDialog.Engine_comboBox.clear()
        self.controlDialog.Engine_comboBox.addItems(self.engine_list)
        self.controlDialog.Engine_comboBox.setCurrentIndex(engine_index)
        if self.controlDialog.Engine_comboBox.currentText() == '':
            self.controlDialog.Engine_comboBox.setCurrentIndex(0)

    def select_S7_port_list(self):
        search_text = "BlueSuite"
        if not is_program_installed(search_text):
            self.comboBox_targetdevice_history.pop()
            self.controlDialog.comboBox_targetdevice.setCurrentIndex(self.comboBox_targetdevice_history[-1])
            res = 'Cannot use S7 platform, please install BlueSuite before use.'
            QMessageBox.about(self.window, "S7 Error", res)
            return
        self.S7_port_list = []
        from bin.S7_helper import usbConnect
        te = usbConnect.UsbConnect("../bin/S7_helper/TestEngine.dll")
        transports = te.list_transports()
        self.S7_port_list = list(transports.keys())
        self.controlDialog.transports_list.clear()
        self.controlDialog.transports_list.addItems(self.S7_port_list)

    def disable_not_supported_ao(self):
        from flowstudio.flow_conf import NOT_SUPPORT_AOS, get_class_from_opcode, OpCodeNotRegistered
        from flowstudio.flow_conf_co import NOT_SUPPORT_COS
        feature_permission_data = self.window.license_mechanism.feature_permission_data
        available_ao_name_list = []
        for ao_code in feature_permission_data[AO_TYPE_NAME]:
            try:
                available_ao_name_list.append(get_class_from_opcode(ao_code).display_name)
            except OpCodeNotRegistered:
                continue

        # When the input device is empty, IN AO is not supported on the PC platform
        if self.inputList() == [] and self.window.target == Target.PC.value:
            NOT_SUPPORT_AOS[Target.PC.value].append(OP_NODE_ADC)
            self.window.updateInAndOut()
        else:
            self.window.updateInAndOut()
            while OP_NODE_ADC in NOT_SUPPORT_AOS[Target.PC.value]:
                NOT_SUPPORT_AOS[Target.PC.value].remove(OP_NODE_ADC)

        # When the output device is empty, OUT AO is not supported on the PC platform
        if self.outputList() == [] and self.window.target == Target.PC.value:
            NOT_SUPPORT_AOS[Target.PC.value].append(OP_NODE_DAC)
            self.window.updateInAndOut()
        else:
            self.window.updateInAndOut()
            while OP_NODE_DAC in NOT_SUPPORT_AOS[Target.PC.value]:
                NOT_SUPPORT_AOS[Target.PC.value].remove(OP_NODE_DAC)

        for ao_in_tree in self.window.nodesListWidget.items:
            if self.window.target in NOT_SUPPORT_AOS:
                not_supported = False
                for ao_code in NOT_SUPPORT_AOS[self.window.target]:
                    if ao_in_tree.text(0) == get_class_from_opcode(ao_code).display_name:
                        ao_in_tree.setFlags(ao_in_tree.flags() & ~Qt.ItemIsEnabled)
                        ao_in_tree.setForeground(0, QBrush(QColor("grey")))
                        not_supported = True
                if not not_supported:
                    if ao_in_tree.text(0) in available_ao_name_list:
                        ao_in_tree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
                        ao_in_tree.setForeground(0, QBrush(QColor("#CCCCCC")))
                    else:
                        ao_in_tree.setFlags(ao_in_tree.flags() & ~Qt.ItemIsEnabled)
                        ao_in_tree.setForeground(0, QBrush(QColor("grey")))
            else:
                if ao_in_tree.text(0) in available_ao_name_list:
                    ao_in_tree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
                    ao_in_tree.setForeground(0, QBrush(QColor("#CCCCCC")))
                else:
                    ao_in_tree.setFlags(ao_in_tree.flags() & ~Qt.ItemIsEnabled)
                    ao_in_tree.setForeground(0, QBrush(QColor("grey")))

        co_display_name = []
        for co_code in NOT_SUPPORT_COS:
            co_display_name.append(get_class_from_opcode(co_code).display_name)

        for ao_control_tree in self.window.nodesControlListWidget.items:
            if ao_control_tree.text(0) in co_display_name:
                ao_control_tree.setFlags(ao_control_tree.flags() & ~Qt.ItemIsEnabled)
                ao_control_tree.setForeground(0, QBrush(QColor("grey")))
            else:
                ao_control_tree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
                ao_control_tree.setForeground(0, QBrush(QColor("#CCCCCC")))



    def onTargetSelect(self):
        """
            Selecting different device platforms on the settings page will result in different UIs
        """
        self.window.target = self.controlDialog.comboBox_targetdevice.currentIndex()
        self.disable_not_supported_ao()
        self.comboBox_targetdevice_history.append(self.window.target)

        if self.window.target:
            # target_idx = 1, 2, 3, 4, 5, 6...

            self.controlDialog.Group4_Editor.setMaximumSize(QtCore.QSize(16777215, 45))
            self.controlDialog.formLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 361, 44))
            self.controlDialog.line_edit_engine_path.setVisible(False)
            self.controlDialog.push_button_browse_engine_path.setVisible(False)
            self.controlDialog.formLayout_Editor.removeItem(self.controlDialog.h_layout_engine_path)

            # disable audio io interface
            # enable path column
            self.onSelAudioInterface(False)
            self.controlDialog.Group2_Audio.setVisible(False)
            self.controlDialog.Group3_Network.setVisible(True)
            self.controlDialog.Group5_Connection.setVisible(False)
            self.controlDialog.Group6_S7.setVisible(False)
            self.onSelPath(True)
            self.controlDialog.lineEdit_freeports.setPlaceholderText("")
            self.controlDialog.lineEdit_path.setPlaceholderText("")
            self.controlDialog.communication_label.setText('Communication Setting')

            if self.window.target == Target.IMX.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(True)
                self.onSelPassword(True)

            elif self.window.target == Target.LINUX.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(True)
                self.onSelPassword(True)

            elif self.window.target == Target.AMLOGIC.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(False)
                self.onSelPassword(False)

            elif self.window.target == Target.LINKPLAY.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(False)
                self.onSelPassword(False)

            elif self.window.target == Target.RASP.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(True)
                self.onSelPassword(True)

            elif self.window.target == Target.QCS.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(False)
                self.onSelPassword(False)

            elif self.window.target == Target.CORTEX_M_USB.value or \
                    self.window.target == Target.FLOW_EVK_UART.value or \
                    self.window.target == Target.GX8008C_USB.value:
                self.onSelHostname(False)
                self.onSelPort(False)
                self.onSelUsername(False)
                self.onSelPassword(False)
                self.controlDialog.Group2_Audio.setVisible(False)
                self.controlDialog.Group3_Network.setVisible(False)
                self.controlDialog.Group5_Connection.setVisible(True)
                self.onAirohaUART(False)
                self.onAirohaUSB(False)
                self.onEngine(False)
                self.onConnectingVisible(True)
                self.controlDialog.comboBox_driver_list_5.currentIndexChanged.connect(self.onCortexMSelectUSBorUART)
                if self.window.target == Target.GX8008C_USB.value:
                    self.controlDialog.comboBox_driver_list_5.model().item(0).setEnabled(True)
                    self.controlDialog.comboBox_driver_list_5.setCurrentIndex(0)
                    self.controlDialog.comboBox_driver_list_5.view().setRowHidden(1, True)
                    self.onEngine(True)
                else:
                    self.controlDialog.comboBox_driver_list_5.view().setRowHidden(1, False)
                    self.controlDialog.comboBox_driver_list_5.model().item(0).setEnabled(True)
                    self.controlDialog.comboBox_driver_list_5.setCurrentIndex(0)
                if self.controlDialog.comboBox_driver_list_5.currentIndex() == 0:
                    self.onCortexMUSB(True)
                    self.onCortexMUART(False)
                elif self.controlDialog.comboBox_driver_list_5.currentIndex() == 1:
                    self.onCortexMUSB(False)
                    self.onCortexMUART(True)

            elif self.window.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
                self.onSelHostname(False)
                self.onSelPort(False)
                self.onSelUsername(False)
                self.onSelPassword(False)
                self.controlDialog.Group2_Audio.setVisible(False)
                self.controlDialog.Group3_Network.setVisible(False)
                self.controlDialog.Group5_Connection.setVisible(True)
                self.onCortexMUSB(False)
                self.onCortexMUART(False)
                self.onConnectingVisible(False)
                self.onEngine(True)
                self.controlDialog.comboBox_driver_list_6.currentIndexChanged.connect(self.onAirohaSelectUSBorUART)
                if self.controlDialog.comboBox_driver_list_6.currentIndex() == 0:
                    self.onAirohaUART(True)
                    self.onAirohaUSB(False)
                elif self.controlDialog.comboBox_driver_list_6.currentIndex() == 1:
                    self.onAirohaUART(False)
                    self.onAirohaUSB(True)

            elif self.window.target == Target.FLOW_APO.value:
                self.onSelHostname(True)
                self.onSelPort(True)
                self.onSelUsername(False)
                self.onSelPassword(False)
                self.controlDialog.lineEdit_freeports.setPlaceholderText("55040")
                self.controlDialog.lineEdit_path.setPlaceholderText("C:/FlowAPO/Config/default_config.flw")

            elif self.window.target == Target.S7.value:
                self.controlDialog.Group2_Audio.setVisible(False)
                self.controlDialog.Group3_Network.setVisible(False)
                self.controlDialog.Group5_Connection.setVisible(False)
                self.controlDialog.Group6_S7.setVisible(True)
                self.select_S7_port_list()

        else:
            # target_idx = 0

            self.controlDialog.Group4_Editor.setMaximumSize(QtCore.QSize(16777215, 100))
            self.controlDialog.formLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 361, 100))
            self.controlDialog.line_edit_engine_path.setVisible(True)
            self.controlDialog.push_button_browse_engine_path.setVisible(True)
            while self.controlDialog.formLayout_Editor.count():
                self.controlDialog.formLayout_Editor.takeAt(0)
            self.controlDialog.formLayout_Editor.setLayout(0, QFormLayout.SpanningRole,
                                                           self.controlDialog.h_layout_engine_path)
            self.controlDialog.formLayout_Editor.setLayout(1, QFormLayout.SpanningRole,
                                                           self.controlDialog.h_layout_connect_to_engine)
            self.controlDialog.line_edit_engine_path.setText(self.pc_engine_path)

            # enable audio io interface
            self.controlDialog.communication_label.setText('Audio Device Setting')

            self.onSelAudioInterface(True)
            self.controlDialog.Group2_Audio.setVisible(True)
            self.controlDialog.Group3_Network.setVisible(False)
            self.controlDialog.Group5_Connection.setVisible(False)
            self.controlDialog.Group6_S7.setVisible(False)
            self.onSelHostname(False)
            self.onSelPort(False)
            self.onSelUsername(False)
            self.onSelPassword(False)
            self.onSelPath(False)

        pid = self.controlDialog.lineEdit_pid.text()
        vid = self.controlDialog.lineEdit_vid.text()
        if self.window.target == Target.FLOW_EVK_UART.value:
            if pid == '' and vid == '':
                self.controlDialog.lineEdit_pid.setText('0x00a4')
                self.controlDialog.lineEdit_vid.setText('0x1fc9')
        else:
            self.controlDialog.lineEdit_pid.setText(pid)
            self.controlDialog.lineEdit_vid.setText(vid)

    def onCortexMSelectUSBorUART(self, num=0):
        """
            Hide or Show UI

            num: is the connection value of Cortex-M
        """
        if num == 0:
            self.onCortexMUSB(True)
            self.onCortexMUART(False)
        elif num == 1:
            self.onCortexMUSB(False)
            self.onCortexMUART(True)

    def onAirohaSelectUSBorUART(self, num=0):
        """
            Hide or Show UI

            num: is the connection value of Airoha
        """
        if num == 0:
            self.onAirohaUART(True)
            self.onAirohaUSB(False)
        elif num == 1:
            self.onAirohaUART(False)
            self.onAirohaUSB(True)

    def onCheckDSPStatus(self, bool):
        if bool == 0:
            # 0 > Unchecked
            self.window.dspstatus = False
            self.window.actUpload.setEnabled(False)
            self.window.actDownload.setEnabled(False)

            self.window.editmode = False
            self.window.actEditMode.setEnabled(True)

            # TODO: we will disable simulation in the current 0.25 version
            # self.window.actQuickAnalysis.setEnabled(True)
            # self.window.actAnalysis.setEnabled(True)

            self.controlDialog.comboBox_targetdevice.setDisabled(False)
            self.controlDialog.lineEdit_path.setEnabled(True)
            self.controlDialog.lineEdit_hostname_1.setEnabled(True)
            self.controlDialog.lineEdit_hostname_2.setEnabled(True)
            self.controlDialog.lineEdit_hostname_3.setEnabled(True)
            self.controlDialog.lineEdit_hostname_4.setEnabled(True)
            self.controlDialog.lineEdit_freeports.setEnabled(True)
            self.controlDialog.lineEdit_username.setEnabled(True)
            self.controlDialog.lineEdit_password.setEnabled(True)
            self.controlDialog.comboBox_input_list.setDisabled(False)
            self.controlDialog.comboBox_driver_list.setDisabled(False)
            self.controlDialog.comboBox_output_list.setDisabled(False)
            self.controlDialog.comboBox_sr_list.setDisabled(False)

        else:
            # 1 > PartiallyChecked
            # 2 > Checked
            self.window.dspstatus = True
            self.window.actUpload.setEnabled(True and self.window.target != Target.PC.value)
            self.window.actDownload.setEnabled(True and self.window.target != Target.PC.value)

            self.window.editmode = True
            self.window.actEditMode.setEnabled(False)

            # TODO: we will disable simulation in the current 0.25 version
            # self.window.actQuickAnalysis.setEnabled(False)
            # self.window.actAnalysis.setEnabled(False)

            self.controlDialog.comboBox_targetdevice.setDisabled(True)
            self.controlDialog.lineEdit_path.setEnabled(False)
            self.controlDialog.lineEdit_hostname_1.setEnabled(False)
            self.controlDialog.lineEdit_hostname_2.setEnabled(False)
            self.controlDialog.lineEdit_hostname_3.setEnabled(False)
            self.controlDialog.lineEdit_hostname_4.setEnabled(False)
            self.controlDialog.lineEdit_freeports.setEnabled(False)
            self.controlDialog.lineEdit_username.setEnabled(False)
            self.controlDialog.lineEdit_password.setEnabled(False)
            self.controlDialog.comboBox_driver_list.setDisabled(True)
            self.controlDialog.comboBox_input_list.setDisabled(True)
            self.controlDialog.comboBox_output_list.setDisabled(True)
            self.controlDialog.comboBox_sr_list.setDisabled(True)

    def onCombobox_driver_sel(self):
        self.currDriver = self.controlDialog.comboBox_driver_list.currentIndex()

        # print('---->', self.currDriver)
        self.controlDialog.comboBox_input_list.clear()
        self.controlDialog.comboBox_output_list.clear()

        inputlist = self.inputList(str(self.currDriver))
        outputlist = self.outputList(str(self.currDriver))
        self.controlDialog.comboBox_input_list.addItems(inputlist)
        self.controlDialog.comboBox_output_list.addItems(outputlist)
        self.controlDialog.comboBox_input_list.setCurrentIndex(0)
        self.controlDialog.comboBox_output_list.setCurrentIndex(0)

        self.onRefreshSampleRateList()

        self.controlDialog.comboBox_sr_list.setCurrentIndex(0)

    def onCombobox_io_sel(self):
        input_ui_text = self.controlDialog.comboBox_input_list.currentText()
        output_ui_text = self.controlDialog.comboBox_output_list.currentText()
        self.currSoundCardInput = input_ui_text
        self.currSoundCardOutput = output_ui_text
        # print(input_ui_text, output_ui_text)
        if (not len(input_ui_text) == 0) and (not len(output_ui_text) == 0):
            input, output = self.dialogStrToPaIndex(input_ui_text, output_ui_text)
            sampleratelist = self.supportedSampleRate(input, output)
            self.controlDialog.comboBox_sr_list.clear()
            if sampleratelist:
                self.controlDialog.comboBox_sr_list.addItems(sampleratelist)

        self.onRefreshSampleRateList()

    def onRefreshSampleRateList(self):
        for i in range(0, self.controlDialog.comboBox_sr_list.count()):
            if self.controlDialog.comboBox_sr_list.itemText(i) == str(44100):
                self.controlDialog.comboBox_sr_list.setCurrentIndex(i)
                break
            else:
                self.controlDialog.comboBox_sr_list.setCurrentIndex(0)
        self.controlDialog.comboBox_sr_list.setCurrentIndex(self.window.itemIndex[3])

    def onAutoSaveFile(self):
        if not self.window.actSave.isEnabled():
            return False
        else:
            if not self.window.onDesignRuleCheck():
                self.window.actRuleCheck.setChecked(True)
                self.window.onIsNodeValid(True)
                return False
            else:
                status = self.window.onFileSave(export_xml=True)
                if type(status[0]) is tuple:
                    return status[0]
                if not status[0]:
                    return False
                else:
                    return True

    def onAutoSaveCloseFile(self):
        if not self.window.actSave.isEnabled():
            return True
        else:
            return False

    def onDialogOption(self, button):
        sb = self.designFileSelect.buttonBox.standardButton(button)
        option = self.designFileSelect.comboBox.currentIndex()
        if sb == QDialogButtonBox.Ok and option == 0:
            self.onUploadTarget()
        elif sb == QDialogButtonBox.Ok and option == 1:
            self.onDownloadTarget()
        else:
            pass
            # self.onTerminateSocket("not closed")

    def onWindowsSaveOption(self, button):

        self.onUploadTarget()


    def onUSBOnlyConnect(self, qdialog):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        commResult = self.onEstablishConnet()
        QApplication.restoreOverrideCursor()

        if self.allow_connect_inconsistent_version:
            return False

        if not commResult:
            self.onTerminateSocket("connect timeout")
            return False

        self.dialogStatus = False

        is_export_success = self.window.onExportXML()
        if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
            if hasattr(self.window, 'custom_message'):
                self.onTerminateSocket("invalid design", custom_message=self.window.custom_message)
                return
            self.onTerminateSocket("invalid design")
            return
        if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
            self.onTerminateSocket("config export failed")
            return
        QApplication.restoreOverrideCursor()

        self.designUsbSelect.upload_bar.setValue(100)

        self.dialogStatus = True
        qdialog.close()

    def onUSBUploadDesign(self, qdialog):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        commResult = self.onEstablishConnet()
        QApplication.restoreOverrideCursor()

        if self.allow_connect_inconsistent_version:
            return False

        if not commResult:
            self.onTerminateSocket("connect timeout")
            return False

        self.is_upload = False

        self.dialogStatus = False

        wnd = self.window.findMain()
        file_path = wnd.widget().filename
        if file_path is None:
            flw_file_path = self.window.userPath + '/' + 'default_config.flw'
        else:
            flw_file_path = file_path.rsplit("/", 1)[0] + '/default_config.flw'

        self.allCmdList = None
        self.window.config2cmd(flw_file_path, target=1)
        allCmdList = self.allCmdList

        try:
            status, self.freeSpace = self.mainSocket.hQuery('memFreeSpace/')
            if not status:
                if Debug.DEBUG_COMMON.value:
                    print('status False, socket query error')
                self.onTerminateSocket("forcibly")
                return
            if Debug.DEBUG_COMMON.value: print("mem pool: ", self.freeSpace)
            self.freeSpace = int(self.freeSpace.decode().rstrip('\n\x00'))/1024

            flag = self.onSumAndUpload(allCmdList)
            if not flag:
                self.dialogStatus = False
                qdialog.close()
                return

        except Exception as e:
            self.dialogStatus = False
            self.onTerminateSocket("manually")
            if Debug.DEBUG_COMMON.value: print('hQuery send Error: %s' % e)

        self.window.actQuickUploadFlash.setEnabled(self.window.target == Target.FLOW_EVK_UART.value)
        self.dialogStatus = True
        qdialog.close()

    def onUSBUploadFlash(self, qdialog):
        self.designUsbSelect.convert_bar.setValue(0)
        self.designUsbSelect.verify_bar.setValue(0)
        self.designUsbSelect.upload_bar.setValue(0)

        statement = "Warning: The operation will directly write to the system's FLASH memory. \n" \
                    "It is recommended to first test in 'Upload to RAM' mode to avoid potential \n " \
                    "system instability caused by untested code being written to FLASH, which could complicate debugging. \n" \
                    "If all tests have been completed, you may proceed by clicking 'Ok'. Otherwise, it is advised to cancel this upload. \n"

        reply = QMessageBox.question(self.window, 'Flash Warning',
                                     statement,
                                     QMessageBox.Ok | QMessageBox.Cancel,
                                     QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            return

        usb_client = self.client.createClient()
        res = usb_client.login()
        if not "connected" in res:
            QMessageBox.about(self.window, "Flash Error", res)
            return

        wnd = self.window.findMain()
        file_path = wnd.widget().filename
        if file_path is None:
            flw_file_path = self.window.userPath + '/' + 'default_config.flw'
        else:
            flw_file_path = file_path.rsplit("/", 1)[0] + '/default_config.flw'

        self.allCmdList = None
        self.window.config2cmd(flw_file_path, target=1)
        allCmdList = self.allCmdList

        for i in range(len(allCmdList)):
            timestamp_before = time.time()
            usb_client.cmdSned(allCmdList[i])
            self.designUsbSelect.verify_bar.setValue(i/len(allCmdList) * 100)
            self.designUsbSelect.upload_bar.setValue(i/len(allCmdList) * 100)
            timestamp_after = time.time()
            if Debug.DEBUG_COMMON.value: print(timestamp_after - timestamp_before)
            if timestamp_after - timestamp_before > 0.5:
                usb_client.logout()
                statement = "Please Manual Restart"
                QMessageBox.about(self.window, "Flash Error", statement)
                return

        usb_client.logout()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        time.sleep(5)
        QApplication.restoreOverrideCursor()
        statement = "Success: The code has been successfully uploaded to the system's FLASH. <br>" \
                    "Please verify that the system is functioning correctly. <br>" \
                    "<b>'Please manually restart'</b>"
        QMessageBox.about(self.window, "Flash", statement)
        qdialog.close()

    def onSumAndUpload(self, allCmdList):
        # User use Total Memory
        self.useTotal = 0
        # AO quantity
        aos = 0
        pv = 0
        for i in range(len(allCmdList)):
            if allCmdList[i][0:3] == 'obj':
                aos += 1

        names = []
        for i in range(len(allCmdList)):
            if allCmdList[i][0:3] == 'obj':
                names.append(allCmdList[i].split('/')[1])

        f_csv = []
        with open('MemoryTable.csv') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                for name in names:
                    if name == row[0]:
                        self.useTotal += int(row[1])
                        pv = pv + 1 / aos * 100
                        self.designUsbSelect.verify_bar.setValue(pv)
            f.close()

        pv = 0
        status, self.totalSpace = self.mainSocket.hQuery('memTotal/')
        self.totalSpace = int(self.totalSpace.decode().rstrip('\n\x00'))
        if self.totalSpace > self.useTotal or self.window.target == Target.FLOW_APO.value:
            for i in range(len(allCmdList)):
                try:
                    flag = self.mainSocket.hQuery(allCmdList[i])
                    pv = pv + 1 / len(allCmdList) * 100
                    self.designUsbSelect.upload_bar.setValue(pv)
                    # print(flag[0])
                    # print(flag[1].decode())
                    if not flag[0]:
                        self.dialogStatus = False
                        self.onTerminateSocket("upload fail")
                        return False
                except Exception as e:
                    self.dialogStatus = False
                    self.onTerminateSocket("manually")
                    if Debug.DEBUG_COMMON.value: print('hQuery send Error: %s' % e)
                    return False

        else:
            self.dialogStatus = False
            self.onTerminateSocket("Upload design failed")
            return False

        return True

    def onisUsbUpdate(self, button):
        sb = self.designUsbLoadSelect.buttonBox.standardButton(button)
        if sb == 1024:
            self.is_upload = True
        else:
            self.is_upload = False


    def onTerminateSocket(self, condition, custom_message=None):
        self.window.actQuickUploadFlash.setEnabled(False)
        self.client.connection = False
        if self.window.target != Target.FLOW_APO.value:
            self.hardKill()

        for gui_widget in self.show_window_objects:
            gui_widget.hide()

        if condition == "manually":
            # User has already setChecked... no need to do that -> self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            self.cpuTimer.stop()

        elif condition == "refused":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "No connection could be made because the target machine actively refused it."
            QMessageBox.about(self.window, "Refused", "%s" % statement)

        elif condition == "Creation Failed":
            statement = "Creation failed, Please check the file path and permissions."
            QMessageBox.about(self.window, "Creation Failed", "%s" % statement)

        elif condition == "abort":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = "No connection could be made because of the operation aborted."
            QMessageBox.about(self.window, "Abort", "%s" % statement)

        elif condition == "forcibly":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            self.cpuTimer.stop()
            self.onCheckDSPStatus(False)
            statement = "An existing connection was forcibly closed by the remote host."
            if custom_message:
                statement = custom_message
            QMessageBox.about(self.window, "Forcibly", "%s" % statement)

        elif condition == "Info Error":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            self.cpuTimer.stop()
            self.onCheckDSPStatus(False)
            statement = "Please check that the equipment is complete."
            QMessageBox.about(self.window, "Info Error", "%s" % statement)

        elif condition == "execute timeout":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "Timeout while executing engine."
            QMessageBox.about(self.window, "Execution Fail", "%s" % statement)

        elif condition == "connect timeout":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "Timeout while connecting engine"
            QMessageBox.about(self.window, "Connection Fail", "%s" % statement)

        # elif condition == "version inconsistency":
        #     self.controlDialog.checkBox_dsp.setChecked(False)
        #     statement = "The version of flow studio is inconsistent with that of Flow Engine\n" \
        #                 "Current version :\n" \
        #                 "Flow Studio:  %s\n" \
        #                 "Flow Engine:  %s\n" % (VERSION, self.FlowEngineVersion)
        #     QMessageBox.about(self.window, "Connection Fail", "%s" % statement)

        elif condition == "usb connect timeout":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "Timeout while connecting engine and Please enter the correct VID and PID"
            QMessageBox.about(self.window, "Connection Fail", "%s" % statement)

        elif condition == "invalid design":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "You're trying to upload a invalid design to target."
            if custom_message is not None:
                statement = custom_message
            QMessageBox.about(self.window, "Connection Fail", "%s" % statement)

        elif condition == "config export failed":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "Config Generation Failed"
            QMessageBox.about(self.window, "Config Generation Failed", "%s" % statement)

        elif condition == "SRC Check Fail":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = custom_message
            QMessageBox.about(self.window, "Invalid Sample Rate Conversion", "%s" % statement)

        elif condition == "upload fail":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = "Failed to upload design to remote device."
            QMessageBox.about(self.window, "Upload Fail", "%s" % statement)

        elif condition == "Upload design failed":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = ("Upload design failed.\n"\
                        "Insufficient memory space \n"\
                        "Design memory: %s KBytes\n"\
                        "Total memory:  %s KBytes\n" % (self.useTotal, self.totalSpace))
            QMessageBox.about(self.window, "Upload Fail", "%s" % statement)

        elif condition == "download fail":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = "Failed to download design from remote device."
            QMessageBox.about(self.window, "Download Fail", "%s" % statement)

        elif condition == "open fail":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = "Failed to open design from remote device."
            QMessageBox.about(self.window, "Open Fail", "%s" % statement)

        elif condition == "not closed":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            statement = "Close the current design first."
            QMessageBox.about(self.window, "Open Fail", "%s" % statement)

        elif condition == "Device Not Found":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "The ' %s ' device you have selected does not exist \n" \
                        "And has been removed from the list. \n" \
                        "Please reselect it. \n" % custom_message
            QMessageBox.about(self.window, "Device Not Found", "%s" % statement)

        elif condition == "Output Device Is Empty":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = "Output devices not found. Unable to use audio object: OUT"
            QMessageBox.about(self.window, "Warning", "%s" % statement)

        elif condition == "Input Device Is Empty":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = 'Input devices not found. Unable to use audio object: IN'
            QMessageBox.about(self.window, "Warning", "%s" % statement)

        elif condition == "Sound Device Is Empty":
            self.controlDialog.checkBox_dsp.setChecked(False)
            statement = 'Please note that Flow Studio have not detected any audio input /output on this device.' \
                        ' This implies that there may be no audio processes running, indirectly causing' \
                        ' the Flow studio to not function properly. Recommend checking your device settings again'
            QMessageBox.about(self.window, "Warning", "%s" % statement)

        elif condition == "close connect":
            self.controlDialog.checkBox_dsp.setChecked(False)
            self.mainSocket.logout()
            self.cpuClient.logout()
            self.cpuTimer.stop()
            self.onCheckDSPStatus(False)

        else:
            pass

        for gui_widget in self.show_window_objects:
            gui_widget.show()

        self.window.editmode = False
        self.window.updateEditMenu()

    def tickSocket(self):
        if Debug.DEBUG_COMMON.value:
            print('Client start to Query CPU loading:')
        if self.client.connection:
            status, result = self.cpuClient.hQuery('cpu/')
            if not status:
                if Debug.DEBUG_COMMON.value:
                    print('status False, socket query error')
                self.window.statusBar().clearMessage()
                self.onTerminateSocket("forcibly")
                return
            current_usage_status, current_usage_result = self.cpuClient.hQuery('mem/')
            if not current_usage_status:
                if Debug.DEBUG_COMMON.value:
                    print('current_usage_status False, socket query error')
                self.window.statusBar().clearMessage()
                self.onTerminateSocket("forcibly")
                return
            total_usage_status, total_usage_result = self.cpuClient.hQuery('memTotal/')
            if not total_usage_status:
                if Debug.DEBUG_COMMON.value:
                    print('total_usage_status False, socket query error')
                self.window.statusBar().clearMessage()
                self.onTerminateSocket("forcibly")
                return
            try:
                percentage = "{:.3%}".format(float(result.decode().rstrip('\n\x00')) / 100)
                current = self.MemoryFormat(int(current_usage_result.decode().rstrip('\n\x00'))/1024)
                total = self.MemoryFormat(int(total_usage_result.decode().rstrip('\n\x00'))/1024)
            except Exception as e:
                percentage = "null"
                current = "null"
                total = "null"
            if Debug.DEBUG_COMMON.value:
                print("   _> Status: %r, Loading: %s" % (status, percentage))
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("CPU Loading: %s    Memory usage: %s KB / %s KB" %(percentage, current, total), 3000)
        else:
            if Debug.DEBUG_COMMON.value:
                print('connection False, socket connection error')
            self.window.statusBar().clearMessage()
            if hasattr(self.window, 'right_label'):
                self.window.right_label.setText('')
            self.onTerminateSocket("forcibly")
            return

    def parse_result_of_info_command(self, input_result):
        """
        Parse result of sending info command to engine

        Parameters:
            input_result(tuple): result of sending info command to engine

        Returns:
            return dict, which contains information of status and result
        """
        status, result = input_result
        if status:
            info = result.decode().rstrip('\n\x00').split(',')
            res = {
                'status': status,
                'result': {
                    'Flow Engine Version': info[0],
                    'Sample Rate': info[1],
                    'Frame Size': info[2],
                    'Maximum Input Channel': info[3],
                    'Maximum Output Channel': info[4]
                }
            }
            return res
        return {
            'status': status,
            'result': None
        }

    def MemoryFormat(self, i):
        il = str(i).split('.')
        il[1] = il[1][0:3]
        il[0] = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", str(il[0]))
        il = il[0]+'.'+il[1]
        return il

    def onSelHostname(self, status: bool):
        self.controlDialog.lineEdit_hostname_1.setVisible(status)
        self.controlDialog.label_17.setVisible(status)
        self.controlDialog.lineEdit_hostname_2.setVisible(status)
        self.controlDialog.label_18.setVisible(status)
        self.controlDialog.lineEdit_hostname_3.setVisible(status)
        self.controlDialog.label_19.setVisible(status)
        self.controlDialog.lineEdit_hostname_4.setVisible(status)
        self.controlDialog.label_12.setVisible(status)

    def onSelPort(self, status: bool):
        self.controlDialog.lineEdit_freeports.setVisible(status)
        self.controlDialog.label_13.setVisible(status)

    def onConnectingVisible(self, status: bool):
        self.controlDialog.comboBox_driver_list_5.setVisible(status)
        self.controlDialog.comboBox_driver_list_6.setVisible(not status)

    def onCortexMUSB(self, status: bool):
        self.controlDialog.Vid.setVisible(status)
        self.controlDialog.lineEdit_vid.setVisible(status)
        self.controlDialog.Pid.setVisible(status)
        self.controlDialog.lineEdit_pid.setVisible(status)

    def onCortexMUART(self,status: bool):
        self.controlDialog.Connection.setVisible(status)
        self.controlDialog.Connection_comboBox.setVisible(status)
        self.controlDialog.Port.setVisible(status)
        self.controlDialog.Port_comboBox.setVisible(status)
        self.controlDialog.Rate.setVisible(status)
        self.controlDialog.Rate_comboBox.setVisible(status)
        self.controlDialog.Parity.setVisible(status)
        self.controlDialog.Parity_comboBox.setVisible(status)
        self.controlDialog.Bits.setVisible(status)
        self.controlDialog.Bites_comboBox.setVisible(status)

    def onAirohaUART(self, status: bool):
        self.controlDialog.Port.setVisible(status)
        self.controlDialog.Port_comboBox.setVisible(status)

    def onAirohaUSB(self, status: bool):
        self.controlDialog.Vid.setVisible(status)
        self.controlDialog.lineEdit_vid.setVisible(status)
        self.controlDialog.Pid.setVisible(status)
        self.controlDialog.lineEdit_pid.setVisible(status)

    def onEngine(self, status: bool):
        self.controlDialog.Engine.setVisible(status)
        self.controlDialog.Engine_comboBox.setVisible(status)
        self.IntiUartData()

    def onSelUsername(self, status: bool):
        self.controlDialog.lineEdit_username.setVisible(status)
        self.controlDialog.label_14.setVisible(status)

    def onSelPassword(self, status: bool):
        self.controlDialog.lineEdit_password.setVisible(status)
        self.controlDialog.label_15.setVisible(status)

    def onSelPath(self, status: bool):
        self.controlDialog.lineEdit_path.setVisible(status)
        self.controlDialog.label_16.setVisible(status)

    def onSelAudioInterface(self, status: bool):
        if Debug.DEBUG_COMMON.value: print('--onSelAudioInterface---')
        self.controlDialog.comboBox_driver_list.setVisible(status)
        self.controlDialog.label_21.setVisible(status)

        self.controlDialog.comboBox_input_list.setVisible(status)
        self.controlDialog.label_22.setVisible(status)

        self.controlDialog.comboBox_output_list.setVisible(status)
        self.controlDialog.label_23.setVisible(status)

        self.controlDialog.comboBox_sr_list.setVisible(status)
        self.controlDialog.label_24.setVisible(status)

        self.controlDialog.pushButton_update.setVisible(status)

    def onUploadTarget(self):
        self.dialogStatus = False
        QApplication.setOverrideCursor(Qt.WaitCursor)
        commResult = self.onEstablishConnet()
        QApplication.restoreOverrideCursor()

        if self.allow_connect_inconsistent_version:
            return False

        if not commResult:
            self.onTerminateSocket("connect timeout")
            return False

        is_export_success = self.window.onExportXML()
        if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
            if hasattr(self.window, 'custom_message'):
                self.onTerminateSocket("invalid design", custom_message=self.window.custom_message)
                return
            self.onTerminateSocket("invalid design")
            return
        if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
            self.onTerminateSocket("config export failed")
            return

        # find the correspond directory for the project file
        fname = self.window.mdiArea.subWindowList()[0].widget().filename
        suffix = os.path.splitext(fname)[1]
        if fname.endswith(suffix):
            target_path = os.path.split(fname)[0]
            files = os.listdir(target_path)
            dst = self.window.path
        else:
            return

        # copy files to the dst
        if self.window.temp_folder_path is not None:
            srcs = [os.path.join(self.window.project_folder_path, self.window.project_file_name()),
                    os.path.join(self.window.temp_folder_path, "default_config.flw")]
        else:
            srcs = [self.window.userPath + "/default_config.flw"]
        for i in range(0, len(srcs)):
            src = srcs[i]
            dst = self.window.path
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.window.target == Target.QCS.value:
                res1 = adbGetUpload(dst, src)
            if self.window.target in [Target.FLOW_APO.value, Target.RASP.value]:
                if Debug.DEBUG_COMMON.value: print("APO config updating...")
                res1 = windowsCopyConfigFile(src)
                self.onTerminateSocket("manually") # we ternimate the socket after file updated
            elif self.window.password != "":
                if self.window.target == Target.RASP.value:
                    return
                res1 = sshGetUploadHasPassword(self.window.username, self.window.password, self.window.hostname, dst, src)
            else:
                res1 = sshGetUpload(self.window.username, self.window.hostname, dst, src)
            QApplication.restoreOverrideCursor()
            if not res1:
                self.onTerminateSocket("upload fail")
                return
        if Debug.DEBUG_COMMON.value: print('Upload Process: upload %s to remote device' % src)



        # mute audio in FLOW
        QApplication.setOverrideCursor(Qt.WaitCursor)
        status1, res1 = self.mainSocket.hQuery("setRoot/muteAudio/1/")
        QApplication.restoreOverrideCursor()
        if Debug.DEBUG_COMMON.value:
            print(status1)
            print(res1)
        if Debug.DEBUG_COMMON.value: print('Upload Process: setRoot/muteAudio/1/')
        # lock audio in FLOW
        if status1:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            status2, res2 = self.mainSocket.hQuery("setRoot/lockAudio/1/")
            QApplication.restoreOverrideCursor()
        else:
            return
        if Debug.DEBUG_COMMON.value: print('Upload Process: setRoot/lockAudio/1/')
        # reset the config file in FLOW
        if status2:
            self.mainSocket.client.settimeout(10)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            status3, res3 = self.mainSocket.hQuery("setRoot/ConfigFile/1/")
            QApplication.restoreOverrideCursor()
            self.mainSocket.client.settimeout(1)
        else:
            return
        if Debug.DEBUG_COMMON.value: print('Upload Process: setRoot/ConfigFile/1/')

        # unlock audio in FLOW
        if status3:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            status4, res4 = self.mainSocket.hQuery("setRoot/lockAudio/0/")
            QApplication.restoreOverrideCursor()
        else:
            return
        if Debug.DEBUG_COMMON.value: print('Upload Process: setRoot/lockAudio/0/')

        # unmute audio in FLOW
        if status4:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            status5, res5 = self.mainSocket.hQuery("setRoot/muteAudio/0/")
            QApplication.restoreOverrideCursor()
        else:
            return
        if Debug.DEBUG_COMMON.value: print('Upload Process: setRoot/muteAudio/0/')

        # final condition expression will return a flag :)
        if status5:
            self.dialogStatus = True
        else:
            return

    def onDownloadTarget(self):
        self.dialogStatus = False
        QApplication.setOverrideCursor(Qt.WaitCursor)
        commResult = self.onEstablishConnet()
        QApplication.restoreOverrideCursor()

        if self.allow_connect_inconsistent_version:
            return False

        if not commResult:
            self.onTerminateSocket("connect timeout")
            return False
        # is design invalid?
        isClosed = self.onAutoSaveCloseFile()

        if not isClosed:
            closeResult = self.window.findMain().close()
            if Debug.DEBUG_COMMON.value: print(closeResult)
            if closeResult is False:
                self.onTerminateSocket("not closed")
                return
        if Debug.DEBUG_COMMON.value: print('Download Process: window closed')

        fdir = QFileDialog.getExistingDirectory(self.window, 'Choose a directory to place project', self.window.getFileDialogDirectory())

        src = self.window.path
        dst = fdir

        # download the folder to dst from remote src
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.window.target == Target.QCS.value:
            res1 = adbGetDownload(src, dst)
        elif self.window.target in [Target.FLOW_APO.value, Target.RASP.value]:
            if Debug.DEBUG_COMMON.value: print("FLOW APO connecting...")
            res1 = True
        elif self.window.password != "":
            if self.window.target == Target.RASP.value:
                return
            res1 = sshGetDownloadHasPassword(self.window.username,self.window.password, self.window.hostname, src, dst)
        else:
            res1 = sshGetDownload(self.window.username, self.window.hostname, src, dst)
        QApplication.restoreOverrideCursor()
        if not res1:
            self.onTerminateSocket("download fail")
            return
        if Debug.DEBUG_COMMON.value: print('Download Process: download .flw to remote device')

        self.window.unCompressZIPFile(fdir+"/default.proj",fdir+"/default")

        self.window.temp_folder_path= fdir + "/default"
        try:
            self.window.onFileOpen(hidden_dir=self.window.temp_folder_path)
        except Exception:
            self.onTerminateSocket("open fail")
            return

        self.dialogStatus = True
        if Debug.DEBUG_COMMON.value: print('Download Process: open .json config file')

    def onStopFlowEngine(self):
        if Debug.DEBUG_COMMON.value: print("stop")

    def onExecuteFlowEngine(self):
        input_ui_text = self.controlDialog.comboBox_input_list.currentText()
        output_ui_text = self.controlDialog.comboBox_output_list.currentText()

        if Debug.DEBUG_COMMON.value: print('------->FLOW ENGINE:', input_ui_text, output_ui_text)
        inIdx, outIdx = self.dialogStrToPaIndex(input_ui_text, output_ui_text)
        ins, outs = self.getMaxChannelCount(inIdx, outIdx)
        # if input[0] == "": input[0] = "-1"
        # if output[0] == "": output[0] = "-1"

        if self.controlDialog.comboBox_sr_list.currentText():
            samplerate = self.controlDialog.comboBox_sr_list.currentText()
        else:
            return False

        fname = self.window.getCurrentNodeEditorWidget().filename
        if self.window.temp_folder_path is not None:
            fconfig = os.path.split(fname)[0] + '/' + 'default_config.flw'
        else:
            fconfig = self.window.userPath + '/' + 'default_config.flw'

        # When starting with template, supplement the file path
        current_path = os.getcwd()
        if not os.path.isabs(fconfig):
            fconfig = current_path + fconfig

        index = current_path.find('flowstudio')

        if platform.system() == 'Windows':
            lib_path = current_path[:index] + 'bin/FlowEngineDLL.dll'
        elif platform.system() == 'Linux':
            lib_path = current_path[:index] + "bin/libFlowEngineLib.so"


        if Debug.DEBUG_COMMON.value: print('lib path:' + lib_path)

        # self.FLOW_Engine = FLOW_Engine_Interface(lib_path)
        # self.instance = self.FLOW_Engine.create('GlobalDsp', fconfig, ins, outs, samplerate, 32)
        # self.FLOW_Engine.prepare(self.instance, float(samplerate), 32)
        # self.FLOW_Engine.createTcpServer(self.instance, 54011)
        # self.worker = AudioThread(self.FLOW_Engine, self.instance,
        #                    int(inIdx), int(outIdx), float(samplerate), ins, outs, 32)
        # print(inIdx, outIdx)
        # print(ins, outs)
        # self.worker.start()
        # flag = True
        #
        # self.startPaStream(self.FLOW_Engine, self.instance,
        #                    int(inIdx), int(outIdx), float(samplerate), ins, outs, 32)
        folder_path = os.path.dirname(self.pc_engine_path)
        engine_file_name = os.path.basename(self.pc_engine_path)
        # cmd = [engine_file_name, "1", fconfig, inIdx, outIdx, samplerate, str(float(samplerate)*0.001), str(ins), str(outs)]
        cmd = [engine_file_name, "1", fconfig, inIdx, outIdx, samplerate, str(32), str(ins),
               str(outs)]
        if Debug.DEBUG_COMMON.value: print("switch directory to: %s" % folder_path)
        if Debug.DEBUG_COMMON.value: print("execute cmd: %s" % cmd)
        self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, cwd=folder_path)
        if Debug.DEBUG_COMMON.value: print("display logs from FLOW Engine:")

        timer = Timer(15, self.hardKill)
        flag = False
        #
        try:
            timer.start()
            while True:

                buff = self.process.stdout.readline()
                if Debug.DEBUG_COMMON.value: print("   _> ", buff.rstrip().decode(errors='ignore'))
                if self.is_debug_mode:
                    msg = buff.rstrip().decode(errors='ignore')
                    self.window.log_window.append_log(msg)
                    self.window.logger.debug(msg)
                if buff == b'FLOW Studio check point: socket created succeed\r\n':
                    flag = True
                    if Debug.DEBUG_COMMON.value:
                        print("\n")
                        print("============================================")
                        print("got key word from FLOW Engine, status break!")
                        print("============================================\n")
                    break
                elif buff == b'FLOW Studio check point: socket created failed\r\n':
                    if Debug.DEBUG_COMMON.value:
                        print("\n")
                        print("============================================")
                        print("Invalid message from console: %s, status break" % buff.rstrip().decode(errors='ignore'))
                        print("============================================\n")
                    break
                elif buff == b'FLOW Studio check point: socket init failed\r\n':
                    if Debug.DEBUG_COMMON.value:
                        print("\n")
                        print("============================================")
                        print("Invalid message from console: %s, status break" % buff.rstrip().decode(errors='ignore'))
                        print("============================================\n")
                    break
                elif buff == b'FLOW Studio check point: socket server stopped\r\n':
                    if Debug.DEBUG_COMMON.value:
                        print("\n")
                        print("============================================")
                        print("Invalid message from console: %s, status break" % buff.rstrip().decode(errors='ignore'))
                        print("============================================\n")
                    break
                elif buff == b'FLOW Studio check point: invalid input file\r\n':
                    if Debug.DEBUG_COMMON.value:
                        print("\n")
                        print("============================================")
                        print("Invalid message from console: %s, status break" % buff.rstrip().decode(errors='ignore'))
                        print("============================================\n")
                    break
        finally:
            if not self.is_debug_mode:
                self.process.stdout.close()
            else:
                self.debug_thread = DebugThread(cmd, folder_path, self.process, self.window)
                try:
                    self.debug_thread.message_received.disconnect(self.window.log_window.append_log)
                except TypeError:
                    # If the signal-slot connection does not exist, ignore the error
                    pass
                self.debug_thread.message_received.connect(self.window.log_window.append_log)
                self.debug_thread.start()
            timer.cancel()

        return flag

    def hardKill(self):
        engine_file_name = os.path.basename(self.pc_engine_path)
        res = isEngineAlive(engine_file_name)
        if Debug.DEBUG_COMMON.value: print("hardkill trigger")
        if not res == b'':
            killEngine(engine_file_name)

    def softKill(self):
        engine_file_name = os.path.basename(self.pc_engine_path)
        res = isEngineAlive(engine_file_name)
        if not res == b'':
            self.mainSocket.hQuery("setRoot/muteAudio/1/")
            self.mainSocket.hQuery("setRoot/lockAudio/1/")
            killEngine(engine_file_name)

    def onEstablishConnet(self, ignore_message_box=False):
        substring = "connected"
        self.allow_connect_inconsistent_version = False
        main_result = False
        for i in range(2):
            if Debug.DEBUG_COMMON.value: print("   _> start to bring up Main socket, %d time connection." % i)
            self.mainSocket = self.client.createClient()
            # self.mainSocket.client.settimeout(1)
            res = self.mainSocket.login()
            if Debug.DEBUG_COMMON.value: print("Get result from Main socket:: %s" % res)
            if substring in res:
                main_result = True
                self.client.__setattr__('mainSocket', self.mainSocket)
                break

        cpu_result = False
        if main_result == True:
            for i in range(2):
                if Debug.DEBUG_COMMON.value: print("   _> start to bring up CPU socket, %d time connection." % i)
                self.cpuClient = self.client.createClient()
                # self.cpuClient.client.settimeout(3)
                res = self.cpuClient.login()
                if Debug.DEBUG_COMMON.value: print("Get result from CPU socket:: %s" % res)
                if substring in res:
                    cpu_result = True
                    self.client.__setattr__('cpuClient', self.cpuClient)
                    break
            try:
                info_result = self.parse_result_of_info_command(self.cpuClient.hQuery('info/'))
                if not info_result['status']:
                    if self.client.target == Target.FLOW_EVK_USB.value:
                        statement = "Please Manual restart \n Reflash!"
                        QMessageBox.about(self.window, "Flash Error", statement)
                    self.onTerminateSocket("Info Error")
                    return False
                if Debug.DEBUG_COMMON.value:
                    print(VERSION, 'Flow Studio')
                    print(info_result['result']['Flow Engine Version'], 'Flow Engine')
                self.FlowEngineVersion = info_result['result']['Flow Engine Version']
                s_version = VERSION.split('.')[0]+'.'+VERSION.split('.')[1]
                e_version = info_result['result']['Flow Engine Version'].split('.')[0]+'.'+info_result['result']['Flow Engine Version'].split('.')[1]
                if main_result and cpu_result and s_version == e_version:
                    if Debug.DEBUG_COMMON.value:
                        print('Main and CPU Socket successfully connected.')
                    # Track user action "Connect To Engine (PC)"
                    if self.window.target == Target.PC.value:
                        self.tracker = TrackManager()
                        self.tracker.track_user_action(action=6, license=self.window.license_mechanism)
                    return True
                else:
                    self.mainSocket.hQuery("setRoot/lockAudio/1/")
                    QApplication.restoreOverrideCursor()
                    if not ignore_message_box:
                        statement = "Your Flow Studio version is %s, \n" \
                                    "but you are attempting to use it with Flow Engine version %s,\n" \
                                    "which may result in unexpected behavior. \n" \
                                    "Do you want to proceed with the connection? \n" % (
                                        VERSION, self.FlowEngineVersion)
                        reply = QMessageBox.question(self.window, 'Connection Warn',
                                                     statement,
                                                     QMessageBox.Ok | QMessageBox.Cancel,
                                                     QMessageBox.Cancel)
                        if reply == QMessageBox.Cancel:
                            QApplication.setOverrideCursor(Qt.WaitCursor)
                            self.onTerminateSocket("close connect")
                            self.allow_connect_inconsistent_version = True
                            return False
                    self.mainSocket.hQuery("setRoot/lockAudio/0/")
                    # Track user action "Connect To Engine (PC)"
                    if self.window.target == Target.PC.value:
                        self.tracker = TrackManager()
                        self.tracker.track_user_action(action=6, license=self.window.license_mechanism)
                    return True
            except Exception as e:
                if Debug.DEBUG_COMMON.value: print(e)
                self.onTerminateSocket("Info Error")
                return False

        else:
            return False

    def onSocketConnection(self, connect, ignore_message_box=False):
        """
        Connect to the target or disconnect from the target, depending on the parameter passed.

        Parameters:
            connect(boolean): True means connecting to the target,
                              False means disconnecting from the target.

        Returns:
            Return True if the processing is successful, and False if the processing is not successful.
        """
        self.window.onProfileSetup()
        timeout = 3000

        if self.client.connection and not connect and self.window.target == Target.PC.value:
            # Disconnect from PC
            if self.is_debug_mode:
                self.window.log_window.close()
                for handler in self.window.logger.handlers[:]:
                    self.window.logger.removeHandler(handler)
                self.debug_thread.stop()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.onTerminateSocket("manually")
            QApplication.restoreOverrideCursor()
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("Disconnect from FLOW Engine", 3000)

        elif self.client.connection and not connect and self.window.target in [Target.FLOW_APO.value, Target.RASP.value]:
            # Disconnect from Flow APO
            if Debug.DEBUG_COMMON.value: print('Flow APO disconnecting...')
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.onTerminateSocket("manually")
            QApplication.restoreOverrideCursor()
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("Disconnect from FLOW APO", 3000)

        elif self.client.connection and not connect and self.window.target != Target.PC.value:
            # Disconnect from Remote Device
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.onTerminateSocket("manually")
            QApplication.restoreOverrideCursor()
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("Disconnect from remote device", 3000)

        elif not self.client.connection and connect and self.window.target in [Target.FLOW_APO.value, Target.RASP.value]:
            if Debug.DEBUG_COMMON.value: print('Flow APO socket connecting...')
            # -------------------- Connect to Flow APO ---------------------------
            self.client.target = self.window.target
            self.client.addr = self.window.hostname
            self.client.port = self.window.port

            is_export_success = self.window.onExportXML()
            if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
                if hasattr(self.window, 'custom_message') and self.window.custom_message != '':
                    self.onTerminateSocket("invalid design", custom_message=self.window.custom_message)
                    return False
                self.onTerminateSocket("invalid design")
                return False

            if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
                self.onTerminateSocket("config export failed")
                return False

            # QApplication.setOverrideCursor(Qt.WaitCursor)
            # commResult = self.onEstablishConnet()
            # QApplication.restoreOverrideCursor()
            # if Debug.DEBUG_COMMON.value: print('is socket connected? %r' % commResult)
            #
            # if self.allow_connect_inconsistent_version:
            #     return False
            #
            # if not commResult:
            #     self.onTerminateSocket("connect timeout")
            #     return False

            self.dialogStatus = False

            qdialog = QDialog(self.window)
            self.designUsbSelect = Ui_dialog_remote_control_selection()
            self.designUsbSelect.setupUi(qdialog)
            self.designUsbSelect.save.setEnabled(False)
            self.designUsbSelect.save.setStyleSheet("""
                                                    QPushButton {
                                                        background-color: darkGray;
                                                        color: black;
                                                    }
                                                    """)
            self.designUsbSelect.only.clicked.connect(lambda: self.onUSBOnlyConnect(qdialog))
            self.designUsbSelect.upload.clicked.connect(lambda: self.onUSBUploadDesign(qdialog))
            self.designUsbSelect.save.clicked.connect(lambda: self.onWindowsSaveOption(qdialog))
            qdialog.exec()

            if self.dialogStatus == True:
                # set the connection into True before the socket ticking
                self.client.connection = True
                self.cpuTimer.start(timeout)
                self.window.statusBar().clearMessage()
                self.window.statusBar().showMessage("Remote Device Connected", 3000)
            else:
                self.controlDialog.checkBox_dsp.setChecked(False)
                return

            # set the connection into True before the socket ticking
            self.client.connection = True
            self.cpuTimer.start(timeout)
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("FLOW Engine Connected", 3000)

        elif not self.client.connection and connect and self.window.target == Target.PC.value:
            from flowstudio.flow_window import LogWindow
            if self.is_debug_mode:
                self.window.log_window = LogWindow(self.window)
                self.window.logger = setup_logger(log_dir=os.path.dirname(self.pc_engine_path))
            # Connect to PC
            if Debug.DEBUG_COMMON.value: print('PC connecting...')

            # Check Sound Device
            is_check_device = self.window.onCheckSoundDevice()
            if not is_check_device:
                return False

            self.client.target = self.window.target
            self.client.addr = "127.0.0.1"
            self.client.port = 54010

            is_export_success = self.window.onExportXML()

            if type(self.window.custom_message) is list:
                statement = 'The SRC is not valid, so the following AO cannot be used.'
                for ao in self.window.custom_message:
                    statement += '\n   ● ' + ao
                statement += '\nPlease verify that the system sample rate and SRC settings are correct.'
                statement += f'\nCurrent system sample rate : {self.controlDialog.comboBox_sr_list.currentText()}Hz'
                self.onTerminateSocket('SRC Check Fail', statement)
                return False

            if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
                if hasattr(self.window, 'custom_message'):
                    self.onTerminateSocket("invalid design", custom_message=self.window.custom_message)
                    return False
                self.onTerminateSocket("invalid design")
                return False

            if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
                self.onTerminateSocket("config export failed")
                return False

            if Debug.DEBUG_COMMON.value:
                print('is Config file export: %r' % is_export_success)

            QApplication.setOverrideCursor(Qt.WaitCursor)
            execResult = self.onExecuteFlowEngine()
            QApplication.restoreOverrideCursor()
            if Debug.DEBUG_COMMON.value: print('FLOW Engine init successfully? %r' % execResult)

            if not execResult:
                self.onTerminateSocket("execute timeout")
                return False

            QApplication.setOverrideCursor(Qt.WaitCursor)
            commResult = self.onEstablishConnet(ignore_message_box)
            QApplication.restoreOverrideCursor()
            if Debug.DEBUG_COMMON.value: print('is socket connected? %r' % commResult)

            if self.allow_connect_inconsistent_version:
                return False

            if not commResult:
                self.onTerminateSocket("connect timeout")
                return False

            # set the connection into True before the socket ticking
            self.client.connection = True
            self.cpuTimer.start(timeout)
            self.window.statusBar().clearMessage()
            self.window.statusBar().showMessage("FLOW Engine Connected", 3000)

        elif not self.client.connection and connect and self.window.target != Target.PC.value:
            # Connect to Remote Device
            if Debug.DEBUG_COMMON.value: print('Remote connecting...')
            self.client.target = self.window.target
            if self.window.target == Target.CORTEX_M_USB.value or \
                    self.window.target == Target.GX8008C_USB.value:
                self.client.vid = self.window.vid
                self.client.pid = self.window.pid
                if self.window.target == Target.GX8008C_USB.value:
                    self.client.engine = self.engine_list[self.window.engine]
                # connect UART
                if self.controlDialog.comboBox_driver_list_5.currentIndex() == 1:
                    self.client.con = self.connect_list[self.window.connection]
                    self.client.com = self.port_list[self.window.comport]
                    self.client.rate = self.rate_list[self.window.rate]
                    self.client.parity = self.parity_list[self.window.parity]
                    self.client.bits = self.bits_list[self.window.bites]
                    self.client.target = Target.CORTEX_M_UART.value
            if self.window.target == Target.FLOW_EVK_UART.value:
                self.client.con = self.connect_list[self.window.connection]
                self.client.com = self.port_list[self.window.comport]
                self.client.rate = self.rate_list[self.window.rate]
                self.client.parity = self.parity_list[self.window.parity]
                self.client.bits = self.bits_list[self.window.bites]
                # region USB Interface
                if self.controlDialog.comboBox_driver_list_5.currentIndex() == 0:
                    self.client.vid = self.window.vid
                    self.client.pid = self.window.pid
                    self.client.target = Target.FLOW_EVK_USB.value
                # endregion
            # connect AIROHA
            elif self.window.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
                self.client.engine = self.engine_list[self.window.engine]
                if self.controlDialog.comboBox_driver_list_6.currentIndex() == 1:
                    self.client.vid = self.window.vid
                    self.client.pid = self.window.pid
                    self.client.target = Target.AIROHA_USB.value
                else:
                    self.client.com = self.port_list[self.window.comport]
            # connect S7
            elif self.window.target == Target.S7.value:
                self.client.transports = self.controlDialog.transports_list.currentText()
                self.client.header = self.controlDialog.header_lineEdit.text()
                self.client.s7_rate = self.controlDialog.s7_rate_list.currentText()
            else:
                self.client.addr = self.window.hostname
                self.client.port = self.window.port

            self.client.cancelClient()

            self.dialogStatus = False
            if self.window.target == Target.CORTEX_M_USB.value or \
                    self.window.target == Target.AIROHA_AB1585_UART.value or \
                    self.window.target == Target.AIROHA_AB1565_UART.value or \
                    self.window.target == Target.FLOW_EVK_UART.value or \
                    self.window.target == Target.GX8008C_USB.value or \
                    self.window.target == Target.S7.value:
                qdialog = QDialog(self.window)
                self.designUsbSelect = Ui_usb_runtime_select_Dialog()
                self.designUsbSelect.setupUi(qdialog)
                self.designUsbSelect.only.clicked.connect(lambda: self.onUSBOnlyConnect(qdialog))
                self.designUsbSelect.upload.clicked.connect(lambda: self.onUSBUploadDesign(qdialog))
                self.designUsbSelect.flash.setVisible(False)
                qdialog.exec()
            else:
                qdialog = QDialog(self.window)
                self.designFileSelect = Ui_runtime_select_Dialog()
                self.designFileSelect.setupUi(qdialog)
                self.designFileSelect.buttonBox.clicked.connect(self.onDialogOption)
                qdialog.exec()

            if self.dialogStatus == True:
                # set the connection into True before the socket ticking
                self.client.connection = True
                self.cpuTimer.start(timeout)
                self.window.statusBar().clearMessage()
                self.window.statusBar().showMessage("Remote Device Connected", 3000)
            else:
                self.controlDialog.checkBox_dsp.setChecked(False)
                return False

        else:
            pass

        if not self.process_target_info_on_status_bar(connect):
            return False
        self.onCheckDSPStatus(connect)
        self.set_toggle_display_of_all_ao(False)
        if connect and self.window.target == Target.PC.value and self.is_debug_mode:
            self.window.log_window.show()
        if connect and self.window.target == Target.PC.value:
            self.controlDialog.debug_mode_check_box.setDisabled(True)
        if not connect and self.window.target == Target.PC.value:
            self.controlDialog.debug_mode_check_box.setEnabled(True)
        return True

    def process_target_info_on_status_bar(self, connect):
        """
            Display target information on the status bar when connecting to the target
            (if the number of inputs or outputs audio objects exceeds the maximum channel capacity,
            the system will stop connecting),
            and clear the target information on the status bar when disconnecting from the target.

            Parameters:
                connect(boolean): True means connecting to the target,
                                  False means disconnecting from the target.

            Returns:
                Return True if the processing is successful, and False if the processing is not successful.
        """
        if connect:
            # region Display selected platform, maximum input/output channel and sample rate on status bar
            info_result = self.parse_result_of_info_command(self.cpuClient.hQuery('info/'))
            if not info_result['status']:
                return False
            main_window = self.window.findMain()
            nodes_in_main = main_window.widget().scene.nodes
            num_in_ao_in_main = 0
            num_in_ao_out_main = 0
            for node in nodes_in_main:
                if node.op_code == OP_NODE_ADC:
                    num_in_ao_in_main += 1
                elif node.op_code == OP_NODE_DAC:
                    num_in_ao_out_main += 1
            if info_result['status']:
                maximum_input_channel = int(info_result["result"]["Maximum Input Channel"])
                maximum_output_channel = int(info_result["result"]["Maximum Output Channel"])
                error_message = ''
                if num_in_ao_in_main > maximum_input_channel:
                    error_message += f'● Number of IN AOs exceeds maximum input channel,\n number of IN AOs:{num_in_ao_in_main}, maximum input channel:{maximum_input_channel}\n'
                if num_in_ao_out_main > maximum_output_channel:
                    error_message += f'● Number of OUT AOs exceeds maximum output channel,\n number of OUT AOs:{num_in_ao_out_main}, maximum output channel:{maximum_output_channel}\n'
                if error_message != '':
                    error_message = 'System fails to connect due to following reasons:\n' + error_message
                    self.onTerminateSocket("forcibly", custom_message=error_message)
                    return False
            if not hasattr(self.window, 'right_label'):
                self.window.right_label = QLabel('', self.window)
                self.window.right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.window.right_label.setStyleSheet('font-family: Calibri; font-size: 11pt;')
                self.window.statusBar().addPermanentWidget(self.window.right_label)
            platform_name = self.controlDialog.comboBox_targetdevice.currentText()
            if info_result['status']:
                label_text = f'Target:{platform_name}, ' \
                             f'In Ch:{info_result["result"]["Maximum Input Channel"]}, ' \
                             f'Out Ch:{info_result["result"]["Maximum Output Channel"]}, ' \
                             f'SR:{info_result["result"]["Sample Rate"]}  '
                self.window.right_label.setText(label_text)
            else:
                self.window.right_label.setText('')
            # endregion
        else:
            if hasattr(self.window, 'right_label'):
                self.window.right_label.setText('')
        return True

    def set_toggle_display_of_all_ao(self, value):
        windows = self.window.mdiArea.subWindowList()
        for window in windows:
            for i in range(len(window.widget().scene.nodes)):
                node = window.widget().scene.nodes[i]
                if hasattr(node, 'widget'):
                    toggle_method = getattr(node.widget, 'toggle', None)
                    if toggle_method:
                        if callable(toggle_method):
                            node.widget.display.toggle.setChecked(value)

    def handle_debug_mode_check_box(self, checked):
        self.is_debug_mode = checked


class DebugThread(QThread):
    message_received = pyqtSignal(str)
    def __init__(self, cmd, folder_path, process, flow_window):
        super().__init__()
        self.cmd = cmd
        self.folder_path = folder_path
        self.process = process
        self.flow_window = flow_window
        self.is_running = True

    def run(self):
        while self.is_running:
            buff = self.process.stdout.readline()
            msg = buff.rstrip().decode(errors='ignore')
            self.message_received.emit(msg)
            self.flow_window.logger.debug(msg)

    def stop(self):
        self.is_running = False
