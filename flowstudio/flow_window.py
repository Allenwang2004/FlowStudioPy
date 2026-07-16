import ast
import copy
# from idlelib.idle_test.test_configdialog import dialog
import ctypes
import datetime
import filecmp
import json
import math
import operator
import os.path
import pickle
import re
import shutil
import time
import zipfile
from binascii import b2a_hex
from collections import defaultdict

from flowstudio.flow_ai_web_manager import FlowAIWebManager
from flowstudio.functions.CallbackHandle import LocalServer

from flowstudio.functions.track_worker import TrackManager
from template.control_dump import Ui_dump_dialog
from template.more_project import Ui_more_project
from template.usb_runtime_select import Ui_usb_runtime_select_Dialog
from template.user_pane import Ui_user_pane

ctypes.CDLL('..\\bin\\hidapi.dll')

import win32api
import win32con
from Crypto.Cipher import AES
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from flowstudio.flow_build_manager import VERSION
from flowstudio.flow_node_property import Node_Property_Widget
from nodeeditor.node_editor_window import NodeEditorWindow
from nodeeditor.utils import dumpException, pp
from flowstudio.flow_sub_window import FLOW_Sub_Window
from flowstudio.flow_sub_group import FLOW_Sub_Group
from flowstudio.flow_window_connection import FLOW_Window_Connection
from flowstudio.flow_window_analysis import FLOW_Window_Analysis
from flowstudio.flow_conf import *
from template.export_command import Ui_export_command
from utilities.utils import *
from flowstudio.flow_node_base import FLOW_Node, FLOW_GUI
from flowstudio.nodes.SUBPATCH import FLOW_Node_SUBPATCH
from template.project_title_edit import *
import xml.etree.ElementTree as ET
from template.decrypt_subpatch import Ui_decryptSubpatchDialog
from template.input_text_generate_flow_dialog import Ui_InputTextGenerateFlowDialog
from template.signal_flow_diff import Ui_Form as SignalFlowDiffUi
from template.custom_ao_builder import Ui_Dialog as CustomAOBuilderUI
from flowstudio.functions.aes_operation import AESOperation
# images for the dark skin
# import implementation.flowstudio.qss.nodeeditor_dark_resouirces
from flowstudio.functions.conversion import Conversion
import base64
import sounddevice as sd
from flowstudio.flow_audio_manager import standard_sample_rates
import requests
import pandas as pd
import tempfile
from flowstudio.setting.error_codes import *
from open_architecture.ConfigFileValidator import ConfigFileValidator
from open_architecture.CustomAOManager import CustomAOManager
from flowstudio.flow_scene import FLOW_Scene
from flowstudio.flow_conf_list import AUDIO_OBJECT_TEMP
from collections import OrderedDict
from nodeeditor.node_socket import *
from control.flow_widget_combo_box import ClickOnlyComboBox
from distutils.dir_util import copy_tree

from flowstudio.flow_ai_manager import FlowAIDialogManager

if os.name == "nt":
    import ctypes

    myappid = "mycompany.myproduct.subproduct.version"  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    "elif Darwin..."
    "elif Linux..."

DEBUG = False
DEBUG_Eval = False
DEBUG_Linked_list = False

timer = QTimer()


class scanAudioDeviceThread(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        target_path = smartCWD()

        cmd = ["AudioInterface.exe"]
        if Debug.DEBUG_Low_Level.value: print(target_path)
        if Debug.DEBUG_Low_Level.value: print("scanning...")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, cwd=target_path)
        res = process.stdout.read()
        if res.decode(errors="ignore").rstrip().rsplit('\n')[-1] == "Processed Finished":
            self.hasPaSupported = True
        else:
            self.hasPaSupported = False
        if Debug.DEBUG_Low_Level.value: print("scanning...done")
        self.finished.emit()
        QApplication.restoreOverrideCursor()

class SettingQDialog(QDialog):
    def closeEvent(self, event):
        super().close()
        timer.stop()

class DumpQDialog(QDialog):

    closeEventSignal = pyqtSignal(str)
    is_confirm = False

    def closeEvent(self, event):
        if self.is_confirm:
            reply = QMessageBox.question(self, 'Confirm',
                                         'Are you sure to close the window? Closing the window will stop the dump process.',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.closeEventSignal.emit("")
            else:
                event.ignore()


class FLOW_Window(NodeEditorWindow):
    _editmode = False
    _dspstatus = False

    target = Target.PC.value
    profile = ""
    hostname = ""
    port = ""
    username = ""
    password = ""
    path = ""
    vid = ""
    pid = ""
    connection = 0
    comport = 0
    rate = 0
    parity = 0
    bites = 0
    engine = 0
    itemIndex = [0, 0, 0, standard_sample_rates.index('44100')]
    encrypt_key = '7235967868936179'
    encrypt_mode = AES.MODE_CBC
    encrypt_iv = '5183946738049788'
    # AO dump, time and directory index
    dump_dialog_index = [0, os.path.expanduser("~\\Documents")]
    # Ao dump title:id list
    dump_ao_title_id_list = []
    # AO dump title list
    dump_ao_tile_list = []
    # Ao dump checked checkbox list
    dump_ao_checked_checkbox_list = []
    # Ao dump name list
    dump_ao_name_list = []

    all_window_objects = FLOW_Window_Connection.show_window_objects

    Node_Property_Widget_Class = Node_Property_Widget

    # User Pane is Open
    user_pane_open = False

    def __init__(self):
        self.exist_custom_aos = False
        super().__init__()

        import os
        os.environ["PATH"] += os.pathsep + 'C:\Windows\System32;'

        cmd = 'path'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        res = process.stdout.read()
        if Debug.DEBUG_Low_Level.value: print(res)

        # if not self.searchAudioInterfaceFile():
        #     self.scanAudioInterface()
        self.initDialog()
        self.hasPaSupported = False
        self.temp_folder_path = None
        self.project_folder_path = None
        self.project_name = None
        self.license_mechanism = None
        self.sub_patchs = []
        self.signal_flow_diff_orig_proj_file_path = ''
        self.signal_flow_diff_chg_proj_file_path = ''
        self.signal_flow_diff_is_use_current_flow = False
        self.flow_ai_manager = FlowAIDialogManager(self)
        self.flow_ai_web_manager = FlowAIWebManager(self)

        # Skip window to save inquiry
        self.skip_save_check = False

    def custom_aos_setup(self):
        self.config_file_validator = ConfigFileValidator(self)
        is_config_file_valid = self.config_file_validator.validate()
        if is_config_file_valid:
            custom_ao_manager = CustomAOManager(self)
            custom_ao_manager.add_aos_to_system_from_config_file()

    @property
    def hasPaSupported(self):
        return self._hasPaSupported

    @hasPaSupported.setter
    def hasPaSupported(self, input_data):
        self._hasPaSupported = input_data

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.flow_ai_manager.flow_ai_dialog_geometry()
        self.flow_ai_web_manager.update_geometry()
        self.UserPaneResize()

    def mousePressEvent(self, event):
        # 先讓 FlowAI 管理器處理，如果它處理了就返回
        if self.flow_ai_manager.handle_mouse_press(event):
            return
        if self.flow_ai_web_manager.handle_mouse_press(event): return
        # 如果 FlowAI 管理器沒有處理，繼續原有的邏輯
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # 先讓 FlowAI 管理器處理，如果它處理了就返回
        if self.flow_ai_manager.handle_mouse_release(event):
            return
        if self.flow_ai_web_manager.handle_mouse_release(event): return
        # 如果 FlowAI 管理器沒有處理，繼續原有的邏輯
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # 先讓 FlowAI 管理器處理，如果它處理了就返回
        if self.flow_ai_manager.handle_mouse_move(event):
            return
        if self.flow_ai_web_manager.handle_mouse_move(event): return
        # 如果 FlowAI 管理器沒有處理，繼續原有的邏輯
        super().mouseMoveEvent(event)


    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                windows = self.mdiArea.subWindowList()
                for window in windows:
                    for i in range(len(window.widget().scene.nodes)):
                        node = window.widget().scene.nodes[i]
                        if hasattr(node, 'widget'):
                            node.widget.setWindowState(QtCore.Qt.WindowMinimized)
            elif not self.windowState() & Qt.WindowNoState:
                windows = self.mdiArea.subWindowList()
                for window in windows:
                    for i in range(len(window.widget().scene.nodes)):
                        node = window.widget().scene.nodes[i]
                        if hasattr(node, 'widget'):
                            if node.widget.isMinimized:
                                node.widget.setWindowState(QtCore.Qt.WindowNoState)

    def searchAudioInterfaceFile(self):
        """
            The function is to search for a file named "audio_interface. flw" in the specified path.
            The function uses the subprocess module to execute system commands

            :return: bool, If the file is found, return true,
                otherwise false
        """
        result = False

        target_path = smartCWD()

        cmd = ["dir", target_path, "/s", "/b", "/d"]
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, cwd=target_path)
        files = process.stdout.read().decode().split()
        for file in files:
            if file.rsplit('\\')[-1] == "audio_interface.flw":
                result = True

        return result

    def initDialog(self):
        """
            Init Dialog (Setting Dialog、Analysis Dialog、TitleEdit Dialog)
            And binding method
        """
        self.settingDialogWidget = SettingQDialog(self)
        self.exportDialogWidget = QDialog(self)
        self.settingDialog = FLOW_Window_Connection(self, self.settingDialogWidget)

        self.settingDialog.controlDialog.checkBox_dsp.stateChanged.connect(self.updateShipText)

        self.analysisDialogWidget = QDialog(self)
        self.analysisDialog = FLOW_Window_Analysis(self, self.analysisDialogWidget)
        self.analysisDialogWidget.setWindowTitle('Design Analysis')
        self.analysisDialog.controlDialog.doubleSpinBox_3.valueChanged.connect(self.updateProcessSampleText)
        self.analysisDialog.controlDialog.comboBox_2.currentTextChanged.connect(self.updateProcessSampleText)

        self.analysisDialog.controlDialog.doubleSpinBox_3.valueChanged.connect(self.updateFrameCountText)
        self.analysisDialog.controlDialog.comboBox_2.currentTextChanged.connect(self.updateFrameCountText)
        self.analysisDialog.controlDialog.spinBox.valueChanged.connect(self.updateFrameCountText)

        self.editTitleDialogWidget = QDialog(self)
        self.editTitleDialog = Ui_projTitleDialog()
        self.editTitleDialog.setupUi(self.editTitleDialogWidget)
        self.editTitleDialogWidget.setWindowTitle('Save Project Name')

        # self.mdiArea.subWindowActivated.connect(self.settingDialog.disable_not_supported_ao)

    def initUI(self):
        """
            Initialize the user interface of the FLOW Studio application
        """
        self.name_company = "Tymphany Acoustic Technology HK Limited"
        self.name_product = "Flow Studio"
        self.name_author = "Tymphany"
        self.setWindowIcon(QIcon("../resources/main-theme.png"))

        # just use an arbitrary way to implement the stylesheet... we might need a better solution
        file = QFile('qss/nodeeditor-dark.qss')
        file.open(QFile.ReadOnly)
        styleSheet = file.readAll()
        QApplication.instance().setStyleSheet(str(styleSheet, encoding='utf-8'))
        # TODO: we need to verify the build result to check what will be missing after releasing .exe
        # belowe is the original design from author
        # self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        # loadStylesheets(
        #     os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"),
        #     self.stylesheet_filename
        # )

        self.empty_icon = QIcon(".")

        if Debug.DEBUG_Low_Level.value:
            print("Registered nodes:")
            pp(FLOW_NODES)

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsMovable(True)
        self.mdiArea.setTabPosition(QTabWidget.South)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        # self.mdiArea.subWindowActivated.connect(self.updateSubPatch)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createUserFoler()
        self.createNodesDock()
        self.createEditorDock()
        self.createCmdDock()

        self.createActions()
        self.createMenus()
        self.createStatusBar()
        self.updateMenus()
        self.update_export_custom_aos_settings_availability()
        self.readSettings()

        self.setWindowTitle("Flow Studio")

        self.onFileNew()
        self.mdiArea.setViewMode(QMdiArea.TabbedView)

    def waitForLicenseInitSuccess(self):
        self.mdiArea.subWindowActivated.connect(self.settingDialog.disable_not_supported_ao)

    def updateSubPatch(self):
        """
            When The current window is FLOW_Sub_Group, SubPatch Item will be hidden,
            otherwise they will be displayed
        """
        if type(self.getCurrentNodeEditorWidget()) is FLOW_Sub_Group:
            self.nodesListWidget.HiddenSubPatchItem(True)
        else:
            self.nodesListWidget.HiddenSubPatchItem(False)

    def updateInAndOut(self):
        """
            When The current window is FLOW_Sub_Group, IN and OUT AO will be hidden,
            otherwise they will be displayed
        """
        # When the input device is empty, IN AO is not supported on the PC platform
        in_ao_is_supported = not (self.settingDialog.inputList(
            str(self.settingDialog.currDriver)) == [] and self.target == Target.PC.value)

        # When the out device is empty, OUT AO is not supported on the PC platform
        out_ao_is_supported = not (self.settingDialog.outputList(
            str(self.settingDialog.currDriver)) == [] and self.target == Target.PC.value)

        if type(self.getCurrentNodeEditorWidget()) is FLOW_Sub_Group:
            self.nodesListWidget.HiddenInOutItem(True, in_ao_is_supported, out_ao_is_supported)
        else:
            self.nodesListWidget.HiddenInOutItem(False, in_ao_is_supported, out_ao_is_supported)

    def createFileMenu(self):
        """
            Create a "File" menu in the main window of the application,
            including operations such as "New", "Open", "Recently Opened Files", "Save", etc
        """
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        # self.fileMenu.addAction(self.actMultiple)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addMenu(self.actOpenRecent)
        self.fileMenu.addMenu(self.actExample)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addAction(self.actExport)
        self.fileMenu.addAction(self.actExportCommit)
        self.fileMenu.addAction(self.actExportRawCommand)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)
        self.createRecent()
        self.createExampleMenu()

    def createRecent(self):
        """
            Create a menu bar for opening recent files

            If the list read is empty, displaying 'No Files' in the' Recently Opened Files' submenu indicates that no files have been opened.
            If the list is not empty, create a QAction object for each history record and add them to actOpenRecent.
        """
        self.actOpenRecent.clear()
        # self.open_file_path is the file where the 'path' is saved
        filename = self.open_file_path
        with open(filename, "r") as f:
            acts = f.readlines()
            opfindex = []
            if len(acts) == 0:
                opfindex = QAction("No Files", self, statusTip='Open this file....')
                self.actOpenRecent.addAction(opfindex)
            else:
                for i in range(len(acts)):
                    opfindex.append("index" + str(i))
                for i in range(len(acts)):
                    # Limit display to 10 items
                    if i < 10:
                        acts[i] = acts[i].rstrip("\n")
                        opfindex[i] = QAction(acts[i], self, statusTip='Open this file....', triggered=self.onOpenRecent)
                        self.actOpenRecent.addAction(opfindex[i])
                        self.actOpenRecent.addSeparator()
                if len(acts) > 10:
                    self.actOpenRecent.addAction(QAction('More....', self, statusTip='More....', triggered=self.onMoreOpenRecentItem))

    def onMoreOpenRecentItem(self):
        """
            Show more 'recently opened file paths'
        """
        qdialog = QDialog(self)
        self.more_recent_dialog = Ui_more_project()
        self.more_recent_dialog.setupUi(qdialog)
        # scroll area
        scroll_layout = QVBoxLayout(self.more_recent_dialog.scrollAreaWidgetContents)
        more_recent_dialog_width = 0

        with open(self.open_file_path, "r") as f:
            acts = f.readlines()
            for i in range(len(acts)):
                font = QFont()
                font.setPointSize(10)
                btn = QPushButton(acts[i].strip())
                btn.setFont(font)
                btn.setStyleSheet("padding:10px;")
                btn.clicked.connect(lambda: self.onMoreRecentDialogOpenFile(qdialog))
                scroll_layout.addWidget(btn)
                width = btn.minimumSizeHint().width() + 40
                if width > more_recent_dialog_width:
                    more_recent_dialog_width = width

        self.more_recent_dialog.scrollArea.setFixedWidth(more_recent_dialog_width)
        qdialog.setFixedWidth(more_recent_dialog_width + 20)

        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def onMoreRecentDialogOpenFile(self, dialog):
        """
            open file in more_recent_dialog

            :param dialog, more recent dialog object
        """
        button = self.sender()
        path = button.text()
        if not self.onFileOpen(project_file_path=path):
            self.onDeletePathFile(path, self.open_file_path)
        dialog.close()


    def createExampleMenu(self):
        """
            File -> Example
            Create Example Menu
        """
        # Root directory traversed
        root_dir = self.templatePath
        # Traverse directory, create template file option
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                filename, filetype = os.path.splitext(file)
                if filetype == '.proj':
                    act = QAction(filename, self, statusTip="Open Example file....", triggered=self.onOpenExampleFile)
                    self.actExample.addAction(act)
                    self.actExample.addSeparator()

    def closeEvent(self, event):
        """
            Update license information when closing the window，

            If the window belongs to the main window, update the license information before closing the main window，
            If it does not belong to the main window, update the license information directly，

            :param event, The object that receives and processes the event when the window is closed
        """
        self.license_mechanism.recordUserCloseAction()
        mainWindow = self.findMain()
        if mainWindow is not None:
            if mainWindow.close() is False:
                event.ignore()
            else:
                self.license_mechanism.createUserRecord()
        else:
            if hasattr(self, 'license_mechanism'):
                if self.license_mechanism:
                    self.license_mechanism.createUserRecord()

    @property
    def dspstatus(self):
        return self._dspstatus

    @dspstatus.setter
    def dspstatus(self, new_data: bool):
        self._dspstatus = new_data

    @property
    def editmode(self):
        return self._editmode

    @editmode.setter
    def editmode(self, new_data: bool):
        """
            Current window edit mode status settings

            if new_data if True: Indicates that the current window is in an editable state.
            if new_data if False: Indicates that the current window is in a non editable state.

            :param new_data: bool, Is it in editing status
        """
        self._editmode = new_data
        FLOW_Sub_Window.editmode = self._editmode
        self.nodesListWidget.updateItemsFlag(self.editmode)
        self.nodesControlListWidget.updateItemsFlag(self.editmode)
        self.actEditMode.setChecked(self.editmode)
        if new_data:
            if self.getCurrentNodeEditorWidget():
                self.getCurrentNodeEditorWidget().view.dragStatus = True
        else:
            if self.getCurrentNodeEditorWidget():
                self.getCurrentNodeEditorWidget().view.dragStatus = False

        self.actInfo.setDisabled(not new_data)

        # Set the dragStatus value when there are multiple windows
        for sub_window in self.mdiArea.subWindowList():
            sub_window.widget().view.dragStatus = new_data

        self.updateQTabBarColor(new_data)
        self.updateEditMenu()
        # Set AO function when edit mode changes
        self.set_AO_feature_edit_mode_change(self.editmode)

    def onEditUndo(self):
        """Handle Edit Undo operation"""
        if self.editmode:
            self.warning_information(FLOW_Window.onEditUndo.__name__)
        else:
            current_window = self.getCurrentNodeEditorWidget()
            sub_windows_to_open = []
            need_to_close_sub_windows = []
            sub_windows_data = []
            encrypted_sub_windows = []
            curr_wgt_history_stack = self.getCurrentNodeEditorWidget().scene.history.history_stack
            curr_wgt_curr_step = self.getCurrentNodeEditorWidget().scene.history.history_current_step
            # region 建了SUBPATCH後要UNDO（要刪掉SUBPATCH，也要把相對應的sub window刪掉）
            if curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[0] == 'Created FLOW_Node_SUBPATCH':
                def dfs_undo_after_create_subpatch(subpatch_name, sub_windows):
                    is_subpatch_inside = False
                    for sub_window in sub_windows:
                        sub_window_name = sub_window.widget().getPrettyFilename()
                        if subpatch_name == sub_window_name:
                            target_window_history_stack = sub_window.widget().scene.history.history_stack
                            target_window_curr_step = sub_window.widget().scene.history.history_current_step
                            sub_window_history_stamp = target_window_history_stack[
                                target_window_curr_step]
                            sub_window_history_stamp['sub_window_name'] = sub_window_name
                            if hasattr(sub_window.widget(), 'encrypted'):
                                sub_window_history_stamp['encrypted'] = sub_window.widget().encrypted
                            if hasattr(sub_window.widget(), 'already_input_password'):
                                sub_window_history_stamp['already_input_password'] = sub_window.widget().already_input_password
                            if hasattr(sub_window.widget(), 'correct_password'):
                                sub_window_history_stamp['correct_password'] = sub_window.widget().correct_password
                            sub_windows_data.append(sub_window_history_stamp)
                            need_to_close_sub_windows.append(sub_window)
                            subpatchs_inside = []
                            for node in sub_window_history_stamp['snapshot']['nodes']:
                                if node['op_code'] == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node['title'])
                    if not is_subpatch_inside:
                        return
                    for subpatch_inside in subpatchs_inside:
                        dfs_undo_after_create_subpatch(subpatch_inside, sub_windows)
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[1]
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                sub_windows = self.mdiArea.subWindowList()
                dfs_undo_after_create_subpatch(subpatch_name, sub_windows)
            # endregion
            # region 刪了SUBPATCH後要undo（復原SUBPATCH）
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'] == 'Delete selected':
                renamed = set()
                if 'sub_windows' in curr_wgt_history_stack[curr_wgt_curr_step]:
                    sub_windows = copy.deepcopy(curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'])
                    first_layer_original_name = set()
                    for i in range(curr_wgt_curr_step - 1, -1, -1):
                        if 'sub_window_names' in curr_wgt_history_stack[i]:
                            for sub_window_name in curr_wgt_history_stack[i]['sub_window_names']:
                                first_layer_original_name.add(sub_window_name)
                    nodesSets = self.getCurrentNodeEditorWidget().collectNodesFromSubWnds()
                    self.setActiveSubWindow(current_window.parent())
                    for sub_window in sub_windows:
                        subwnd = self.createGroupChild()
                        subwnd.widget().title = sub_window['sub_window_name']
                        if 'encrypted' in sub_window:
                            subwnd.widget().encrypted = sub_window['encrypted']
                        if 'already_input_password' in sub_window:
                            subwnd.widget().already_input_password = sub_window['already_input_password']
                        if 'correct_password' in sub_window:
                            subwnd.widget().correct_password = sub_window['correct_password']

                        sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(OP_NODE_SUBPATCH, nodesSets)
                        subpatch_node = TempNode()
                        subpatch_node.op_code = OP_NODE_SUBPATCH
                        not_available_titles = []
                        for sorted_node in sortedNodes:
                            not_available_titles.append(sorted_node.title)
                        if subwnd.widget().title in not_available_titles:
                            original_title = subwnd.widget().title
                            num = 1
                            found = False
                            while not found:
                                if f'SUBPATCH_{str(num)}' not in not_available_titles:
                                    found = True
                                else:
                                    num += 1
                            new_title = f'SUBPATCH_{str(num)}'
                            subwnd.widget().title = f'SUBPATCH_{str(num)}'
                            sub_window['sub_window_name'] = f'SUBPATCH_{str(num)}'

                            for i in range(len(curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'])):
                                # print(f'1 {renamed}')
                                if ('sub', i, 'sub_window_name') not in renamed:
                                    if curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'][i][
                                        'sub_window_name'] == original_title:
                                        curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'][i][
                                            'sub_window_name'] = f'SUBPATCH_{str(num)}'
                                        renamed.add(
                                            ('sub', i,
                                             'sub_window_name'))
                                if ('sub', i, 'nodes') not in renamed:
                                    for node in \
                                    curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'][i]['snapshot'][
                                        'nodes']:
                                        if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                            # print(i, original_title, f'SUBPATCH_{str(num)}')
                                            node['title'] = f'SUBPATCH_{str(num)}'
                                            node['designator'] = num
                                            node['cwd'] = f'SUBPATCH_{str(num)}'
                                            renamed.add(
                                                ('sub', i,
                                                 'nodes'))



                            for i in range(curr_wgt_curr_step - 1, -1, -1):
                                if ('curr', i, 'desc') not in renamed:
                                    if curr_wgt_history_stack[i]['desc'].split('-')[-1] == original_title:
                                        curr_wgt_history_stack[i]['desc'] = curr_wgt_history_stack[i]['desc'].split('-')[0] + '-' + f'SUBPATCH_{str(num)}'
                                        renamed.add(('curr', i, 'desc'))
                                if 'sub_window_names' in curr_wgt_history_stack[i]:
                                    if ('curr', i, 'sub_window_names', original_title, new_title) not in renamed:
                                        if original_title in first_layer_original_name and original_title in curr_wgt_history_stack[i]['sub_window_names']:
                                            curr_wgt_history_stack[i]['sub_window_names'].remove(original_title)
                                            curr_wgt_history_stack[i]['sub_window_names'].append(new_title)
                                            curr_wgt_history_stack[i]['sub_window_names'].sort()
                                            renamed.add(('curr', i, 'sub_window_names',original_title, new_title))
                                for node in curr_wgt_history_stack[i]['snapshot']['nodes']:
                                    if ('curr', i, 'nodes', node['id']) not in renamed:
                                        if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                            # print(original_title, f'SUBPATCH_{str(num)}', i, node['id'])
                                            node['title'] = f'SUBPATCH_{str(num)}'
                                            node['designator'] = num
                                            node['cwd'] = f'SUBPATCH_{str(num)}'
                                            # print(f'{original_title}->SUBPATCH_{str(num)}')
                                            renamed.add(('curr', i, 'nodes', node['id']))
                                            subpatch_node.title = f'SUBPATCH_{str(num)}'
                                            nodesSets = [*nodesSets, subpatch_node]
                            found = False
                            for sub_window_to_open in sub_windows_to_open:
                                for node in sub_window_to_open.widget().scene.nodes:
                                    if (sub_window_to_open, 'nodes', node.id) not in renamed:
                                        if node.op_code == OP_NODE_SUBPATCH and node.title == original_title and not hasattr(node, 'renamed'):
                                            for hs_node in sub_window_to_open.widget().scene.history.history_stack[sub_window_to_open.widget().scene.history.history_current_step]['snapshot']['nodes']:
                                                if (sub_window_to_open, 'his_stamp','nodes', hs_node['id']) not in renamed:
                                                    if hs_node['op_code'] == OP_NODE_SUBPATCH and hs_node['title'] == original_title:
                                                        hs_node['title'] = f'SUBPATCH_{str(num)}'
                                                        hs_node['designator'] = num
                                                        hs_node['cwd'] = f'SUBPATCH_{str(num)}'
                                                        renamed.add((sub_window_to_open, 'his_stamp','nodes', hs_node['id']))
                                            node.title = f'SUBPATCH_{str(num)}'
                                            node.designator = num
                                            node.cwd = f'SUBPATCH_{str(num)}'
                                            node.renamed = True
                                            renamed.add((sub_window_to_open, 'nodes', node.id))
                                            found = True
                                            subpatch_node.title = f'SUBPATCH_{str(num)}'
                                            nodesSets = [*nodesSets, subpatch_node]
                                            break
                                if found:
                                    break

                        # subpatch_node = TempNode()
                        # subpatch_node.op_code = OP_NODE_SUBPATCH
                        if subpatch_node not in nodesSets:
                            subpatch_node.title = subwnd.widget().title
                            nodesSets = [*nodesSets, subpatch_node]

                        subwnd.widget().fileNew()
                        subwnd.widget().setTitle()
                        subwnd.widget().scene.history.history_stack = [sub_window]
                        subwnd.widget().scene.history.history_current_step = len(
                            subwnd.widget().scene.history.history_stack) - 1
                        subwnd.widget().scene.deserialize(subwnd.widget().scene.history.history_stack[-1]['snapshot'])
                        subwnd.widget().scene.has_been_modified = True
                        for i in range(len(subwnd.widget().scene.nodes)):
                            node = subwnd.widget().scene.nodes[i]
                            node.eval()
                            # nodesSets.append(node)
                        sub_windows_to_open.append(subwnd)
                        if hasattr(subwnd.widget(), 'encrypted'):
                            if subwnd.widget().encrypted and not subwnd.widget().already_input_password:
                                encrypted_sub_windows.append(subwnd)
            # endregion
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'] == 'Pasted elements in scene':
                if 'sub_window_names' in curr_wgt_history_stack[curr_wgt_curr_step]:
                    for sub_window_name in curr_wgt_history_stack[curr_wgt_curr_step]['sub_window_names']:
                        self.open_subwindow_in_subpatch_recursively(sub_window_name)
                    self.setActiveSubWindow(current_window.parent())
                    current_sub_windows = self.mdiArea.subWindowList()
                    to_close_sub_window_names = curr_wgt_history_stack[curr_wgt_curr_step]['sub_window_names']
                    # print(to_close_sub_window_names)
                    def dfs_undo_after_paste(to_close_sub_window_name, current_sub_windows):
                        is_subpatch_inside = False
                        for sub_window in current_sub_windows:
                            sub_window_name = sub_window.widget().getPrettyFilename()
                            if to_close_sub_window_name == sub_window_name:
                                need_to_close_sub_windows.append(sub_window)
                                if hasattr(sub_window.widget(), 'already_input_password'):
                                    sub_window.widget().scene.history.history_stack[
                                        sub_window.widget().scene.history.history_current_step]['already_input_password'] = sub_window.widget().already_input_password
                                if hasattr(sub_window.widget(), 'correct_password'):
                                    sub_window.widget().scene.history.history_stack[
                                        sub_window.widget().scene.history.history_current_step]['correct_password'] = sub_window.widget().correct_password
                                if hasattr(sub_window.widget(), 'encrypted'):
                                    sub_window.widget().scene.history.history_stack[
                                        sub_window.widget().scene.history.history_current_step]['encrypted'] = sub_window.widget().encrypted
                                sub_windows_data.append(sub_window.widget().scene.history.history_stack[sub_window.widget().scene.history.history_current_step])
                                sub_windows_data[-1]['sub_window_name'] = sub_window_name
                                subpatchs_inside = []
                                for node in sub_window.widget().scene.nodes:
                                    if node.op_code == OP_NODE_SUBPATCH:
                                        is_subpatch_inside = True
                                        subpatchs_inside.append(node.title)
                                        # print(node.title)
                        if not is_subpatch_inside:
                            return
                        for subpatch_inside in subpatchs_inside:
                            dfs_undo_after_paste(subpatch_inside, current_sub_windows)
                    # print(to_close_sub_window_names)
                    for to_close_sub_window_name in to_close_sub_window_names:
                        dfs_undo_after_paste(to_close_sub_window_name, current_sub_windows)
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('Rename SubPatch'):
                desc = curr_wgt_history_stack[curr_wgt_curr_step]['desc']
                current_subpatch_name = desc.split(' ')[-1]
                restore_subpatch_name = desc.split(' ')[-3]
                # 將subpatch子視窗名字改回去
                self.open_subwindow_in_subpatch_recursively(current_subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                current_sub_windows = self.mdiArea.subWindowList()
                for sub_window in current_sub_windows:
                    if type(sub_window.widget()) == FLOW_Sub_Group:
                        sub_window_name = sub_window.widget().title
                        if sub_window_name.replace('.json', '') == current_subpatch_name:
                            sub_window.widget().scene.has_been_modified = True
                            # 看有沒有存在SUBPATCH原名稱的檔案
                            if self.temp_folder_path:
                                if os.path.exists(self.temp_folder_path + '/' + restore_subpatch_name + '.json'):
                                    sub_window.widget().title = restore_subpatch_name+'.json'
                                else:
                                    sub_window.widget().title = restore_subpatch_name
                            else:
                                sub_window.widget().title = restore_subpatch_name
                            sub_window.widget().renamed = True
                            sub_window.widget().setWindowTitle(sub_window.widget().title + '*')
                        if hasattr(sub_window.widget(), 'close_if_no_problem'):
                            self.close_sub_window(sub_window)
            # add password -> undo
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('AddPassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                windows = self.mdiArea.subWindowList()
                correct_password = None
                for window in windows:
                    window_name = window.widget().getPrettyFilename()
                    if window_name == subpatch_name:
                        if hasattr(window.widget(), 'encrypted'):
                            correct_password = window.widget().correct_password
                if correct_password is None:
                    for ele in self.sub_patchs:
                        if ele.title == subpatch_name + '.json' or ele.title == subpatch_name:
                            if hasattr(ele, 'encrypted'):
                                correct_password = ele.correct_password
                to_close_sub_windows = []
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.decrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=correct_password,
                                                  windows=windows)
                self.setActiveSubWindow(current_window.parent())
                curr_wgt_history_stack[curr_wgt_curr_step]['password'] = correct_password
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem:
                            self.close_sub_window(sub_window)
            # remove password -> undo
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('RemovePassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                input_password = curr_wgt_history_stack[curr_wgt_curr_step]['password']
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.encrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=input_password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem:
                            self.close_sub_window(sub_window)
            # modify password -> undo
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('ModifyPassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1].split(' ')[0]
                # region delete password firstly
                original_password = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split(' ')[-1]
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.decrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=original_password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                            self.close_sub_window(sub_window)
                self.setActiveSubWindow(current_window.parent())

                # endregion
                # region add password secondly
                new_password = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split(' ')[-3]
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.encrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=new_password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                            self.close_sub_window(sub_window)
                self.setActiveSubWindow(current_window.parent())
                # endregion
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('Add Inlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                    self.delete_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                        node_op_code=OP_NODE_INLET)
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('Reduce Inlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                    self.add_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                     node_op_code=OP_NODE_INLET)
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('Add Outlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                    self.delete_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                        node_op_code=OP_NODE_OUTLET)
            elif curr_wgt_history_stack[curr_wgt_curr_step]['desc'].startswith('Reduce Outlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step]['desc'].split('-')[-1]
                    self.add_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                     node_op_code=OP_NODE_OUTLET)
            if sub_windows_data:
                curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'] = sub_windows_data
            super().onEditUndo()
            # region prevent conflict AO name or designator
            # endregion
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()
            if sub_windows_to_open:
                for sub_window_to_open in sub_windows_to_open:
                    sub_window_to_open.show()
            if need_to_close_sub_windows:
                for need_to_close_sub_window in need_to_close_sub_windows:
                    need_to_close_sub_window.widget().parent().close()
            for encrypted_sub_window in encrypted_sub_windows:
                self.close_sub_window(encrypted_sub_window)
            self.setActiveSubWindow(current_window.parent())
            self.prevent_conflict_name_and_designators()
            self.setActiveSubWindow(current_window.parent())
            self.setActiveSubWindow(current_window.parent())

    def popup_custom_ao_builder_window(self):
        self.is_ok_btn_clicked_in_custom_ao_builder = False
        self.custom_ao_builder_dialog = CustomAOBuilderDialog(self)
        # self.custom_ao_builder_dialog.setFixedSize(1200, 780)
        self.custom_ao_builder_ui = CustomAOBuilderUI()
        self.custom_ao_builder_ui.setupUi(self.custom_ao_builder_dialog)
        self.custom_ao_builder_ui.add_ao_btn.clicked.connect(self.handle_add_ao_btn_clicked)
        self.custom_ao_builder_ui.remove_ao_btn.clicked.connect(self.handle_remove_ao_btn_clicked)
        self.custom_ao_builder_ui.aos_list_widget.currentItemChanged.connect(self.handle_custom_aos_current_item_changed)
        self.custom_ao_builder_ui.aos_list_widget.model().rowsMoved.connect(self.handle_change_custom_ao_order)
        self.custom_ao_builder_ui.name_line_edit.textChanged.connect(self.handle_custom_ao_name_changed)
        self.custom_ao_builder_ui.display_name_line_edit.textChanged.connect(self.handle_custom_ao_display_name_changed)
        self.custom_ao_builder_ui.description_line_edit.textChanged.connect(self.handle_custom_ao_description_changed)
        self.custom_ao_builder_ui.icon_push_btn.clicked.connect(self.open_custom_ao_icon_dialog)
        self.custom_ao_builder_ui.remove_icon_push_btn.clicked.connect(self.handle_click_remove_icon_btn)
        self.custom_ao_builder_ui.is_float_point_check_box.stateChanged.connect(self.handle_custom_ao_is_float_point_changed)
        self.custom_ao_builder_ui.addition_type_combo_box.currentIndexChanged.connect(self.handle_addition_type_current_index_changed)
        self.custom_ao_builder_ui.num_input_sockets_spin_box.valueChanged.connect(self.handle_num_input_sockets_spin_box_value_changed)
        self.custom_ao_builder_ui.num_output_sockets_spin_box.valueChanged.connect(self.handle_num_output_sockets_spin_box_value_changed)
        self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.valueChanged.connect(self.handle_num_inctrl_sockets_spin_box_value_changed)
        self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.valueChanged.connect(self.handle_num_outctrl_sockets_spin_box_value_changed)
        self.custom_ao_builder_ui.collapsible_check_box.stateChanged.connect(self.handle_custom_ao_collapsible_changed)
        self.custom_ao_builder_ui.add_tuning_param_btn.clicked.connect(self.handle_add_tuning_param_btn_clicked)
        self.custom_ao_builder_ui.remove_tuning_param_btn.clicked.connect(self.handle_remove_tuning_param_btn_clicked)
        self.custom_ao_builder_ui.move_tuning_param_up_btn.clicked.connect(self.handle_move_tuning_param_up_btn_clicked)
        self.custom_ao_builder_ui.move_tuning_param_down_btn.clicked.connect(self.handle_move_tuning_param_down_btn_clicked)
        self.custom_ao_builder_ui.is_popup_allowed_check_box.stateChanged.connect(self.handle_is_popup_allowed_changed)
        self.custom_ao_builder_ui.save_btn.clicked.connect(self.handle_save_btn_clicked)
        self.custom_ao_builder_ui.generate_code_template_btn.clicked.connect(self.handle_generate_code_template_btn_clicked)
        self.setup_custom_aos_data_structures()
        self.setup_custom_ao_builder_ui()
        self.custom_ao_builder_dialog.setWindowTitle('Custom AO Builder')
        # Track user action "Launch Custom AO Builder"
        self.tracker = TrackManager()
        self.tracker.track_user_action(action=8, license=self.license_mechanism)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        self.custom_ao_builder_dialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def import_custom_aos_settings(self):
        def get_unique_backup_folder_path(base_path):
            counter = 1
            unique_path = base_path
            while os.path.exists(unique_path):
                unique_path = f'{base_path}_{counter}'
                counter += 1
            return unique_path

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Import Custom AOs Settings', '', 'Config Files (*.fsoa)',
                                                   options=options)

        if not file_path or not file_path.endswith('.fsoa'):
            return
        backup_folder_path = get_unique_backup_folder_path(self.custom_folder_path + '_backup')
        try:
            # Create a backup of the custom folder
            shutil.copytree(self.custom_folder_path, backup_folder_path)

            # Extract the .fsoa file to a temporary directory
            temp_extract_path = get_unique_backup_folder_path(self.custom_folder_path + '_temp')
            os.makedirs(temp_extract_path)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)

            # Replace the custom folder with the extracted contents
            if os.path.exists(self.custom_folder_path):
                shutil.rmtree(self.custom_folder_path)
            shutil.move(temp_extract_path, self.custom_folder_path)

            custom_ao_manager = CustomAOManager(self)
            custom_ao_manager.clear_custom_aos_from_system()
            # Move all files from temp folder to custom folder
            temp_folder_path = os.path.join(self.custom_folder_path, 'temp')
            if os.path.exists(temp_folder_path):
                for item in os.listdir(temp_folder_path):
                    s = os.path.join(temp_folder_path, item)
                    d = os.path.join(self.custom_folder_path, item)
                    if os.path.isfile(s):
                        shutil.move(s, d)
                shutil.rmtree(temp_folder_path)
            custom_ao_manager.add_aos_to_system_from_config_file()
            self.update_export_custom_aos_settings_availability()
            self.statusBar().showMessage('Custom AOs settings were imported successfully.', 3000)
        except Exception as e:
            # Restore the backup in case of failure
            if os.path.exists(self.custom_folder_path):
                shutil.rmtree(self.custom_folder_path)
            if os.path.exists(backup_folder_path):
                shutil.move(backup_folder_path, self.custom_folder_path)
            QMessageBox.critical(self, 'Error', 'Failed to import Custom AOs settings.')
        finally:
            # Clean up temporary directories if they exist
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path)
            if os.path.exists(backup_folder_path):
                shutil.rmtree(backup_folder_path)

    def export_custom_aos_settings(self):
        # Open a file dialog to let the user choose the save location and filename
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Custom AOs Settings", "", "Config Files (*.fsoa)",
                                                   options=options)

        if not file_path:
            return

        # Ensure the chosen filename has a .fsoa extension
        if not file_path.endswith('.fsoa'):
            file_path += '.fsoa'

        # Create a zip file directly at the chosen location
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            source_dir = self.custom_folder_path
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, start=source_dir)
                        zip_file.write(file_path, arc_name)
        self.statusBar().showMessage('Custom AOs settings were exported successfully.', 3000)

    def check_display_name(self, aos):
        issues = []
        for ao in aos:
            if not ao['display_name']:
                issues.append(ao['ao_name'])
        return issues

    def check_gui_type_no(self, temp_custom_aos):
        issues = []
        for ao in temp_custom_aos:
            for param in ao['tuning_parameters']:
                if param['gui_type_no'] is None:
                    issues.append((ao['ao_name'], param['name']))
        return issues

    def check_params_under_tuning_parameters(self, aos):
        issues = []
        for ao in aos:
            ao_name = ao['ao_name']
            tuning_params = ao['tuning_parameters']
            for tuning_param in tuning_params:
                tuning_param_name = tuning_param['name']
                gui_type_no = tuning_param['gui_type_no']
                parameters_under_tuning_parameter = tuning_param['parameters']
                if gui_type_no == ControlType.MENU.value:
                    p_list = []
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pList':
                            p_list = parameter_under_tuning_parameter['value']
                    if not p_list:
                        issues.append((ao_name, tuning_param_name, 'pList', 'Value of this parameter is empty.'))
                elif (gui_type_no == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value
                      or gui_type_no == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value):
                    p_max = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pMax':
                            p_max = int(parameter_under_tuning_parameter['value'])
                    p_min = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pMin':
                            p_min = int(parameter_under_tuning_parameter['value'])
                    p_value = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pValue':
                            p_value = int(parameter_under_tuning_parameter['value'])
                    if p_max < p_min:
                        issues.append((ao_name, tuning_param_name, 'pMax, pMin', 'pMax is less than pMin.'))
                    else:
                        if p_value < p_min or p_value > p_max:
                            issues.append((ao_name, tuning_param_name, 'pValue', 'pValue is out of range.'))
                elif (gui_type_no == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value
                      or gui_type_no == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value):
                    p_max = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pMax':
                            p_max = float(parameter_under_tuning_parameter['value'])
                    p_min = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pMin':
                            p_min = float(parameter_under_tuning_parameter['value'])
                    p_value = 0
                    for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                        if parameter_under_tuning_parameter['key'] == 'pValue':
                            p_value = float(parameter_under_tuning_parameter['value'])
                    if p_max < p_min:
                        issues.append((ao_name, tuning_param_name, 'pMax, pMin', 'pMax is less than pMin.'))
                    else:
                        if p_value < p_min or p_value > p_max:
                            issues.append((ao_name, tuning_param_name, 'pValue', 'pValue is out of range.'))
        return issues

    def save_ao_to_json(self, ao_data):
        def convert_sets_to_lists(data):
            if isinstance(data, dict):
                return {key: convert_sets_to_lists(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [convert_sets_to_lists(element) for element in data]
            elif isinstance(data, set):
                return list(data)
            else:
                return data

        new_ao_data = convert_sets_to_lists(ao_data)

        # Construct the JSON file path
        custom_aos_config_file_path = os.path.join(self.custom_folder_path, 'custom-aos-config.json')

        if os.path.exists(custom_aos_config_file_path):
            with open(custom_aos_config_file_path, 'r') as file:
                existing_ao_data = json.load(file)
        else:
            existing_ao_data = []

        # Create a dictionary for quick lookup of existing AO names and their ao_code
        existing_ao_dict = {ao['ao_name']: ao['ao_code'] for ao in existing_ao_data}
        existing_ao_codes = set(existing_ao_dict.values())

        max_ao_code = 2000000000

        # First pass: Assign ao_code to AOs that already exist in the JSON file
        for ao in new_ao_data:
            if ao['ao_name'] in existing_ao_dict:
                ao['ao_code'] = existing_ao_dict[ao['ao_name']]

        # Second pass: Assign unique ao_code values to new AOs
        for ao in new_ao_data:
            if 'ao_code' not in ao:
                while max_ao_code in existing_ao_codes:
                    max_ao_code -= 1
                ao['ao_code'] = max_ao_code
                existing_ao_codes.add(max_ao_code)

        # Write AO data to the JSON file
        with open(custom_aos_config_file_path, 'w') as json_file:
            json.dump(new_ao_data, json_file, indent=4)

    def handle_save_btn_clicked(self):
        self.handle_click_ok_or_apply_button_in_custom_ao_builder(is_ok_btn_clicked=True)

    def handle_generate_code_template_btn_clicked(self):
        self.handle_click_ok_or_apply_button_in_custom_ao_builder(is_ok_btn_clicked=False)

    def handle_click_ok_or_apply_button_in_custom_ao_builder(self, is_ok_btn_clicked):
        # region validation
        display_name_issues = self.check_display_name(self.temp_custom_aos_in_builder)
        gui_type_issues = self.check_gui_type_no(self.temp_custom_aos_in_builder)
        params_under_tuning_parameters_issues = self.check_params_under_tuning_parameters(
            self.temp_custom_aos_in_builder)
        if display_name_issues or gui_type_issues or params_under_tuning_parameters_issues:
            message = ""
            if display_name_issues:
                message += "The following AOs have empty display names. Please check:\n"
                for ao_name in display_name_issues:
                    message += f"AO Name: {ao_name}\n"

            if gui_type_issues:
                message += "The following AOs have parameters with undefined GUI types. Please check:\n"
                for ao_name, param_name in gui_type_issues:
                    message += f"AO Name: {ao_name}, Parameter Name: {param_name}\n"

            if params_under_tuning_parameters_issues:
                message += "Please check following issues:\n"
                for ao_name, tuning_param_name, param_name, issue in params_under_tuning_parameters_issues:
                    message += f"AO Name: {ao_name}, Tuning Parameter Name: {tuning_param_name}, Parameter Name: {param_name}, Issue: {issue}\n"

            QMessageBox.warning(self, "Warning", message)
            return False
        # endregion
        is_need_to_change_engine = self.is_need_to_change_engine()
        if not is_ok_btn_clicked:
            options = QFileDialog.Options()
            while True:  # Keep letting user select until a valid path is chosen
                dir_path = QFileDialog.getExistingDirectory(self, "Select directory to put code templates",
                                                            options=options)

                # User clicked cancel
                if not dir_path:
                    return

                # Get absolute path of OA_template
                oa_template_source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "OA_template"))
                try:
                    is_under_template_source_path = os.path.commonpath([oa_template_source_path]) == os.path.commonpath(
                        [oa_template_source_path, dir_path])
                except ValueError:  # Different disk drives
                    is_under_template_source_path = False
                # Check if selected path is under OA_template directory
                if is_under_template_source_path:
                    QMessageBox.warning(self, "Warning", 'Please do not select path under OA_template folder.')
                    continue

                break
            self.code_template_generation_thread = CodeTemplateGenerationThread(
                current_custom_aos_setting=copy.deepcopy(self.temp_custom_aos_in_builder),
                dir_path=dir_path,
                parent=self)
            self.code_template_generation_thread.status_update.connect(self.handle_updating_status_text_box_content)
            self.code_template_generation_thread.start()
        custom_ao_manager = CustomAOManager(self)
        custom_ao_manager.clear_custom_aos_from_system()
        custom_ao_manager.handle_icon_of_aos(self.temp_custom_aos_in_builder)
        self.save_ao_to_json(self.temp_custom_aos_in_builder)
        custom_ao_manager.add_aos_to_system_from_config_file()
        icon_file_path = self.custom_ao_builder_ui.icon_line_edit.text()
        if os.path.dirname(icon_file_path):
            self.custom_ao_builder_ui.icon_line_edit.setText(os.path.basename(icon_file_path))
        self.update_export_custom_aos_settings_availability()
        if is_ok_btn_clicked:
            self.is_ok_btn_clicked_in_custom_ao_builder = True
            # self.custom_ao_builder_dialog.close()
        self.handle_updating_status_text_box_content('Custom Audio Objects saved successfully.', '#3498db')

    def handle_updating_status_text_box_content(self, status, color):
        self.custom_ao_builder_ui.status_text_box.append(
            f'<span style="color: {color};">{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}: {status}</span>')

    def setup_custom_ao_builder_ui(self):
        self.custom_ao_builder_ui.open_vs_btn.hide()

        for ao in self.custom_aos_in_builder:
            ao_name = ao['ao_name']
            self.custom_ao_builder_ui.aos_list_widget.addItem(ao_name)
        for text, ao_addition_type_val in AO_ADDITION_TYPES_FOR_OA:
            self.custom_ao_builder_ui.addition_type_combo_box.addItem(text, ao_addition_type_val)
        self.custom_ao_builder_ui.addition_type_combo_box.setCurrentIndex(-1)
        self.custom_ao_builder_ui.tuning_parameters_label.setText('Tuning \nparameters:')
        self.custom_ao_builder_ui.tuning_parameters_table = QTableWidget(0, 2, parent=self.custom_ao_builder_dialog)
        self.custom_ao_builder_ui.tuning_parameters_table.setHorizontalHeaderLabels(["Name", "GUI Type"])
        self.custom_ao_builder_ui.tuning_parameters_table.setColumnWidth(1, 185)
        self.custom_ao_builder_ui.tuning_parameters_table.setColumnWidth(2, 270)
        self.custom_ao_builder_ui.tuning_parameters_table.setStyleSheet("""
                                                                        QTableWidget {
                                                                            background-color: transparent;
                                                                            color: #ffffff;
                                                                            gridline-color: #404040;
                                                                            border: 1px solid #404040;
                                                                            border-radius: 4px;
                                                                        }
                                                                        /* Header style */
                                                                        QHeaderView::section {
                                                                            background-color: #323232;
                                                                            color: #ffffff;
                                                                            padding: 5px;
                                                                            border: 1px solid #404040;
                                                                            border-top-color: transparent;
                                                                            border-left-color: transparent;
                                                                        }
                                                                        QTableWidget::item:selected {
                                                                            background-color: #f39c12;
                                                                        }
                                                                        QTableWidget::item {
                                                                            padding: 2px;
                                                                        }
                                                                        """)
        self.custom_ao_builder_ui.tuning_parameters_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Set to select the entire row
        self.custom_ao_builder_ui.tuning_parameters_table.setSelectionMode(QAbstractItemView.SingleSelection)  # Set to single-selection mode
        self.custom_ao_builder_ui.tuning_parameters_table.setGeometry(QtCore.QRect(200, 505, 315, 205))
        self.custom_ao_builder_ui.tuning_parameters_table.itemSelectionChanged.connect(self.handle_tuning_params_table_item_selection_changed)
        self.custom_ao_builder_ui.supported_platforms_label.setText('Platforms\nsupported:')
        self.custom_ao_builder_ui.supported_platforms_combobox = CustomTextComboBox('Please select',
                                                                                    parent=self.custom_ao_builder_dialog)
        delegate = CustomItemDelegate(self.custom_ao_builder_ui.supported_platforms_combobox)
        self.custom_ao_builder_ui.supported_platforms_combobox.setItemDelegate(delegate)
        self.custom_ao_builder_ui.supported_platforms_combobox.setGeometry(QtCore.QRect(245, 425, 120, 20))
        platforms = []
        platforms.append('Select all')
        for i in range(self.settingDialog.controlDialog.comboBox_targetdevice.count()):
            platforms.append(self.settingDialog.controlDialog.comboBox_targetdevice.itemText(i))
        self.supported_platforms_combobox_model = QStandardItemModel(len(platforms), 1)
        for index, platform_name in enumerate(platforms):
            item = QStandardItem(platform_name)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            self.supported_platforms_combobox_model.setItem(index, 0, item)

        self.custom_ao_builder_ui.supported_platforms_combobox.setModel(self.supported_platforms_combobox_model)
        self.supported_platforms_combobox_model.itemChanged.connect(self.handle_supported_platforms_item_changed)
        self.custom_ao_builder_ui.supported_platforms_combobox.view().setStyleSheet(
            """
                QListView::item { color: black; }
            """
        )
        self.hide_controls_in_custom_ao_builder_ui()
        self.custom_ao_builder_ui.preview_widget = PreviewWidget(parent=self.custom_ao_builder_dialog,
                                                                 flow_window=self)
        self.custom_ao_builder_ui.preview_widget.setGeometry(QtCore.QRect(555, 1, 350, 450))
        if len(self.custom_aos_in_builder) > 0:
            self.custom_ao_builder_ui.aos_list_widget.setCurrentItem(self.custom_ao_builder_ui.aos_list_widget.item(0))
        self.add_custom_ao_if_empty()

    def setup_custom_aos_data_structures(self):
        if os.path.exists(self.config_file_validator.custom_aos_config_file_path):
            with open(self.config_file_validator.custom_aos_config_file_path, 'r') as file:
                aos = json.load(file)
                self.custom_aos_in_builder = aos
                for ao in self.custom_aos_in_builder:
                    ao['support_platforms'] = set(ao['support_platforms'])
        else:
            self.custom_aos_in_builder = []
        self.temp_custom_aos_in_builder = copy.deepcopy(self.custom_aos_in_builder)

    def add_custom_ao_if_empty(self):
        if not self.temp_custom_aos_in_builder:
            self.handle_add_ao_btn_clicked()

    def is_same_between_changes_and_original_state_in_custom_ao_builder(self):
        if len(self.custom_aos_in_builder) != len(self.temp_custom_aos_in_builder):
            return False
        for i in range(len(self.custom_aos_in_builder)):
            if self.custom_aos_in_builder[i]['ao_name'] != self.temp_custom_aos_in_builder[i]['ao_name']:
                return False
            if self.custom_aos_in_builder[i]['display_name'] != self.temp_custom_aos_in_builder[i]['display_name']:
                return False
            if self.custom_aos_in_builder[i]['description'] != self.temp_custom_aos_in_builder[i]['description']:
                return False
            if self.custom_aos_in_builder[i]['icon_file_path'] != self.temp_custom_aos_in_builder[i]['icon_file_path']:
                return False
            if self.custom_aos_in_builder[i]['is_float_point'] != self.temp_custom_aos_in_builder[i]['is_float_point']:
                return False
            if self.custom_aos_in_builder[i]['type_ao_addition'] != self.temp_custom_aos_in_builder[i][
                'type_ao_addition']:
                return False
            if self.custom_aos_in_builder[i]['type_ao_addition'] == TypeAOAddition.FIXED.value and \
                    self.temp_custom_aos_in_builder[i]['type_ao_addition'] == TypeAOAddition.FIXED.value:
                if self.custom_aos_in_builder[i]['num_input_sockets'] != self.temp_custom_aos_in_builder[i][
                    'num_input_sockets']:
                    return False
                if self.custom_aos_in_builder[i]['num_output_sockets'] != self.temp_custom_aos_in_builder[i][
                    'num_output_sockets']:
                    return False
                if self.custom_aos_in_builder[i]['num_inctrl_sockets'] != self.temp_custom_aos_in_builder[i][
                    'num_inctrl_sockets']:
                    return False
                if self.custom_aos_in_builder[i]['num_outctrl_sockets'] != self.temp_custom_aos_in_builder[i][
                    'num_outctrl_sockets']:
                    return False
            if self.custom_aos_in_builder[i]['collapsible'] != self.temp_custom_aos_in_builder[i]['collapsible']:
                return False
            if len(self.custom_aos_in_builder[i]['tuning_parameters']) != len(
                    self.temp_custom_aos_in_builder[i]['tuning_parameters']):
                return False
            for j in range(len(self.custom_aos_in_builder[i]['tuning_parameters'])):
                if self.custom_aos_in_builder[i]['tuning_parameters'][j]['name'] != \
                        self.temp_custom_aos_in_builder[i]['tuning_parameters'][j]['name']:
                    return False
                if self.custom_aos_in_builder[i]['tuning_parameters'][j]['gui_type_no'] != \
                        self.temp_custom_aos_in_builder[i]['tuning_parameters'][j]['gui_type_no']:
                    return False
                if len(self.custom_aos_in_builder[i]['tuning_parameters'][j]['parameters']) != len(
                        self.temp_custom_aos_in_builder[i]['tuning_parameters'][j]['parameters']):
                    return False
                for k in range(len(self.custom_aos_in_builder[i]['tuning_parameters'][j]['parameters'])):
                    if self.custom_aos_in_builder[i]['tuning_parameters'][j]['parameters'][k]['key'] != \
                            self.temp_custom_aos_in_builder[i]['tuning_parameters'][j]['parameters'][k]['key']:
                        return False
                    if self.custom_aos_in_builder[i]['tuning_parameters'][j]['parameters'][k]['value'] != \
                            self.temp_custom_aos_in_builder[i]['tuning_parameters'][j]['parameters'][k]['value']:
                        return False
            if self.custom_aos_in_builder[i]['is_popup_allowed'] != self.temp_custom_aos_in_builder[i][
                'is_popup_allowed']:
                return False
            if self.custom_aos_in_builder[i]['support_platforms'] != self.temp_custom_aos_in_builder[i][
                'support_platforms']:
                return False
        return True

    def is_need_to_change_engine(self):
        for original_ao in self.custom_aos_in_builder:
            original_ao_name = original_ao['ao_name']
            found = False
            for modified_ao in self.temp_custom_aos_in_builder:
                modified_ao_name = modified_ao['ao_name']
                if original_ao_name == modified_ao_name:
                    found = True
                    break
            if not found:
                return True
        for modified_ao in self.temp_custom_aos_in_builder:
            modified_ao_name = modified_ao['ao_name']
            found = False
            for original_ao in self.custom_aos_in_builder:
                original_ao_name = original_ao['ao_name']
                if modified_ao_name == original_ao_name:
                    found = True
                    break
            if not found:
                return True
        # region If the parameter is deleted, for the sake of convenience, assume it is related to engine changes.
        for original_ao in self.custom_aos_in_builder:
            original_ao_name = original_ao['ao_name']
            found = False
            for modified_ao in self.temp_custom_aos_in_builder:
                modified_ao_name = modified_ao['ao_name']
                if original_ao_name == modified_ao_name:
                    found = True
                    original_tuning_parameters = original_ao['tuning_parameters']
                    modified_tuning_parameters = modified_ao['tuning_parameters']
                    for original_tuning_parameter in original_tuning_parameters:
                        original_tuning_parameter_name = original_tuning_parameter['name']
                        original_tuning_parameter_found = False
                        for modified_tuning_parameter in modified_tuning_parameters:
                            modified_tuning_parameter_name = modified_tuning_parameter['name']
                            if original_tuning_parameter_name == modified_tuning_parameter_name:
                                original_tuning_parameter_found = True
                                break
                        if not original_tuning_parameter_found:
                            return True
                if found:
                    break
        # endregion
        # region If the parameter is added, for the sake of convenience, assume it is related to engine changes.
        for modified_ao in self.temp_custom_aos_in_builder:
            modified_ao_name = modified_ao['ao_name']
            found = False
            for original_ao in self.custom_aos_in_builder:
                original_ao_name = original_ao['ao_name']
                if modified_ao_name == original_ao_name:
                    found = True
                    modified_tuning_parameters = modified_ao['tuning_parameters']
                    original_tuning_parameters = original_ao['tuning_parameters']
                    for modified_tuning_parameter in modified_tuning_parameters:
                        modified_tuning_parameter_name = modified_tuning_parameter['name']
                        modified_tuning_parameter_found = False
                        for original_tuning_parameter in original_tuning_parameters:
                            original_tuning_parameter_name = original_tuning_parameter['name']
                            if modified_tuning_parameter_name == original_tuning_parameter_name:
                                modified_tuning_parameter_found = True
                                break
                        if not modified_tuning_parameter_found:
                            return True
                if found:
                    break
        # endregion
        return False

    def hide_controls_in_custom_ao_builder_ui(self):
        controls_to_hide = [self.custom_ao_builder_ui.name_label,
                            self.custom_ao_builder_ui.name_line_edit,
                            self.custom_ao_builder_ui.display_name_label,
                            self.custom_ao_builder_ui.display_name_line_edit,
                            self.custom_ao_builder_ui.description_label,
                            self.custom_ao_builder_ui.description_line_edit,
                            self.custom_ao_builder_ui.icon_label,
                            self.custom_ao_builder_ui.icon_line_edit,
                            self.custom_ao_builder_ui.icon_push_btn,
                            self.custom_ao_builder_ui.remove_icon_push_btn,
                            self.custom_ao_builder_ui.is_float_point_label,
                            self.custom_ao_builder_ui.is_float_point_check_box,
                            self.custom_ao_builder_ui.addition_type_label,
                            self.custom_ao_builder_ui.addition_type_combo_box,
                            self.custom_ao_builder_ui.num_input_sockets_label,
                            self.custom_ao_builder_ui.num_input_sockets_spin_box,
                            self.custom_ao_builder_ui.num_output_sockets_label,
                            self.custom_ao_builder_ui.num_output_sockets_spin_box,
                            self.custom_ao_builder_ui.num_inctrl_sockets_label,
                            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box,
                            self.custom_ao_builder_ui.num_outctrl_sockets_label,
                            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box,
                            self.custom_ao_builder_ui.collapsible_label,
                            self.custom_ao_builder_ui.collapsible_check_box,
                            self.custom_ao_builder_ui.tuning_parameters_label,
                            self.custom_ao_builder_ui.add_tuning_param_btn,
                            self.custom_ao_builder_ui.remove_tuning_param_btn,
                            self.custom_ao_builder_ui.tuning_parameters_table,
                            self.custom_ao_builder_ui.is_popup_allowed_label,
                            self.custom_ao_builder_ui.is_popup_allowed_check_box,
                            self.custom_ao_builder_ui.supported_platforms_label,
                            self.custom_ao_builder_ui.supported_platforms_combobox]
        for control in controls_to_hide:
            control.setVisible(False)
        self.clear_custom_ao_icon_in_builder()

    def show_controls_in_custom_ao_builder_ui(self):
        controls_to_show = [self.custom_ao_builder_ui.name_label,
                            self.custom_ao_builder_ui.name_line_edit,
                            self.custom_ao_builder_ui.display_name_label,
                            self.custom_ao_builder_ui.display_name_line_edit,
                            self.custom_ao_builder_ui.description_label,
                            self.custom_ao_builder_ui.description_line_edit,
                            self.custom_ao_builder_ui.icon_label,
                            self.custom_ao_builder_ui.icon_line_edit,
                            self.custom_ao_builder_ui.icon_push_btn,
                            self.custom_ao_builder_ui.remove_icon_push_btn,
                            self.custom_ao_builder_ui.is_float_point_label,
                            self.custom_ao_builder_ui.is_float_point_check_box,
                            self.custom_ao_builder_ui.addition_type_label,
                            self.custom_ao_builder_ui.addition_type_combo_box,
                            self.custom_ao_builder_ui.collapsible_label,
                            self.custom_ao_builder_ui.collapsible_check_box,
                            self.custom_ao_builder_ui.tuning_parameters_label,
                            self.custom_ao_builder_ui.add_tuning_param_btn,
                            self.custom_ao_builder_ui.remove_tuning_param_btn,
                            self.custom_ao_builder_ui.tuning_parameters_table,
                            self.custom_ao_builder_ui.supported_platforms_label,
                            self.custom_ao_builder_ui.supported_platforms_combobox]
        for control in controls_to_show:
            control.setVisible(True)
        current_addition_type_index = self.custom_ao_builder_ui.addition_type_combo_box.currentIndex()
        current_addition_type_value = self.custom_ao_builder_ui.addition_type_combo_box.itemData(current_addition_type_index)
        if current_addition_type_value == TypeAOAddition.FIXED.value:
            self.custom_ao_builder_ui.num_input_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_input_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_output_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_output_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_inctrl_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_outctrl_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setVisible(True)

    def handle_change_custom_ao_order(self, parent, start, end, destination, row):
        ao = self.temp_custom_aos_in_builder.pop(start)
        if row > start:
            row -= 1
        self.temp_custom_aos_in_builder.insert(row, ao)

    def handle_custom_aos_current_item_changed(self, current):
        if current:  # When an item is selected
            if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
                self.preview_popup.close()
            current_index = self.custom_ao_builder_ui.aos_list_widget.row(current)
            self.custom_ao_builder_ui.remove_ao_btn.setEnabled(True)
            self.custom_ao_builder_ui.remove_ao_btn.setStyleSheet(  "QPushButton {\n"
                                                                    "    background-color: #3d3d3d;\n"
                                                                    "    color: #ffffff;\n"
                                                                    "    border: none;           /* Removed border completely */\n"
                                                                    "    border-radius: 4px;\n"
                                                                    "    min-width: 10px;\n"
                                                                    "    font-family: \"Calibri\";\n"
                                                                    "}\n"
                                                                    "\n"
                                                                    "QPushButton:hover {\n"
                                                                    "    background-color: #4a4a4a;  /* Simple color change on hover */\n"
                                                                    "}\n"
                                                                    "\n"
                                                                    "QPushButton:pressed {\n"
                                                                    "    background-color: #303030;\n"
                                                                    "}\n"
                                                                    "\n"
                                                                    "QPushButton:disabled {\n"
                                                                    "    background-color: #2d2d2d;\n"
                                                                    "    color: #808080;\n"
                                                                    "}")
            self.load_selected_custom_ao_settings(current_index)
            self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        else:
            self.custom_ao_builder_ui.remove_ao_btn.setEnabled(False)
            self.custom_ao_builder_ui.remove_ao_btn.setStyleSheet('background: #302E2E')
            self.hide_controls_in_custom_ao_builder_ui()
            self.custom_ao_builder_ui.preview_widget.clear()

    def load_selected_custom_ao_settings(self, selected_index):
        self.show_controls_in_custom_ao_builder_ui()
        selected_custom_ao = self.temp_custom_aos_in_builder[selected_index]
        self.custom_ao_builder_ui.name_line_edit.setText(selected_custom_ao['ao_name'])
        self.custom_ao_builder_ui.display_name_line_edit.setText(selected_custom_ao['display_name'])
        self.custom_ao_builder_ui.description_line_edit.setText(selected_custom_ao['description'])
        if ('is_icon_file_in_predefined_folder' in selected_custom_ao and not selected_custom_ao[
            'is_icon_file_in_predefined_folder']) or 'is_icon_file_in_predefined_folder' not in selected_custom_ao:
            icon_file_path = selected_custom_ao['icon_file_path']
            self.custom_ao_builder_ui.icon_line_edit.setText(icon_file_path)
            self.display_custom_ao_icon_in_builder(icon_file_path)
        elif 'is_icon_file_in_predefined_folder' in selected_custom_ao and selected_custom_ao['is_icon_file_in_predefined_folder']:
            icon_file_path = os.path.join(self.custom_folder_path, selected_custom_ao['icon_file_path'])
            self.custom_ao_builder_ui.icon_line_edit.setText(os.path.basename(icon_file_path))
            self.display_custom_ao_icon_in_builder(icon_file_path)
        self.custom_ao_builder_ui.is_float_point_check_box.setChecked(selected_custom_ao['is_float_point'])
        addition_type = selected_custom_ao['type_ao_addition']
        index = self.custom_ao_builder_ui.addition_type_combo_box.findData(addition_type)
        if 'num_input_sockets' in selected_custom_ao:
            original_num_input_sockets = selected_custom_ao['num_input_sockets']
        if 'num_output_sockets' in selected_custom_ao:
            original_num_output_sockets = selected_custom_ao['num_output_sockets']
        if 'num_inctrl_sockets' in selected_custom_ao:
            original_num_inctrl_sockets = selected_custom_ao['num_inctrl_sockets']
        if 'num_outctrl_sockets' in selected_custom_ao:
            original_num_outctrl_sockets = selected_custom_ao['num_outctrl_sockets']
        if index != -1:
            self.custom_ao_builder_ui.addition_type_combo_box.setCurrentIndex(index)
        if 'num_input_sockets' in selected_custom_ao:
            selected_custom_ao['num_input_sockets'] = original_num_input_sockets
        if 'num_output_sockets' in selected_custom_ao:
            selected_custom_ao['num_output_sockets'] = original_num_output_sockets
        if 'num_inctrl_sockets' in selected_custom_ao:
            selected_custom_ao['num_inctrl_sockets'] = original_num_inctrl_sockets
        if 'num_outctrl_sockets' in selected_custom_ao:
            selected_custom_ao['num_outctrl_sockets'] = original_num_outctrl_sockets
        if addition_type == TypeAOAddition.FIXED.value:
            self.custom_ao_builder_ui.num_input_sockets_spin_box.setValue(selected_custom_ao['num_input_sockets'])
            self.custom_ao_builder_ui.num_output_sockets_spin_box.setValue(selected_custom_ao['num_output_sockets'])
            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setValue(selected_custom_ao['num_inctrl_sockets'])
            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setValue(selected_custom_ao['num_outctrl_sockets'])
        self.custom_ao_builder_ui.collapsible_check_box.setChecked(selected_custom_ao['collapsible'])
        self.custom_ao_builder_ui.tuning_parameters_table.setRowCount(0)
        self.add_tuning_params_in_custom_ao_builder(selected_custom_ao['tuning_parameters'])
        self.custom_ao_builder_ui.is_popup_allowed_check_box.setChecked(selected_custom_ao['is_popup_allowed'])
        if selected_custom_ao['tuning_parameters']:
            self.custom_ao_builder_ui.is_popup_allowed_label.setVisible(True)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setVisible(True)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setEnabled(True)
        else:
            self.custom_ao_builder_ui.is_popup_allowed_label.setVisible(False)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setVisible(False)
        support_platforms = selected_custom_ao.get('support_platforms', set())
        model = self.custom_ao_builder_ui.supported_platforms_combobox.model()
        for i in range(1, model.rowCount()):
            item = model.item(i)
            i = i - 1
            if i in support_platforms:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def handle_tuning_params_table_item_selection_changed(self):
        selected_items = self.custom_ao_builder_ui.tuning_parameters_table.selectedItems()
        if selected_items:
            row_index = self.custom_ao_builder_ui.tuning_parameters_table.row(selected_items[0])
            total_rows = self.custom_ao_builder_ui.tuning_parameters_table.rowCount()
            if total_rows == 1:
                self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
                self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
            else:
                if row_index == 0:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(True)
                elif row_index == total_rows - 1:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(True)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
                else:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(True)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(True)

            self.custom_ao_builder_ui.remove_tuning_param_btn.setEnabled(True)
            self.custom_ao_builder_ui.remove_tuning_param_btn.setStyleSheet("QPushButton {\n"
                                                                            "    background-color: #3d3d3d;\n"
                                                                            "    color: #ffffff;\n"
                                                                            "    border: none;           /* Removed border completely */\n"
                                                                            "    border-radius: 4px;\n"
                                                                            "    min-width: 10px;\n"
                                                                            "    font-family: \"Calibri\";\n"
                                                                            "}\n"
                                                                            "\n"
                                                                            "QPushButton:hover {\n"
                                                                            "    background-color: #4a4a4a;  /* Simple color change on hover */\n"
                                                                            "}\n"
                                                                            "\n"
                                                                            "QPushButton:pressed {\n"
                                                                            "    background-color: #303030;\n"
                                                                            "}\n"
                                                                            "\n"
                                                                            "QPushButton:disabled {\n"
                                                                            "    background-color: #2d2d2d;\n"
                                                                            "    color: #808080;\n"
                                                                            "}")
            current_selected_tuning_param_index = self.get_current_selected_tuning_param_index()
            self.show_params_table()
            current_selected_tuning_param_name = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(
                current_selected_tuning_param_index, 0).text()
            for param_name, widget in self.preview_node.manager.widgetSet.items():
                if param_name == current_selected_tuning_param_name:
                    widget.trigger_preview_click_logic()
                    break
        else:
            self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
            self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
            self.custom_ao_builder_ui.remove_tuning_param_btn.setEnabled(False)
            self.custom_ao_builder_ui.remove_tuning_param_btn.setStyleSheet('background: #302E2E')
            # self.custom_ao_builder_dialog.resize(877, 857)
            if hasattr(self.custom_ao_builder_ui, 'params_widget'):
                self.custom_ao_builder_ui.params_widget.table.setRowCount(0)
            if hasattr(self.custom_ao_builder_ui, 'params_label'):
                self.custom_ao_builder_ui.params_label.close()
            if hasattr(self.custom_ao_builder_ui, 'params_frame'):
                self.custom_ao_builder_ui.params_frame.close()

    def show_params_table(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = self.get_current_selected_tuning_param_index()
        tuning_param_name = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(
            current_selected_tuning_param_index, 0).text()
        if not hasattr(self.custom_ao_builder_ui, 'params_label'):
            # Create Frame container
            self.custom_ao_builder_ui.params_frame = QFrame(self.custom_ao_builder_dialog)
            self.custom_ao_builder_ui.params_frame.setGeometry(QtCore.QRect(610, 470, 200, 35))
            self.custom_ao_builder_ui.params_frame.setFrameShape(QFrame.Box)
            self.custom_ao_builder_ui.params_frame.setFrameShadow(QFrame.Plain)
            self.custom_ao_builder_ui.params_frame.setLineWidth(1)
            # Make the frame invisible by setting the border color to be same as the dialog background color
            self.custom_ao_builder_ui.params_frame.setStyleSheet("""
                            QFrame {
                                        background-color: transparent;
                                        border: 1px solid #2b2b2b;
                                        border-radius: 0px;
                                    }
                        """)

            # Create layout for the frame
            frame_layout = QVBoxLayout(self.custom_ao_builder_ui.params_frame)
            frame_layout.setContentsMargins(1, 1, 1, 1)  # Set minimal margins

            # Create QTextEdit
            self.custom_ao_builder_ui.params_label = QTextEdit()
            self.custom_ao_builder_ui.params_label.setReadOnly(True)

            # Set stylesheet for customizing appearance
            self.custom_ao_builder_ui.params_label.setStyleSheet("""
                QTextEdit {
                    border: none;
                    background-color: transparent;
                    font-size: 10pt;
                    font-family: Calibri;
                }
                QScrollBar:horizontal {
                    height: 8px;
                }
                QScrollBar:vertical {
                    width: 8px;
                }
            """)

            # Configure scrollbar policies
            self.custom_ao_builder_ui.params_label.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.custom_ao_builder_ui.params_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            # Add QTextEdit to the frame's layout
            frame_layout.addWidget(self.custom_ao_builder_ui.params_label)
        self.custom_ao_builder_ui.params_label.setText(f' {tuning_param_name}')
        self.custom_ao_builder_ui.params_label.setStyleSheet("color: #f39c12; font-size: 14px; font-weight: bold;")
        self.custom_ao_builder_ui.params_label.show()
        self.custom_ao_builder_ui.params_frame.show()
        self.custom_ao_builder_ui.params_widget = ParametersTableWidget(current_selected_tuning_param_index,
                                                                        self.custom_ao_builder_dialog, self)
        self.custom_ao_builder_ui.params_widget.load_parameters(self.temp_custom_aos_in_builder
                                                                [current_selected_custom_ao_index]
                                                                ['tuning_parameters']
                                                                [current_selected_tuning_param_index]
                                                                ['parameters'])
        self.custom_ao_builder_ui.params_widget.setGeometry(QtCore.QRect(600, 500, 220, 200))
        self.custom_ao_builder_ui.params_widget.show()


    def handle_add_ao_btn_clicked(self):
        existing_ao_names = set()
        for custom_ao in self.temp_custom_aos_in_builder:
            existing_ao_names.add(custom_ao['ao_name'])
        name_to_give = 'Unnamed'
        i = 0
        while name_to_give in existing_ao_names:
            i += 1
            name_to_give = f'Unnamed ({i})'
        element = {
            'ao_name': name_to_give,
            'display_name': name_to_give,
            'description': '',
            'icon_file_path': '',
            'is_float_point': True,
            'type_ao_addition': TypeAOAddition.FIXED.value,
            'num_input_sockets': 0,
            'num_output_sockets': 0,
            'num_inctrl_sockets': 0,
            'num_outctrl_sockets': 0,
            'collapsible': True,
            'tuning_parameters': [],
            'is_popup_allowed': False,
            'support_platforms': {Target.PC.value} # Add support for PC by default
        }
        self.temp_custom_aos_in_builder.append(element)
        self.custom_ao_builder_ui.aos_list_widget.addItem(name_to_give)
        self.custom_ao_builder_ui.aos_list_widget.setCurrentItem(self.custom_ao_builder_ui.aos_list_widget.item(len(self.temp_custom_aos_in_builder)-1))
        self.show_controls_in_custom_ao_builder_ui()
        self.custom_ao_builder_ui.name_line_edit.setText(name_to_give)
        self.custom_ao_builder_ui.display_name_line_edit.setText(name_to_give)
        self.custom_ao_builder_ui.description_line_edit.setText('')
        self.custom_ao_builder_ui.icon_line_edit.setText('')
        self.display_custom_ao_icon_in_builder('')
        self.custom_ao_builder_ui.is_float_point_check_box.setChecked(True)
        self.custom_ao_builder_ui.addition_type_combo_box.setCurrentIndex(0)
        self.custom_ao_builder_ui.num_input_sockets_spin_box.setValue(0)
        self.custom_ao_builder_ui.num_output_sockets_spin_box.setValue(0)
        self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setValue(0)
        self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setValue(0)
        self.custom_ao_builder_ui.collapsible_check_box.setChecked(True)
        self.custom_ao_builder_ui.tuning_parameters_table.clearContents()
        self.custom_ao_builder_ui.is_popup_allowed_check_box.setChecked(False)
        model = self.custom_ao_builder_ui.supported_platforms_combobox.model()
        for i in range(1, model.rowCount()):
            item = model.item(i)
            i = i - 1
            if i in element['support_platforms']:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)


    def handle_remove_ao_btn_clicked(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_custom_ao_name = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['ao_name']
        # Confirmation dialog
        reply = QMessageBox.question(self, 'Confirmation',
                                     f"Are you sure you want to remove the AO '{current_selected_custom_ao_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.custom_ao_builder_ui.aos_list_widget.takeItem(current_selected_custom_ao_index)
            self.temp_custom_aos_in_builder.pop(current_selected_custom_ao_index)
            if current_selected_custom_ao_name:
                AUDIO_OBJECT_TEMP.pop(current_selected_custom_ao_name, None)
        else:
            return


    def handle_custom_ao_name_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_custom_ao = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        existing_names = set()
        for ao_name, _ in FLOW_NODES_TYPES.items():
            existing_names.add(ao_name)
        for ao in self.temp_custom_aos_in_builder:
            existing_names.add(ao['ao_name'])
        original_ao_name = current_selected_custom_ao['ao_name']
        existing_names.remove(original_ao_name)
        new_ao_name = self.custom_ao_builder_ui.name_line_edit.text()
        if original_ao_name == new_ao_name:
            return
        if not new_ao_name:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: Empty AO name. The value will revert to the original.")
            msg_box.setWindowTitle("Empty AO Name Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            self.custom_ao_builder_ui.name_line_edit.blockSignals(True)
            self.custom_ao_builder_ui.name_line_edit.setText(original_ao_name)
            self.custom_ao_builder_ui.name_line_edit.blockSignals(False)
        elif new_ao_name in existing_names:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: Duplicate AO name. The value will revert to the original.")
            msg_box.setWindowTitle("Duplicate AO Name Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            self.custom_ao_builder_ui.name_line_edit.blockSignals(True)
            self.custom_ao_builder_ui.name_line_edit.setText(original_ao_name)
            self.custom_ao_builder_ui.name_line_edit.blockSignals(False)
        else:
            if original_ao_name in AUDIO_OBJECT_TEMP:
                AUDIO_OBJECT_TEMP[new_ao_name] = copy.deepcopy(AUDIO_OBJECT_TEMP[original_ao_name])
                AUDIO_OBJECT_TEMP.pop(original_ao_name, None)
            self.custom_ao_builder_ui.aos_list_widget.item(current_selected_custom_ao_index).setText(new_ao_name)
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['ao_name'] = new_ao_name
            self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
            if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
                self.preview_popup.setWindowTitle(new_ao_name)
                self.preview_node.collapseNode()

    def handle_custom_ao_display_name_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_custom_ao = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        new_ao_display_name = self.custom_ao_builder_ui.display_name_line_edit.text()
        current_selected_custom_ao['display_name'] = new_ao_display_name

    def handle_custom_ao_description_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        new_ao_description = self.custom_ao_builder_ui.description_line_edit.toPlainText()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['description'] = new_ao_description

    def open_custom_ao_icon_dialog(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PNG File", "", "PNG Files (*.png)",
                                                   options=options)
        if file_path:
            all_icon_file_names = set()
            for ao in self.temp_custom_aos_in_builder:
                full_file_name = os.path.basename(ao['icon_file_path'])
                file_name, file_extension = os.path.splitext(full_file_name)
                all_icon_file_names.add(file_name)
            current_full_file_name = os.path.basename(file_path)
            file_name, file_extension = os.path.splitext(current_full_file_name)
            if file_name in all_icon_file_names:
                QMessageBox.warning(self, 'Warning', "The file name duplicates the icon's file name of existing AOs, please rename the file and select again.")
                return
            self.custom_ao_builder_ui.icon_line_edit.setText(file_path)
            self.display_custom_ao_icon_in_builder(file_path)
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['icon_file_path'] = file_path
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index][
                'is_icon_file_in_predefined_folder'] = False

    def handle_click_remove_icon_btn(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['icon_file_path'] = ''
        if 'is_icon_file_in_predefined_folder' in self.temp_custom_aos_in_builder[current_selected_custom_ao_index]:
            del self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['is_icon_file_in_predefined_folder']
        self.custom_ao_builder_ui.icon_line_edit.setText('')
        self.clear_custom_ao_icon_in_builder()

    def clear_custom_ao_icon_in_builder(self):
        pixmap = QPixmap()
        self.custom_ao_builder_ui.icon_image.setPixmap(pixmap)
        self.custom_ao_builder_ui.icon_image.setScaledContents(True)
        self.custom_ao_builder_ui.remove_icon_push_btn.setVisible(False)

    def display_custom_ao_icon_in_builder(self, file_path):
        pixmap = QPixmap(file_path)
        self.custom_ao_builder_ui.icon_image.setPixmap(pixmap)
        self.custom_ao_builder_ui.icon_image.setScaledContents(True)
        if not file_path:
            self.custom_ao_builder_ui.remove_icon_push_btn.setVisible(False)
        else:
            self.custom_ao_builder_ui.remove_icon_push_btn.setVisible(True)

    def handle_custom_ao_is_float_point_changed(self, state):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        if state == Qt.Checked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['is_float_point'] = True
        elif state == Qt.Unchecked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['is_float_point'] = False

    def handle_addition_type_current_index_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_index = self.custom_ao_builder_ui.addition_type_combo_box.currentIndex()
        current_value = self.custom_ao_builder_ui.addition_type_combo_box.itemData(current_index)
        if current_value == TypeAOAddition.FIXED.value:
            self.custom_ao_builder_ui.num_input_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_input_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_output_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_output_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_inctrl_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_outctrl_sockets_label.setVisible(True)
            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setVisible(True)
            self.custom_ao_builder_ui.num_input_sockets_spin_box.setValue(0)
            self.custom_ao_builder_ui.num_output_sockets_spin_box.setValue(0)
            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setValue(0)
            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setValue(0)
            if current_selected_custom_ao_index != -1:
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['type_ao_addition'] = current_value
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_input_sockets'] = 0
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_output_sockets'] = 0
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_inctrl_sockets'] = 0
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_outctrl_sockets'] = 0
        else:
            self.custom_ao_builder_ui.num_input_sockets_label.setVisible(False)
            self.custom_ao_builder_ui.num_input_sockets_spin_box.setVisible(False)
            self.custom_ao_builder_ui.num_output_sockets_label.setVisible(False)
            self.custom_ao_builder_ui.num_output_sockets_spin_box.setVisible(False)
            self.custom_ao_builder_ui.num_inctrl_sockets_label.setVisible(False)
            self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.setVisible(False)
            self.custom_ao_builder_ui.num_outctrl_sockets_label.setVisible(False)
            self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.setVisible(False)
            if current_selected_custom_ao_index != -1:
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['type_ao_addition'] = current_value
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_input_sockets'] = 1
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_output_sockets'] = 1
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_inctrl_sockets'] = 0
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['num_outctrl_sockets'] = 0
        if hasattr(self.custom_ao_builder_ui, 'preview_widget') and self.custom_ao_builder_ui.preview_widget is not None:
            self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()

    def handle_num_input_sockets_spin_box_value_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index][
            'num_input_sockets'] = self.custom_ao_builder_ui.num_input_sockets_spin_box.value()
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
            self.preview_node.collapseNode()

    def handle_num_output_sockets_spin_box_value_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index][
            'num_output_sockets'] = self.custom_ao_builder_ui.num_output_sockets_spin_box.value()
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
            self.preview_node.collapseNode()

    def handle_num_inctrl_sockets_spin_box_value_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index][
            'num_inctrl_sockets'] = self.custom_ao_builder_ui.num_inctrl_sockets_spin_box.value()
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
            self.preview_node.collapseNode()

    def handle_num_outctrl_sockets_spin_box_value_changed(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index][
            'num_outctrl_sockets'] = self.custom_ao_builder_ui.num_outctrl_sockets_spin_box.value()
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
            self.preview_node.collapseNode()

    def handle_custom_ao_collapsible_changed(self, state):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        if state == Qt.Checked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['collapsible'] = True
        elif state == Qt.Unchecked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['collapsible'] = False
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()

    def handle_add_tuning_param_btn_clicked(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        # Loop until a valid, non-empty, non-duplicate name is entered
        while True:
            # Create a custom input dialog
            dialog = QtWidgets.QInputDialog(self)
            dialog.setWindowTitle("Input name of tuning parameter")
            dialog.setLabelText("Please enter a name:")
            dialog.resize(400, dialog.sizeHint().height())

            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                name = dialog.textValue()
            else:
                return  # User canceled

            if not name:  # Name is empty
                QtWidgets.QMessageBox.warning(self, "Empty Name",
                                              "The name cannot be empty. Please enter a valid name.")
                continue
            if not re.match(r'^[a-zA-Z0-9_]+$', name):
                QtWidgets.QMessageBox.warning(self, "Invalid Name",
                                              "The name can only contain English letters, numbers, and underscores (_). Please enter a valid name.")
                continue
            # Check if the name already exists
            existing_names = [
                param['name'] for param in
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters']
            ]

            if name in existing_names:
                QtWidgets.QMessageBox.warning(self, "Duplicate Name",
                                              "The name already exists. Please use a different name.")
                continue

            break  # Valid name entered
        # self.custom_ao_builder_dialog.resize(877, 857)
        self.custom_ao_builder_ui.is_popup_allowed_label.setVisible(True)
        self.custom_ao_builder_ui.is_popup_allowed_check_box.setVisible(True)
        self.custom_ao_builder_ui.is_popup_allowed_check_box.setEnabled(True)
        tuning_params = [
            {
                'name': name,
                'gui_type_no': None,
                'parameters': []
            }
        ]
        self.add_tuning_params_in_custom_ao_builder(tuning_params)
        for tuning_param in tuning_params:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'].append({
                'name': tuning_param['name'],
                'gui_type_no': tuning_param['gui_type_no'],
                'parameters': tuning_param['parameters']
            })
        self.custom_ao_builder_ui.tuning_parameters_table.setCurrentCell(
            self.custom_ao_builder_ui.tuning_parameters_table.rowCount() - 1, 0)
        self.custom_ao_builder_ui.params_widget.table.setRowCount(0)

    def add_tuning_params_in_custom_ao_builder(self, tuning_params):
        for tuning_param in tuning_params:
            row_position = self.custom_ao_builder_ui.tuning_parameters_table.rowCount()
            self.custom_ao_builder_ui.tuning_parameters_table.insertRow(row_position)
            # self.custom_ao_builder_ui.tuning_parameters_table.setRowHeight(row_position, 150)
            name_item = QTableWidgetItem()
            name_edit = QLineEdit(tuning_param['name'])
            name_edit.textChanged.connect(
                lambda name_val, row=row_position: self.handle_tuning_param_name_changed(name_val, row))
            self.custom_ao_builder_ui.tuning_parameters_table.setItem(row_position, 0, name_item)
            self.custom_ao_builder_ui.tuning_parameters_table.setCellWidget(row_position, 0, name_edit)
            control_type_item = QTableWidgetItem()
            combo_box = ClickOnlyComboBox()
            for text, control_type_val in CONTROL_TYPES_FOR_OA:
                combo_box.addItem(text, control_type_val)
            gui_type_no = tuning_param['gui_type_no']
            if gui_type_no is None:
                combo_box.setCurrentIndex(-1)
            else:
                combo_box_index = combo_box.findData(gui_type_no)
                if combo_box_index != -1:
                    combo_box.setCurrentIndex(combo_box_index)
            combo_box.currentIndexChanged.connect(
                lambda index, row=row_position: self.handle_control_type_current_index_changed(index, row))
            self.custom_ao_builder_ui.tuning_parameters_table.setItem(row_position, 1, control_type_item)
            self.custom_ao_builder_ui.tuning_parameters_table.setCellWidget(row_position, 1, combo_box)

    def handle_move_tuning_param_up_btn_clicked(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        selected_custom_ao = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = selected_custom_ao['ao_name']
        tuning_params = selected_custom_ao['tuning_parameters']
        current_row_index = self.custom_ao_builder_ui.tuning_parameters_table.currentRow()
        tuning_param = tuning_params.pop(current_row_index)
        new_row_index = current_row_index - 1
        tuning_params.insert(new_row_index, tuning_param)
        self.custom_ao_builder_ui.tuning_parameters_table.setRowCount(0)
        AUDIO_OBJECT_TEMP[ao_name] = OrderedDict()
        self.add_tuning_params_in_custom_ao_builder(selected_custom_ao['tuning_parameters'])
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        self.custom_ao_builder_ui.tuning_parameters_table.selectRow(new_row_index)

    def handle_move_tuning_param_down_btn_clicked(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        selected_custom_ao = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = selected_custom_ao['ao_name']
        tuning_params = selected_custom_ao['tuning_parameters']
        current_row_index = self.custom_ao_builder_ui.tuning_parameters_table.currentRow()
        tuning_param = tuning_params.pop(current_row_index)
        new_row_index = current_row_index + 1
        tuning_params.insert(new_row_index, tuning_param)
        self.custom_ao_builder_ui.tuning_parameters_table.setRowCount(0)
        AUDIO_OBJECT_TEMP[ao_name] = OrderedDict()
        self.add_tuning_params_in_custom_ao_builder(selected_custom_ao['tuning_parameters'])
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        self.custom_ao_builder_ui.tuning_parameters_table.selectRow(new_row_index)

    def handle_tuning_param_name_changed(self, name_val, row):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        tuning_parameters = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters']

        # Check for duplicate values or empty string
        existing_names = [param['name'] for param in tuning_parameters]
        if name_val == '':
            # Show error message box for empty string
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: The value cannot be an empty string. The value will revert to the original.")
            msg_box.setWindowTitle("Empty String Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            # Revert to the original value
            original_name = tuning_parameters[row]['name']
            # Get the corresponding QLineEdit widget and set it back to the original value
            line_edit = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(row, 0)
            line_edit.blockSignals(True)
            line_edit.setText(original_name)
            line_edit.blockSignals(False)
        elif name_val in existing_names:
            # Show error message box for duplicate value
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: Duplicate value. The value will revert to the original.")
            msg_box.setWindowTitle("Duplicate Value Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            # Revert to the original value
            original_name = tuning_parameters[row]['name']
            # Get the corresponding QLineEdit widget and set it back to the original value
            line_edit = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(row, 0)
            line_edit.blockSignals(True)
            line_edit.setText(original_name)
            line_edit.blockSignals(False)
        elif not re.match(r'^[a-zA-Z0-9_]+$', name_val):
            # Show error message box for empty string
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: The name can only contain English letters, numbers, and underscores. The value will revert to the original.")
            msg_box.setWindowTitle("Invalid Character Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            # Revert to the original value
            original_name = tuning_parameters[row]['name']
            # Get the corresponding QLineEdit widget and set it back to the original value
            line_edit = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(row, 0)
            line_edit.blockSignals(True)
            line_edit.setText(original_name)
            line_edit.blockSignals(False)
        else:
            original_name = tuning_parameters[row]['name']
            ao_name = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['ao_name']
            AUDIO_OBJECT_TEMP[ao_name][name_val] = copy.deepcopy(AUDIO_OBJECT_TEMP[ao_name].get(original_name, {}))
            AUDIO_OBJECT_TEMP[ao_name].pop(original_name, None)
            # Update the value
            tuning_parameters[row]['name'] = name_val
            if hasattr(self.custom_ao_builder_ui, 'params_label'):
                self.custom_ao_builder_ui.params_label.setText(f' {name_val}')

    def handle_control_type_current_index_changed(self, index, row):
        if hasattr(self, 'preview_popup'):
            was_preview_popup_visible = self.preview_popup.isVisible()
            if was_preview_popup_visible:
                original_position = self.preview_popup.pos()
                self.preview_popup.close()
            else:
                original_position = None
        else:
            was_preview_popup_visible = False
            original_position = None
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = self.get_current_selected_tuning_param_index()
        combo_box = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(row, 1)
        selected_value = int(combo_box.currentData())
        parameters = []
        for required_parameter in CONTROLS_MAPPING[selected_value].required_parameters:
            required_parameter_copy = copy.deepcopy(required_parameter)
            required_parameter_copy['required'] = True
            parameters.append(required_parameter_copy)
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['gui_type_no'] = selected_value
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'] = parameters
        # self.custom_ao_builder_dialog.resize(1127, 857)
        self.custom_ao_builder_ui.params_widget.load_parameters(parameters)
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if was_preview_popup_visible and hasattr(self, 'preview_popup'):
            self.preview_node.onDoubleClicked(None)
            if original_position:
                self.preview_popup.move(original_position)

    def handle_remove_tuning_param_btn_clicked(self):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = self.get_current_selected_tuning_param_index()
        current_selected_custom_ao = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = current_selected_custom_ao['ao_name']
        self.custom_ao_builder_ui.tuning_parameters_table.removeRow(current_selected_tuning_param_index)
        tuning_parameter_name = self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['name']
        self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'].pop(
            current_selected_tuning_param_index)
        AUDIO_OBJECT_TEMP[ao_name].pop(tuning_parameter_name, None)
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if self.custom_ao_builder_ui.tuning_parameters_table.rowCount() == 0:
            self.custom_ao_builder_ui.is_popup_allowed_label.setVisible(False)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setVisible(False)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setEnabled(False)
            self.custom_ao_builder_ui.is_popup_allowed_check_box.setChecked(False)
        current_selected_tuning_param_index = self.get_current_selected_tuning_param_index()
        if current_selected_tuning_param_index != -1:
            self.show_params_table()
        # Iterate through each row in the tuning parameters table to update signal connections.
        for i in range(self.custom_ao_builder_ui.tuning_parameters_table.rowCount()):
            name_edit = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(i, 0)
            try:
                name_edit.textChanged.disconnect()
            except:
                pass
            name_edit.textChanged.connect(
                lambda name_val, row=i: self.handle_tuning_param_name_changed(name_val, row))
            combo_box = self.custom_ao_builder_ui.tuning_parameters_table.cellWidget(i, 1)
            try:
                combo_box.currentIndexChanged.disconnect()
            except:
                pass
            combo_box.currentIndexChanged.connect(
                lambda index, row=i: self.handle_control_type_current_index_changed(index, row))
        if current_selected_tuning_param_index == -1:
            self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
            self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
        else:
            total_rows = self.custom_ao_builder_ui.tuning_parameters_table.rowCount()
            if total_rows == 1:
                self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
                self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
            else:
                if current_selected_tuning_param_index == 0:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(False)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(True)
                elif current_selected_tuning_param_index == total_rows - 1:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(True)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(False)
                else:
                    self.custom_ao_builder_ui.move_tuning_param_up_btn.setEnabled(True)
                    self.custom_ao_builder_ui.move_tuning_param_down_btn.setEnabled(True)


    def handle_is_popup_allowed_changed(self, state):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        if state == Qt.Checked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['is_popup_allowed'] = True
            self.custom_ao_builder_ui.collapsible_check_box.setChecked(True)
            self.custom_ao_builder_ui.collapsible_check_box.setDisabled(True)
        elif state == Qt.Unchecked:
            self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['is_popup_allowed'] = False
            if hasattr(self, 'preview_popup') and self.preview_popup.isVisible():
                self.preview_popup.close()
            self.custom_ao_builder_ui.collapsible_check_box.setEnabled(True)
        self.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()

    def handle_supported_platforms_item_changed(self, item):
        current_selected_custom_ao_index = self.get_current_selected_custom_ao_index()
        index = item.index().row()
        if index == 0:
            if item.checkState() == Qt.Checked:
                self.select_all_items(Qt.Checked)
            elif item.checkState() == Qt.Unchecked:
                self.select_all_items(Qt.Unchecked)
        else:
            index -= 1
            if item.checkState() == Qt.Checked:
                self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['support_platforms'].add(index)
            else:
                if index in self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['support_platforms']:
                    self.temp_custom_aos_in_builder[current_selected_custom_ao_index]['support_platforms'].remove(index)
            self.update_select_all_state()

    def select_all_items(self, state):
        # Set all items (except "Select all") to the given state
        for row in range(1, self.supported_platforms_combobox_model.rowCount()):
            item = self.supported_platforms_combobox_model.item(row, 0)
            item.setCheckState(state)

    def update_select_all_state(self):
        checked_count = 0
        total_count = self.supported_platforms_combobox_model.rowCount() - 1  # Exclude "Select all"
        for row in range(1, self.supported_platforms_combobox_model.rowCount()):
            item = self.supported_platforms_combobox_model.item(row, 0)
            if item.checkState() == Qt.Checked:
                checked_count += 1
        select_all_item = self.supported_platforms_combobox_model.item(0, 0)  # "Select all" item
        if checked_count == total_count:
            select_all_item.setCheckState(Qt.Checked)
            select_all_item.setText(f'All({total_count}) selected')
        elif checked_count == 0:
            select_all_item.setCheckState(Qt.Unchecked)
            select_all_item.setText('Select all')
        else:
            select_all_item.setCheckState(Qt.PartiallyChecked)
            select_all_item.setText(f'{checked_count}/{total_count} selected')

    def get_current_selected_tuning_param_index(self):
        return self.custom_ao_builder_ui.tuning_parameters_table.currentIndex().row()

    def get_current_selected_custom_ao_index(self):
        return self.custom_ao_builder_ui.aos_list_widget.currentIndex().row()

    def popup_signal_flow_diff_window(self):
        self.signal_flow_diff_q_widget = QWidget(self)
        self.signal_flow_diff_q_widget.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.signal_flow_diff_q_widget.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.signal_flow_diff_q_widget.setStyleSheet("background-color: #474747")
        self.signal_flow_diff_q_widget.setFixedSize(485, 130)
        self.signal_flow_diff_ui = SignalFlowDiffUi()
        self.signal_flow_diff_ui.setupUi(self.signal_flow_diff_q_widget)
        self.signal_flow_diff_q_widget.setWindowTitle('Signal Flow Diff')
        self.signal_flow_diff_ui.orig_proj_push_btn.clicked.connect(self.load_orig_proj)
        self.signal_flow_diff_ui.chg_proj_push_btn.clicked.connect(self.load_chg_proj)
        self.signal_flow_diff_ui.use_edited_flow_check_box.stateChanged.connect(self.use_edited_flow_check_box_state_changed)
        self.signal_flow_diff_ui.buttonBox.clicked.connect(self.handle_signal_flow_diff_dialog_options)
        # region bring in the settings from the last operation
        self.signal_flow_diff_ui.orig_proj_line_edit.setText(self.signal_flow_diff_orig_proj_file_path)
        self.signal_flow_diff_ui.chg_proj_line_edit.setText(self.signal_flow_diff_chg_proj_file_path)
        self.signal_flow_diff_ui.use_edited_flow_check_box.setChecked(self.signal_flow_diff_is_use_current_flow)
        # endregion
        self.signal_flow_diff_q_widget.show()
        # Track user action "Launch Signal Flow Diff"
        self.tracker = TrackManager()
        self.tracker.track_user_action(action=7, license=self.license_mechanism)

    def load_orig_proj(self):
        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.hide()
        try:
            selected_file_path, selected_filter_str = QFileDialog.getOpenFileName(None, 'Load proj file',
                                                                                  getFileDialogDirectory(),
                                                                                  'Flow Studio Project File (*.proj)')
            if selected_file_path != '' and os.path.isfile(selected_file_path):
                self.signal_flow_diff_ui.orig_proj_line_edit.setText(selected_file_path)
                self.signal_flow_diff_orig_proj_file_path = selected_file_path
        except Exception as e:
            dumpException(e)
        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.show()

    def load_chg_proj(self):
        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.hide()
        try:
            selected_file_path, selected_filter_str = QFileDialog.getOpenFileName(None, 'Load proj file',
                                                                                  getFileDialogDirectory(),
                                                                                  'Flow Studio Project File (*.proj)')
            if selected_file_path != '' and os.path.isfile(selected_file_path):
                self.signal_flow_diff_ui.chg_proj_line_edit.setText(selected_file_path)
                self.signal_flow_diff_chg_proj_file_path = selected_file_path
        except Exception as e:
            dumpException(e)
        for gui_widget in FLOW_Window.all_window_objects:
            gui_widget.show()

    def use_edited_flow_check_box_state_changed(self, state):
        if state == Qt.Checked:
            self.signal_flow_diff_ui.chg_proj_line_edit.setText('')
            self.signal_flow_diff_ui.chg_proj_line_edit.setStyleSheet("background: #302E2E")
            self.signal_flow_diff_ui.chg_proj_push_btn.setStyleSheet("background: #302E2E")
            self.signal_flow_diff_ui.chg_proj_push_btn.setEnabled(False)
            self.signal_flow_diff_is_use_current_flow = True
            self.signal_flow_diff_chg_proj_file_path = ''
        else:
            self.signal_flow_diff_ui.chg_proj_line_edit.setStyleSheet('')
            self.signal_flow_diff_ui.chg_proj_push_btn.setStyleSheet('')
            self.signal_flow_diff_ui.chg_proj_push_btn.setEnabled(True)
            self.signal_flow_diff_is_use_current_flow = False

    def handle_signal_flow_diff_dialog_options(self, button):
        curr_btn = self.signal_flow_diff_ui.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            orig_proj_file_path = self.signal_flow_diff_ui.orig_proj_line_edit.text()
            chg_proj_file_path = self.signal_flow_diff_ui.chg_proj_line_edit.text()
            is_use_current_flow = self.signal_flow_diff_ui.use_edited_flow_check_box.isChecked()
            current_window = self.getCurrentNodeEditorWidget()
            if orig_proj_file_path == '':
                QMessageBox.warning(self, 'Please select original project file',
                                    f'Please select original project file.')
                return
            elif not is_use_current_flow and chg_proj_file_path == '':
                QMessageBox.warning(self, 'Please select changed project file',
                                    f'Please select changed project file.')
                return
            elif is_use_current_flow and current_window is None:
                QMessageBox.warning(self, 'Current flow is empty',
                                    f'Please click "New" button to start a new flow.')
                return
            else:
                if (self.project_folder_path is not None and is_use_current_flow is False and os.path.normpath(os.path.join(
                        self.project_folder_path, self.project_file_name())) != os.path.normpath(orig_proj_file_path) and os.path.normpath(os.path.join(
                        self.project_folder_path, self.project_file_name())) != os.path.normpath(chg_proj_file_path)) or (self.project_folder_path is None and is_use_current_flow is False):
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('Confirm whether to open changed project')
                    msg_box.setText('Do you want to open the changed project for comparison?')
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    result = msg_box.exec_()
                    if result == QMessageBox.Yes:
                        res_file_open = self.onFileOpen(project_file_path=chg_proj_file_path)
                        if not res_file_open:
                            return
                        self.signal_flow_diff_ui.use_edited_flow_check_box.setChecked(True)
                        is_use_current_flow = self.signal_flow_diff_ui.use_edited_flow_check_box.isChecked()
                try:
                    orig_proj_temp_folder = tempfile.mkdtemp()
                except PermissionError:
                    QMessageBox.critical(
                        self,
                        'Error',
                        f'Error code:{PERMISSION_ERROR_WHEN_CREATE_TEMP_FOLDER}'
                    )
                    return
                # The original project file has an issue. Please choose another file.
                if not self.unCompressZIPFile(orig_proj_file_path, orig_proj_temp_folder):
                    QMessageBox.warning(self, 'The original project file has an issue',
                                        f'The original project file has an issue. Please choose another file.')
                    return
                file_names = os.listdir(orig_proj_temp_folder)
                main_file = orig_proj_temp_folder + '/main.json'
                if not os.path.exists(main_file):
                    QMessageBox.warning(self, 'The original project file has an issue',
                                        f'The original project file has an issue. Please choose another file.')
                    return
                orig_passwords = {}
                for file_name in file_names:
                    if file_name.endswith('.json'):
                        file_path = orig_proj_temp_folder + '/' + file_name
                        with open(file_path) as f:
                            file_data = json.load(f)
                            if 'is_encrypted' in file_data and file_data['is_encrypted']:
                                correct_password = AESOperation().decrypt_string(password=SECRET_KEY,
                                                                                 input_string=file_data[
                                                                                     'password'])
                                orig_passwords[file_name] = correct_password
                chg_passwords = {}
                if chg_proj_file_path != '':
                    try:
                        chg_proj_temp_folder = tempfile.mkdtemp()
                    except PermissionError:
                        QMessageBox.critical(
                            self,
                            'Error',
                            f'Error code:{PERMISSION_ERROR_WHEN_CREATE_TEMP_FOLDER}'
                        )
                        return
                    # The original project file has an issue. Please choose another file.
                    if not self.unCompressZIPFile(chg_proj_file_path, chg_proj_temp_folder):
                        QMessageBox.warning(self, 'The changed project file has an issue',
                                            f'The changed project file has an issue. Please choose another file.')
                        return
                    file_names = os.listdir(chg_proj_temp_folder)
                    main_file = chg_proj_temp_folder + '/main.json'
                    if not os.path.exists(main_file):
                        QMessageBox.warning(self, 'The changed project file has an issue',
                                            f'The changed project file has an issue. Please choose another file.')
                        return
                    for file_name in file_names:
                        if file_name.endswith('.json'):
                            file_path = chg_proj_temp_folder + '/' + file_name
                            with open(file_path) as f:
                                file_data = json.load(f)
                                if 'is_encrypted' in file_data and file_data['is_encrypted']:
                                    correct_password = AESOperation().decrypt_string(password=SECRET_KEY,
                                                                                     input_string=file_data[
                                                                                         'password'])
                                    chg_passwords[file_name] = correct_password
                else:
                    main_window = self.findMain().widget()
                    current_window = self.window().getCurrentNodeEditorWidget()
                    nodes_in_main = main_window.scene.nodes
                    for node in nodes_in_main:
                        if node.op_code == OP_NODE_SUBPATCH:
                            self.window().open_subwindow_in_subpatch_recursively(node.title)
                            self.window().setActiveSubWindow(current_window.parent())
                    # find windows which hasn't been inputted password
                    for window in self.window().mdiArea.subWindowList():
                        if hasattr(window.widget(), 'encrypted'):
                            if window.widget().encrypted and not window.widget().already_input_password:
                                chg_passwords[window.widget().title] = window.widget().correct_password
                                self.window().close_sub_window(window)
                                continue
                        if hasattr(window.widget(), 'close_if_no_problem'):
                            if window.widget().close_if_no_problem:
                                self.window().close_sub_window(window)
                orig_input_passwords, chg_input_passwords = {}, {}
                if orig_passwords or chg_passwords:
                    user_input_password_dialog = UserInputPasswordDialog(orig_passwords, chg_passwords, self)
                    orig_input_passwords, chg_input_passwords = user_input_password_dialog.get_user_input_data()
                    if not orig_input_passwords and not chg_input_passwords:  # When the user cancels in the password input dialog.
                        return
                # region original project
                hidden_dir = orig_proj_temp_folder
                file_names = os.listdir(hidden_dir)
                file_names.remove('main.json')
                file_names.sort()
                file_names.insert(0, 'main.json')
                orig_aos = []
                orig_edges = []
                sub_patch_title_name_mappings = {}
                if len(file_names) > 1:
                    for file_name in file_names:
                        if file_name == 'main.json':
                            continue
                        else:
                            found = False
                            for inner_file_name in file_names:
                                if inner_file_name.endswith('.json'):
                                    file_path = hidden_dir + '/' + inner_file_name
                                    with open(file_path) as f:
                                        file_data = json.load(f)
                                        for node in file_data['nodes']:
                                            if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == file_name.rstrip('.json'):
                                                sub_patch_title_name_mappings[file_name.rstrip('.json')] = f"{node['type']}_{node['designator']}"
                                                found = True
                                                break
                                        if found:
                                            break
                for file_name in file_names:
                    if file_name.endswith('.json'):
                        file_path = hidden_dir + '/' + file_name
                        with open(file_path) as f:
                            file_data = json.load(f)
                            if 'is_encrypted' in file_data and file_data['is_encrypted']:
                                if orig_passwords[file_name] == orig_input_passwords[file_name]:
                                    file_data = json.loads(AESOperation().decrypt_string(password=orig_passwords[file_name],
                                                                                         input_string=file_data['object']))
                                else:
                                    continue
                            for node in file_data['nodes']:
                                adjusted_node = {
                                    'id': node['id'],
                                    'name': f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]}"
                                    if node['op_code'] == OP_NODE_INLET or node['op_code'] == OP_NODE_OUTLET
                                    else f"{node['type']}_{node['designator']}",
                                    'title': node['title'],
                                    'ao_code': node['op_code'],
                                    'parameters': node['content'],
                                    'num_input_sockets': len(node['inputs']) if 'inputs' in node else 0,
                                    'num_output_sockets': len(node['outputs']) if 'outputs' in node else 0,
                                    'num_in_ctrl_sockets': len(node['inctrls']) if 'inctrls' in node else 0,
                                    'num_out_ctrl_sockets': len(node['outctrls']) if 'outctrls' in node else 0
                                }
                                orig_aos.append(adjusted_node)
                            for edge in file_data['edges']:
                                edge_id = edge['id']
                                edge_start_socket_id = edge['start']
                                edge_end_socket_id = edge['end']
                                start_socket = ''
                                end_socket = ''
                                start_socket_found = False
                                end_socket_found = False
                                for node in file_data['nodes']:
                                    for output_socket in node['outputs']:
                                        if edge_start_socket_id == output_socket['id']:
                                            start_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]} output {output_socket['index']}" \
                                            if node['op_code'] == OP_NODE_INLET or node['op_code'] == OP_NODE_OUTLET else \
                                            f"{node['type']}_{node['designator']} output {output_socket['index']}"
                                            start_socket_found = True
                                            break
                                    if not start_socket_found:
                                        if 'outctrls' in node:
                                            for out_ctrl_socket in node['outctrls']:
                                                if edge_start_socket_id == out_ctrl_socket['id']:
                                                    start_socket = f"{node['type']}_{node['designator']} out ctrl {out_ctrl_socket['index']}"
                                                    start_socket_found = True
                                                    break
                                    for input_socket in node['inputs']:
                                        if edge_end_socket_id == input_socket['id']:
                                            end_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]} input {input_socket['index']}" \
                                            if node['op_code'] == OP_NODE_INLET or node['op_code'] == OP_NODE_OUTLET else \
                                            f"{node['type']}_{node['designator']} input {input_socket['index']}"
                                            end_socket_found = True
                                            break
                                    if not end_socket_found:
                                        if 'inctrls' in node:
                                            for in_ctrl_socket in node['inctrls']:
                                                if edge_end_socket_id == in_ctrl_socket['id']:
                                                    end_socket = f"{node['type']}_{node['designator']} in ctrl {in_ctrl_socket['index']}"
                                                    end_socket_found = True
                                                    break
                                    if start_socket_found and end_socket_found:
                                        break
                                adjusted_edge = {
                                    'id': edge_id,
                                    'description': f'{start_socket} → {end_socket}',
                                }
                                orig_edges.append(adjusted_edge)
                # endregion
                chg_aos = []
                chg_edges = []
                # region changed project
                if chg_proj_file_path != '':
                    hidden_dir = chg_proj_temp_folder
                    file_names = os.listdir(hidden_dir)
                    file_names.remove('main.json')
                    file_names.sort()
                    file_names.insert(0, 'main.json')
                    sub_patch_title_name_mappings = {}
                    if len(file_names) > 1:
                        for file_name in file_names:
                            if file_name == 'main.json':
                                continue
                            else:
                                found = False
                                for inner_file_name in file_names:
                                    if inner_file_name.endswith('.json'):
                                        file_path = hidden_dir + '/' + inner_file_name
                                        with open(file_path) as f:
                                            file_data = json.load(f)
                                            for node in file_data['nodes']:
                                                if node['op_code'] == OP_NODE_SUBPATCH and node[
                                                    'title'] == file_name.rstrip('.json'):
                                                    sub_patch_title_name_mappings[file_name.rstrip(
                                                        '.json')] = f"{node['type']}_{node['designator']}"
                                                    found = True
                                                    break
                                            if found:
                                                break
                    for file_name in file_names:
                        if file_name.endswith('.json'):
                            file_path = hidden_dir + '/' + file_name
                            with open(file_path) as f:
                                file_data = json.load(f)
                                if 'is_encrypted' in file_data and file_data['is_encrypted']:
                                    if chg_passwords[file_name] == chg_input_passwords[file_name]:
                                        file_data = json.loads(
                                            AESOperation().decrypt_string(password=chg_passwords[file_name],
                                                                          input_string=file_data['object']))
                                    else:
                                        continue
                                for node in file_data['nodes']:
                                    adjusted_node = {
                                        'id': node['id'],
                                        'name': f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]}"
                                        if node['op_code'] == OP_NODE_INLET or node['op_code'] == OP_NODE_OUTLET
                                        else f"{node['type']}_{node['designator']}",
                                        'title': node['title'],
                                        'ao_code': node['op_code'],
                                        'parameters': node['content'],
                                        'num_input_sockets': len(node['inputs']) if 'inputs' in node else 0,
                                        'num_output_sockets': len(node['outputs']) if 'outputs' in node else 0,
                                        'num_in_ctrl_sockets': len(node['inctrls']) if 'inctrls' in node else 0,
                                        'num_out_ctrl_sockets': len(node['outctrls']) if 'outctrls' in node else 0
                                    }
                                    chg_aos.append(adjusted_node)
                                for edge in file_data['edges']:
                                    edge_id = edge['id']
                                    edge_start_socket_id = edge['start']
                                    edge_end_socket_id = edge['end']
                                    start_socket = ''
                                    end_socket = ''
                                    start_socket_found = False
                                    end_socket_found = False
                                    for node in file_data['nodes']:
                                        for output_socket in node['outputs']:
                                            if edge_start_socket_id == output_socket['id']:
                                                start_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]} output {output_socket['index']}" \
                                                    if node['op_code'] == OP_NODE_INLET or node[
                                                    'op_code'] == OP_NODE_OUTLET else \
                                                    f"{node['type']}_{node['designator']} output {output_socket['index']}"
                                                start_socket_found = True
                                                break
                                        if not start_socket_found:
                                            if 'outctrls' in node:
                                                for out_ctrl_socket in node['outctrls']:
                                                    if edge_start_socket_id == out_ctrl_socket['id']:
                                                        start_socket = f"{node['type']}_{node['designator']} out ctrl {out_ctrl_socket['index']}"
                                                        start_socket_found = True
                                                        break
                                        for input_socket in node['inputs']:
                                            if edge_end_socket_id == input_socket['id']:
                                                end_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[file_name.rstrip('.json')]} input {input_socket['index']}" \
                                                    if node['op_code'] == OP_NODE_INLET or node[
                                                    'op_code'] == OP_NODE_OUTLET else \
                                                    f"{node['type']}_{node['designator']} input {input_socket['index']}"
                                                end_socket_found = True
                                                break
                                        if not end_socket_found:
                                            if 'inctrls' in node:
                                                for in_ctrl_socket in node['inctrls']:
                                                    if edge_end_socket_id == in_ctrl_socket['id']:
                                                        end_socket = f"{node['type']}_{node['designator']} in ctrl {in_ctrl_socket['index']}"
                                                        end_socket_found = True
                                                        break
                                        if start_socket_found and end_socket_found:
                                            break
                                    adjusted_edge = {
                                        'id': edge_id,
                                        'description': f'{start_socket} → {end_socket}',
                                    }
                                    chg_edges.append(adjusted_edge)
                else:
                    main_window = self.findMain().widget()
                    current_window = self.window().getCurrentNodeEditorWidget()
                    nodes_in_main = main_window.scene.nodes
                    for node in nodes_in_main:
                        if node.op_code == OP_NODE_SUBPATCH:
                            self.window().open_subwindow_in_subpatch_recursively(node.title)
                            self.window().setActiveSubWindow(current_window.parent())
                    sub_patch_title_name_mappings = {}
                    for window in self.window().mdiArea.subWindowList():
                        if type(window.widget()) is not FLOW_Sub_Window:
                            title = window.widget().title.rstrip('.json')
                            found = False
                            for inner_loop_window in self.window().mdiArea.subWindowList():
                                for node in inner_loop_window.widget().scene.nodes:
                                    if node.op_code == OP_NODE_SUBPATCH and node.title == title:
                                        sub_patch_title_name_mappings[title] = f'{node.content_label_objname}_{node.designator}'
                                        found = True
                                        break
                                if found:
                                    break
                    for window in self.window().mdiArea.subWindowList():
                        if type(window.widget()) is FLOW_Sub_Window or (type(window.widget()) is not FLOW_Sub_Window and window.widget().title not in chg_passwords) or \
                           (type(window.widget()) is not FLOW_Sub_Window and window.widget().title in chg_passwords and chg_passwords[window.widget().title] == chg_input_passwords[window.widget().title]):
                            for node in window.widget().scene.nodes:
                                node = node.serialize()
                                adjusted_node = {
                                    'id': node['id'],
                                    'name': f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[window.widget().title.rstrip('.json')]}"
                                    if node['op_code'] == OP_NODE_INLET or node['op_code'] == OP_NODE_OUTLET
                                    else f"{node['type']}_{node['designator']}",
                                    'title': node['title'],
                                    'ao_code': node['op_code'],
                                    'parameters': node['content'],
                                    'num_input_sockets': len(node['inputs']),
                                    'num_output_sockets': len(node['outputs']),
                                    'num_in_ctrl_sockets': len(node['inctrls']),
                                    'num_out_ctrl_sockets': len(node['outctrls'])
                                }
                                chg_aos.append(adjusted_node)
                            for edge in window.widget().scene.edges:
                                edge = edge.serialize()
                                edge_id = edge['id']
                                edge_start_socket_id = edge['start']
                                edge_end_socket_id = edge['end']
                                start_socket = ''
                                end_socket = ''
                                start_socket_found = False
                                end_socket_found = False
                                for node in window.widget().scene.nodes:
                                    node = node.serialize()
                                    for output_socket in node['outputs']:
                                        if edge_start_socket_id == output_socket['id']:
                                            start_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[window.widget().title.rstrip('.json')]} output {output_socket['index']}" \
                                                if node['op_code'] == OP_NODE_INLET or node[
                                                'op_code'] == OP_NODE_OUTLET else \
                                                f"{node['type']}_{node['designator']} output {output_socket['index']}"
                                            start_socket_found = True
                                            break
                                    if not start_socket_found:
                                        for out_ctrl_socket in node['outctrls']:
                                            if edge_start_socket_id == out_ctrl_socket['id']:
                                                start_socket = f"{node['type']}_{node['designator']} out ctrl {out_ctrl_socket['index']}"
                                                start_socket_found = True
                                                break
                                    for input_socket in node['inputs']:
                                        if edge_end_socket_id == input_socket['id']:
                                            end_socket = f"{node['type']}_{node['designator']} in {sub_patch_title_name_mappings[window.widget().title.rstrip('.json')]} input {input_socket['index']}" \
                                                if node['op_code'] == OP_NODE_INLET or node[
                                                'op_code'] == OP_NODE_OUTLET else \
                                                f"{node['type']}_{node['designator']} input {input_socket['index']}"
                                            end_socket_found = True
                                            break
                                    if not end_socket_found:
                                        for in_ctrl_socket in node['inctrls']:
                                            if edge_end_socket_id == in_ctrl_socket['id']:
                                                end_socket = f"{node['type']}_{node['designator']} in ctrl {in_ctrl_socket['index']}"
                                                end_socket_found = True
                                                break
                                    if start_socket_found and end_socket_found:
                                        break
                                adjusted_edge = {
                                    'id': edge_id,
                                    'description': f'{start_socket} → {end_socket}',
                                }
                                chg_edges.append(adjusted_edge)
                            if hasattr(window.widget(), 'encrypted') and window.widget().encrypted:
                                window.widget().already_input_password = True
                        if hasattr(window.widget(), 'close_if_no_problem'):
                            if window.widget().close_if_no_problem:
                                self.window().close_sub_window(window)
                # endregion
            # region compare audio objects
            details = []
            orig_ao_names = [orig_ao['name'] for orig_ao in orig_aos]
            chg_ao_names = [chg_ao['name'] for chg_ao in chg_aos]
            for chg_ao in chg_aos:
                chg_ao_name = chg_ao['name']
                chg_ao_code = chg_ao['ao_code']
                if chg_ao_name in orig_ao_names:  # represents that it may be "changed"
                    orig_ao = orig_aos[orig_ao_names.index(chg_ao_name)]
                    for key, value in chg_ao.items():
                        if key != 'id' and key != 'parameters':
                            if orig_ao[key] != value:
                                details.append({
                                    'type': 'changed',
                                    'ao_or_edge': 'ao',
                                    'ao_name': chg_ao_name,
                                    'field_name': key,
                                    'original_value': orig_ao[key],
                                    'changed_value': value,
                                    'id': chg_ao['id']
                                })
                        elif key == 'parameters':
                            for parameter_name, changed_parameter_value in value.items():
                                if parameter_name in orig_ao[key] and orig_ao[key][parameter_name] != changed_parameter_value:
                                    details.append({
                                        'type': 'changed',
                                        'ao_or_edge': 'ao',
                                        'ao_name': chg_ao_name,
                                        'field_name': f'param: {parameter_name}',
                                        'original_value': orig_ao[key][parameter_name],
                                        'changed_value': changed_parameter_value,
                                        'id': chg_ao['id']
                                    })
                else:  # This AO is newly added
                    details.append({
                        'type': 'added',
                        'ao_or_edge': 'ao',
                        'ao_name': chg_ao_name,
                        'details': chg_ao_name,
                        'id': chg_ao['id']
                    })
            for orig_ao in orig_aos:
                orig_ao_name = orig_ao['name']
                orig_ao_code = orig_ao['ao_code']
                if orig_ao_code == OP_NODE_INLET or orig_ao_code == OP_NODE_OUTLET:
                    continue
                if orig_ao_name not in chg_ao_names:  # This AO is deleted
                    details.append({
                        'type': 'deleted',
                        'ao_or_edge': 'ao',
                        'ao_name': orig_ao_name,
                        'details': orig_ao_name
                    })
            # endregion
            # region compare edges
            for chg_edge in chg_edges:
                existed = False
                for orig_edge in orig_edges:
                    if chg_edge['description'] == orig_edge['description']:
                        existed = True
                        break
                if not existed:
                    details.append({
                        'type': 'added',
                        'ao_or_edge': 'edge',
                        'edge_name': chg_edge['description'],
                        'id': chg_edge['id'],
                        'details': f"wire: {chg_edge['description']}"
                    })
            for orig_edge in orig_edges:
                exist = False
                for chg_edge in chg_edges:
                    if chg_edge['description'] == orig_edge['description']:
                        exist = True
                        break
                if not exist:
                    details.append({
                        'type': 'deleted',
                        'ao_or_edge': 'edge',
                        'edge_name': orig_edge['description'],
                        'details': f"wire: {orig_edge['description']}"
                    })
            # endregion
            adjusted_details = []
            groups = {}
            for detail in details:
                if detail['type'] == 'changed':
                    if detail['ao_name'] not in groups:
                        groups[detail['ao_name']] = {
                            'details': f"{detail['ao_name']}\n{detail['field_name']} {detail['original_value']}→{detail['changed_value']}",
                            'ao_or_edge': detail['ao_or_edge'],
                            'ao_name': detail['ao_name'],
                            'id': detail['id']
                        }
                    else:
                        groups[detail['ao_name']]['details'] += f"\n{detail['field_name']} {detail['original_value']}→{detail['changed_value']}"
                else:
                    adjusted_details.append(detail)
            for ao_name, values in groups.items():
                adjusted_details.append({
                    'type': 'changed',
                    **values
                })
            index = 1
            for adjusted_detail in adjusted_details:
                adjusted_detail['index'] = index
                index += 1
            if not adjusted_details:
                QMessageBox.about(self, 'Comparison result', 'There is no difference between the original project and the changed project.')
            else:
                self.signal_flow_diff_q_widget.hide()
                dialog = SignalFlowComparisonResultDialog(adjusted_details,
                                                          is_use_current_flow,
                                                          orig_proj_file_path,
                                                          chg_proj_file_path,
                                                          self)
                dialog.show()
        elif curr_btn == QDialogButtonBox.Cancel:
            self.signal_flow_diff_q_widget.close()

    def project_file_name(self):
        if self.project_name is None:
            return None
        return f'{self.project_name}.proj'

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        if self.editmode:
            self.warning_information(FLOW_Window.onEditRedo.__name__)
        else:
            current_window = self.getCurrentNodeEditorWidget()
            need_to_close_sub_windows = []
            need_to_open_sub_windows = []
            sub_windows_inf = []
            encrypted_sub_windows = []
            curr_wgt_history_stack = self.getCurrentNodeEditorWidget().scene.history.history_stack
            curr_wgt_curr_step = self.getCurrentNodeEditorWidget().scene.history.history_current_step
            # region 還原undo刪掉的SUBPATCH
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[0] == 'Created FLOW_Node_SUBPATCH':
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[1]
                sub_window_infos = copy.deepcopy(curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'])
                nodesSets = self.getCurrentNodeEditorWidget().collectNodesFromSubWnds()
                self.setActiveSubWindow(current_window.parent())
                renamed = set()  # (obj, 'desc'), (obj, 'sub_window_name'), (obj, 'nodes')
                def dfs_redo_to_create_subpatch(subpatch_name, sub_window_infos, nodesSets, parent_subwnd=None):
                    is_subpatch_inside = False
                    for sub_window_info in sub_window_infos:
                        if subpatch_name == sub_window_info['sub_window_name']:
                            subwnd = self.createGroupChild()
                            subwnd.widget().title = subpatch_name
                            # print(subpatch_name)
                            if 'encrypted' in sub_window_info:
                                subwnd.widget().encrypted = sub_window_info['encrypted']
                            if 'already_input_password' in sub_window_info:
                                subwnd.widget().already_input_password = sub_window_info['already_input_password']
                            if 'correct_password' in sub_window_info:
                                subwnd.widget().correct_password = sub_window_info['correct_password']
                            sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(OP_NODE_SUBPATCH, nodesSets)
                            not_available_titles = []
                            for sorted_node in sortedNodes:
                                not_available_titles.append(sorted_node.title)
                            subpatchs_inside = []
                            for i in range(len([sub_window_info][-1]['snapshot']['nodes'])):
                                node = [sub_window_info][-1]['snapshot']['nodes'][i]
                                if node['op_code'] == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node['title'])
                            if subwnd.widget().title in not_available_titles:
                                original_title = subwnd.widget().title
                                num = 1
                                found = False
                                while not found:
                                    if f'SUBPATCH_{str(num)}' not in not_available_titles:
                                        found = True
                                    else:
                                        num += 1
                                subwnd.widget().title = f'SUBPATCH_{str(num)}'
                                # sub_window_info['sub_window_name'] = f'SUBPATCH_{str(num)}'
                                if ('curr', curr_wgt_curr_step + 1, 'desc') not in renamed:
                                    curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'] = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[0]+'-'+f'SUBPATCH_{str(num)}'
                                    renamed.add(('curr', curr_wgt_curr_step + 1, 'desc'))
                                for i in range(len(curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'])):
                                    # print(f'1 {renamed}')
                                    if ('sub', i, 'sub_window_name') not in renamed:
                                        if curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i]['sub_window_name'] == original_title:
                                            curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i][
                                                'sub_window_name'] = f'SUBPATCH_{str(num)}'
                                            renamed.add(
                                                ('sub', i,
                                                'sub_window_name'))
                                    # print(f'2 {renamed}')
                                    if ('sub',i,'nodes') not in renamed:
                                        for node in curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i]['snapshot']['nodes']:
                                            if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                                node['title'] = f'SUBPATCH_{str(num)}'
                                                node['designator'] = num
                                                node['cwd'] = f'SUBPATCH_{str(num)}'
                                                renamed.add(
                                                    ('sub',i,
                                                    'nodes'))
                                    # print(f'3 {renamed}')
                                for i in range(curr_wgt_curr_step + 1, len(curr_wgt_history_stack)):
                                    if ('curr', i, 'nodes') not in renamed:
                                        for node in curr_wgt_history_stack[i]['snapshot']['nodes']:
                                            if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                                node['title'] = f'SUBPATCH_{str(num)}'
                                                node['designator'] = num
                                                node['cwd'] = f'SUBPATCH_{str(num)}'
                                                renamed.add(
                                                    ('curr', i,
                                                     'nodes'))
                                if parent_subwnd is not None:
                                    for i in range(len(parent_subwnd.widget().scene.nodes)):
                                        node = parent_subwnd.widget().scene.nodes[i]
                                        if node.op_code == OP_NODE_SUBPATCH:
                                            if node.title == subpatch_name:
                                                node.title = subwnd.widget().title
                                                node.cwd = subwnd.widget().title
                                                node.designator = num
                                                for hs_node in parent_subwnd.widget().scene.history.history_stack[
                                                    parent_subwnd.widget().scene.history.history_current_step][
                                                    'snapshot']['nodes']:
                                                    if hs_node['op_code'] == OP_NODE_SUBPATCH and hs_node[
                                                        'title'] == subpatch_name:
                                                        hs_node['title'] = subwnd.widget().title
                                                        hs_node['designator'] = num
                                                        hs_node['cwd'] = subwnd.widget().title


                            subwnd.widget().fileNew()
                            subwnd.widget().setTitle()
                            subwnd.widget().scene.history.history_stack = [sub_window_info]
                            subwnd.widget().scene.history.history_current_step = len(
                                subwnd.widget().scene.history.history_stack) - 1
                            subwnd.widget().scene.has_been_modified = True
                            subwnd.widget().scene.deserialize(subwnd.widget().scene.history.history_stack[-1]['snapshot'])
                            need_to_open_sub_windows.append(subwnd)
                            subpatch_node = TempNode()
                            subpatch_node.op_code = OP_NODE_SUBPATCH
                            subpatch_node.title = subwnd.widget().title
                            nodesSets = [*nodesSets, subpatch_node]

                            for i in range(len(subwnd.widget().scene.nodes)):
                                node = subwnd.widget().scene.nodes[i]
                                node.eval()

                                # if node.op_code == OP_NODE_SUBPATCH:
                                #     is_subpatch_inside = True
                                #     subpatchs_inside.append(node.title)

                                if node.op_code > 0 and node.op_code != OP_NODE_SUBPATCH:
                                    sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(node.op_code,
                                                                                                 nodesSets)
                                    designator = self.getCurrentNodeEditorWidget().findMinimalConseqSequence(
                                        sortedNodes)
                                    node.designator = designator
                                    node.title = f"{node.title.split('_')[0]}_{designator}"
                                    nodesSets.append(node)
                            if hasattr(subwnd.widget(), 'already_input_password'):
                                if not subwnd.widget().already_input_password:
                                    encrypted_sub_windows.append(subwnd)

                    if not is_subpatch_inside:
                        return
                    for subpatch_inside in subpatchs_inside:
                        dfs_redo_to_create_subpatch(subpatch_inside, sub_window_infos, nodesSets, subwnd)

                dfs_redo_to_create_subpatch(subpatch_name, sub_window_infos, nodesSets)
            # endregion
            # region delete subpatch -> undo(restore subpatch) -> redo(delete subpatch again)
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'] == 'Delete selected':
                if 'sub_windows' in curr_wgt_history_stack[curr_wgt_curr_step + 1]:
                    if curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows']:
                        to_close_sub_windows = curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows']
                        current_sub_windows = self.mdiArea.subWindowList()
                        for to_close_sub_window in to_close_sub_windows:
                            for sub_window in current_sub_windows:
                                sub_window_name = sub_window.widget().getPrettyFilename()
                                if to_close_sub_window['sub_window_name'] == sub_window_name:
                                    need_to_close_sub_windows.append(sub_window)
                                    target_window_history_stack = sub_window.widget().scene.history.history_stack
                                    sub_window_history_stamp = target_window_history_stack[-1]
                                    sub_window_history_stamp['sub_window_name'] = sub_window_name
                                    sub_windows_inf.append(sub_window_history_stamp)
            # endregion
            # region copy subpatch -> paste -> undo(delete pasted subpatch) -> redo (restore pasted subpatch)
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'] == 'Pasted elements in scene':
                if 'sub_windows' in curr_wgt_history_stack[curr_wgt_curr_step + 1]:
                    sub_window_infos = copy.deepcopy(curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'])
                    first_layer_original_name = copy.deepcopy(curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_window_names'])
                    renamed = set()  # (obj, 'desc'), (obj, 'sub_window_name'), (obj, 'nodes')
                    nodesSets = self.getCurrentNodeEditorWidget().collectNodesFromSubWnds()
                    self.setActiveSubWindow(current_window.parent())
                    for sub_window in sub_window_infos:
                        subwnd = self.createGroupChild()
                        subwnd.widget().title = sub_window['sub_window_name']
                        if 'encrypted' in sub_window:
                            subwnd.widget().encrypted = sub_window['encrypted']
                        if 'already_input_password' in sub_window:
                            subwnd.widget().already_input_password = sub_window['already_input_password']
                        if 'correct_password' in sub_window:
                            subwnd.widget().correct_password = sub_window['correct_password']
                        sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(OP_NODE_SUBPATCH, nodesSets)
                        not_available_titles = []
                        for sorted_node in sortedNodes:
                            not_available_titles.append(sorted_node.title)
                        subpatch_node = TempNode()
                        subpatch_node.op_code = OP_NODE_SUBPATCH
                        if subwnd.widget().title in not_available_titles:
                            original_title = subwnd.widget().title
                            num = 1
                            found = False
                            new_title = ''
                            while not found:
                                if f'SUBPATCH_{str(num)}' not in not_available_titles:
                                    new_title = f'SUBPATCH_{str(num)}'
                                    found = True
                                else:
                                    num += 1
                            subwnd.widget().title = new_title
                            # sub_window_info['sub_window_name'] = f'SUBPATCH_{str(num)}'
                            for i in range(len(curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'])):
                                # print(f'1 {renamed}')
                                if ('sub', i, 'sub_window_name') not in renamed:
                                    if curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i][
                                        'sub_window_name'] == original_title:
                                        curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i][
                                            'sub_window_name'] = new_title
                                        renamed.add(
                                            ('sub', i,
                                             'sub_window_name'))
                                # print(f'2 {renamed}')
                                if ('sub', i, 'nodes') not in renamed:
                                    for node in \
                                    curr_wgt_history_stack[curr_wgt_curr_step + 1]['sub_windows'][i]['snapshot'][
                                        'nodes']:
                                        if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                            node['title'] = new_title
                                            node['cwd'] = new_title
                                            renamed.add(
                                                ('sub', i,
                                                 'nodes'))
                                # print(f'3 {renamed}')
                            for i in range(curr_wgt_curr_step + 1, len(curr_wgt_history_stack)):
                                if i == curr_wgt_curr_step + 1:
                                    if ('curr', i, 'sub_window_names', original_title, new_title) not in renamed:
                                        if original_title in first_layer_original_name:
                                            curr_wgt_history_stack[i]['sub_window_names'].remove(original_title)
                                            curr_wgt_history_stack[i]['sub_window_names'].append(new_title)
                                            curr_wgt_history_stack[i]['sub_window_names'].sort()
                                            # print(original_title, new_title)
                                            renamed.add(('curr', i, 'sub_window_names', original_title, new_title))

                                for node in curr_wgt_history_stack[i]['snapshot']['nodes']:
                                    if ('curr', i, 'nodes', node['id']) not in renamed:
                                        if node['op_code'] == OP_NODE_SUBPATCH and node['title'] == original_title:
                                            # print(original_title, new_title, i, node['id'])
                                            node['title'] = new_title
                                            node['designator'] = num
                                            node['cwd'] = new_title
                                            renamed.add(
                                                ('curr', i, 'nodes', node['id']))
                            for sub_window_to_open in need_to_open_sub_windows:
                                for node in sub_window_to_open.widget().scene.nodes:
                                    if (sub_window_to_open, 'nodes', node.id) not in renamed:
                                        if node.op_code == OP_NODE_SUBPATCH and node.title == original_title and not hasattr(
                                                node, 'renamed'):
                                            for hs_node in sub_window_to_open.widget().scene.history.history_stack[
                                                sub_window_to_open.widget().scene.history.history_current_step][
                                                'snapshot']['nodes']:
                                                if (sub_window_to_open, 'his_stamp', 'nodes', hs_node['id']) not in renamed:
                                                    if hs_node['op_code'] == OP_NODE_SUBPATCH and hs_node[
                                                        'title'] == original_title:
                                                        hs_node['title'] = f'SUBPATCH_{str(num)}'
                                                        hs_node['designator'] = num
                                                        hs_node['cwd'] = f'SUBPATCH_{str(num)}'
                                                        renamed.add((sub_window_to_open, 'his_stamp', 'nodes', hs_node['id']))
                                            node.title = new_title
                                            node.designator = num
                                            node.cwd = new_title
                                            node.renamed = True
                                            renamed.add((sub_window_to_open, 'nodes', node.id))


                            subpatch_node.title = f'SUBPATCH_{str(num)}'
                            nodesSets = [*nodesSets, subpatch_node]
                        subwnd.widget().fileNew()
                        subwnd.widget().setTitle()
                        subwnd.widget().scene.history.history_stack = [sub_window]
                        subwnd.widget().scene.history.history_current_step = len(
                            subwnd.widget().scene.history.history_stack) - 1
                        subwnd.widget().scene.deserialize(subwnd.widget().scene.history.history_stack[-1]['snapshot'], restore_id=False)
                        subwnd.widget().scene.has_been_modified = True
                        need_to_open_sub_windows.append(subwnd)
                        if subpatch_node not in nodesSets:
                            subpatch_node.title = subwnd.widget().title
                            nodesSets = [*nodesSets, subpatch_node]

                        for i in range(len(subwnd.widget().scene.nodes)):
                            node = subwnd.widget().scene.nodes[i]
                            node.eval()
                            if node.op_code > 0 and node.op_code != OP_NODE_SUBPATCH:
                                sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(node.op_code,
                                                                                             nodesSets)
                                designator = self.getCurrentNodeEditorWidget().findMinimalConseqSequence(
                                    sortedNodes)
                                node.designator = designator
                                nodesSets.append(node)
                        if hasattr(subwnd.widget(), 'already_input_password'):
                            if not subwnd.widget().already_input_password:
                                encrypted_sub_windows.append(subwnd)
            # endregion
            # rename subpatch, then undo, then redo
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('Rename SubPatch'):
                desc = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc']
                current_subpatch_name = desc.split(' ')[-3]
                new_subpatch_name = desc.split(' ')[-1]
                # 將subpatch子視窗名字改回去
                self.open_subwindow_in_subpatch_recursively(current_subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                current_sub_windows = self.mdiArea.subWindowList()
                for sub_window in current_sub_windows:
                    if type(sub_window.widget()) == FLOW_Sub_Group:
                        sub_window_name = sub_window.widget().title
                        if '.json' in sub_window_name:
                            sub_window_name = sub_window_name.replace('.json','')
                        if sub_window_name == current_subpatch_name:
                            sub_window.widget().scene.has_been_modified = True
                            # 看有沒有存在SUBPATCH原名稱的檔案
                            if self.temp_folder_path:
                                if os.path.exists(self.temp_folder_path + '/' + new_subpatch_name + '.json'):
                                    sub_window.widget().title = new_subpatch_name + '.json'
                                else:
                                    sub_window.widget().title = new_subpatch_name
                            else:
                                sub_window.widget().title = new_subpatch_name
                            sub_window.widget().renamed = True
                            sub_window.widget().setWindowTitle(sub_window.widget().title + '*')
                        if hasattr(sub_window.widget(), 'close_if_no_problem'):
                            self.close_sub_window(sub_window)
            # add password -> undo -> redo
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('AddPassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                input_password = curr_wgt_history_stack[curr_wgt_curr_step + 1]['password']
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.encrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=input_password,
                                                  windows=windows)
            # remove password -> undo -> redo
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('RemovePassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                password = curr_wgt_history_stack[curr_wgt_curr_step + 1]['password']
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.decrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem:
                            self.close_sub_window(sub_window)
                self.setActiveSubWindow(current_window.parent())
            # modify password -> undo -> redo
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('ModifyPassword'):
                subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1].split(' ')[0]
                # region delete password firstly
                original_password = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split(' ')[-3]
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.decrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=original_password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                            self.close_sub_window(sub_window)
                self.setActiveSubWindow(current_window.parent())

                # endregion
                # region add password secondly
                new_password = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split(' ')[-1]
                self.open_subwindow_in_subpatch_recursively(subpatch_name)
                self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                self.encrypt_subpatch_recursively(input_subpatch_name=subpatch_name,
                                                  input_password=new_password,
                                                  windows=windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                            self.close_sub_window(sub_window)
                self.setActiveSubWindow(current_window.parent())
                # endregion
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('Add Inlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                    self.add_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                     node_op_code=OP_NODE_INLET)
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('Reduce Inlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                    self.delete_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                        node_op_code=OP_NODE_INLET)
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('Add Outlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                    self.add_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                     node_op_code=OP_NODE_OUTLET)
            if curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].startswith('Reduce Outlet'):
                node_type = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-2]
                if node_type == 'FLOW_Node_SUBPATCH':
                    subpatch_name = curr_wgt_history_stack[curr_wgt_curr_step + 1]['desc'].split('-')[-1]
                    self.delete_node_in_subpatch_window(subpatch_name=subpatch_name,
                                                        node_op_code=OP_NODE_OUTLET)
            if need_to_close_sub_windows:
                for need_to_close_sub_window in need_to_close_sub_windows:
                    need_to_close_sub_window.widget().parent().close()
            # print(f'before:{curr_wgt_curr_step}')
            super().onEditRedo()
            # print(f'after:{curr_wgt_curr_step}')
            # region prevent conflict AO name or designator
            # endregion
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()
            if sub_windows_inf:
                curr_wgt_history_stack = self.getCurrentNodeEditorWidget().scene.history.history_stack
                curr_wgt_curr_step = self.getCurrentNodeEditorWidget().scene.history.history_current_step
                for sub_window_inf in sub_windows_inf:
                    target_index = None
                    for i in range(len(curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'])):
                        if curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'][i]['sub_window_name'] == sub_window_inf['sub_window_name']:
                            target_index = i
                            break
                    if target_index is not None:
                        curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'][target_index] = sub_window_inf
            if need_to_open_sub_windows:
                for need_to_open_sub_window in need_to_open_sub_windows:
                    need_to_open_sub_window.show()
            for encrypted_sub_window in encrypted_sub_windows:
                self.close_sub_window(encrypted_sub_window)
            self.setActiveSubWindow(current_window.parent())
            self.prevent_conflict_name_and_designators()
            self.setActiveSubWindow(current_window.parent())

    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        if self.editmode:
            self.warning_information(FLOW_Window.onEditCut.__name__)
        else:
            current_window = self.getCurrentNodeEditorWidget()
            close_windows_list = []
            sub_windows_info = []
            def dfs_cut_subpatch(subpatch_name, windows):
                is_subpatch_inside = False
                for window in windows:
                    if type(window.widget()) == FLOW_Sub_Group:
                        window_name = window.widget().getPrettyFilename()
                        if window_name == subpatch_name:
                            sub_window_history_stamp = window.widget().scene.history.history_stack[
                                window.widget().scene.history.history_current_step]
                            if hasattr(window.widget(), 'encrypted'):
                                sub_window_history_stamp['already_input_password'] = window.widget().already_input_password
                                sub_window_history_stamp['correct_password'] = window.widget().correct_password
                                sub_window_history_stamp['encrypted'] = window.widget().encrypted
                            sub_window_history_stamp['sub_window_name'] = window_name
                            sub_windows_info.append(sub_window_history_stamp)
                            close_windows_list.append(window)
                            subpatchs_inside = []
                            for node in sub_window_history_stamp['snapshot']['nodes']:
                                if node['op_code'] == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node['title'])
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_cut_subpatch(subpatch_inside, windows)
            selected_items = self.getCurrentNodeEditorWidget().getSelectedItems()
            for item in selected_items:
                if hasattr(item, 'node'):
                    if item.node.openable:
                        item.node.widget.close()
                    if item.node.op_code == OP_NODE_SUBPATCH:
                        self.open_subwindow_in_subpatch_recursively(item.node.title)
                        self.setActiveSubWindow(current_window.parent())
                        windows = self.mdiArea.subWindowList()
                        dfs_cut_subpatch(item.node.title, windows)
            if close_windows_list:
                for close_window in close_windows_list:
                    close_window.close()
            if self.getCurrentNodeEditorWidget():
                data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
                data['sub_windows'] = sub_windows_info
                is_need_encrypt = False
                if 'sub_windows' in data:
                    for sub_window in data['sub_windows']:
                        if 'encrypted' in sub_window and sub_window['encrypted'] and 'already_input_password' in sub_window and not sub_window['already_input_password']:
                            is_need_encrypt = True
                            break
                str_data = json.dumps(data, indent=4)
                if is_need_encrypt:
                    str_data = str(json.dumps({
                        'object': str(base64.b64encode(AESOperation().encrypt_string(password=SECRET_KEY,
                                                                                     input_string=str_data)), 'utf-8'),
                        'is_encrypted': True
                    }))
                QApplication.instance().clipboard().setText(str_data)
            if sub_windows_info:
                curr_wgt_history_stack = self.getCurrentNodeEditorWidget().scene.history.history_stack
                curr_wgt_curr_step = self.getCurrentNodeEditorWidget().scene.history.history_current_step
                curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'] = sub_windows_info
                # 因為cut也會呼叫delete，所以會有兩個history stamp(Delete selected以及Cut out elements from scene)
                curr_wgt_history_stack[curr_wgt_curr_step-1]['sub_windows'] = sub_windows_info
            self.statusBar().clearMessage()
            self.statusBar().showMessage('Cut Node', 3000)
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()

    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        if self.editmode:
            self.warning_information(FLOW_Window.onEditCopy.__name__)
        else:
            sub_windows_info = []
            current_window = self.getCurrentNodeEditorWidget()
            def dfs_copy_subpatch(subpatch_name, windows):
                is_subpatch_inside = False
                for window in windows:
                    if type(window.widget()) == FLOW_Sub_Group:
                        sub_window_name = window.widget().getPrettyFilename()
                        if sub_window_name == subpatch_name:
                            sub_window_history_stamp = window.widget().scene.history.history_stack[
                                window.widget().scene.history.history_current_step]
                            if hasattr(window.widget(), 'encrypted'):
                                sub_window_history_stamp['already_input_password'] = window.widget().already_input_password
                                sub_window_history_stamp['correct_password'] = window.widget().correct_password
                                sub_window_history_stamp['encrypted'] = window.widget().encrypted
                            sub_window_history_stamp['sub_window_name'] = sub_window_name
                            sub_windows_info.append(sub_window_history_stamp)
                            subpatchs_inside = []
                            for node in sub_window_history_stamp['snapshot']['nodes']:
                                if node['op_code'] == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node['title'])
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_copy_subpatch(subpatch_inside, windows)
            selected_items = self.getCurrentNodeEditorWidget().getSelectedItems()
            for item in selected_items:
                if hasattr(item, 'node'):
                    if item.node.op_code == OP_NODE_SUBPATCH:
                        self.open_subwindow_in_subpatch_recursively(item.node.title)
                        self.setActiveSubWindow(current_window.parent())
                        windows = self.mdiArea.subWindowList()
                        dfs_copy_subpatch(item.node.title, windows)
                        for window in windows:
                            if hasattr(window.widget(), 'close_if_no_problem'):
                                if window.widget().close_if_no_problem:
                                    self.close_sub_window(window)
                        self.setActiveSubWindow(current_window.parent())
            if self.getCurrentNodeEditorWidget():
                data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
                data['sub_windows'] = sub_windows_info
                is_need_encrypt = False
                if 'sub_windows' in data:
                    for sub_window in data['sub_windows']:
                        if 'encrypted' in sub_window and sub_window['encrypted'] and 'already_input_password' in sub_window and not sub_window['already_input_password']:
                            is_need_encrypt = True
                            break
                str_data = json.dumps(data, indent=4)
                if is_need_encrypt:
                    str_data = str(json.dumps({
                        'object': str(base64.b64encode(AESOperation().encrypt_string(password=SECRET_KEY,
                                                                                  input_string=str_data)), 'utf-8'),
                        'is_encrypted': True
                    }))
                QApplication.instance().clipboard().setText(str_data)
            self.statusBar().clearMessage()
            self.statusBar().showMessage('Copy Node', 3000)
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        if self.editmode:
            self.warning_information(FLOW_Window.onEditPaste.__name__)
        else:
            current_window = self.getCurrentNodeEditorWidget()
            nodes = self.getCurrentNodeEditorWidget().collectNodesFromSubWnds()
            self.setActiveSubWindow(current_window.parent())
            dict = []
            sub_windows_to_open = []
            need_to_close_encrypted_sub_windows = []
            sub_window_names = []
            for node in nodes:
                dict.append(node.serialize())

            if self.getCurrentNodeEditorWidget():
                raw_data = QApplication.instance().clipboard().text()

                try:
                    data = json.loads(raw_data)
                    if 'is_encrypted' in data and data['is_encrypted']:
                        data = json.loads(AESOperation().decrypt_string(password=SECRET_KEY,
                                                                        input_string=data['object']))
                except ValueError as e:
                    if Debug.DEBUG_Low_Level.value: print("Pasting of not valid json data!", e)
                    return

                # check if the json data are correct
                if 'nodes' not in data:
                    if Debug.DEBUG_Low_Level.value: print("JSON does not contain any nodes!")
                    return

                for node in data['nodes']:
                    if node['op_code'] in [OP_NODE_INLET, OP_NODE_OUTLET]:
                        if Debug.DEBUG_Low_Level.value: print("Forbidden Inlet/Outlet Object Copy/Paste")
                        return

                for new_node in data['nodes']:
                    op_code = new_node['op_code']
                    sortedNodes = self.getDictByOP(op_code, dict)
                    designator = self.findMinimalConseqSequence(sortedNodes)
                    new_node['designator'] = designator
                    if new_node['type'] == 'SUBPATCH':
                        new_node['node_from'] = new_node['title']
                    # rename title with type + designator
                    new_node['title'] = new_node['type'] + '_' + str(designator)
                    self.adjust_title_of_new_in_out_ao(new_node, sortedNodes)
                    # region SUBPATCH的貼上，將子視窗也一起貼上
                    if new_node['op_code'] == OP_NODE_SUBPATCH:
                        if 'sub_windows' in data:  # 剪下貼上的情況(也包括「複製→改名→貼上」以及「複製→刪除→貼上」)
                            new_node['title'] = new_node['node_from']
                        not_available_titles = []
                        for sorted_node in sortedNodes:
                            not_available_titles.append(sorted_node['title'])
                        if new_node['title'] in not_available_titles:
                            num = 1
                            found = False
                            while not found:
                                if f'SUBPATCH_{str(num)}' not in not_available_titles:
                                    found = True
                                else:
                                    num += 1
                            new_node['title'] = f'SUBPATCH_{str(num)}'
                            new_node['cwd'] = f'SUBPATCH_{str(num)}'
                        if 'sub_windows' not in data:
                            current_sub_windows = self.mdiArea.subWindowList()
                            for sub_window in current_sub_windows:
                                if type(sub_window.widget()) == FLOW_Sub_Group:
                                    if sub_window.widget().renamed:
                                        sub_window_name = sub_window.widget().title
                                    else:
                                        sub_window_name = sub_window.widget().getPrettyFilename()
                                    if new_node['node_from'] == sub_window_name:
                                        subwnd = self.createGroupChild()
                                        subwnd.widget().title = new_node['title']
                                        subwnd.widget().fileNew()
                                        subwnd.widget().setTitle()
                                        target_window_history_stack = sub_window.widget().scene.history.history_stack
                                        for node in target_window_history_stack[-1]['snapshot']['nodes']:
                                            if node['op_code'] > 0:
                                                sortedNodes = self.getDictByOP(node['op_code'], dict)
                                                designator = self.findMinimalConseqSequence(sortedNodes)
                                                node['designator'] = designator
                                                node['title'] = node['type'] + '_' + str(designator)
                                                dict.append(node)
                                        subwnd.widget().scene.history.history_stack = [target_window_history_stack[-1]]
                                        subwnd.widget().scene.history.history_current_step = len(
                                            subwnd.widget().scene.history.history_stack) - 1
                                        subwnd.widget().scene.deserialize(
                                            subwnd.widget().scene.history.history_stack[-1]['snapshot'], restore_id=False)
                                        for i in range(len(subwnd.widget().scene.nodes)):
                                            node = subwnd.widget().scene.nodes[i]
                                            node.eval()
                                        subwnd.widget().scene.has_been_modified = True
                                        sub_windows_to_open.append(subwnd)
                                        sub_window_names.append(new_node['title'])
                        else:
                            def dfs_paste_subpatch(paste_from_subpatch_name, sub_window_infos, new_node_title):
                                is_subpatch_inside = False
                                for sub_window_info in sub_window_infos:
                                    if paste_from_subpatch_name == sub_window_info['sub_window_name']:
                                        subwnd = self.createGroupChild()
                                        subwnd.widget().title = new_node_title
                                        subwnd.widget().fileNew()
                                        subwnd.widget().setTitle()
                                        target_window_history_stack = [sub_window_info]
                                        subpatchs_inside = []
                                        for node in target_window_history_stack[-1]['snapshot']['nodes']:
                                            if node['op_code'] > 0:
                                                if node['op_code'] == OP_NODE_SUBPATCH:
                                                    is_subpatch_inside = True
                                                    subpatchs_inside.append([node['title']])
                                                self.reassign_designator(node, dict)
                                                if node['op_code'] == OP_NODE_SUBPATCH:
                                                    subpatchs_inside[-1].append(node['title'])
                                                dict.append(node)
                                        subwnd.widget().scene.history.history_stack = target_window_history_stack
                                        subwnd.widget().scene.history.history_current_step = len(
                                            subwnd.widget().scene.history.history_stack) - 1
                                        subwnd.widget().scene.deserialize(
                                            subwnd.widget().scene.history.history_stack[-1]['snapshot'],
                                            restore_id=False)
                                        for i in range(len(subwnd.widget().scene.nodes)):
                                            node = subwnd.widget().scene.nodes[i]
                                            node.eval()
                                        subwnd.widget().scene.has_been_modified = True
                                        if 'encrypted' in sub_window_info:
                                            subwnd.widget().encrypted = sub_window_info['encrypted']
                                        if 'correct_password' in sub_window_info:
                                            subwnd.widget().correct_password = sub_window_info['correct_password']
                                        if 'already_input_password' in sub_window_info:
                                            subwnd.widget().already_input_password = sub_window_info['already_input_password']
                                            if not sub_window_info['already_input_password']:
                                                need_to_close_encrypted_sub_windows.append((subwnd,
                                                                                           sub_window_info['correct_password']))
                                        sub_windows_to_open.append(subwnd)
                                if not is_subpatch_inside:
                                    return
                                for subpatch_inside in subpatchs_inside:
                                    dfs_paste_subpatch(subpatch_inside[0], sub_window_infos, subpatch_inside[1])

                            dict.append(new_node)
                            sub_window_names.append(new_node['title'])
                            dfs_paste_subpatch(new_node['node_from'], data['sub_windows'], new_node['title'])
                    # endregion
                    if new_node not in dict:
                        dict.append(new_node)

                new_nodes = self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)
            if sub_window_names:
                self.getCurrentNodeEditorWidget().scene.history.history_stack[-1]['sub_window_names'] = sub_window_names
            self.onEval()
            self.statusBar().clearMessage()
            self.statusBar().showMessage('Paste Node', 3000)
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()

            if sub_windows_to_open:
                for sub_window_to_open in sub_windows_to_open:
                    sub_window_to_open.show()
            for need_to_close_encrypted_sub_window in need_to_close_encrypted_sub_windows:
                self.close_sub_window(need_to_close_encrypted_sub_window[0])
                for ele in self.sub_patchs:
                    if ele.title == need_to_close_encrypted_sub_window[0].widget().title.replace('.json', '') \
                            or ele.title == need_to_close_encrypted_sub_window[0].widget().title:
                        ele.already_input_password = False
                        ele.correct_password = need_to_close_encrypted_sub_window[1]
                        ele.encrypted = True
            self.setActiveSubWindow(current_window.parent())
            self.prevent_conflict_name_and_designators()
            self.setActiveSubWindow(current_window.parent())

    def onEditDelete(self, unit_test_parameters=None):
        """
            Handle the logic of deleting selected items

            :param unit_test_parameters: Optional. Default: None.
                A dictionary containing unit test parameters.
                This parameter is used for unit testing purposes.
                - 'delete_sub_patch': bool.
                  If True, allows direct deletion of sub-patches.
                  If False, cancel deletion of sub-patches.
        """
        if self.editmode:
            self.warning_information(FLOW_Window.onEditDelete.__name__)
        else:
            current_window = self.mdiArea.activeSubWindow()
            current_nodeeditor = self.getCurrentNodeEditorWidget()
            selecteditems = current_nodeeditor.getSelectedItems()

            close_windows_list = []
            delete_files_list = []

            sub_windows_inf = []

            def dfs_delete_subpatch(subpatch_name, windows):
                is_subpatch_inside = False
                for window in windows:
                    if type(window.widget()) == FLOW_Sub_Group:
                        sub_window_name = window.widget().getPrettyFilename()
                        if subpatch_name == sub_window_name:
                            target_window_history_stack = window.widget().scene.history.history_stack
                            target_window_current_step = window.widget().scene.history.history_current_step
                            sub_window_history_stamp = target_window_history_stack[target_window_current_step]
                            sub_window_history_stamp['sub_window_name'] = sub_window_name
                            if hasattr(window.widget(), 'encrypted'):
                                sub_window_history_stamp['encrypted'] = window.widget().encrypted
                            if hasattr(window.widget(), 'already_input_password'):
                                sub_window_history_stamp['already_input_password'] = window.widget().already_input_password
                            if hasattr(window.widget(), 'correct_password'):
                                sub_window_history_stamp['correct_password'] = window.widget().correct_password
                            sub_windows_inf.append(sub_window_history_stamp)
                            close_windows_list.append(window)
                            self.remove_subwindow_obj(subpatch_name)
                            if not item.node.cwd == "temp":
                                delete_files_list.append(window.widget().filename)
                            subpatchs_inside = []
                            for node in sub_window_history_stamp['snapshot']['nodes']:
                                if node['op_code'] == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node['title'])
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_delete_subpatch(subpatch_inside, windows)

            for item in selecteditems:
                if hasattr(item, 'node'):
                    if item.node.content_label_objname in ["INLET", "OUTLET"]:
                        return

                    elif item.node.op_code == OP_NODE_SUBPATCH:
                        self.open_subwindow_in_subpatch_recursively(item.node.title)
                        self.setActiveSubWindow(current_window)
                        windows = self.mdiArea.subWindowList()
                        ao_name = item.node.title
                        dfs_delete_subpatch(ao_name, windows)

            if delete_files_list or close_windows_list:
                if delete_files_list:
                    if unit_test_parameters:
                        res = QMessageBox.Yes if unit_test_parameters['delete_sub_patch'] else QMessageBox.No
                    else:
                        res = QMessageBox.question(self, "About to delete SUBPATCH from your project?",
                                                   "The document inside the SUBPATCH node will be modified and can't be retrieved.\n "
                                                   "Do you want to delete SUBPATCH node?",
                                                   QMessageBox.Yes | QMessageBox.No)
                    if res == QMessageBox.Yes:
                        for file in delete_files_list:
                            if file:
                                os.remove(file)
                        for window in close_windows_list:
                            for ele in self.sub_patchs:
                                if ele.title == window.widget().title.replace('.json', '') or ele.title == window.widget().title:
                                    ele.closed = True
                            window.close()
                        super().onEditDelete()
                        # current_nodeeditor.scene.history.clear()
                        # current_nodeeditor.scene.history.storeInitialHistoryStamp()
                        # current_nodeeditor.scene.has_been_modified = False
                        # current_nodeeditor.fileSave()
                        # current_nodeeditor.setTitle()
                    else:
                        windows = self.mdiArea.subWindowList()
                        for window in windows:
                            if hasattr(window.widget(), 'close_if_no_problem'):
                                if window.widget().close_if_no_problem:
                                    self.close_sub_window(window)
                        self.setActiveSubWindow(current_window)
                        return
                else:
                    for window in close_windows_list:
                        window.close()
                    super().onEditDelete()
                    # current_nodeeditor.scene.history.clear()
                    # current_nodeeditor.scene.history.storeInitialHistoryStamp()
            else:
                for item in selecteditems:
                    if hasattr(item, 'node'):
                        if item.node.openable:
                            item.node.widget.close()
                super().onEditDelete()
            # 假如有關掉子視窗，要把關掉的視窗資訊存在history stamp裡
            if sub_windows_inf:
                curr_wgt_history_stack = self.getCurrentNodeEditorWidget().scene.history.history_stack
                curr_wgt_curr_step = self.getCurrentNodeEditorWidget().scene.history.history_current_step
                curr_wgt_history_stack[curr_wgt_curr_step]['sub_windows'] = sub_windows_inf
            self.setActiveSubWindow(current_window)
            self.statusBar().clearMessage()
            self.statusBar().showMessage('Delete Node', 3000)
            # self.getCurrentNodeEditorWidget().scene.onItemSelected()

    def adjust_designator_of_in_out_aos(self):
        """
            Adjust the designator values of the audio objects IN and OUT
            so that they become sequentially numbered as 1, 2, 3, and so on.
        """

        def adjust_designator_of_specific_type_of_ao_in_main(ao_no):
            """
                Adjust the designator values of the specific type of audio object
                so that they become sequentially numbered as 1, 2, 3, and so on.

                :param ao_no: int, number of specified audio object
            """
            main_window = self.findMain()
            nodes_in_main = main_window.widget().scene.nodes
            aos = []
            for node in nodes_in_main:
                if node.op_code == ao_no:
                    aos.append((node.id, node.designator))
            aos = sorted(aos, key=lambda x: x[1])
            for i in range(len(aos)):
                new_designator = i + 1
                if aos[i][1] != new_designator:
                    for node in nodes_in_main:
                        if node.id == aos[i][0]:
                            node.designator = new_designator
                            break

        adjust_designator_of_specific_type_of_ao_in_main(OP_NODE_ADC)
        adjust_designator_of_specific_type_of_ao_in_main(OP_NODE_DAC)

    def adjust_title_of_new_in_out_ao(self, new_node, nodes_of_same_type=None):
        """
            Adjust title of new dragged or pasted IN/OUT audio object to avoid duplicate names.

            :param new_node: when dragging, type is subclass of FLOW_Node,
            when pasting, type is dict; new dragged or pasted audio object

            :param nodes_of_same_type: list,
            when pasting, nodes of same type as new_node need to be passed in
        """
        type_new_node = type(new_node)
        titles_nodes_in_main = set()
        if issubclass(type_new_node, FLOW_Node):
            if new_node.op_code == OP_NODE_ADC or new_node.op_code == OP_NODE_DAC:
                main_window = self.findMain()
                nodes_in_main = main_window.widget().scene.nodes
                for node_in_main in nodes_in_main:
                    if node_in_main.id != new_node.id:
                        titles_nodes_in_main.add(node_in_main.title)
                prefix = 'IN_' if new_node.op_code == OP_NODE_ADC else 'OUT_'
                i = 1
                while True:
                    new_title = prefix + str(i)
                    if new_title not in titles_nodes_in_main:
                        new_node.title = new_title
                        return
                    i += 1
            else:
                return
        elif type_new_node is dict:
            if new_node['op_code'] == OP_NODE_ADC or new_node['op_code'] == OP_NODE_DAC:
                for node in nodes_of_same_type:
                    titles_nodes_in_main.add(node['title'])
                prefix = 'IN_' if new_node['op_code'] == OP_NODE_ADC else 'OUT_'
                i = 1
                while True:
                    new_title = prefix + str(i)
                    if new_title not in titles_nodes_in_main:
                        new_node['title'] = new_title
                        return
                    i += 1
            else:
                return


    def onEditSelectAll(self):
        """
            Select all nodes and edges in the current node editor window.
        """
        nodes = self.getCurrentNodeEditorWidget().scene.nodes
        for node in nodes:
            node.doSelect(True)

        edges = self.getCurrentNodeEditorWidget().scene.edges
        for edge in edges:
            edge.doSelect(True)

    def createActions(self):
        """
            Create various actions applied in the main program window,
            including opening, saving, editing, exporting configurations, and other operations
        """
        super().createActions()
        self.actSelectAll = QAction('&Select All', self, shortcut='Ctrl+A', statusTip="Select All Objects",
                                    triggered=self.onEditSelectAll)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Y', statusTip="Redo last operation",
                               triggered=self.onEditRedo)

        self.actExport = QAction('Expor&t', self, shortcut='Ctrl+T', statusTip="Export Configuration File", triggered=self.onExportXMLTip)
        self.actExportCommit = QAction('Export Command', self, statusTip="Export Configuration File")
        self.actExportCommit.triggered.connect(lambda: self.onExportCommand())
        self.actExportRawCommand = QAction('Export Raw Command', self)
        self.actExportRawCommand.triggered.connect(lambda: self.onExportCommand(export_type=ExportType.RAW_COMMAND.value))
        self.act_signal_flow_diff = QAction('Signal Flow Diff', self, triggered=self.popup_signal_flow_diff_window)
        self.act_custom_ao_builder = QAction('Custom AO Builder', self, triggered=self.popup_custom_ao_builder_window)
        self.act_import_custom_aos_settings = QAction('Import Custom AOs Settings', self, triggered=self.import_custom_aos_settings)
        self.act_export_custom_aos_settings = QAction('Export Custom AOs Settings', self, triggered=self.export_custom_aos_settings)
        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window",
                                triggered=self.closeMdiAreaActiveSubWindowRecursively)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows",
                                   triggered=self.closeMdiAreaAllSubWindows)

        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        # self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        # self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        # self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Display the application's About box", triggered=self.about)
        self.actInfo = QAction("&Info", self, statusTip="Display the version of Flow Engine", triggered=self.info)
        self.actInfo.setDisabled(True)

        self.actUserGuide = QAction("&User Guide", self, statusTip="Display User Guide", triggered=self.userGuide)
        self.actFeedback = QAction("&Submit Feedback", self, statusTip="Submit Feedback", triggered=self.handleFeedback)
        self.actOAGuide = QAction("&Open Architecture Guide", self, statusTip="Display Open Architecture Guide", triggered=self.onOpenArchitectureGuide)

        self.actPreference = QAction("&Connect Setting", self, shortcut='Shift+,',
                                     statusTip="Setup audio I/O of application", triggered=self.onOpenControlDialog)
        # TODO: we will disable simulation in the current 0.25 version
        # self.actAnalysis = QAction("&Analysis Setting", self, shortcut='Shift+Y', statusTip="Setup audio I/O of simulation", triggered=self.onSimulationDialog)

        self.actEditMode = QAction('Tun&ing Mode', self, shortcut='Ctrl+I', statusTip="Toggle Edit Mode",
                                   triggered=self.onEditMode)
        self.actEditMode.setCheckable(True)
        self.actEditMode.setChecked(self.editmode)

        self.actUpload = QAction("&Upload Design", self, shortcut='Ctrl+U', statusTip="Upload Design to Target",
                                 triggered=self.upload_target)
        self.actDownload = QAction("&Download Design", self, shortcut='Ctrl+D', statusTip="Download Design from Target",
                                   triggered=self.download_target)

        self.actRuleCheck = QAction("&Rule Check", self, shortcut='Ctrl+R', statusTip="Toggle Dirty State",
                                    triggered=self.onIsNodeValid)
        self.actRuleCheck.setCheckable(True)

        # self.actScanAudioInterface = QAction("Scan Audi&o Preference", self, shortcut='Ctrl+O', statusTip="Rescan Hardware Information", triggered=self.scanAudioInterface)
        # self.actScanAudioInterface.setEnabled(not self.editmode)

    def getCurrentNodeEditorWidget(self):
        """
            Gets the node editor window that is currently active (i.e. the user is viewing).
        """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        main_window = self.findMain()
        if main_window:
            return main_window.widget()
        return None

    def index_subwindow_obj(self, title_name):
        """
            Find the sub window object in the sub window object list (self. sub_patches)
            that matches the given sub window title name (titlename),
            and return the index of its location

            :param title_name, Sub window title name

            :return, target index
        """
        target_index = None
        for index in range(len(self.sub_patchs)):
            if self.sub_patchs[index].title == title_name or self.sub_patchs[index].title == title_name+'.json':
                target_index = index
        return target_index


    # 針對self.sub_patchs裡，刪除title為title_name的object
    def remove_subwindow_obj(self, title_name):
        """
            in self.sub_patches, delete title as title_name object

            :param title_name, title name of sub_patch
        """
        need_to_delete_indice = []
        for index in range(len(self.sub_patchs)):
            if self.sub_patchs[index].title == title_name or self.sub_patchs[index].title == title_name+'.json':
                need_to_delete_indice.append(index)
        for index in sorted(need_to_delete_indice, reverse=True):
            del self.sub_patchs[index]

    def close_sub_window(self, sub_window):
        """
            Close the sub window (i.e. the given sub_window object)

            :param sub_window, close sub_window
        """
        self.setActiveSubWindow(sub_window)
        self.closeMdiAreaActiveSubWindow()

    def closeMdiAreaActiveSubWindow(self):
        """
            Close the active sub windows in the sub window of the main program.
            At the same time, it will also update the information of sub window related objects and lists
        """
        main_window = self.findMain()
        if main_window is not None:
            if self.mdiArea.activeSubWindow().windowTitle() != main_window.windowTitle():
                current_sub_window = self.mdiArea.activeSubWindow().widget()
                copy_window = current_sub_window.create_copy()
                copy_window.closed = True
                # 看self.sub_patchs裡有沒有同名的sub_window，有的話要取代它
                self.remove_subwindow_obj(current_sub_window.title)
                self.sub_patchs.append(copy_window)
                self.getCurrentNodeEditorWidget().scene.propertyDockWidget.dict_value = {}
                self.mdiArea.closeActiveSubWindow()

    def closeMdiAreaActiveSubWindowRecursively(self):
        """
            Close the active window
        """
        main_window = self.findMain()
        if main_window is not None:
            if self.mdiArea.activeSubWindow().windowTitle() != main_window.windowTitle():
                def dfs_close_window(input_sub_window_name, windows):
                    is_subpatch_inside = False
                    for window in windows:
                        if type(window.widget()) == FLOW_Sub_Group:
                            sub_window_name = window.widget().getPrettyFilename()
                            if sub_window_name == input_sub_window_name:
                                self.setActiveSubWindow(window)
                                current_sub_window = self.mdiArea.activeSubWindow().widget()
                                copy_window = current_sub_window.create_copy()
                                copy_window.closed = True
                                # 看self.sub_patchs裡有沒有同名的sub_window，有的話要取代它
                                self.remove_subwindow_obj(current_sub_window.title)
                                self.sub_patchs.append(copy_window)
                                self.getCurrentNodeEditorWidget().scene.propertyDockWidget.dict_value = {}
                                subpatchs_inside = []
                                for node in current_sub_window.scene.nodes:
                                    if node.op_code == OP_NODE_SUBPATCH:
                                        is_subpatch_inside = True
                                        subpatchs_inside.append(node.title)
                                self.mdiArea.closeActiveSubWindow()
                    if not is_subpatch_inside:
                        return
                    for subpatch_inside in subpatchs_inside:
                        dfs_close_window(subpatch_inside, windows)
                windows = self.mdiArea.subWindowList()
                dfs_close_window(self.mdiArea.activeSubWindow().widget().getPrettyFilename(), windows)
                # 回到最右邊的sub window
                windows = self.mdiArea.subWindowList()
                self.setActiveSubWindow(windows[-1])



    def closeMdiAreaAllSubWindows(self):
        """
            Close all the windows
        """
        self.findMain().close()

    def onFileNew(self):
        """
            Create a window
        """
        isReCreate = False
        mainWindow = self.findMain()
        if mainWindow is not None:
            if mainWindow.close():
                isReCreate = True
        else:
            isReCreate = True
        if isReCreate:
            try:
                subwnd = self.createMdiChild()
                subwnd.widget().fileNew()
                subwnd.show()
                self.temp_folder_path = None
                self.clear_sub_patchs_window_objects()
                self.setWindowTitle('Flow Studio - New')
            except Exception as e:
                dumpException(e)

    def onMultipleFile(self):
        """
            Create multiple windows
        """
        try:
            subWindowLen = 0
            for i in self.mdiArea.subWindowList():
                if i.windowTitle().split('_')[0] != SUBPATCH:
                    subWindowLen += 1
            if subWindowLen == 0:
                self.onFileNew()
            else:
                title = "Multiple_" + str(subWindowLen)
                subwnd = self.createGroupChild()
                subwnd.widget().title = title
                subwnd.widget().fileNew()
                subwnd.widget().setTitle()

                current_nodeeditor = self.getCurrentNodeEditorWidget()

                if current_nodeeditor.filename is not None:
                    fname = os.path.split(current_nodeeditor.filename)[0] + '/' + title + '.json'
                    subwnd.widget().scene.saveToFile(fname)
                    subwnd.widget().filename = fname
                    subwnd.widget().setTitle()
                    subwnd.widget().scene.history.clear()
                    subwnd.widget().scene.history.storeInitialHistoryStamp()
                else:
                    subwnd.widget().scene.history.clear()
                    subwnd.widget().scene.history.storeInitialHistoryStamp()
                    subwnd.widget().scene.has_been_modified = True

                subwnd.show()
            self.mdiArea.tileSubWindows()
        except Exception as e:
            dumpException(e)

    def is_node_connected(self, node):
        """
            Check if there is a connection between the given node and other nodes

            :param node, Checked node
        """
        if node.op_code == OP_NODE_SUBPATCH:
            sockets = node.inputs + node.outputs
            for socket in sockets:
                connected = False
                for edge in node.scene.edges:
                    if edge.start_socket.id == socket.id or edge.end_socket.id == socket.id:
                        connected = True
                        break
                if not connected:
                    return False
            return True
        else:
            input_sockets = node.inputs
            input_connected = False
            for input_socket in input_sockets:
                for edge in node.scene.edges:
                    if edge.start_socket.id == input_socket.id or edge.end_socket.id == input_socket.id:
                        input_connected = True
                        break
                if input_connected:
                    break
            if len(input_sockets) > 0 and not input_connected:
                return False
            output_sockets = node.outputs
            output_connected = False
            for output_socket in output_sockets:
                for edge in node.scene.edges:
                    if edge.start_socket.id == output_socket.id or edge.end_socket.id == output_socket.id:
                        output_connected = True
                        break
                if output_connected:
                    break
            if len(output_sockets) > 0 and not output_connected:
                return False
            return True

    def set_closed_value_in_subpatch(self, subpatch_name, value):
        for sub_window in self.sub_patchs:
            if (sub_window.title == subpatch_name or sub_window.title == subpatch_name + '.json'):
                sub_window.closed = value

    def open_subwindow_in_subpatch_recursively(self, subpatch_name):
        exist_in_sub_patchs_objects = False
        target_win_obj = None
        renamed = False
        filename = None
        already_input_password = None
        encrypted = None
        correct_password = None
        is_subpatch_inside = False
        for sub_window in self.sub_patchs:
            if (sub_window.title == subpatch_name or sub_window.title == subpatch_name+'.json')\
                    and sub_window.closed:
                sub_window.closed = False
                exist_in_sub_patchs_objects = True
                target_win_obj = sub_window
                if sub_window.renamed:
                    renamed = True
                filename = sub_window.filename
                if hasattr(sub_window, 'already_input_password'):
                    already_input_password = sub_window.already_input_password
                if hasattr(sub_window, 'correct_password'):
                    correct_password = sub_window.correct_password
                if hasattr(sub_window, 'encrypted'):
                    encrypted = sub_window.encrypted
        if exist_in_sub_patchs_objects:  # If it exists in self.sub_patchs, open it
            target_win_obj.scene.propertyDockWidget = self.nodesPropertyWidget
            subwnd = self.mdiArea.addSubWindow(target_win_obj)
            self.set_custom_menu_for_sub_window(subwnd)
            subwnd.setWindowIcon(self.empty_icon)
            if self.temp_folder_path:
                if os.path.exists(self.temp_folder_path + '/' + target_win_obj.title + ".json"):
                    subwnd.widget().title = target_win_obj.title + '.json'
            else:
                subwnd.widget().title = target_win_obj.title
            subwnd.widget().filename = filename
            subwnd.widget().renamed = renamed
            subwnd.widget().close_if_no_problem = True
            if already_input_password is not None:
                subwnd.widget().already_input_password = already_input_password
            if correct_password is not None:
                subwnd.widget().correct_password = correct_password
            if encrypted is not None:
                subwnd.widget().encrypted = encrypted
            subwnd.widget().title = target_win_obj.title
            subwnd.widget().setTitle()
            subwnd.widget().scene.has_been_modified = target_win_obj.scene.has_been_modified
            subwnd.widget().scene.history.addHistoryModifiedListener(self.updateEditMenu)
            subwnd.widget().scene.deserialize(
                target_win_obj.scene.history.history_stack[target_win_obj.scene.history.history_current_step][
                    'snapshot'])
            subpatchs_inside = []
            for i in range(len(subwnd.widget().scene.nodes)):
                node = subwnd.widget().scene.nodes[i]
                node.eval()
                if node.op_code == OP_NODE_SUBPATCH:
                    is_subpatch_inside = True
                    subpatchs_inside.append(node.title)
            subwnd.widget().show()
        else:
            windows = self.mdiArea.subWindowList()
            for window in windows:
                sub_window_name = window.widget().getPrettyFilename()
                if sub_window_name == subpatch_name:
                    subpatchs_inside = []
                    for i in range(len(window.widget().scene.nodes)):
                        node = window.widget().scene.nodes[i]
                        if node.op_code == OP_NODE_SUBPATCH:
                            is_subpatch_inside = True
                            subpatchs_inside.append(node.title)
        if not is_subpatch_inside:
            return
        for subpatch_inside in subpatchs_inside:
            self.open_subwindow_in_subpatch_recursively(subpatch_inside)


    def onEnterGroupFile(self, node):
        '''
        is main file saved?
        yes:
            is node opened?
            yes:
                redirect active window to there!
            no:
                does it exisit?
                no:
                    create new group file directly to the file dir
                yes:
                    open that node via fname
        no:
            is cwd not temp?
            yes:
                create new group file
            no:
                redirect active window to there!
        '''
        if node.cwd:
            AO_Name = node.title
            existing = self.findMdiChildFriendly(AO_Name)
            exist_in_sub_patchs_objects = False
            for sub_window in self.sub_patchs:
                if (sub_window.title == AO_Name or sub_window.title == AO_Name + '.json') \
                        and sub_window.closed:
                    if hasattr(sub_window, 'already_input_password'):
                        if sub_window.already_input_password:
                            exist_in_sub_patchs_objects = True
                    else:
                        exist_in_sub_patchs_objects = True
            open_from_encrypted_file = False
            is_encrypted = node.is_encrypted()
            # Only prompt for a password if the file is encrypted and has not been previously opened with a password
            if is_encrypted and not existing and not exist_in_sub_patchs_objects:
                self.current_subpatch = node
                self.show_decrypt_subpatch_dialog()
                open_from_encrypted_file = True
                if hasattr(self, 'cancel_dialog'):
                    if self.cancel_dialog:
                        return
            if not open_from_encrypted_file:
                if existing:  # 假如子視窗已經有開啟了
                    self.mdiArea.setActiveSubWindow(existing)
                else:
                    exist_in_sub_patchs_objects = False
                    target_win_obj = None
                    for sub_window in self.sub_patchs:
                        if (sub_window.title == AO_Name or sub_window.title == AO_Name + '.json') \
                                and sub_window.closed:
                            exist_in_sub_patchs_objects = True
                            target_win_obj = sub_window
                            sub_window.closed = False
                    if exist_in_sub_patchs_objects:  # If it exists in self.sub_patchs, open it
                        target_win_obj.scene.propertyDockWidget = self.nodesPropertyWidget
                        subwnd = self.mdiArea.addSubWindow(target_win_obj)
                        self.set_custom_menu_for_sub_window(subwnd)
                        subwnd.setWindowIcon(self.empty_icon)
                        if self.temp_folder_path:
                            if os.path.exists(self.temp_folder_path + '/' + target_win_obj.title + ".json"):
                                subwnd.widget().title = target_win_obj.title + '.json'
                        else:
                            subwnd.widget().title = target_win_obj.title
                        subwnd.widget().scene.has_been_modified = target_win_obj.scene.has_been_modified
                        subwnd.widget().setTitle()
                        subwnd.widget().scene.history.addHistoryModifiedListener(self.updateEditMenu)
                        subwnd.widget().scene.deserialize(target_win_obj.scene.history.history_stack[target_win_obj.scene.history.history_current_step]['snapshot'])
                        for i in range(len(subwnd.widget().scene.nodes)):
                            node = subwnd.widget().scene.nodes[i]
                            node.eval()
                        subwnd.widget().show()
                    else:
                        try:
                            mainFname = self.mdiArea.activeSubWindow().widget().filename
                            fname = os.path.split(mainFname)[0] + '/' + AO_Name + '.json'
                            self.onSubpatchFileOpen(fname)
                        except:
                            self.createNewGroupFile(node)
        else:
            current_nodeeditor = self.getCurrentNodeEditorWidget()
            if current_nodeeditor.filename:
                self.createNewGroupFile(node, current_nodeeditor.filename)
                # self.onFileSave(export_xml=False)
            else:
                self.createNewGroupFile(node)

    def show_decrypt_subpatch_dialog(self):
        qdialog = QDialog(self)
        self.decryptSubpatchDialog = Ui_decryptSubpatchDialog()
        self.decryptSubpatchDialog.setupUi(qdialog)
        qdialog.setWindowTitle("Enter Password")
        self.decryptSubpatchDialog.buttonBox.clicked.connect(self.onDecryptSubpatchDialogOption)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def decrypt_subpatch(self, subpatch_to_decrypt, input_password, ignore_message_box=False):
        """
            decrypt subpatch

            :param subpatch_to_decrypt: FLOW_Node_SUBPATCH, subpatch node to decrypt
            :param input_password: str, given password
            :param ignore_message_box: Optional. Default: False.
            A boolean value indicating whether to ignore showing the message box or not.
        """
        correct_password = None
        for ele in self.sub_patchs:
            if ele.title == subpatch_to_decrypt.title + '.json' or ele.title == subpatch_to_decrypt.title:
                correct_password = ele.correct_password
        if input_password == '':
            if not ignore_message_box:
                QMessageBox.warning(self, 'Please input password',
                                    f'Please input password')
            self.cancel_dialog = True
            return
        elif input_password != correct_password:
            if not ignore_message_box:
                QMessageBox.warning(self, 'Warning',
                                    f'Input password is not correct.')
            self.cancel_dialog = True
            return
        elif input_password == correct_password:
            need_to_close_sub_windows = []
            need_to_switch_to_window = []
            def dfs_decrypt_subpatch(subpatch_name, input_password, level):
                is_subpatch_inside = False
                exist_in_sub_patchs_objects = False
                target_win_obj = None
                renamed = False
                for sub_window in self.sub_patchs:
                    if (sub_window.title == subpatch_name or sub_window.title == subpatch_name + '.json') \
                            and sub_window.closed:
                        if hasattr(sub_window, 'correct_password'):
                            correct_password = sub_window.correct_password
                            if input_password != correct_password:
                                return
                        if hasattr(sub_window, 'encrypted'):
                            encrypted = sub_window.encrypted
                        if hasattr(sub_window, 'already_input_password'):
                            sub_window.already_input_password = True
                            already_input_password = sub_window.already_input_password
                        sub_window.closed = False
                        exist_in_sub_patchs_objects = True
                        target_win_obj = sub_window
                        if sub_window.renamed:
                            renamed = True
                        filename = sub_window.filename
                if exist_in_sub_patchs_objects:  # If it exists in self.sub_patchs, open it
                    target_win_obj.scene.propertyDockWidget = self.nodesPropertyWidget
                    subwnd = self.mdiArea.addSubWindow(target_win_obj)
                    self.set_custom_menu_for_sub_window(subwnd)
                    subwnd.setWindowIcon(self.empty_icon)
                    if self.temp_folder_path:
                        if os.path.exists(self.temp_folder_path + '/' + target_win_obj.title + ".json"):
                            subwnd.widget().title = target_win_obj.title + '.json'
                    else:
                        subwnd.widget().title = target_win_obj.title
                    subwnd.widget().filename = filename
                    subwnd.widget().renamed = renamed
                    subwnd.widget().title = target_win_obj.title
                    subwnd.widget().setTitle()
                    subwnd.widget().scene.has_been_modified = target_win_obj.scene.has_been_modified
                    subwnd.widget().scene.history.addHistoryModifiedListener(self.updateEditMenu)
                    subwnd.widget().scene.deserialize(
                        target_win_obj.scene.history.history_stack[
                            target_win_obj.scene.history.history_current_step][
                            'snapshot'])
                    if already_input_password is not None:
                        subwnd.widget().already_input_password = True

                        subwnd.widget().scene.history.history_stack[subwnd.widget().scene.history.history_current_step][
                            'already_input_password'] = True
                        subwnd.widget().correct_password = input_password
                        subwnd.widget().scene.history.history_stack[
                            subwnd.widget().scene.history.history_current_step]['correct_password'] = input_password
                        subwnd.widget().encrypted = encrypted
                        subwnd.widget().scene.history.history_stack[
                            subwnd.widget().scene.history.history_current_step][
                            'encrypted'] = encrypted
                    subpatchs_inside = []
                    for i in range(len(subwnd.widget().scene.nodes)):
                        node = subwnd.widget().scene.nodes[i]
                        node.eval()
                        if node.op_code == OP_NODE_SUBPATCH:
                            is_subpatch_inside = True
                            subpatchs_inside.append(node.title)
                    subwnd.widget().show()
                    if level != 1:
                        need_to_close_sub_windows.append(subwnd)
                    else:
                        need_to_switch_to_window.append(subwnd)
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_decrypt_subpatch(subpatch_inside, input_password, level=level + 1)
            dfs_decrypt_subpatch(subpatch_to_decrypt.title, input_password, 1)
            if need_to_close_sub_windows:
                for need_to_close_sub_window in need_to_close_sub_windows:
                    self.close_sub_window(need_to_close_sub_window)
            self.mdiArea.setActiveSubWindow(need_to_switch_to_window[-1])

    def onDecryptSubpatchDialogOption(self, button):
        """
            Executes the appropriate action based on the button clicked in the enter password dialog.

            Args:
                button: The button clicked in the enter password dialog.
        """
        curr_btn = self.decryptSubpatchDialog.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            input_password = self.decryptSubpatchDialog.lineEditPassword.text()
            self.decrypt_subpatch(subpatch_to_decrypt=self.current_subpatch,
                                  input_password=input_password)
        elif curr_btn == QDialogButtonBox.Cancel:
            self.cancel_dialog = True

    def onFileOpen(self, hidden_dir=None, project_file_path=None):
        """
            If both hidden_dir and project_file_path parameters are None,
            ask user to choose project file to open;\n
            If hidden_dir parameter is not None,
            directly open json files under hidden_dir;\n
            If hidden_dir parameter is None and project_file_path is not None,
            open project of given project_file_path parameter

            :param hidden_dir: str, path of the directory which contains json files and user wants to open;
                default:None

            :param project_file_path: str, path of project file which user wants to open;
                default:None

            :return: bool, if opening without problems, return True,
                otherwise, return False
        """
        mainWindow = self.findMain()
        if mainWindow is not None:
            if not mainWindow.close():
                return False

        if not hidden_dir:
            if project_file_path is None:
                project_file_path, filter_ext = QFileDialog.getOpenFileName(self, "Please choose a project to open",
                                                                            getFileDialogDirectory(),
                                                                            getFileDialogPROJFilter())
            if len(project_file_path) == 0:
                return False
            if os.path.splitext(project_file_path)[1] != ".proj":
                QMessageBox.about(self, "File Type Error",
                                  "Please select .proj file, other files can't be opened in Flow Studio.")
                return False
            try:
                self.temp_folder_path = tempfile.mkdtemp()
            except PermissionError:
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Error code:{PERMISSION_ERROR_WHEN_CREATE_TEMP_FOLDER}'
                )
                return
            self.project_folder_path = os.path.dirname(project_file_path)
            self.project_name = os.path.splitext(os.path.basename(project_file_path))[0]
            if not self.unCompressZIPFile(project_file_path, self.temp_folder_path):
                return False

            self.setWindowTitle('Flow Studio - ' + self.project_folder_path.split('/')[-1])

            # Write path to file
            self.onWritePathToFile(project_file_path)

        try:
            if self.temp_folder_path:
                files = os.listdir(self.temp_folder_path)
                main_file = self.temp_folder_path + "/main.json"
                if not os.path.exists(main_file):
                    QMessageBox.about(self, "File content is empty",
                                      "Don't have main.json file in %s.proj" % hidden_dir)
                    return False
                # ensure main.json window is on the most left
                files.remove('main.json')
                files.sort()
                files.insert(0, 'main.json')
                main_window = None
                self.clear_sub_patchs_window_objects()
                for file in files:
                    if file.endswith('.json'):
                        fname = self.temp_folder_path + '/' + file
                        with open(fname) as f:
                            file_data = json.load(f)
                            if 'is_encrypted' in file_data:
                                # If file has been encrypted, don't open it
                                if file_data['is_encrypted']:
                                    to_close_windows = []
                                    def dfs_decrypt_subpatch(subpatch_name):
                                        with open(fr'{self.temp_folder_path}\{subpatch_name}.json') as f:
                                            file_data = json.load(f)
                                            correct_password = AESOperation().decrypt_string(password=SECRET_KEY,
                                                                                             input_string=file_data[
                                                                                                 'password'])
                                            decrypt_object = AESOperation().decrypt_string(password=correct_password,
                                                                                           input_string=file_data[
                                                                                               'object'])
                                        dic = json.loads(decrypt_object)
                                        with open(fr'{self.temp_folder_path}\{subpatch_name}.json', 'w') as file:
                                            json.dump(dic, file, indent=4)
                                        fname = fr'{self.temp_folder_path}\{subpatch_name}.json'
                                        nodeeditor = FLOW_Sub_Group()
                                        if nodeeditor.fileLoad(fname):
                                            self.statusBar().showMessage(
                                                "File %s.proj has been loaded" % self.temp_folder_path,
                                                3000)
                                            nodeeditor.setTitle()
                                            nodeeditor.title = nodeeditor.getPrettyFilename()
                                            subwnd = self.createGroupChild(nodeeditor)
                                            subwnd.widget().already_input_password = False
                                            subwnd.widget().encrypted = True
                                            subwnd.widget().correct_password = correct_password
                                            subwnd.show()
                                            to_close_windows.append(subwnd)
                                        subpatchs_inside = []
                                        for node in dic['nodes']:
                                            if node['op_code'] == OP_NODE_SUBPATCH:
                                                is_subpatch_inside = True
                                                subpatchs_inside.append(node['title'])
                                        # region Here, save file in encrypted format
                                        with open(fr'{self.temp_folder_path}\{subpatch_name}.json') as f:
                                            file_data = json.load(f)
                                            encrypted_object = AESOperation().encrypt_string(password=correct_password,
                                                                                             input_string=json.dumps(
                                                                                                 file_data))
                                            encrypted_password = AESOperation().encrypt_string(password=SECRET_KEY,
                                                                                               input_string=correct_password)
                                            dic = {
                                                'object': str(base64.b64encode(encrypted_object), 'utf-8'),
                                                'password': str(base64.b64encode(encrypted_password), 'utf-8'),
                                                'is_encrypted': True
                                            }
                                            with open(fr'{self.temp_folder_path}\{subpatch_name}.json', 'w') as file:
                                                json.dump(dic, file)
                                        # endregion
                                    dfs_decrypt_subpatch(file.replace('.json', ''))
                                    for to_close_window in to_close_windows:
                                        self.close_sub_window(to_close_window)
                                    continue
                        existing = self.findMdiChildPath(fname)
                        if existing:
                            self.mdiArea.setActiveSubWindow(existing)
                        else:
                            # we need to create new subWindow and open the file
                            basename = os.path.splitext(file)[0]
                            if basename == 'main':
                                nodeeditor = FLOW_Sub_Window()
                            else:
                                nodeeditor = FLOW_Sub_Group()

                            if fname.endswith('main.json'):
                                subwnd = self.createMdiChild(nodeeditor)
                            else:
                                subwnd = self.createGroupChild(nodeeditor)

                            if nodeeditor.fileLoad(fname):
                                self.statusBar().showMessage(f'File {os.path.normpath(os.path.join(self.project_folder_path, self.project_file_name()))} has been loaded', 3000)
                                if fname.endswith('main.json'):
                                    nodeeditor.setTitle()
                                    main_window = subwnd
                                    subwnd.show()
                                else:
                                    nodeeditor.setTitle()
                                    nodeeditor.title = nodeeditor.getPrettyFilename()
                                    subwnd.show()
                            else:
                                nodeeditor.close()
                if main_window:
                    self.setActiveSubWindow(main_window)

                for node in main_window.widget().scene.nodes:
                    from flowstudio.flow_conf_co import OP_NODE_CO_CONSTANT
                    if node.op_code in [OP_NODE_CO_CONSTANT]:
                        node.value_change()

                # Track user action "Open Project"
                self.tracker = TrackManager()
                self.tracker.track_user_action(action=5, license=self.license_mechanism)
                return True
        except Exception as e:
            dumpException(e)
            return False

    def onOpenRecent(self):
        """
            Method triggered when clicking on a file name in the 'Open Recent' menu

            self.open_file_path attribute represents a list of file paths that have been successfully opened and edited,
            and is updated every time a new file is successfully opened
        """
        action = self.sender()
        project_file_path = action.text()
        if not self.onFileOpen(project_file_path=project_file_path):
            self.onDeletePathFile(project_file_path, self.open_file_path)

    def onOpenExampleFile(self):
        """
            By clicking Example file, this function will be called,
            and the selected project file will be opened
        """
        action = self.sender()
        filename = action.text()
        project_file_path = os.path.join(self.userPath, 'template', filename + '.proj')
        self.onFileOpen(project_file_path=project_file_path)
        self.onDeletePathFile(project_file_path, self.open_file_path)

    def onFileSave(self, export_xml=False):
        """
            Save all currently open node editor windows, including the main and sub windows.
        """
        main_window = self.findMain()
        main_nodeeditor = main_window.widget()
        content = []  # Store the flow information to be uploaded to the database
        if main_nodeeditor is not None:

            if self.temp_folder_path is not None:
                is_template_path = os.path.join(self.templatePath, self.project_file_name())
                if os.path.isfile(is_template_path):
                    return self.onFileSaveAs(export_xml=export_xml), True

            if not main_nodeeditor.isFilenameSet():
                return self.onFileSaveAs(export_xml=export_xml), True
            else:
                is_exist_closed_subwindow = False
                current_window = self.getCurrentNodeEditorWidget()
                for subwindow in self.sub_patchs:
                    if subwindow.closed:
                        is_exist_closed_subwindow = True
                if is_exist_closed_subwindow:
                    main_window = self.findMain()
                    nodes_in_main = main_window.widget().scene.nodes
                    for node in nodes_in_main:
                        if node.op_code == OP_NODE_SUBPATCH:
                            self.open_subwindow_in_subpatch_recursively(node.title)
                            self.setActiveSubWindow(current_window.parent())
                windows = self.mdiArea.subWindowList()
                all_save_file_names = []
                # main_nodeeditor.fileSave()
                for window in windows:
                    for node in window.widget().scene.nodes:
                        if node.content_label_objname == 'SUBPATCH':
                            # AO_Name = node.content_label_objname + "_" + str(node.designator)
                            node.cwd = node.title
                    if not window.widget().filename:
                        filename = window.widget().getPrettyFilename()
                        window.widget().fileSave(filename=os.path.join(self.temp_folder_path, filename + '.json'))
                        if hasattr(window.widget(), 'encrypted'):
                            if window.widget().encrypted:
                                self.encrypt_file_not_recursively(file_name=os.path.join(self.temp_folder_path, filename + '.json'),
                                                                  input_password=window.widget().correct_password)
                        all_save_file_names.append(filename + '.json')
                    else:
                        if type(window.widget()) == FLOW_Sub_Group:
                            if window.widget().renamed:
                                if os.path.basename(window.widget().filename) != window.widget().title+'.json':
                                    os.remove(window.widget().filename)
                                    if '.json' in window.widget().title:
                                        filename = window.widget().title
                                        window.widget().fileSave(filename=self.temp_folder_path + '/' + filename)
                                        all_save_file_names.append(filename)
                                        if hasattr(window.widget(), 'encrypted'):
                                            if window.widget().encrypted:
                                                self.encrypt_file_not_recursively(file_name=self.temp_folder_path + '/' + filename,
                                                                                  input_password=window.widget().correct_password)
                                    else:
                                        filename = window.widget().title + '.json'
                                        window.widget().fileSave(filename=self.temp_folder_path + '/' + filename)
                                        all_save_file_names.append(filename)
                                        if hasattr(window.widget(), 'encrypted'):
                                            if window.widget().encrypted:
                                                self.encrypt_file_not_recursively(
                                                    file_name=self.temp_folder_path + '/' + filename,
                                                    input_password=window.widget().correct_password)
                                else:
                                    window.widget().fileSave()
                                    all_save_file_names.append(os.path.basename(window.widget().filename))
                                    if hasattr(window.widget(), 'encrypted'):
                                        if window.widget().encrypted:
                                            self.encrypt_file_not_recursively(file_name=self.temp_folder_path + '/' + os.path.basename(window.widget().filename),
                                                                              input_password=window.widget().correct_password)
                            else:
                                if os.path.basename(window.widget().filename) != window.widget().getPrettyFilename()+'.json':
                                    os.remove(window.widget().filename)
                                    filename = window.widget().getPrettyFilename() + '.json'
                                    window.widget().fileSave(filename=self.temp_folder_path + '/' + filename)
                                    all_save_file_names.append(filename)
                                    if hasattr(window.widget(), 'encrypted'):
                                        if window.widget().encrypted:
                                            self.encrypt_file_not_recursively(file_name=self.temp_folder_path + '/' + filename,
                                                                              input_password=window.widget().correct_password)
                                else:
                                    window.widget().fileSave()
                                    all_save_file_names.append(os.path.basename(window.widget().filename))
                                    if hasattr(window.widget(), 'encrypted'):
                                        if window.widget().encrypted:
                                            self.encrypt_file_not_recursively(file_name=self.temp_folder_path + '/' + os.path.basename(window.widget().filename),
                                                                              input_password=window.widget().correct_password)

                        else:
                            window.widget().fileSave()
                            all_save_file_names.append(os.path.basename(window.widget().filename))
                    if type(window.widget()) == FLOW_Sub_Group:
                        window.widget().renamed = False
                        window.widget().setTitle(is_save_file=True)
                    else:
                        # support for MDI app
                        if hasattr(window.widget(), "setTitle"):
                            window.widget().setTitle()
                        else:
                            self.setTitle()
                    # region Store the flow information to content variable
                    scene_hash_map = {}
                    scene_hash_map['name'] = 'main' if type(window.widget()) != FLOW_Sub_Group else window.widget().getPrettyFilename()
                    scene_hash_map['nodes'] = window.widget().scene.serialize()['nodes']
                    scene_hash_map['edges'] = window.widget().scene.serialize()['edges']
                    # region delete unnecessary node info
                    keys_to_delete = ['color']
                    for node in scene_hash_map['nodes']:
                        for key_to_delete in keys_to_delete:
                            if key_to_delete in node:
                                del node[key_to_delete]
                    # endregion
                    # region delete unnecessary edge info
                    keys_to_delete = ['edge_type']
                    for edge in scene_hash_map['edges']:
                        for key_to_delete in keys_to_delete:
                            if key_to_delete in edge:
                                del edge[key_to_delete]
                    # endregion
                    if hasattr(window.widget(), 'encrypted') and \
                            window.widget().encrypted and \
                            hasattr(window.widget(), 'already_input_password') and \
                            not window.widget().already_input_password:
                        scene_hash_map['encrypted'] = window.widget().encrypted
                        scene_hash_map['already_input_password'] = window.widget().already_input_password
                        del scene_hash_map['nodes']
                        del scene_hash_map['edges']
                    content.append(scene_hash_map)
                    # endregion
                    if hasattr(window.widget(), 'close_if_no_problem'):
                        if window.widget().close_if_no_problem:
                            self.close_sub_window(window)
                # region 刪除沒有存檔的檔案
                files = os.listdir(self.temp_folder_path)
                for file in files:
                    if file not in all_save_file_names:
                        os.remove(self.temp_folder_path + '/' + file)
                # endregion
                if export_xml:
                    self.findMain().widget().exportXML(sub_window=self.findMain().widget(),
                                                       flw_file_path=self.temp_folder_path + "/default_config.flw")
                self.statusBar().showMessage(f'Saved {os.path.normpath(os.path.join(self.project_folder_path, self.project_file_name()))} successfully.', 5000)

                if self.temp_folder_path is not None:
                    if os.path.exists(self.project_folder_path + ".proj"):
                        os.remove(self.project_folder_path + ".proj")
                    self.convertFileToZIPFormat(self.temp_folder_path, os.path.join(self.project_folder_path, self.project_name + ".proj"))
                self.setActiveSubWindow(current_window.parent())

                # When there is a subpatch, saving will add the path to open_file_path.txt file
                self.onWritePathToFile(os.path.normpath(os.path.join(self.project_folder_path, self.project_file_name())))
                if self.license_mechanism.is_online and self.license_mechanism.is_tracking:
                    self.upload_project_info(action='save',
                                             content=content,
                                             project_name=self.temp_folder_path.split('/')[-1])

                # Track user action "Save Project"
                self.tracker = TrackManager()
                self.tracker.track_user_action(action=4, license=self.license_mechanism)
                return True, False

    def onFileSaveAs(self, export_xml=False, dir_path=None, project_file_name=None):
        """
            Save as new file\n
            If both dir_path and project_file_name parameters are None,
            ask user to specify directory path and project file name to save\n

            :param export_xml: boolean, export flw file or not
                default:False

            :param dir_path: str, directory path to save
                default:None

            :param project_file_name: str, name of project file to save
                default:None

            :return: boolean, if no problems, return True,
                if having problems, return False.
        """
        # region The dir_path parameter and the project_file_name parameter must both be None, or they must both not be None
        if dir_path is not None and project_file_name is None:
            return False
        if dir_path is None and project_file_name is not None:
            return False
        # endregion
        for gui_window in self.all_window_objects:
            gui_window.hide()
        if dir_path is None and project_file_name is None:
            fdir = QFileDialog.getExistingDirectory(self, 'Choose a directory to place project',
                                                    self.getFileDialogDirectory())

            if fdir == '':
                return False

            result = self.editTitleDialogWidget.exec()
            if result == 0:
                return False
            pname = self.editTitleDialog.lineEdit.text()
            if pname == '':
                return False
        else:
            fdir = dir_path
            pname = project_file_name

        try:
            self.setWindowTitle('Flow Studio - ' + pname)
            try:
                self.temp_folder_path = tempfile.mkdtemp()
            except PermissionError:
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Error code:{PERMISSION_ERROR_WHEN_CREATE_TEMP_FOLDER}'
                )
                return False
            self.project_folder_path = fdir
            self.project_name = pname
            # When you click Save As, the path will be added to open_file_path.txt file
            self.onWritePathToFile(os.path.normpath(os.path.join(self.project_folder_path, self.project_file_name())))

            if Debug.DEBUG_Low_Level.value:
                print("Successfully created the directory %s " % fdir)
        except OSError:
            if Debug.DEBUG_Low_Level.value:
                print("Creation of the directory %s failed" % fdir)
            self.settingDialog.onTerminateSocket("Creation Failed")
            return False
        num_windows = len(self.mdiArea.subWindowList())
        is_exist_closed_subwindow = False
        current_window = self.getCurrentNodeEditorWidget()
        for subwindow in self.sub_patchs:
            if subwindow.closed:
                is_exist_closed_subwindow = True
        content = []  # Store the flow information to be uploaded to the database
        if num_windows > 1 or is_exist_closed_subwindow:  # there is subpatch
            main_window = self.findMain()
            nodes_in_main = main_window.widget().scene.nodes
            for node in nodes_in_main:
                if node.op_code == OP_NODE_SUBPATCH:
                    self.open_subwindow_in_subpatch_recursively(node.title)
                    self.setActiveSubWindow(current_window.parent())
            windows = self.mdiArea.subWindowList()
            # region generate json file for each window
            for window in windows:
                if window.widget().filename:
                    title = os.path.split(window.widget().filename)
                    file_name = os.path.join(self.temp_folder_path, title[1])
                else:
                    # main window
                    if window.widget().getUserFriendlyFilename() in ["New FLOW", "New FLOW*"]:
                        title = 'main'
                    # not main window
                    else:
                        title = window.widget().getPrettyFilename()
                    file_name = os.path.join(self.temp_folder_path, title + '.json')
                # region Store the flow information to content variable
                scene_hash_map = {}
                scene_hash_map['name'] = 'main' if type(window.widget()) != FLOW_Sub_Group else window.widget().getPrettyFilename()
                scene_hash_map['nodes'] = window.widget().scene.serialize()['nodes']
                scene_hash_map['edges'] = window.widget().scene.serialize()['edges']
                # region delete unnecessary node info
                keys_to_delete = ['color']
                for node in scene_hash_map['nodes']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in node:
                            del node[key_to_delete]
                # endregion
                # region delete unnecessary edge info
                keys_to_delete = ['edge_type']
                for edge in scene_hash_map['edges']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in edge:
                            del edge[key_to_delete]
                # endregion
                if hasattr(window.widget(), 'encrypted') and \
                        window.widget().encrypted and \
                        hasattr(window.widget(), 'already_input_password') and \
                        not window.widget().already_input_password:
                    scene_hash_map['encrypted'] = window.widget().encrypted
                    scene_hash_map['already_input_password'] = window.widget().already_input_password
                    del scene_hash_map['nodes']
                    del scene_hash_map['edges']
                content.append(scene_hash_map)
                # endregion
                for node in window.widget().scene.nodes:
                    if node.content_label_objname == 'SUBPATCH':
                        # AO_Name = node.content_label_objname + "_" + str(node.designator)
                        node.cwd = node.title
                self.onBeforeSaveAs(window.widget(), file_name)
                window.widget().fileSave(file_name)
                if type(window.widget()) == FLOW_Sub_Group:
                    window.widget().renamed = False
                    window.widget().setTitle(is_save_file=True)
                else:
                    if hasattr(window.widget(), "setTitle"):
                        window.widget().setTitle()
                if hasattr(window.widget(), 'encrypted'):
                    if window.widget().encrypted:
                        sub_window_name = window.widget().getPrettyFilename()
                        with open(fr'{self.temp_folder_path}\{sub_window_name}.json') as f:
                            file_data = json.load(f)
                            encrypted_object = AESOperation().encrypt_string(password=window.widget().correct_password,
                                                                             input_string=json.dumps(file_data))
                            encrypted_password = AESOperation().encrypt_string(password=SECRET_KEY,
                                                                               input_string=window.widget().correct_password)
                            dic = {
                                'object': str(base64.b64encode(encrypted_object), 'utf-8'),
                                'password': str(base64.b64encode(encrypted_password), 'utf-8'),
                                'is_encrypted': True
                            }
                            # overwrite SUBPATCH file
                            with open(fr'{self.temp_folder_path}\{window.widget().title}.json', 'w') as file:
                                json.dump(dic, file)
                if hasattr(window.widget(), 'close_if_no_problem'):
                    if window.widget().close_if_no_problem:
                        self.close_sub_window(window)
            self.setActiveSubWindow(current_window.parent())
            # endregion
            # region generate flw file
            if export_xml:
                self.findMain().widget().exportXML(sub_window=self.findMain().widget(),
                                                   flw_file_path=self.temp_folder_path + "/default_config.flw")
            # endregion
        else:
            for window in self.mdiArea.subWindowList():
                if window.widget().filename:
                    # project has been saved...
                    title = os.path.split(window.widget().filename)
                    # combine title, pname, fdir together
                    fname = os.path.join(self.temp_folder_path, title[1])
                else:
                    # project has not been saved, new project
                    if window.widget().getUserFriendlyFilename() in ["New FLOW", "New FLOW*"]:
                        # main page
                        title = 'main'
                    else:
                        # sub patch page
                        if window.widget().getUserFriendlyFilename().endswith('*'):
                            # if modified, ends with asterisk
                            title = window.widget().getUserFriendlyFilename()[:-1]
                        else:
                            # if not modified
                            title = window.widget().getUserFriendlyFilename()
                    fname = os.path.join(self.temp_folder_path, title + '.json')
                # region Store the flow information to content variable
                scene_hash_map = {}
                scene_hash_map['name'] = 'main'
                scene_hash_map['nodes'] = window.widget().scene.serialize()['nodes']
                scene_hash_map['edges'] = window.widget().scene.serialize()['edges']
                # region delete unnecessary node info
                keys_to_delete = ['color']
                for node in scene_hash_map['nodes']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in node:
                            del node[key_to_delete]
                # endregion
                # region delete unnecessary edge info
                keys_to_delete = ['edge_type']
                for edge in scene_hash_map['edges']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in edge:
                            del edge[key_to_delete]
                # endregion
                content.append(scene_hash_map)
                # endregion
                for node in window.widget().scene.nodes:
                    if node.content_label_objname == 'SUBPATCH':
                        # AO_Name = node.content_label_objname + "_" + str(node.designator)
                        node.cwd = node.title
                self.onBeforeSaveAs(window.widget(), fname)
                window.widget().fileSave(fname)
                if export_xml:
                    window.widget().exportXML(sub_window=self.findMain().widget(),
                                              flw_file_path=self.temp_folder_path + "/default_config.flw")
                # support for MDI app
                if hasattr(window.widget(), "setTitle"):
                    window.widget().setTitle()
        if self.license_mechanism.is_online and self.license_mechanism.is_tracking:
            self.upload_project_info(action='save',
                                     content=content,
                                     project_name=pname)
        self.statusBar().showMessage("Successfully saved as %s under %s" % (pname + ".proj", fdir), 5000)

        if self.temp_folder_path is not None:
            if os.path.exists(self.project_folder_path + ".proj"):
                os.remove(self.project_folder_path + ".proj")
            self.convertFileToZIPFormat(self.temp_folder_path, os.path.join(self.project_folder_path, self.project_name + ".proj"))
        for gui_window in self.all_window_objects:
            gui_window.show()
        return True

    def onWritePathToFile(self, path):
        """
            Write the recently opened file path into the file
            self.open_file_path attribute represents a list of file paths that have been successfully opened and edited

            :param path, Recently opened file path
        """
        filename = self.open_file_path
        with open(filename, 'r+') as file_object:
            lines = file_object.readlines()
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip("\n")
            if len(lines) == 0:
                lines.insert(0, path)
            else:
                for i in range(len(lines)):
                    if lines[i] == path:
                        lines[i] = "m"
                if "m" in lines:
                    lines.remove("m")
                lines.insert(0, path)
            with open(filename, 'w') as file_object:
                for i in range(len(lines)):
                    file_object.write(lines[i] + "\n")
        self.createRecent()

    def onDeletePathFile(self, path, filepath):
        """
            If the recently opened file path not exist, this path will be deleted from the file

            :param path, recently opened file path
            :param filepath, Record the file path of the path list
        """
        with open(filepath, 'r+') as file_object:
            lines = file_object.readlines()
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip("\n")
                if lines[i] == path:
                    if Debug.DEBUG_Low_Level.value: print(lines)
                    lines[i] = "m"
            lines.remove("m")
            if Debug.DEBUG_Low_Level.value: print(lines)
            with open(filepath, 'w') as file_object:
                for i in range(len(lines)):
                    file_object.write(lines[i] + "\n")
        self.createRecent()

    def convertFileToZIPFormat(self, folder_path, zip_path):
        """
            Convert the file to zip format

            :param folder_path, Path of the file
            :param zip_path, Generated compressed file path
        """
        try:
            z = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
            for dirPath, dirNames, fileNames in os.walk(folder_path):
                for filename in fileNames:
                    z.write(os.path.join(dirPath, filename), filename)
            z.close()
        except Exception as e:
            if Debug.DEBUG_Low_Level.value: print("Error: " % (e))
            self.statusBar().showMessage('')
            self.settingDialog.onTerminateSocket("Creation Failed")

    def unCompressZIPFile(self, zip_src, dst_dir):
        """
            Unconvert the file to zip format

            :param zip_src, Path to extract files
            :param dst_dir, Decompress the path to a certain location
        """
        try:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
            win32api.SetFileAttributes(dst_dir, win32con.FILE_ATTRIBUTE_HIDDEN)
            fz.close()
            return True
        except Exception as e:
            QMessageBox.about(self, "invalid file content format",
                              "sorry, file content is invalid format,please check it.")
            return False

    def onSubpatchFileOpen(self, file_path):
        """
            Open SubPatch File
        """
        nodeeditor = FLOW_Sub_Group()
        if nodeeditor.fileLoad(file_path):
            self.statusBar().showMessage("File %s loaded" % file_path, 3000)
            nodeeditor.setTitle()
            subwnd = self.createGroupChild(nodeeditor)
            self.set_custom_menu_for_sub_window(subwnd)
            subwnd.show()
            return True
        else:
            nodeeditor.close()
            return False

    def createNewGroupFile(self, node, fdir=None):
        """
            Create a new group file

            :param node, Nodes added to group files
            :param fdir, Save location for group files
        """
        AO_Name = node.content_label_objname + '_' + str(node.designator)
        AO_Name = node.title
        node.cwd = "temp"

        subwnd = self.createGroupChild()
        subwnd.widget().title = AO_Name
        subwnd.widget().fileNew()
        subwnd.widget().setTitle()

        inputChannels = len(node.inputs)
        for index in range(inputChannels):
            inlet_node = INLET.FLOW_Node_INLET(subwnd.widget().scene)
            inlet_node.designator = index + 1
            inlet_node.grNode.title += '_' + str(index + 1)
            inlet_node.title += '_' + str(index + 1)
            inlet_node.setPos(-400, -150 + index * 150)
            # inlet_node.grNode.setFlag(QGraphicsItem.ItemIsSelectable, False)

        outputChannels = len(node.outputs)
        for index in range(outputChannels):
            outlet_node = OUTLET.FLOW_Node_OUTLET(subwnd.widget().scene)
            outlet_node.designator = index + 1
            outlet_node.grNode.title += '_' + str(index + 1)
            outlet_node.title += '_' + str(index + 1)
            outlet_node.setPos(400, -150 + index * 150)
            # outlet_node.grNode.setFlag(QGraphicsItem.ItemIsSelectable, False)

        if fdir:
            node.cwd = AO_Name
            fname = os.path.split(fdir)[0] + '/' + AO_Name + '.json'
            subwnd.widget().scene.saveToFile(fname)
            subwnd.widget().filename = fname
            subwnd.widget().setTitle()
            subwnd.widget().scene.history.clear()
            subwnd.widget().scene.history.storeInitialHistoryStamp()
        else:
            subwnd.widget().scene.history.clear()
            subwnd.widget().scene.history.storeInitialHistoryStamp()
            subwnd.widget().scene.has_been_modified = True
        subwnd.show()

    def onEval(self):
        for node in self.getCurrentNodeEditorWidget().scene.nodes:
            if node.isDirty():
                if Debug.DEBUG_Low_Level.value: print("Dirty Node:", node)
                node.eval()

        # TODO: actuall it's not a very efficient way to eval node... better strategy as follows
        # 1. eval the new node, from selected item like this: new_items = self.getCurrentNodeEditorWidget().getSelectedItems()
        # 2. to eval the rest node... like this: select_all = self.getCurrentNodeEditorWidget().scene.nodes
        # select_all pop out new_items...
        # above procedure could save a lot of time rather than eval all node arbitrary!!

    def about(self):
        """
            menu selection： Help -> About Execution method
        """
        for gui_window in self.all_window_objects: gui_window.hide()
        # Create and show the dialog
        dialog = CustomAboutDialog(self)
        dialog.exec_()
        for gui_window in self.all_window_objects: gui_window.show()

    def info(self):
        """
            menu selection： Help -> Info Execution method
        """
        if self.settingDialog.client.connection:
            info_result = self.settingDialog.parse_result_of_info_command(self.settingDialog.cpuClient.hQuery('info/'))
            if info_result['status']:
                for gui_window in self.all_window_objects: gui_window.hide()
                QMessageBox.about(self, "About Flow Engine",
                                  "Flow Engine Version: %s <br> "
                                  "Sample Rate: %s <br>"
                                  "Frame Size: %s <br>"
                                  "Maximum Input Channel: %s <br>"
                                  "Maximum Output Channel: %s <br>" % (info_result['result']['Flow Engine Version'],
                                                                       info_result['result']['Sample Rate'],
                                                                       info_result['result']['Frame Size'],
                                                                       info_result['result']['Maximum Input Channel'],
                                                                       info_result['result']['Maximum Output Channel']))
                for gui_window in self.all_window_objects: gui_window.show()

    def userGuide(self):
        """
            menu selection： Help -> User Guide Execution method
        """
        subprocess.Popen(["Flow Studio - User Guide.pdf"], shell=True)

    def handleFeedback(self):
        """
            menu selection： Help -> Submit Feedback
        """
        import webbrowser
        from urllib.parse import quote
        import textwrap

        recipient = "support@flow-dsp.com"
        subject = "My suggestion for Flow Studio"
        raw_body = """
            We value your experience with Flow Studio and would love to hear your suggestions for improvement.
            
            What features would you like to see added or enhanced? Any workflows we could simplify?

            [SHARE YOUR SUGGESTION]

            Your input directly shapes our development roadmap. Every suggestion is reviewed by our team.

            Thank you for helping us make Flow Studio better!

            Best regards,
            The Flow Studio Team
        """

        body = textwrap.dedent(raw_body)
        body = body.strip()
        body = body.replace("\n", "\r\n")
        encoded_body = quote(body)
        encoded_subject = quote(subject)
        mailto_url = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"
        webbrowser.open(mailto_url)

    def onOpenArchitectureGuide(self):
        """
            menu selection： Help -> Open Architecture Execution method
        """
        subprocess.Popen(["FlowStudio - Open Architecture User Guide.pdf"], shell=True)

    def warning_information(self, shortcut):
        """
           warning information
        """
        if Debug.DEBUG_Low_Level.value: print(shortcut)
        if Debug.DEBUG_Low_Level.value: print(type(shortcut))
        infoDispText = ("you're currently <b>connected to FLOW Engine</b>, <b>" + str(
            shortcut) + "</b> function can be operated.")
        QMessageBox.about(self, "Information", infoDispText)

    def createMenus(self):
        """
           Create a menu for the navigation bar（'File', 'Edit', 'Window', 'Options', 'Help'）
        """
        super().createMenus()
        self.tools_menu = self.menuBar().addMenu("&Tools")
        self.update_tools_menu()
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.editMenu.aboutToShow.connect(self.updateEditMenu)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actSelectAll)

        self.optionsMenu = self.menuBar().addMenu("&Options")
        self.optionsMenu.addAction(self.actPreference)
        # TODO: we will disable simulation in the current 0.25 version
        # self.optionsMenu.addAction(self.actAnalysis)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction(self.actEditMode)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction(self.actRuleCheck)
        self.optionsMenu.addSeparator()
        # self.optionsMenu.addAction(self.actScanAudioInterface)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction(self.actUpload)
        self.optionsMenu.addAction(self.actDownload)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)
        self.helpMenu.addAction(self.actInfo)
        self.helpMenu.addAction(self.actUserGuide)
        self.helpMenu.addAction(self.actFeedback)
        self.helpMenu.addAction(self.actOAGuide)

        self.actUpload.setEnabled(False)
        self.actDownload.setEnabled(False)

        # 将按钮组添加到菜单栏右上角
        mixed_btn = QPushButton(QIcon("../resources/user.png"), '')
        mixed_btn.setIconSize(QSize(18, 18))
        mixed_btn.clicked.connect(self.OpenUserInfoPane)
        mixed_btn.setStyleSheet("""
            QPushButton {
                background: #474747;
                border: None;
                border-radius: 4px;
                margin-top: 3px;
                margin-right: 2px;
            }
            QPushButton:hover {
                background: #7d7d7d;
            }
        """)
        right_widget = QWidget()
        hbox = QHBoxLayout(right_widget)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setAlignment(Qt.AlignTop)
        hbox.addWidget(mixed_btn)
        self.menuBar().setCornerWidget(right_widget, Qt.TopRightCorner)

    def updateMenus(self):
        """
            If at least one child window is activated at this time, set hasMdiChild to true.
            Based on the value of hasMdiChild, enable or disable some menu items related to sub windows, such as "Save", "Save As", "Export", etc.
            Finally, call the updateEditMenu() method to update the Edit menu.
        """
        # print("update Menus")
        if len(self.mdiArea.subWindowList()) == 0:
            if self.editmode:
                self.toolbtnpressed()
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actExport.setEnabled(hasMdiChild)
        self.actExportCommit.setEnabled(hasMdiChild)
        self.actExportRawCommand.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        # self.actCascade.setEnabled(hasMdiChild)
        # self.actNext.setEnabled(hasMdiChild)
        # self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)
        self.actRuleCheck.setEnabled(hasMdiChild)

        self.updateEditMenu()

    def update_export_custom_aos_settings_availability(self):
        """
            Update the availability of the export custom aos settings action
        """
        if self.exist_custom_aos:
            self.act_export_custom_aos_settings.setEnabled(True)
        else:
            self.act_export_custom_aos_settings.setEnabled(False)

    def updateEditMenu(self):
        """
           Set Edit Menu bar options to enable or disable
        """
        try:
            # print("update Edit Menu")
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)

            self.actNew.setEnabled(not self.editmode)
            # self.actMultiple.setEnabled(not self.editmode)
            self.actOpen.setEnabled(not self.editmode)
            self.actOpenRecent.setEnabled(not self.editmode)
            self.actExample.setEnabled(not self.editmode)
            self.actPaste.setEnabled(hasMdiChild and not self.editmode)

            self.actCut.setEnabled((hasMdiChild and active.hasSelectedItems()) and not self.editmode)
            self.actCopy.setEnabled((hasMdiChild and active.hasSelectedItems()) and not self.editmode)
            self.actDelete.setEnabled((hasMdiChild and active.hasSelectedItems()) and not self.editmode)

            self.actUndo.setEnabled((hasMdiChild and active.canUndo()) and not self.editmode)
            self.actRedo.setEnabled((hasMdiChild and active.canRedo()) and not self.editmode)

            self.actQuickNew.setEnabled(self.actNew.isEnabled())
            self.actQuickOpen.setEnabled(self.actOpen.isEnabled())
            self.actQuickOpen.setEnabled(self.actOpenRecent.isEnabled())
            self.actQuickSave.setEnabled(self.actSave.isEnabled())
            self.actQuickSaveAs.setEnabled(self.actSaveAs.isEnabled())

            self.actQuickUndo.setEnabled(self.actUndo.isEnabled())
            self.actQuickRedo.setEnabled(self.actRedo.isEnabled())

            self.actQuickCut.setEnabled(self.actCut.isEnabled())
            self.actQuickCopy.setEnabled(self.actCopy.isEnabled())
            self.actQuickPaste.setEnabled(self.actPaste.isEnabled())
            self.actQuickDelete.setEnabled(self.actDelete.isEnabled())

            self.actQuickSetting.setEnabled(self.actPreference.isEnabled())

            self.actQuickDump.setEnabled(self.editmode)

            # self.actQuickUpload.setEnabled(self.actUpload.isEnabled())
            # self.actQuickDownload.setEnabled(self.actDownload.isEnabled())
            # self.actScanAudioInterface.setEnabled(not self.editmode)

            self.actClose.setEnabled(hasMdiChild)
            self.actCloseAll.setEnabled(hasMdiChild)
            self.actTile.setEnabled(hasMdiChild)

        except Exception as e:
            dumpException(e)

    def update_tools_menu(self):
        self.tools_menu.clear()
        self.tools_menu.addAction(self.act_signal_flow_diff)
        self.tools_menu.addAction(self.act_custom_ao_builder)
        self.tools_menu.addAction(self.act_import_custom_aos_settings)
        self.tools_menu.addAction(self.act_export_custom_aos_settings)

    def updateWindowMenu(self):
        """
           update Window Menu
           1. Create two options, namely "Audio Object Toolbar" and "Editor Toolbar"
           2. Create basic menu items such as Close, Close All, Tile, etc
           3. Traverse all sub windows, creating a corresponding option for each sub window
        """
        self.windowMenu.clear()

        # TODO: temporary hides the node dock, node toolbar
        toolbar_Editor = self.windowMenu.addAction("Editor Toolbar")
        toolbar_Editor.setCheckable(True)
        toolbar_Editor.triggered.connect(self.onWindowEditorToolbar)
        toolbar_Editor.setChecked(self.editorDock.isVisible())

        toolbar_nodes_filter = self.windowMenu.addAction("Audio Object Filter")
        toolbar_nodes_filter.setCheckable(True)
        toolbar_nodes_filter.triggered.connect(self.handle_nodes_filter_visible)
        toolbar_nodes_filter.setChecked(self.nodeFilterDock.isVisible())

        toolbar_nodes = self.windowMenu.addAction("Audio Object Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        toolbar_node_property = self.windowMenu.addAction('Property Pane')
        toolbar_node_property.setCheckable(True)
        toolbar_node_property.triggered.connect(self.handle_node_property_panel_visible)
        toolbar_node_property.setChecked(self.nodesPropertDock.isVisible())

        self.windowMenu.addSeparator()
        toolbar_nodes_co = self.windowMenu.addAction("Control Object Toolbar")
        toolbar_nodes_co.setCheckable(True)
        toolbar_nodes_co.triggered.connect(self.handle_nodes_control_object_visible)
        toolbar_nodes_co.setChecked(self.nodesControlDock.isVisible())
        self.windowMenu.addSeparator()

        cmd_window_action = self.windowMenu.addAction("Command Input")
        cmd_window_action.setCheckable(True)
        cmd_window_action.triggered.connect(self.onWindowCmdInput)
        cmd_window_action.setChecked(self.cmdDock.isVisible())

        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addSeparator()
        # self.windowMenu.addAction(self.actCascade)
        # self.windowMenu.addSeparator()
        # self.windowMenu.addAction(self.actNext)
        # self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = "&" + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowEditorToolbar(self):
        """
            Control the display or hiding of the Edit ToolBar (image Tool Bar)
        """
        if self.editorDock.isVisible():
            self.editorDock.hide()
        else:
            self.editorDock.show()

    def onWindowNodesToolbar(self):
        """
            Control the display or hiding of the Nodes ToolBar (Audio Object Toolbar)
        """
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def handle_nodes_filter_visible(self):
        """
            Control the display or hiding of the Nodes ToolBar (Audio Object Filter Toolbar)
        """
        if self.nodeFilterDock.isVisible():
            self.nodeFilterDock.hide()
        else:
            self.nodeFilterDock.show()

    def handle_node_property_panel_visible(self):
        """
            Handle the visibility of the node property panel.

            This function manages the visibility of the node property panel and any associated actions when called.
        """
        if self.nodesPropertDock.isVisible():
            self.nodesPropertDock.hide()
        else:
            self.nodesPropertDock.show()

    def handle_nodes_control_object_visible(self):
        """
            Control the display or hiding of the Control Object ToolBar (Control Object Toolbar)
        """
        if self.nodesControlDock.isVisible():
            self.nodesControlDock.hide()
        else:
            self.nodesControlDock.show()

    def createEditorDock(self):
        """
           Create Editor Toolbar (image Tool Bar)
        """
        self.editorDock = self.addToolBar("Edit Toolbar")
        self.editorDock.setIconSize(QSize(24, 24))
        self.editorDock.setStyleSheet("background-color: gray")

        self.actQuickNew = QAction(QIcon("../resources/new.png"), "New", self, triggered=self.onFileNew)
        self.editorDock.addAction(self.actQuickNew)

        self.actQuickOpen = QAction(QIcon("../resources/open.png"), "Open", self, triggered=self.onFileOpen)
        self.editorDock.addAction(self.actQuickOpen)

        self.actQuickSave = QAction(QIcon("../resources/save.png"), "Save", self, triggered=self.onFileSave)
        self.editorDock.addAction(self.actQuickSave)

        self.actQuickSaveAs = QAction(QIcon("../resources/saveas.png"), "Save As", self, triggered=self.onFileSaveAs)
        self.editorDock.addAction(self.actQuickSaveAs)

        self.actQuickUndo = QAction(QIcon("../resources/undo.png"), "Undo", self, triggered=self.onEditUndo)
        self.editorDock.addAction(self.actQuickUndo)

        self.actQuickRedo = QAction(QIcon("../resources/redo.png"), "Redo", self, triggered=self.onEditRedo)
        self.editorDock.addAction(self.actQuickRedo)

        self.actQuickCut = QAction(QIcon("../resources/cut.png"), "Cut", self, triggered=self.onEditCut)
        self.editorDock.addAction(self.actQuickCut)

        self.actQuickCopy = QAction(QIcon("../resources/copy.png"), "Copy", self, triggered=self.onEditCopy)
        self.editorDock.addAction(self.actQuickCopy)

        self.actQuickPaste = QAction(QIcon("../resources/paste.png"), "Paste", self, triggered=self.onEditPaste)
        self.editorDock.addAction(self.actQuickPaste)

        self.actQuickDelete = QAction(QIcon("../resources/delete.png"), "Delete", self, triggered=self.onEditDelete)
        self.editorDock.addAction(self.actQuickDelete)

        self.actQuickDump = QAction(QIcon("../resources/dump.png"), "Dump", self,
                                    triggered=self.onOpenControlDump)
        self.editorDock.addAction(self.actQuickDump)

        self.actQuickSetting = QAction(QIcon("../resources/setting.png"), "Connect Setting", self,
                                       triggered=self.onOpenControlDialog)
        self.editorDock.addAction(self.actQuickSetting)

        # self.actQuickUpload = QAction(QIcon("../resources/upload-cloud.png"), "Upload", self,
        #                               triggered=self.upload_target)
        # self.editorDock.addAction(self.actQuickUpload)

        # self.actQuickDownload = QAction(QIcon("../resources/download.png"), "download", self,
        #                                 triggered=self.download_target)
        # self.editorDock.addAction(self.actQuickDownload)

        self.actQuickConnect = QAction(QIcon("../resources/shut-down-line.png"), "Connect", self,
                                       triggered=self.toolbtnpressed)
        self.editorDock.addAction(self.actQuickConnect)

        # TODO: we will disable simulation in the current 0.25 version
        # self.actQuickAnalysis = QAction(QIcon("../resources/line-chart-line.png"), "Analysis", self, triggered=self.onSimulationDialog)
        # self.editorDock.addAction(self.actQuickAnalysis)

        self.actQuickAlignToLeft = QAction(QIcon("../resources/align-left.png"), "", self,
                                           triggered=self.quickAlignToLeft, statusTip="Align to left")
        self.editorDock.addAction(self.actQuickAlignToLeft)

        self.actQuickAlignToCenter = QAction(QIcon("../resources/align-center.png"), "", self,
                                             triggered=self.quickAlignToCenter, statusTip="Align to center")
        self.editorDock.addAction(self.actQuickAlignToCenter)

        self.actQuickAlignToRight = QAction(QIcon("../resources/align-right.png"), "", self,
                                            triggered=self.quickAlignToRight, statusTip="Align to right")
        self.editorDock.addAction(self.actQuickAlignToRight)

        self.actQuickAlignToTop = QAction(QIcon("../resources/align-top.png"), "", self, triggered=self.quickAlignToTop,
                                          statusTip="Align to top")
        self.editorDock.addAction(self.actQuickAlignToTop)

        self.actQuickAlignToMiddle = QAction(QIcon("../resources/align-middle.png"), "", self,
                                             triggered=self.quickAlignToMiddle, statusTip="Align to middle")
        self.editorDock.addAction(self.actQuickAlignToMiddle)

        self.actQuickAlignToBottom = QAction(QIcon("../resources/align-bottom.png"), "", self,
                                             triggered=self.quickAlignToBottom, statusTip="Align to bottom")
        self.editorDock.addAction(self.actQuickAlignToBottom)

        self.actQuickUploadFlash = QAction(QIcon("../resources/flash.png"), "Upload Flash", self,
                                           triggered=self.upload_flash)
        self.actQuickUploadFlash.setEnabled(False)
        self.editorDock.addAction(self.actQuickUploadFlash)

        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setVisible(True)
        self.editorDock.addWidget(spacer)
        self.actQuickSignalFlowAi = QAction(QIcon("../resources/signal-flow-assistant-icon.png"), "Flow AI Agent",
                                                   self,
                                                   triggered=self.open_flow_ai_dialog)
        self.editorDock.addAction(self.actQuickSignalFlowAi)

        self.actQuickSignalFlowAi1 = QAction(QIcon("../resources/signal-flow-assistant-icon.png"), "Flow AI Agent",
                                                   self,
                                                   triggered=self.open_flow_ai_dialog1)
        self.editorDock.addAction(self.actQuickSignalFlowAi1)

        self.setWindowTitle("toolbar demo")

    def quickAlignToLeft(self):
        """
            Eidt Tool Bar -> Left icon : Align the selected nodes to the left
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            left_grNode = order_grNodes[0]
            for grNode in order_grNodes:
                if grNode.pos().x() < left_grNode.pos().x():
                    left_grNode = grNode
            for grNode in order_grNodes:
                grNode.setPos(left_grNode.pos().x(), grNode.pos().y())
                grNode.node.updateConnectedEdges()

    def quickAlignToCenter(self):
        """
            Eidt Tool Bar -> Center icon : Align the selected nodes to the Center
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            left_grNode = order_grNodes[0]
            right_grNode = order_grNodes[0]
            for grNode in order_grNodes:
                if grNode.pos().x() < left_grNode.pos().x():
                    left_grNode = grNode
            for grNode in order_grNodes:
                if grNode.pos().x() > right_grNode.pos().x():
                    right_grNode = grNode

            centerX = (left_grNode.pos().x() + right_grNode.pos().x()) / 2

            for grNode in order_grNodes:
                grNode.setPos(centerX, grNode.pos().y())
                grNode.node.updateConnectedEdges()

    def quickAlignToRight(self):
        """
            Eidt Tool Bar -> Right icon : Align the selected nodes to the Right
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            right_grNode = order_grNodes[0]
            for grNode in order_grNodes:
                if grNode.pos().x() > right_grNode.pos().x():
                    right_grNode = grNode
            for grNode in order_grNodes:
                grNode.setPos(right_grNode.pos().x(), grNode.pos().y())
                grNode.node.updateConnectedEdges()

    def quickAlignToTop(self):
        """
            Eidt Tool Bar -> Top icon : Align the selected nodes to the Top
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            top_grNode = order_grNodes[0]
            for grNode in order_grNodes:
                if grNode.pos().y() < top_grNode.pos().y():
                    top_grNode = grNode
            for grNode in order_grNodes:
                grNode.setPos(grNode.pos().x(), top_grNode.pos().y())
                grNode.node.updateConnectedEdges()

    def quickAlignToMiddle(self):
        """
            Eidt Tool Bar -> Middle icon : Align the selected nodes to the Middle
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            top_grNode = order_grNodes[0]
            bottom_grNode = order_grNodes[0]
            for grNode in order_grNodes:
                if grNode.pos().y() > top_grNode.pos().y():
                    top_grNode = grNode
            for grNode in order_grNodes:
                if grNode.pos().y() < bottom_grNode.pos().y():
                    bottom_grNode = grNode

            centerY = (top_grNode.pos().y() + bottom_grNode.pos().y()) / 2

            for grNode in order_grNodes:
                grNode.setPos(grNode.pos().x(), centerY)
                grNode.node.updateConnectedEdges()

    def quickAlignToBottom(self):
        """
            Eidt Tool Bar -> Bottom icon : Align the selected nodes to the Bottom
        """
        if len(self.getCurrentNodeEditorWidget().scene.getSelectedItems()) > 1:
            order_grNodes = self.getCurrentNodeEditorWidget().scene.getOrderSelectedNodes()
            bottom_grNode = order_grNodes[0]
            height = order_grNodes[0].height
            for grNode in order_grNodes:
                if grNode.pos().y() + grNode.height > bottom_grNode.pos().y() + bottom_grNode.height:
                    bottom_grNode = grNode
            for grNode in order_grNodes:
                if grNode == bottom_grNode:
                    grNode.setPos(grNode.pos().x(), bottom_grNode.pos().y())
                    continue
                grNode.setPos(grNode.pos().x(), bottom_grNode.pos().y() + (bottom_grNode.height - grNode.height))
                grNode.node.updateConnectedEdges()

    def toolbtnpressed(self):
        """
            Used to handle toolbar button press events
        """
        self.settingDialog.controlDialog.checkBox_dsp.click()
        self.updateMenus()

    def updateShipText(self):
        """
            if checkBox_dsp is selected,
            Set the text of the 'Quick Connect' menu item to 'Disconnect', otherwise set it to 'Connect'
        """
        if self.settingDialog.controlDialog.checkBox_dsp.checkState() == 2:
            self.actQuickConnect.setText("Disconnect")
        elif self.settingDialog.controlDialog.checkBox_dsp.checkState() == 0:
            self.actQuickConnect.setText("Connect")

    def updateProcessSampleText(self):
        """
            Update the 'Sample Count' text label
        """
        sampleRate = float(self.analysisDialog.controlDialog.comboBox_2.currentText())
        duration = float(self.analysisDialog.controlDialog.doubleSpinBox_3.text())
        result = math.ceil(sampleRate * duration)
        self.analysisDialog.controlDialog.label_10.setText(str(result))

    def updateFrameCountText(self):
        """
            Update the 'Frame Count' text label
        """
        sample = int(self.analysisDialog.controlDialog.label_10.text())
        frameSize = self.analysisDialog.controlDialog.spinBox.value()
        result = math.ceil(sample / frameSize)
        self.analysisDialog.controlDialog.label_11.setText(str(result))

    def createUserFoler(self):
        """
            Create open_file_path.txt and helpRecordDataForLicense.pkl files in the user directory
        """
        self.userPath = os.path.join(os.path.expanduser('~'), 'flow')
        if not os.path.exists(self.userPath):
            os.mkdir(self.userPath)

        self.open_file_path = self.userPath + '/open_file_path.txt'
        if not os.path.isfile(self.open_file_path):
            f = open(self.open_file_path, 'w')
            f.close()

        with open('constant.json', 'r') as file:
            data = json.load(file)
        env = data['env']
        tier = data['tier']
        self.license_file_path = self.userPath + f'/helpRecordDataForLicense_{env}_{tier}.pkl'
        if not os.path.isfile(self.license_file_path):
            self.write_local_license(feature_permission_data={'AO': []},
                                     technical_provider_info_data={},
                                     ao_info_data={},
                                     token="",
                                     user="",
                                     tier="",
                                     remain_time="")
        self.templatePath = os.path.join(self.userPath, 'template')
        os.makedirs(self.templatePath, exist_ok=True)

        # copy ./template to ~/flow/template
        source_folder = './template'
        target_folder = self.templatePath
        # Use filecmp.dircmp() function to perform folder comparison
        dcmp = filecmp.dircmp(source_folder, target_folder)
        # Remove files in the target folder that only appear there
        for file in (dcmp.right_only):
            file_path = os.path.join(target_folder, file)
            if not os.path.isfile(file_path): continue
            os.remove(file_path)
        # Copy files from the source folder that only appear there
        for file in (dcmp.left_only):
            source_file = os.path.join(source_folder, file)
            target_file = os.path.join(target_folder, file)
            shutil.copy2(source_file, target_file)
        # Compare files with the same name in both folders and replace if their sizes differ
        for common_file in dcmp.common_files:
            source_file = os.path.join(source_folder, common_file)
            target_file = os.path.join(target_folder, common_file)
            if os.path.isfile(source_file) and os.path.isfile(target_file):
                if os.path.getsize(source_file) != os.path.getsize(target_file):
                    shutil.copy2(source_file, target_file)

        self.custom_folder_path = os.path.join(self.userPath, 'custom')
        if not os.path.exists(self.custom_folder_path):
            os.makedirs(self.custom_folder_path)

    def write_local_license(self,
                            feature_permission_data,
                            technical_provider_info_data,
                            ao_info_data,
                            token,
                            user,
                            tier,
                            remain_time):
        """
            Serialize and store data to a pickle file with encryption.

            This function serializes and stores data provided as parameters to a pickle file after encrypting it.

            Args:
                feature_permission_data (dict): Data related to feature permissions, typically in dictionary format.
                technical_provider_info_data (dict): Data related to technical provider information,
                    typically in dictionary format.
                ao_info_data (dict): Data related to audio object information, typically in dictionary format.
                token (str): User authentication token.
                user (dict): User information, typically in dictionary format.
                tier (str): User subscription tier (e.g., Free, Pro).
                remain_time (datetime.timedelta): Remaining time for the license.
            Returns:
                None
        """
        content = {'feature_permission_data': json.dumps(feature_permission_data),
                   'technical_provider_info_data': json.dumps(technical_provider_info_data),
                   'ao_info_data': json.dumps(ao_info_data),
                   'token':token,
                   'user': user,
                   'tier': tier,
                   'remain_time': remain_time}

        encrypted_data = self.encrypt(str(content))
        with open(self.license_file_path, 'wb') as license_file:
            pickle.dump(encrypted_data, license_file)

    # encrypt function
    def encrypt(self, raw_data):
        """
           encryption helpRecordDataForLicense.pkl

           :param raw_data, Data to be encrypted
        """
        cryptos = AES.new(self.encrypt_key.encode("utf8"), self.encrypt_mode, self.encrypt_iv.encode("utf8"))
        cipher_data = cryptos.encrypt(bytes(self.pad(raw_data), encoding="utf8"))
        return b2a_hex(cipher_data)

    def pad(self,text):
        """
            Fill in before encrypting data

            :param text, Text to be encrypted

            :return, Filled Text
        """
        return text + (len(self.encrypt_key) - len(text) % len(self.encrypt_key)) \
                         * chr(len(self.encrypt_key) - len(text) % len(self.encrypt_key))

    def createNodesDock(self):
        """
           Create a navigation bar for the left area
           1. Create a filter panel named 'Audio Objects Filter'
           1. Create a nodes toolbar named 'Audio Objects'
           2. Create a toolbar named 'Property'
        """
        from flowstudio.flow_drag_listbox import QDMDragTreebox
        self.nodeFilterDock = QtWidgets.QDockWidget("Audio Objects Filter")
        self.nodeFilterDock.setFont(QFont("Calibri"))
        self.nodeFilterDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.nodeFilterDock.setFloating(False)
        self.nodeFilterDock.setFixedHeight(50)
        self.nodeFilterDock.setFixedWidth(300)
        self.filterDockWidgetContents = QtWidgets.QWidget()
        self.filterDockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.filterDockWidgetContents)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 208, 27))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.float_point_aos_checkbox = QtWidgets.QCheckBox(self.horizontalLayoutWidget)
        self.float_point_aos_checkbox.setText("Float AOs")
        self.float_point_aos_checkbox.setFont(QFont("Calibri", 10))
        self.float_point_aos_checkbox.setStyleSheet("QCheckBox { color: white;}"
                                                    "QCheckBox::indicator{background-color: white;}"
                                                    "QCheckBox::indicator:checked { image: url(../resources/checked.png); }"
                                                    )
        self.horizontalLayout.addWidget(self.float_point_aos_checkbox)
        self.fixed_point_aos_checkbox = QtWidgets.QCheckBox(self.horizontalLayoutWidget)
        self.fixed_point_aos_checkbox.setText("FP AOs")
        self.fixed_point_aos_checkbox.setFont(QFont("Calibri", 10))
        self.fixed_point_aos_checkbox.setStyleSheet("QCheckBox { color: white;}"
                                                    "QCheckBox::indicator{background-color: white;}"
                                                    "QCheckBox::indicator:checked { image: url(../resources/checked.png); }"
                                                    )
        self.horizontalLayout.addWidget(self.fixed_point_aos_checkbox)

        self.float_point_aos_checkbox.setChecked(True)
        self.fixed_point_aos_checkbox.setChecked(True)
        self.float_point_aos_checkbox.stateChanged.connect(self.handle_ao_filter_q_checkbox)
        self.fixed_point_aos_checkbox.stateChanged.connect(self.handle_ao_filter_q_checkbox)
        self.nodeFilterDock.setWidget(self.filterDockWidgetContents)

        self.nodesListWidget = QDMDragTreebox(self)
        self.nodesListWidget.setFont(QFont("Calibri"))

        self.nodesDock = QDockWidget("Audio Objects")
        self.nodesDock.setFont(QFont("Calibri"))
        self.nodesDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.nodesControlListWidget = QDMDragTreebox(self)
        self.nodesControlListWidget.setFont(QFont("Calibri"))

        self.nodesControlDock = QDockWidget("Control Objects")
        self.nodesControlDock.setFont(QFont("Calibri"))
        self.nodesControlDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.nodesControlDock.setWidget(self.nodesControlListWidget)
        self.nodesControlDock.setFloating(False)

        nodesPropertyClass = self.__class__.Node_Property_Widget_Class
        self.nodesPropertyWidget = nodesPropertyClass()
        self.nodesPropertyWidget.dict_value = {}

        self.nodesPropertDock = QDockWidget("Property")
        self.nodesPropertDock.setFont(QFont("Calibri"))
        self.nodesPropertDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.nodesPropertDock.setWidget(self.nodesPropertyWidget)
        self.nodesPropertDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodeFilterDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesControlDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesPropertDock)

    def createCmdDock(self):
        self.cmdDock = QDockWidget("Command Input", self)

        cmdWidget = QWidget()
        layout = QVBoxLayout()

        self.cmd_input = QTextEdit()
        self.cmd_input.setStyleSheet("font-size: 13pt;")

        self.cmd_execute_btn = QPushButton('Execute')
        self.cmd_execute_btn.clicked.connect(self.onExecuteCmd)

        layout.addWidget(self.cmd_input)
        layout.addWidget(self.cmd_execute_btn)
        cmdWidget.setLayout(layout)

        self.cmdDock.setWidget(cmdWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.cmdDock)
        self.cmdDock.setVisible(False)

    def onWindowCmdInput(self):
        if self.cmdDock.isVisible():
            self.cmdDock.hide()
        else:
            self.cmdDock.show()

    def onExecuteCmd(self):
        windows = self.findMain()
        nodes = windows.widget().scene.nodes
        edges = windows.widget().scene.edges

        # "delete/12/2"
        # "deleteEdge/32/1/1/12/1/0"
        text = self.cmd_input.toPlainText()
        cmds = text.replace('\\n', '\n').split('\n')

        for cmd in cmds:
            try:
                print("cmd:", cmd)
                parts = cmd.split('/')
                action = parts[0]

                if action == "add":
                    code = int(parts[1])
                    designator = int(parts[2])
                    x = int(parts[3])
                    y = int(parts[4])

                    if len(parts) > 5 and parts[5].strip():
                        parameters = ast.literal_eval(parts[5])
                    else:
                        parameters = None

                    if parameters is None:
                        parameters = {'num_channels': 1, 'num_in_channels': 1, 'num_out_channels': 1, 'num_bands': 1, 'num_taps': 1, 'configure': '2.0'}
                    parameters['control'] = False
                    designators = []
                    for node in nodes:
                        if node.op_code == code:
                            designators.append(node.designator)

                    if designator in designators: return

                    new_node = windows.widget().initNewNodeCondition(code, parameters)
                    new_node.designator = designator
                    new_node.setPos(x, y)
                    new_node.title = new_node.title + '_' + str(designator)

                    if code == OP_NODE_SUBPATCH:
                        windows.window().onEnterGroupFile(new_node)
                        new_node.cwd = new_node.title
                        self.mdiArea.setActiveSubWindow(self.findMain())

                    windows.widget().scene.history.storeHistory(f"Created {new_node.__class__.__name__}-{new_node.title}", setModified=True)
                elif action == "delete":
                    code = int(parts[1])
                    designator = int(parts[2])
                    for node in nodes:
                        if node.op_code == code and node.designator == designator:
                            node.grNode.setSelected(True)
                            node.scene.getView().window().onEditDelete()
                            break
                elif action in ["connect", "connectControl"]:
                    code_1 = int(parts[1])
                    designator_1 = int(parts[2])
                    port_1 = int(parts[3])
                    code_2 = int(parts[4])
                    designator_2 = int(parts[5])
                    port_2 = int(parts[6])

                    start_socket = None
                    end_socket = None

                    for node in nodes:
                        if node.op_code == code_1 and node.designator == designator_1:
                            if action == "connect":
                                start_socket = node.outputs[port_1]
                            else:
                                start_socket = node.outctrls[port_1]
                            continue
                        if node.op_code == code_2 and node.designator == designator_2:
                            if action == "connect":
                                end_socket = node.inputs[port_2]
                            else:
                                end_socket = node.inctrls[port_2]
                            continue

                    windows.widget().view.dragging.add_edge(start_socket=start_socket,
                                                           end_socket=end_socket,
                                                           ignore_message_box=True,
                                                           ignore_drag_edge=True)
                elif action == "disconnect":
                    code_1 = int(parts[1])
                    designator_1 = int(parts[2])
                    port_1 = int(parts[3])
                    code_2 = int(parts[4])
                    designator_2 = int(parts[5])
                    port_2 = int(parts[6])

                    for edge in edges:
                        if (edge.start_socket.node.op_code == code_1 and
                            edge.start_socket.node.designator == designator_1 and
                            edge.start_socket.index == port_1 and
                            edge.end_socket.node.op_code == code_2 and
                            edge.end_socket.node.designator == designator_2 and
                            edge.end_socket.index == port_2):
                            edge.grEdge.setSelected(True)
                            edge.scene.getView().window().onEditDelete()
                            break
                elif action == "set":
                    code = int(parts[1])
                    designator = int(parts[2])
                    parameter_name = parts[3]
                    parameter_value = parts[4]

                    for node in nodes:
                        if node.op_code == code and node.designator == designator:
                            for widget_label in node.manager.widgetSet:
                                if widget_label == parameter_name:
                                    widget = node.manager.widgetSet[widget_label]
                                    if type(widget.widget_value) is int:
                                        widget.widget_value = int(parameter_value)
                                    elif type(widget.widget_value) is float:
                                        widget.widget_value = float(parameter_value)
                                    elif type(widget.widget_value) is list:
                                        parameter_value = json.loads(parameter_value.replace('\\"', '"'))
                                        widget.widget_value = parameter_value
                                    node.manager.parameterStored()
                elif action == "move":
                    code = int(parts[1])
                    designator = int(parts[2])
                    x = int(parts[3])
                    y = int(parts[4])

                    for node in nodes:
                        if node.op_code == code and node.designator == designator:
                            node.grNode.setPos(x,y)
                            break
                    windows.widget().scene.history.storeHistory("Node moved", setModified=True)
            except Exception as e:
                print(f"Critical error executing command: {cmd}")
                print(f"Error details: {str(e)}")

    def createStatusBar(self):
        """
            Create bottom status bar
        """
        self.statusBar().showMessage("Window Init Success", 5000)

    def createMdiChild(self, child_widget=None):
        """
            If child_widget is None, Create a child sub_window nodededitor named 'FLOW_Sub_Window()'
            else, Create a child sub_window nodededitor named 'child_widget'
            And set properties

            :param child_widget, Object to create sub_window

            :return, sub_window object
        """
        nodeeditor = child_widget if child_widget is not None else FLOW_Sub_Window()
        nodeeditor.scene.propertyDockWidget = self.nodesPropertyWidget
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setSystemMenu(None)
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def createGroupChild(self, child_widget=None, title=None):
        """
            If child_widget is None, Create a child group nodededitor named 'FLOW_Sub_Group()'
            else, Create a child group nodededitor named 'child_widget'
            And set properties

            :param child_widget, Object to create window

            :return, group object
        """
        nodeeditor = child_widget if child_widget is not None else FLOW_Sub_Group()
        nodeeditor.scene.propertyDockWidget = self.nodesPropertyWidget
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        self.set_custom_menu_for_sub_window(subwnd)
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        # nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        """
            Handle the closing event of a child window

            :param widget, Object to close sub_window
            :param event, The object that receives and processes the event when the window is closed
        """
        if self.skip_save_check: return
        existing = self.findMdiChildPath(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        for gui_window in self.all_window_objects: gui_window.hide()

        groupChilds = self.mdiArea.subWindowList()
        midChild = self.findMain()
        if midChild in groupChilds:
            groupChilds.remove(midChild)
        if self.maybeSave():
            for child in groupChilds:
                child.close()
            if not self.getCurrentNodeEditorWidget() == None:
                self.getCurrentNodeEditorWidget().scene.propertyDockWidget.dict_value = {}

            if self.temp_folder_path is not None and os.path.exists(self.temp_folder_path):
                shutil.rmtree(self.temp_folder_path)
            event.accept()
        else:
            for gui_window in self.all_window_objects: gui_window.show()
            event.ignore()

    def findMain(self):
        """
            Find the main editor sub_window named 'New FLOW', 'New FLOW*', 'main.json', or 'main.json*' from the MDI sub window list

            :return, Object sub_window
        """
        for window in self.mdiArea.subWindowList():
            if window.widget().getUserFriendlyFilename() in ["New FLOW", "New FLOW*", "main.json", "main.json*"]:
                return window
        return None

    def findMdiChildPath(self, file_path):
        """
            Find the main editor sub_window named 'file_path' from the MDI sub window list

            :param file_path, specify the path to a file

            :return If found, return window object. Otherwise, return to None
        """
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == file_path:
                return window
        return None

    def findMdiChildFriendly(self, friendly_name):
        """
            Find sub_windows with specified 'friendly_name' from the MDI sub window list

            :param friendly_name, specify the node title

            :return If found, return window object. Otherwise, return to None
        """
        for window in self.mdiArea.subWindowList():
            if window.widget().getUserFriendlyFilename() in [friendly_name, friendly_name + '*',
                                                             friendly_name + '.json', friendly_name + '.json*']:
                return window
        return None

    def setActiveSubWindow(self, window):
        """
            Set the specified window as the active sub_window

            :param window, the specified window object
        """
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def handle_ao_filter_q_checkbox(self):
        def hide_item(tree_item):
            def is_condition_met_to_hide(tree_item):
                if tree_item in self.nodesListWidget.items:
                    if FLOW_NODES_DISPLAY_NAMES[tree_item.text(0)].is_float_point:
                        return True if not self.float_point_aos_checkbox.isChecked() else False
                    if not FLOW_NODES_DISPLAY_NAMES[tree_item.text(0)].is_float_point:
                        return True if not self.fixed_point_aos_checkbox.isChecked() else False
                else:
                    return False

            if tree_item is None:
                return

            if is_condition_met_to_hide(tree_item):
                tree_item.setHidden(True)
            else:
                tree_item.setHidden(False)

            all_child_hidden = True
            for i in range(tree_item.childCount()):
                child_item = tree_item.child(i)
                hide_item(child_item)
                if not child_item.isHidden():
                    all_child_hidden = False

            if all_child_hidden and tree_item not in self.nodesListWidget.items:
                tree_item.setHidden(True)
            elif not all_child_hidden:
                tree_item.setHidden(False)

        tree_item = self.nodesListWidget.invisibleRootItem()
        hide_item(tree_item)

    def hideAudioSettinginControlDialog(self):
        """
            Hide audio device related options in the setting controlDialog
        """
        self.settingDialog.controlDialog.comboBox_sr_list.hide()
        self.settingDialog.controlDialog.comboBox_input_list.hide()
        self.settingDialog.controlDialog.comboBox_output_list.hide()
        self.settingDialog.controlDialog.comboBox_driver_list.hide()
        self.settingDialog.controlDialog.label_21.setText("Scanning Audio Interface...")
        self.settingDialog.controlDialog.label_22.hide()
        self.settingDialog.controlDialog.label_23.hide()
        self.settingDialog.controlDialog.label_24.hide()

    def showAudioSettinginControlDialog(self):
        """
            show audio device related options in the setting controlDialog
        """
        self.settingDialog.controlDialog.comboBox_sr_list.show()
        self.settingDialog.controlDialog.comboBox_input_list.show()
        self.settingDialog.controlDialog.comboBox_output_list.show()
        self.settingDialog.controlDialog.comboBox_driver_list.show()
        self.settingDialog.controlDialog.label_21.setText("Driver Select:")
        self.settingDialog.controlDialog.label_22.show()
        self.settingDialog.controlDialog.label_23.show()
        self.settingDialog.controlDialog.label_24.show()

    def onOpenControlDialog(self):
        """
            Open setting controlDialog
        """

        self.onSavePCOption()

        if Debug.DEBUG_Low_Level.value: print("is Port Audio Supported: %r" % self.hasPaSupported)

        # if self.profile: self.onLoadProfile()

        for gui_widget in self.all_window_objects: gui_widget.hide()

        # # Step 2: Create a QThread object
        # self.thread = QThread()
        # # Step 3: Create a worker object
        # self.worker = scanAudioDeviceThread()
        # # Step 4: Move worker to the thread
        # self.worker.moveToThread(self.thread)
        # # Step 5: Connect signals and slots
        # self.thread.started.connect(self.worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        # # Step 6: Start the thread
        # self.thread.start()
        #
        # self.settingDialogWidget.setEnabled(False)
        # self.hideAudioSettinginControlDialog()
        #
        # # self.scanAudioInterface()
        # self.thread.finished.connect(
        #     lambda: self.settingDialogWidget.setEnabled(True)
        # )
        # self.thread.finished.connect(
        #     lambda: self.settingDialog.initData()
        # )
        # self.thread.finished.connect(
        #     lambda: self.settingDialogWidget.update()
        # )
        #
        # self.thread.finished.connect(
        #     lambda: self.settingDialog.audioInterfaceSetUp()
        # )
        #
        # self.thread.finished.connect(
        #     lambda: self.settingDialogWidget.exec()
        # )
        #
        # self.thread.finished.connect(
        #     lambda: self.showAudioSettinginControlDialog()
        # )
        timer.timeout.connect(self.UARTDataUpdate)
        timer.start(3000)

        self.settingDialogWidget.setEnabled(True)
        self.settingDialog.initData()
        self.settingDialogWidget.update()
        self.settingDialogWidget.exec()
        self.showAudioSettinginControlDialog()

        for gui_widget in self.all_window_objects: gui_widget.show()

    def handleCloseEvent(self):
        """
            dump_qdialog CloseEvent
        """
        self.onTerminateDump()

    def handleDumpCheckboxState(self, state):
        """
            handle control dump checkbox state
        """
        checkbox = self.sender()
        if state == 2:
            self.dump_ao_checked_checkbox_list.append(checkbox.text())
        else:
            self.dump_ao_checked_checkbox_list.remove(checkbox.text())

    def onOpenControlDump(self):
        """
            Open Control Dump Dialog
        """
        dump_qdialog = DumpQDialog(self)
        self.controlDump = Ui_dump_dialog()
        self.controlDump.setupUi(dump_qdialog)

        # find all dump AO id and title
        self.dump_ao_title_id_list = []
        dump_ao_tile_list = []

        windows = self.mdiArea.subWindowList()
        for window in windows:
            for i in range(len(window.widget().scene.nodes)):
                node = window.widget().scene.nodes[i]
                if node.op_code == OP_NODE_DUMP:
                    dump_ao_tile_list.append(node.title)
                    self.dump_ao_title_id_list.append({node.title: node.content_label_objname+"_"+str(node.designator)})

        # when dump AO list change
        if self.dump_ao_tile_list != dump_ao_tile_list:
            self.dump_ao_tile_list = dump_ao_tile_list
            self.dump_ao_checked_checkbox_list = []
            self.dump_dialog_index[0] = 0

        if self.dump_ao_tile_list != []:
            scroll_layout = QVBoxLayout(self.controlDump.scrollAreaWidgetContents)
            for title in self.dump_ao_tile_list:
                checkbox = QCheckBox(title)
                checkbox.setStyleSheet('''
                QCheckBox {
                    color: white;
                    font-family: Calibri;
                }
                QCheckBox::indicator{
                    border: 2px solid #b1b1b1;
                    background-color: white;
                }
                
                QCheckBox::indicator:checked {
                    background-color: black;
                }
                
                
                QCheckBox::indicator:unchecked {
                    background-color: white;
                }
                ''')
                if title in self.dump_ao_checked_checkbox_list:
                    checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.handleDumpCheckboxState)
                scroll_layout.addWidget(checkbox)

        time_list = ['60 s', '120 s', '180 s', '240 s', '300 s']
        self.controlDump.comboBox_time_list.clear()
        self.controlDump.comboBox_time_list.addItems(time_list)
        self.controlDump.comboBox_time_list.setCurrentIndex(self.dump_dialog_index[0])
        self.controlDump.comboBox_time_list.currentIndexChanged.connect(self.onSaveControlDumpOption)

        self.controlDump.lineEdit_path.setText(self.dump_dialog_index[1])
        self.controlDump.lineEdit_path.setReadOnly(True)

        self.controlDump.open.clicked.connect(self.onStoreDumpFilePath)
        self.controlDump.checkBox_dump.clicked.connect(self.onDump)

        dump_qdialog.setWindowTitle("Dump")
        dump_qdialog.closeEventSignal.connect(self.handleCloseEvent)

        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        dump_qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()


    def onSaveControlDumpOption(self):
        """
            record AO_list and time_list index
        """
        self.dump_dialog_index[0] = self.controlDump.comboBox_time_list.currentIndex()
        self.dump_dialog_index[1] = self.controlDump.lineEdit_path.text()

    def onDump(self):
        """
            Dump Process
        """
        if self.settingDialog.client.connection:

            if  self.dump_ao_checked_checkbox_list == []:
                self.controlDump.checkBox_dump.setChecked(False)
                statement = 'Please check dump AO.'
                QMessageBox.about(self, "Tip", "%s" % statement)
                return

            directory_path = self.controlDump.lineEdit_path.text() + '/'
            if not self.can_create_file(directory_path):
                self.controlDump.checkBox_dump.setChecked(False)
                statement = 'This directory cannot create files, Please reselect.'
                QMessageBox.about(self, "Tip", "%s" % statement)
                return

            if self.controlDump.checkBox_dump.isChecked():
                DumpQDialog.is_confirm = True
                for title_id in self.dump_ao_title_id_list:
                    if list(title_id.keys())[0] in self.dump_ao_checked_checkbox_list:
                        dump_ao_name = list(title_id.values())[0]
                        self.dump_ao_name_list.append(dump_ao_name)
                        self.dump_count = int(self.controlDump.comboBox_time_list.currentText().split(' ')[0])

                        self.controlDump.label_4.setText("Start Dump!")
                        self.controlDump.checkBox_dump.setEnabled(False)
                        path = os.path.join(self.controlDump.lineEdit_path.text(), list(title_id.keys())[0])
                        cmds = [
                            "setStringCoord:#%s:#Path:#%s:#0:#0:#" % (dump_ao_name, path + '.wav'),
                            "set/%s/timer/%s" % (dump_ao_name, self.dump_count),
                            "set/%s/onoff/1" % dump_ao_name
                        ]

                        for cmd in cmds:
                            self.settingDialog.cpuClient.cmdQuery(cmd, 16)

                timer.timeout.connect(self.onDumpProcessTimerOperation)
                timer.start(1000)

    def onDumpProcessTimerOperation(self):
        """
            Dump Process Timer Operation
        """
        if self.dump_count > 0:
            self.dump_count -= 1
            text = "Time Remaining:  %s s" % self.dump_count
            self.controlDump.label_4.setText(text)
        else:
            self.onTerminateDump()

    def onTerminateDump(self):
        """
            Some actions at the end of Dump
        """
        for name in self.dump_ao_name_list:
            off_cmd = "set/%s/onoff/0" % name
            self.settingDialog.cpuClient.cmdQuery(off_cmd, 16)
        timer.timeout.disconnect(self.onDumpProcessTimerOperation)
        timer.stop()
        self.controlDump.label_4.setText("Success!")
        self.controlDump.checkBox_dump.setChecked(False)
        self.controlDump.checkBox_dump.setEnabled(True)
        DumpQDialog.is_confirm = False

    def onStoreDumpFilePath(self):
        """
            Get And Set Dump File Store Path
        """
        directory = QFileDialog.getExistingDirectory(self, "Choose Directory", self.dump_dialog_index[1])

        # Determine if it contains Chinese
        pattern = re.compile(r'[\u4e00-\u9fa5]')
        has_chinese_character = bool(re.search(pattern, directory))

        if has_chinese_character:
            statement = 'The directory path cannot contain Chinese characters, please reselect.'
            QMessageBox.about(self, "Tip", "%s" % statement)
            return

        if directory:
            self.controlDump.lineEdit_path.setText(directory)
            self.onSaveControlDumpOption()

    def can_create_file(self, directory):
        try:
            test_file = os.path.join(directory, "test.txt")
            open(test_file, 'w').close()  # 创建一个测试文件
            os.remove(test_file)  # 删除测试文件
            return True
        except PermissionError:
            return False

    def onSavePCOption(self):
        """
            save audio device related options index in the setting controlDialog -> PC
        """

        driver_list_index = self.settingDialog.controlDialog.comboBox_driver_list.currentIndex()
        input_list_index = self.settingDialog.controlDialog.comboBox_input_list.currentIndex()
        input_list_index = input_list_index if input_list_index != -1 else 0
        output_list_index = self.settingDialog.controlDialog.comboBox_output_list.currentIndex()
        output_list_index = output_list_index if output_list_index != -1 else 0
        sr_list_index = self.settingDialog.controlDialog.comboBox_sr_list.currentIndex()

        self.itemIndex = [driver_list_index, input_list_index, output_list_index, sr_list_index]

    def UARTDataUpdate(self):
        """
            update the value of COM PORT in UART
        """
        self.settingDialog.checkPort()

    def onSimulationDialog(self):
        if Debug.DEBUG_Low_Level.value: print('GO GO GO')
        self.analysisDialogWidget.exec()

    def _finditem(self, obj, key):
        if key in obj:
            return obj[key]
        for k, v in obj.items():
            if isinstance(v, dict):
                item = self._finditem(v, key)
                if item is not None:
                    return item

    def collectGroupList(self, nodes):
        groupList = []
        for node in nodes:
            if node.op_code == OP_NODE_SUBPATCH:
                return self.openAllGroupNode()

    def onDesignRuleCheck(self):
        """
            Check design valid or not

            :return: boolean, if no problems, return True,
                if having problems, return False.
        """

        def dfs_find_accessible_parent_window(sub_window, parent=None):
            """
                Depth-first search to find the accessible parent window for a sub-window.

                This function recursively searches for the accessible parent window of a given sub-window
                and returns information about the window's title and accessibility.

                Args:
                    sub_window: The sub-window to examine.
                    parent: The parent window found during the search.

                Returns:
                    tuple: A tuple containing the title of the accessible parent window and a boolean
                    indicating whether the sub-window is accessible from the parent.

                Note:
                    - This function is used to determine the accessibility of sub-windows and their parent windows.
            """
            title = sub_window.windowTitle()
            if type(sub_window) is FLOW_Sub_Group:
                if title != sub_window.title + '.json' and title != sub_window.title + '.json*' and title != sub_window.title:
                    title = sub_window.title
            if type(sub_window) is FLOW_Sub_Window and parent is not None:
                return parent, True
            if not hasattr(sub_window, 'already_input_password'):
                return (title, False) if parent is None else (parent, True)
            if hasattr(sub_window, 'already_input_password'):
                if sub_window.already_input_password:
                    return (title, False) if parent is None else (parent, True)
            for sub_patch_window in self.sub_patchs:
                if sub_patch_window.closed:
                    for node_in_sub_patch_window in \
                    sub_patch_window.scene.history.history_stack[sub_patch_window.scene.history.history_current_step][
                        'snapshot']['nodes']:
                        if node_in_sub_patch_window['op_code'] == OP_NODE_SUBPATCH and (
                                node_in_sub_patch_window['title'] == title or node_in_sub_patch_window[
                            'title'] + '.json' == title):
                            return dfs_find_accessible_parent_window(sub_patch_window, parent=title)
            for open_window in self.mdiArea.subWindowList():
                for node_in_open_window in open_window.widget().scene.nodes:
                    if node_in_open_window.title == title or node_in_open_window.title + '.json' == title:
                        return dfs_find_accessible_parent_window(open_window.widget(), parent=title)
        current_window = self.getCurrentNodeEditorWidget()
        if not current_window:
            return False
        valid_node_list = []
        drc_flag = []

        # 先把所有SUBPATCH的子視窗都打開，檢查完沒問題的再關掉
        main_window = self.findMain()
        nodes_in_main = main_window.widget().scene.nodes
        for node in nodes_in_main:
            if node.op_code == OP_NODE_SUBPATCH:
                self.open_subwindow_in_subpatch_recursively(node.title)
                self.setActiveSubWindow(current_window.parent())
        windows = self.window().mdiArea.subWindowList()
        set_active_window = None
        content = []  # Store the flow information to be uploaded to the database
        if nodes_in_main:
            not_supported = defaultdict(list)
            no_permission = defaultdict(list)
            custom_error_nodes_msg = defaultdict(list)
            is_dirty_node_exist = False
            is_not_supported_node_exist = False
            is_user_has_no_permission_nodes_exist = False
            is_custom_error_node_exist = False
            for window in windows:
                scene_hash_map = {}
                scene_hash_map['name'] = 'main' if type(window.widget()) != FLOW_Sub_Group else window.widget().getPrettyFilename()
                scene_hash_map['nodes'] = window.widget().scene.serialize()['nodes']
                scene_hash_map['edges'] = window.widget().scene.serialize()['edges']
                # region delete unnecessary node info
                keys_to_delete = ['color']
                for node in scene_hash_map['nodes']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in node:
                            del node[key_to_delete]
                # endregion
                # region delete unnecessary edge info
                keys_to_delete = ['edge_type']
                for edge in scene_hash_map['edges']:
                    for key_to_delete in keys_to_delete:
                        if key_to_delete in edge:
                            del edge[key_to_delete]
                # endregion
                if hasattr(window.widget(), 'encrypted') and \
                        window.widget().encrypted and \
                        hasattr(window.widget(), 'already_input_password') and \
                        not window.widget().already_input_password:
                    scene_hash_map['encrypted'] = window.widget().encrypted
                    scene_hash_map['already_input_password'] = window.widget().already_input_password
                    del scene_hash_map['nodes']
                    del scene_hash_map['edges']
                content.append(scene_hash_map)
                nodes = window.widget().scene.nodes
                no_problem = True
                for node in nodes:
                    if node.node_type == "CO":
                        self.custom_message = ""
                        return True
                    if node.isDirty() or not node.is_supported() or not node.is_user_has_permission():
                        if not node.is_supported() and node.op_code != OP_NODE_SUBPATCH:
                            is_not_supported_node_exist = True
                            not_supported[dfs_find_accessible_parent_window(window.widget())].append(node)
                        if not node.is_user_has_permission() and node.op_code != OP_NODE_SUBPATCH:
                            is_user_has_no_permission_nodes_exist = True
                            no_permission[dfs_find_accessible_parent_window(window.widget())].append(node)
                        if node.isDirty() and not hasattr(node, 'error_msg'):
                            is_dirty_node_exist = True
                        if node.isDirty() and hasattr(node, 'error_msg'):
                            is_custom_error_node_exist = True
                            custom_error_nodes_msg[dfs_find_accessible_parent_window(window.widget())].append(node.error_msg)
                        valid_node_list.append(node)
                        drc_flag.append(node.isDirty())
                        no_problem = False
                        set_active_window = window
                        if hasattr(window.widget(), 'close_if_no_problem'):
                            window.widget().close_if_no_problem = False
                    elif not node.is_support_feedback_path():
                        drc_flag.append(True)
                if no_problem and hasattr(window.widget(), 'close_if_no_problem'):
                    if window.widget().close_if_no_problem:
                        self.close_sub_window(window)
                if hasattr(window.widget(), 'encrypted'):
                    if window.widget().encrypted and not window.widget().already_input_password:
                        self.close_sub_window(window)
            if is_not_supported_node_exist:
                message = f'Audio objects below are not supported in {self.settingDialog.controlDialog.comboBox_targetdevice.currentText()}:\n'
            else:
                message = None
            for window_title, not_supported_aos in not_supported.items():
                if window_title[1]:
                    not_supported[window_title] = []
            for window_title, not_supported_aos in not_supported.items():
                if not not_supported_aos:
                    message += f'●{window_title[0]}(encrypted)\n'
                    continue
                message += f'●{window_title[0]}:\n'
                for not_supported_ao in not_supported_aos:
                    message += '    -'+not_supported_ao.title + ' ' + not_supported_ao.content_label_objname + '\n'
            if is_dirty_node_exist and is_not_supported_node_exist:
                message += 'and nodes whose socket is not connected also exist.'
            if is_user_has_no_permission_nodes_exist:
                if message is None:
                    message = ''
                message += "You don't have permission to use the following audio objects:\n"
                for window_title, no_permission_aos in no_permission.items():
                    if window_title[1]:
                        no_permission[window_title] = []
                for window_title, no_permission_aos in no_permission.items():
                    if not no_permission_aos:
                        message += f'●{window_title[0]}(encrypted)\n'
                        continue
                    message += f'●{window_title[0]}:\n'
                    for no_permission_ao in no_permission_aos:
                        message += '    -' + no_permission_ao.title + ' ' + no_permission_ao.content_label_objname + '\n'
            if is_custom_error_node_exist:
                if message is None:
                    message = ''
                for window_title, err_msgs in custom_error_nodes_msg.items():
                    if window_title[1]:
                        custom_error_nodes_msg[window_title] = []
                for window_title, err_msgs in custom_error_nodes_msg.items():
                    for err_msg in err_msgs:
                        if not err_msg:
                            continue
                        message += f'{err_msg}\n'
                if message == '':
                    message = None
            self.custom_message = message
        else:
            valid_node_list.append("null design")
            drc_flag.append(False)

        if drc_flag:
            if set_active_window:
                self.setActiveSubWindow(set_active_window)
            if Debug.DEBUG_COMMON.value: print('Design Rule Check Result: %r' % False)
            return False
        else:
            if Debug.DEBUG_COMMON.value: print('Design Rule Check Result: %r' % True)
            if self.license_mechanism.is_online and self.license_mechanism.is_tracking:
                if self.temp_folder_path is None:
                    self.upload_project_info(action='connect',
                                             content=content)
                else:
                    self.upload_project_info(action='connect',
                                             content=content,
                                             project_name=self.temp_folder_path.split('/')[-1])
            return True

    def onIsNodeValid(self, status):
        """
            Show Dirty Node, Is there a node in the upper left corner '?' Symbol

            :param status, If status is True, Show Dirty Node
        """
        if Debug.DEBUG_Low_Level.value: print("Show Dirty Node: %r" % status)
        windows = self.mdiArea.subWindowList()
        FLOW_Node.showDirty = status
        for window in windows:
            for i in range(len(window.widget().scene.nodes)):
                node = window.widget().scene.nodes[i]
                node.showDirty = status
                if node.isDirty():
                    node.grNode.update()
                if not node.is_supported():
                    node.grNode.update()
                if not node.is_user_has_permission():
                    node.grNode.update()
                if not node.is_support_feedback_path():
                    node.grNode.update()


    def scanAudioInterface(self):
        """
            Scan audio interface and set support status
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        target_path = smartCWD()

        cmd = ["AudioInterface.exe"]
        if Debug.DEBUG_COMMON.value: print(target_path)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, cwd=target_path)
        res = process.stdout.read()
        if res.decode(errors="ignore").rstrip().rsplit('\n')[-1] == "Processed Finished":
            self.hasPaSupported = True
        else:
            self.hasPaSupported = False
        QApplication.restoreOverrideCursor()

    def onProfileSetup(self):
        """
            Save the parameters of the setting controlDialog
        """
        hostname1 = self.settingDialog.controlDialog.lineEdit_hostname_1
        hostname2 = self.settingDialog.controlDialog.lineEdit_hostname_2
        hostname3 = self.settingDialog.controlDialog.lineEdit_hostname_3
        hostname4 = self.settingDialog.controlDialog.lineEdit_hostname_4

        port = self.settingDialog.controlDialog.lineEdit_freeports

        username = self.settingDialog.controlDialog.lineEdit_username

        password = self.settingDialog.controlDialog.lineEdit_password

        path = self.settingDialog.controlDialog.lineEdit_path

        vid = self.settingDialog.controlDialog.lineEdit_vid

        pid = self.settingDialog.controlDialog.lineEdit_pid

        connection = self.settingDialog.controlDialog.Connection_comboBox

        comport = self.settingDialog.controlDialog.Port_comboBox

        rate = self.settingDialog.controlDialog.Rate_comboBox

        parity = self.settingDialog.controlDialog.Parity_comboBox

        bites = self.settingDialog.controlDialog.Bites_comboBox

        engine = self.settingDialog.controlDialog.Engine_comboBox

        if hostname1.text() and hostname2.text() and hostname3.text() and hostname4.text():
            self.hostname = str(int(hostname1.text())) + "." + \
                            str(int(hostname2.text())) + "." + \
                            str(int(hostname3.text())) + "." + \
                            str(int(hostname4.text()))
        else:
            self.hostname = ""

        if port.text():
            self.port = int(port.text())
        else:
            self.port = 0

        if username.text():
            self.username = username.text()
        else:
            if self.target == Target.PC.value:
                self.username = ""
            else:
                self.username = "root"

        if password.text():
            self.password = password.text()
        else:
            self.password = ""

        if path.text():
            self.path = path.text()
        else:
            self.path = ""

        if vid.text():
            self.vid = vid.text()
        else:
            self.vid = ""

        if pid.text():
            self.pid = pid.text()
        else:
            self.pid = ""

        if connection.currentIndex():
            self.connection = connection.currentIndex()
        else:
            self.connection = 0

        if comport.currentIndex():
            self.comport = comport.currentIndex()
        else:
            self.comport = 0

        if rate.currentIndex():
            self.rate = rate.currentIndex()
        else:
            self.rate = 0

        if parity.currentIndex():
            self.parity = parity.currentIndex()
        else:
            self.parity = 0

        if bites.currentIndex():
            self.bites = bites.currentIndex()
        else:
            self.bites = 0

        if engine.currentIndex():
            self.engine = engine.currentIndex()
        else:
            self.engine = 0

    def onProfileImport(self):
        """
            Implemented the function of reading and importing configuration files.
            1. self.onProfileSetup() to Save Current Parameters
            2. Import the configuration file and make judgments and assignments
        """
        self.onProfileSetup()
        fname, filter = QFileDialog.getOpenFileName(self, 'Import Profile File', getFileDialogDirectory(),
                                                    getProfileFilter())
        if fname:
            with open(fname, "r") as file:
                try:
                    raw_data = file.read()
                    profile = json.loads(raw_data)
                    self.profile = fname

                    self.settingDialog.controlDialog.comboBox_targetdevice.setCurrentIndex(profile["target"])
                    if profile["target"] == Target.PC.value and self.hasPaSupported:
                        self.settingDialog.controlDialog.comboBox_driver_list.setCurrentIndex(profile["driver"])
                        self.settingDialog.controlDialog.comboBox_input_list.setCurrentIndex(profile["input"])
                        self.settingDialog.controlDialog.comboBox_output_list.setCurrentIndex(profile["output"])
                        self.settingDialog.controlDialog.comboBox_sr_list.setCurrentIndex(profile["samplerate"])
                        self.settingDialog.controlDialog.line_edit_engine_path.setText(profile['engine_path'])
                        self.settingDialog.pc_engine_path = profile['engine_path']

                    elif profile["target"] == Target.PC.value:
                        self.settingDialog.controlDialog.comboBox_driver_list.setCurrentIndex(profile["driver"])
                        self.settingDialog.controlDialog.comboBox_input_list.setCurrentIndex(profile["input"])
                        self.settingDialog.controlDialog.comboBox_output_list.setCurrentIndex(profile["output"])
                        self.settingDialog.controlDialog.comboBox_sr_list.setCurrentIndex(profile["samplerate"])
                        self.settingDialog.controlDialog.line_edit_engine_path.setText(profile['engine_path'])
                        self.settingDialog.pc_engine_path = profile['engine_path']

                    elif profile["target"] in [Target.IMX.value, Target.LINUX.value, Target.RASP.value]:
                        self.settingDialog.controlDialog.lineEdit_path.setText(profile["path"])
                        self.settingDialog.controlDialog.lineEdit_hostname_1.setText(profile["hostname"][0])
                        self.settingDialog.controlDialog.lineEdit_hostname_2.setText(profile["hostname"][1])
                        self.settingDialog.controlDialog.lineEdit_hostname_3.setText(profile["hostname"][2])
                        self.settingDialog.controlDialog.lineEdit_hostname_4.setText(profile["hostname"][3])
                        self.settingDialog.controlDialog.lineEdit_freeports.setText(str(profile["port"]))
                        self.settingDialog.controlDialog.lineEdit_username.setText(profile["username"])
                        self.settingDialog.controlDialog.lineEdit_password.setText(profile["password"])

                    elif profile["target"] in [Target.AMLOGIC.value, Target.QCS.value, Target.FLOW_APO.value, Target.LINKPLAY.value]:
                        self.settingDialog.controlDialog.lineEdit_path.setText(profile["path"])
                        self.settingDialog.controlDialog.lineEdit_hostname_1.setText(profile["hostname"][0])
                        self.settingDialog.controlDialog.lineEdit_hostname_2.setText(profile["hostname"][1])
                        self.settingDialog.controlDialog.lineEdit_hostname_3.setText(profile["hostname"][2])
                        self.settingDialog.controlDialog.lineEdit_hostname_4.setText(profile["hostname"][3])
                        self.settingDialog.controlDialog.lineEdit_freeports.setText(str(profile["port"]))

                    elif profile["target"] in [Target.CORTEX_M_USB.value, Target.FLOW_EVK_UART.value, Target.GX8008C_USB.value]:
                        self.settingDialog.controlDialog.comboBox_driver_list_5.setCurrentIndex(
                            self.on_check_profile_value(profile, 'interface_list_index'))
                        self.settingDialog.controlDialog.lineEdit_vid.setText(profile["vid"])
                        self.settingDialog.controlDialog.lineEdit_pid.setText(profile["pid"])
                        self.settingDialog.controlDialog.Connection_comboBox.setCurrentIndex(profile['connection'])
                        self.settingDialog.controlDialog.Port_comboBox.setCurrentIndex(profile['comport'])
                        self.settingDialog.controlDialog.Rate_comboBox.setCurrentIndex(profile['rate'])
                        self.settingDialog.controlDialog.Parity_comboBox.setCurrentIndex(profile['parity'])
                        self.settingDialog.controlDialog.Bites_comboBox.setCurrentIndex(profile['bites'])
                        if profile["target"] == Target.GX8008C_USB.value:
                            self.settingDialog.controlDialog.Engine_comboBox.setCurrentIndex(
                                self.on_check_profile_value(profile, 'engine'))

                    elif profile["target"] in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
                        self.settingDialog.controlDialog.comboBox_driver_list_6.setCurrentIndex(
                            self.on_check_profile_value(profile, 'interface_list_index'))
                        self.settingDialog.controlDialog.lineEdit_vid.setText(profile["vid"])
                        self.settingDialog.controlDialog.lineEdit_pid.setText(profile["pid"])
                        self.settingDialog.controlDialog.Connection_comboBox.setCurrentIndex(profile['connection'])
                        self.settingDialog.controlDialog.Port_comboBox.setCurrentIndex(profile['comport'])
                        self.settingDialog.controlDialog.Rate_comboBox.setCurrentIndex(profile['rate'])
                        self.settingDialog.controlDialog.Parity_comboBox.setCurrentIndex(profile['parity'])
                        self.settingDialog.controlDialog.Bites_comboBox.setCurrentIndex(profile['bites'])
                        self.settingDialog.controlDialog.Engine_comboBox.setCurrentIndex(
                            self.on_check_profile_value(profile, 'engine'))

                except Exception as e:
                    dumpException(e)

    def on_check_profile_value(self, profile, value):
        try:
            return profile[value]
        except Exception as e:
            return 0


    def onProfileSave(self):
        """
            Save the parameters of the setting controlDialog in the configuration file.
            1. self.onProfileSetup() to init Current Parameters
            2. Save relative parameters based on different platforms
            3. Open a file dialog box for users to choose the path and file name to save the configuration file
        """
        self.onProfileSetup()
        profile = {}
        profile["target"] = self.target

        if self.target == Target.PC.value:
            profile["driver"] = self.settingDialog.controlDialog.comboBox_driver_list.currentIndex()
            profile["input"] = self.settingDialog.controlDialog.comboBox_input_list.currentIndex()
            profile["output"] = self.settingDialog.controlDialog.comboBox_output_list.currentIndex()
            profile["samplerate"] = self.settingDialog.controlDialog.comboBox_sr_list.currentIndex()
            profile['engine_path'] = self.settingDialog.controlDialog.line_edit_engine_path.text()

        elif self.target in [Target.IMX.value, Target.LINUX.value, Target.RASP.value]:
            profile["path"] = self.path
            profile["hostname"] = [self.settingDialog.controlDialog.lineEdit_hostname_1.text(),
                                  self.settingDialog.controlDialog.lineEdit_hostname_2.text(),
                                  self.settingDialog.controlDialog.lineEdit_hostname_3.text(),
                                  self.settingDialog.controlDialog.lineEdit_hostname_4.text()]
            profile["port"] = self.port
            profile["username"] = self.username
            profile["password"] = self.password

        elif self.target in [Target.AMLOGIC.value, Target.QCS.value, Target.FLOW_APO.value,
                                   Target.LINKPLAY.value]:
            profile["path"] = self.path
            profile["hostname"] = [self.settingDialog.controlDialog.lineEdit_hostname_1.text(),
                                   self.settingDialog.controlDialog.lineEdit_hostname_2.text(),
                                   self.settingDialog.controlDialog.lineEdit_hostname_3.text(),
                                   self.settingDialog.controlDialog.lineEdit_hostname_4.text()]
            profile["port"] = self.port

        elif self.target in [Target.CORTEX_M_USB.value, Target.FLOW_EVK_UART.value, Target.GX8008C_USB.value]:
            profile["interface_list_index"] = self.settingDialog.controlDialog.comboBox_driver_list_5.currentIndex()
            profile["vid"] = self.vid
            profile["pid"] = self.pid
            profile['connection'] = self.settingDialog.controlDialog.Connection_comboBox.currentIndex()
            profile['comport'] = self.settingDialog.controlDialog.Port_comboBox.currentIndex()
            profile['rate'] = self.settingDialog.controlDialog.Rate_comboBox.currentIndex()
            profile['parity'] = self.settingDialog.controlDialog.Parity_comboBox.currentIndex()
            profile['bites'] = self.settingDialog.controlDialog.Bites_comboBox.currentIndex()
            if self.target == Target.GX8008C_USB.value:
                profile['engine'] = self.engine

        elif self.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
            profile["interface_list_index"] = self.settingDialog.controlDialog.comboBox_driver_list_6.currentIndex()
            profile["vid"] = self.vid
            profile["pid"] = self.pid
            profile['connection'] = self.settingDialog.controlDialog.Connection_comboBox.currentIndex()
            profile['comport'] = self.settingDialog.controlDialog.Port_comboBox.currentIndex()
            profile['rate'] = self.settingDialog.controlDialog.Rate_comboBox.currentIndex()
            profile['parity'] = self.settingDialog.controlDialog.Parity_comboBox.currentIndex()
            profile['bites'] = self.settingDialog.controlDialog.Bites_comboBox.currentIndex()
            profile['engine'] = self.engine


        fname, filter = QFileDialog.getSaveFileName(self, 'Save Profile File', getFileDialogDirectory(),
                                                    getProfileFilter())

        if fname:
            with open(fname, "w") as file:
                file.write(json.dumps(profile, indent=4))
                self.profile = fname

    def onLoadProfile(self):
        """
            load profile
        """
        with open(self.profile, "r") as file:
            try:
                raw_data = file.read()
                profile = json.loads(raw_data)

                if profile["target"] == Target.PC.value and self.hasPaSupported:
                    self.settingDialog.controlDialog.comboBox_targetdevice.setCurrentIndex(profile["target"])
                    self.settingDialog.controlDialog.comboBox_driver_list.setCurrentIndex(profile["driver"])
                    self.settingDialog.controlDialog.comboBox_input_list.setCurrentIndex(profile["input"])
                    self.settingDialog.controlDialog.comboBox_output_list.setCurrentIndex(profile["output"])
                    self.settingDialog.controlDialog.comboBox_sr_list.setCurrentIndex(profile["samplerate"])

                elif not profile["target"] == Target.PC.value:
                    self.settingDialog.controlDialog.comboBox_targetdevice.setCurrentIndex(profile["target"])
                    self.settingDialog.controlDialog.lineEdit_hostname_1.setText(profile["hostname"][0])
                    self.settingDialog.controlDialog.lineEdit_hostname_2.setText(profile["hostname"][1])
                    self.settingDialog.controlDialog.lineEdit_hostname_3.setText(profile["hostname"][2])
                    self.settingDialog.controlDialog.lineEdit_hostname_4.setText(profile["hostname"][3])
                    self.settingDialog.controlDialog.lineEdit_freeports.setText(str(profile["port"]))
                    self.settingDialog.controlDialog.lineEdit_username.setText(profile["username"])
                    self.settingDialog.controlDialog.lineEdit_password.setText(profile["password"])
                    self.settingDialog.controlDialog.lineEdit_path.setText(profile["path"])

            except Exception as e:
                dumpException(e)

    def onSoundDeviceUpdate(self):
        """
            Update audio sound devices
            1. Rescan audio sound device
            2. Save options for the current PC platform
            3. Update values to the UI
            4. Update supported ao
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        sd._terminate()
        sd._initialize()
        self.settingDialog.initData()
        self.onSavePCOption()
        self.settingDialog.audioInterfaceSetUp()
        QApplication.restoreOverrideCursor()
        self.statusBar().showMessage("Successfully Updated Sound Device", 3000)
        self.settingDialog.disable_not_supported_ao()

    def onCheckSoundDevice(self):
        """
            Check if the device has updates
            1. Obtain a list of old devices
            2. Rescan Sound Device and Obtain a new device list
            3. determine

            :return, if not found device, return False
        """
        input_device = self.settingDialog.controlDialog.comboBox_input_list.currentText()
        output_device = self.settingDialog.controlDialog.comboBox_output_list.currentText()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        sd._terminate()
        sd._initialize()
        self.settingDialog.initData()
        self.onSavePCOption()
        self.settingDialog.audioInterfaceSetUp()
        QApplication.restoreOverrideCursor()

        inputList = self.settingDialog.inputList(str(self.settingDialog.currDriver))
        outputList = self.settingDialog.outputList(str(self.settingDialog.currDriver))

        # When the input and output device is empty
        if inputList == [] and outputList == [] and self.target == Target.PC.value:
            self.settingDialog.onTerminateSocket("Sound Device Is Empty")
            return False

        # When the input device is empty, IN AO is not supported on the PC platform
        if inputList == [] and self.target == Target.PC.value:
            nodes = self.getCurrentNodeEditorWidget().scene.nodes
            for node in nodes:
                if node.op_code == OP_NODE_ADC:
                    self.settingDialog.onTerminateSocket("Input Device Is Empty")
                    return False

        # When the out device is empty, OUT AO is not supported on the PC platform
        if outputList == [] and self.target == Target.PC.value:
            nodes = self.getCurrentNodeEditorWidget().scene.nodes
            for node in nodes:
                if node.op_code == OP_NODE_DAC:
                    self.settingDialog.onTerminateSocket("Output Device Is Empty")
                    return False

        # when Device Not Found
        if not input_device in inputList and inputList != []:
            self.settingDialog.onTerminateSocket("Device Not Found", input_device)
            return False

        # when Device Not Found
        if not output_device in outputList and outputList != []:
            self.settingDialog.onTerminateSocket("Device Not Found", output_device)
            return False

        return True

    def onExportXML(self, flw_file_path=None):
        """
            Check design valid or not, if valid, export flw file

            :param flw_file_path: str, flw file path that you want to output;
                default:None, if no parameter value provided,
                file will be stored in location which is specified by system

            :return: boolean or tuple, if no problems, return True,
                if having problems, return tuple, whose first element is False,
                second element is error message.
        """
        isChecked = self.onDesignRuleCheck()
        if not isChecked:
            self.actRuleCheck.setChecked(True)
            self.onIsNodeValid(True)
            if Debug.DEBUG_COMMON.value:
                print("Design rule check failed!")
            return False, 'Design rule check failed'

        sub_window = self.findMain().widget()

        try:
            sub_window.exportXML(sub_window=sub_window,
                                 flw_file_path=flw_file_path)
            return True
        except Exception as e:
            if Debug.DEBUG_COMMON.value:
                print("export fail " + str(e))
            return False, 'Export failed'

    def onExportXMLTip(self):
        """
            export flw file, system will ask user for the desired file path to output.
        """
        try:
            flw_file_path_without_extension, extension = QFileDialog.getSaveFileName(self, "export flw file",
                                                                                     self.getFileDialogDirectory() + "/default_config",
                                                                                     filter="FLW Files (*.flw)")
            if not flw_file_path_without_extension: return
            flw_file_path = flw_file_path_without_extension
            is_export_success = self.onExportXML(flw_file_path=flw_file_path)
            if type(self.custom_message) is list:
                statement = 'The SRC is not valid, so the following AO cannot be used.'
                for ao in self.custom_message:
                    statement += '\n   ● ' + ao
                statement += '\nPlease verify that the system sample rate and SRC settings are correct.'
                statement += f'\nCurrent system sample rate : {self.settingDialog.controlDialog.comboBox_sr_list.currentText()}Hz'
                QMessageBox.about(self, 'Invalid Sample Rate Conversion', statement)
                return
            if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
                QMessageBox.about(self, 'invalid design', 'invalid design')
                return
            if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
                QMessageBox.about(self, 'config export failed', 'config export failed')
                return
            QMessageBox.about(self, "Export flw file successfully", "Path:%s" % flw_file_path)
        except Exception as e:
            if Debug.DEBUG_COMMON.value:
                print("fail to export, error message:" + str(e))

    def onExportCommand(self, export_type=ExportType.COMMAND.value):
        """
            Export command on dialog
            :param export_type: int, determines which content should be outputted,
                the value of parameter should be defined in ExportType.
                default:ExportType.COMMAND.value
        """
        if export_type not in [member.value for member in ExportType]:
            if Debug.DEBUG_COMMON.value:
                print(f'Value of export_type parameter:{export_type} is not defined in ExportType.')
            return
        self.export = Ui_export_command()
        self.export.setupUi(self.exportDialogWidget)
        if export_type == ExportType.RAW_COMMAND.value:
            self.exportDialogWidget.setWindowTitle('Export Raw Command')
        else:
            self.exportDialogWidget.setWindowTitle('Export Command')
        wnd = self.findMain()
        file_path = wnd.widget().filename
        if file_path is None:
            flw_file_path = self.userPath + '/' + 'default_config.flw'
        else:
            flw_file_path = os.path.join(self.temp_folder_path, 'default_config.flw')

        self.export.Copy.clicked.connect(self.copy)
        self.export.Close.clicked.connect(self.command_close)
        self.export.generate.clicked.connect(lambda: self.config2cmd(flw_file_path, export_type=export_type))

        self.exportDialogWidget.exec()

    def OpenUserInfoPane(self):
        """ Open User Info Pane """
        if self.user_pane_open == False:
            self.user_pane_open = True
            self.user_pane_dialog = QDialog(self)
            self.user_pane = Ui_user_pane()
            self.user_pane.setupUi(self.user_pane_dialog)
            self.user_pane_dialog.setWindowFlags(Qt.FramelessWindowHint)
            self.UserPaneResize()
            self.user_pane_dialog.setVisible(True)

            self.user_pane.signin.setCursor(Qt.PointingHandCursor)
            self.user_pane.signin.clicked.connect(self.StartLoginServer)
            self.user_pane.signout.clicked.connect(self.UserSignoutSuccess)
            self.user_pane.feedback.clicked.connect(self.handleFeedback)

            self.UserPaneSwitch()
        else:
            self.user_pane_open = False
            self.user_pane_dialog.setVisible(False)

    def UserPaneSwitch(self):
        if self.license_mechanism.user == None:
            self.user_pane.action.setVisible(True)
            self.user_pane.info.setVisible(False)
            self.user_pane.text_2.setText(f'Not signed-in users, Flow Studio will expire in {self.license_mechanism.remain_time.days} days')
        else:
            self.user_pane.action.setVisible(False)
            self.user_pane.info.setVisible(True)

            self.user_pane.email.setText(self.license_mechanism.user['email'])
            self.user_pane.expired.setText('Expired Date: Never expired (Tymphany user)')
            self.user_pane.tier.setText(f'Plan: {self.license_mechanism.tier}')
            if self.license_mechanism.remain_time.days == 9999:
                expired_time = 'Expired Date: Never expired (Tymphany user)'
            else:
                expired_time = f'Expired in {self.license_mechanism.remain_time.days} days'
            self.user_pane.expired.setText(expired_time)

    def UserPaneResize(self):
        if hasattr(self, 'user_pane_dialog') and self.user_pane_dialog:
            self.user_pane_dialog.setGeometry(self.geometry().width() - self.user_pane_dialog.width() - 2,
                                              self.menuBar().height() + 4,
                                              self.user_pane_dialog.width(),
                                              self.user_pane_dialog.height())

    def StartLoginServer(self):
        local_server_thread = LocalServer(parent=self)
        local_server_thread.callback_token.connect(self.UserSignInSuccess)
        local_server_thread.callback_port.connect(self.OpenLoginURL)
        local_server_thread.start()

    def OpenLoginURL(self, port):
        import webbrowser
        url = self.license_mechanism.user_login_url + port
        webbrowser.open(url)

    def UserSignInSuccess(self, token):
        self.license_mechanism.check_user_metadata(token=token)
        self.settingDialog.disable_not_supported_ao()
        self.UserPaneSwitch()

    def UserSignoutSuccess(self):
        self.license_mechanism.check_user_metadata(token='')
        self.settingDialog.disable_not_supported_ao()
        self.UserPaneSwitch()

    def open_input_text_generate_flow_dialog(self):
        self.open_input_text_generate_flow_q_dialog = QDialog(self)
        self.input_text_generate_flow_dialog = Ui_InputTextGenerateFlowDialog()
        self.open_input_text_generate_flow_q_dialog.setFixedSize(400, 300)
        self.input_text_generate_flow_dialog.setupUi(self.open_input_text_generate_flow_q_dialog)
        self.open_input_text_generate_flow_q_dialog.setWindowTitle('Generate Flow By Text')
        self.input_text_generate_flow_dialog.buttonBox.button(QDialogButtonBox.Ok).setText('Generate')
        self.input_text_generate_flow_dialog.buttonBox.clicked.connect(
            self.handle_input_text_generate_flow_dialog_options)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        self.open_input_text_generate_flow_q_dialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def open_flow_ai_dialog(self):
        self.flow_ai_manager.open_flow_ai_dialog()

    def open_flow_ai_dialog1(self):
        self.flow_ai_web_manager.toggle(route='/ai')

    def handle_input_text_generate_flow_dialog_options(self, button):
        curr_btn = self.input_text_generate_flow_dialog.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            input_text = self.input_text_generate_flow_dialog.plainTextEdit.toPlainText()
            if input_text == '':
                QMessageBox.warning(self, 'Please input text',
                                    f'Please input text.')
            else:
                is_do_nothing = self.is_do_nothing(input_text)
                if not is_do_nothing:
                    mainWindow = self.findMain()
                    if mainWindow is not None:
                        if not mainWindow.close():
                            return
                    nodeeditor = FLOW_Sub_Window()
                    subwnd = self.createMdiChild(nodeeditor)
                    nodeeditor.scene.has_been_modified = False
                    nodeeditor.scene.history.clear()
                    nodeeditor.scene.history.storeInitialHistoryStamp()
                    nodeeditor.setTitle()
                    subwnd.show()
                    sub_windows = self.mdiArea.subWindowList()
                    main_sub_window = sub_windows[0].widget()
                    self.generate_flow_info_by_text(input_text, main_sub_window)
                    for i in range(len(main_sub_window.scene.nodes)):
                        node = main_sub_window.scene.nodes[i]
                        node.eval()
                    self.open_input_text_generate_flow_q_dialog.close()
        elif curr_btn == QDialogButtonBox.Cancel:
            self.open_input_text_generate_flow_q_dialog.close()

    def is_do_nothing(self, text):
        in_matches = re.findall(r'(\d+)\s*in', text, re.IGNORECASE)
        out_matches = re.findall(r'(\d+)\s*out', text, re.IGNORECASE)
        channel_matches = re.findall(r'(\d+)\s*channel(s)?', text, re.IGNORECASE)
        gain_matches = re.search(r'gain', text, re.IGNORECASE)
        two_way_matches = re.search(r'(2|two)\s*way(s)?', text, re.IGNORECASE)

        in_numbers = [int(match) for match in in_matches]
        out_numbers = [int(match) for match in out_matches]
        channel_numbers = [int(match[0]) for match in channel_matches]
        has_gain = bool(gain_matches)
        has_2way = bool(two_way_matches)

        if has_2way:
            return False
        elif len(in_numbers) > 0 and len(out_numbers) > 0 and in_numbers[0] == out_numbers[0] and not has_gain:
            return False
        elif len(channel_numbers) > 0 and not has_gain:
            return False
        elif len(in_numbers) > 0 and len(out_numbers) > 0 and in_numbers[0] == out_numbers[0] and has_gain:
            return False
        elif len(channel_numbers) > 0 and has_gain:
            return False
        else:
            res = QMessageBox.question(self, 'Limited Scenario Support and Default Graph Inquiry',
                                       'This is a demo version, so it does not support all scenarios.\nDo you want default graph?',
                                       QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.Yes:
                return False
            else:
                return True

    def generate_flow_info_by_text(self, text, sub_window):
        in_matches = re.findall(r'(\d+)\s*in', text, re.IGNORECASE)
        out_matches = re.findall(r'(\d+)\s*out', text, re.IGNORECASE)
        channel_matches = re.findall(r'(\d+)\s*channel(s)?', text, re.IGNORECASE)
        gain_matches = re.search(r'gain', text, re.IGNORECASE)
        two_way_matches = re.search(r'(2|two)\s*way(s)?', text, re.IGNORECASE)

        in_numbers = [int(match) for match in in_matches]
        out_numbers = [int(match) for match in out_matches]
        channel_numbers = [int(match[0]) for match in channel_matches]
        has_gain = bool(gain_matches)
        has_2way = bool(two_way_matches)

        if has_2way:
            first_in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-790, y_position=-290)
            second_in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-790, y_position=-210)
            merger_node = sub_window.add_ao(OP_NODE_MERGER, x_position=-630, y_position=-290)
            sub_window.view.dragging.add_edge(start_socket=first_in_node.outputs[0],
                                              end_socket=merger_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            sub_window.view.dragging.add_edge(start_socket=second_in_node.outputs[0],
                                              end_socket=merger_node.inputs[1],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            gain_node = sub_window.add_ao(OP_NODE_GAIN,
                                          parameters={'num_channels': 1},
                                          x_position=-440,
                                          y_position=-290)
            gain_node.collapseNode()
            sub_window.view.dragging.add_edge(start_socket=merger_node.outputs[0],
                                              end_socket=gain_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            first_peq_node = sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 8, 'num_channels': 1},
                                               x_position=-300, y_position=-290)
            first_peq_node.collapseNode()
            sub_window.view.dragging.add_edge(start_socket=gain_node.outputs[0],
                                              end_socket=first_peq_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            xover_node = sub_window.add_ao(OP_NODE_XOVER,
                                           x_position=-150,
                                           y_position=-290)
            xover_node.collapseNode()
            sub_window.view.dragging.add_edge(start_socket=first_peq_node.outputs[0],
                                              end_socket=xover_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            second_peq_node = sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 8, 'num_channels': 1},
                                                x_position=73, y_position=-310)
            second_peq_node.collapseNode()
            third_peq_node = sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 8, 'num_channels': 1},
                                               x_position=73, y_position=-230)
            third_peq_node.collapseNode()
            sub_window.view.dragging.add_edge(start_socket=xover_node.outputs[0],
                                              end_socket=second_peq_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            sub_window.view.dragging.add_edge(start_socket=xover_node.outputs[1],
                                              end_socket=third_peq_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            first_limiter = sub_window.add_ao(OP_NODE_LIMITER, parameters={'num_channels': 1},
                                              x_position=230, y_position=-310)
            first_limiter.collapseNode()
            second_limiter = sub_window.add_ao(OP_NODE_LIMITER, parameters={'num_channels': 1},
                                               x_position=230, y_position=-230)
            second_limiter.collapseNode()
            sub_window.view.dragging.add_edge(start_socket=second_peq_node.outputs[0],
                                              end_socket=first_limiter.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            sub_window.view.dragging.add_edge(start_socket=third_peq_node.outputs[0],
                                              end_socket=second_limiter.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            first_out_node = sub_window.add_ao(OP_NODE_DAC, x_position=400, y_position=-310)
            second_out_node = sub_window.add_ao(OP_NODE_DAC, x_position=400, y_position=-230)
            sub_window.view.dragging.add_edge(start_socket=first_limiter.outputs[0],
                                              end_socket=first_out_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
            sub_window.view.dragging.add_edge(start_socket=second_limiter.outputs[0],
                                              end_socket=second_out_node.inputs[0],
                                              ignore_message_box=True,
                                              ignore_drag_edge=True)
        elif len(in_numbers) > 0 and len(out_numbers) > 0 and in_numbers[0] == out_numbers[0] and not has_gain:
            num_in = in_numbers[0]
            for i in range(num_in):
                in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-650, y_position=-250 + 150 * i)
                out_node = sub_window.add_ao(OP_NODE_DAC, x_position=0, y_position=-250 + 150 * i)
                in_node_output_socket = in_node.outputs[0]
                out_node_input_socket = out_node.inputs[0]
                sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                                  end_socket=out_node_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
        elif len(channel_numbers) > 0 and not has_gain:
            num_channels = channel_numbers[0]
            for i in range(num_channels):
                in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-650, y_position=-250 + 150 * i)
                out_node = sub_window.add_ao(OP_NODE_DAC, x_position=0, y_position=-250 + 150 * i)
                in_node_output_socket = in_node.outputs[0]
                out_node_input_socket = out_node.inputs[0]
                sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                                  end_socket=out_node_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
        elif len(in_numbers) > 0 and len(out_numbers) > 0 and in_numbers[0] == out_numbers[0] and has_gain:
            num_in = in_numbers[0]
            gain_node = sub_window.add_ao(OP_NODE_GAIN,
                                          parameters={'num_channels': num_in},
                                          x_position=-325,
                                          y_position=0)
            for i in range(num_in):
                in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-650, y_position=-250 + 150 * i)
                out_node = sub_window.add_ao(OP_NODE_DAC, x_position=0, y_position=-250 + 150 * i)
                in_node_output_socket = in_node.outputs[0]
                out_node_input_socket = out_node.inputs[0]
                sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                                  end_socket=gain_node.inputs[i],
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
                sub_window.view.dragging.add_edge(start_socket=gain_node.outputs[i],
                                                  end_socket=out_node_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
        elif len(channel_numbers) > 0 and has_gain:
            num_channels = channel_numbers[0]
            gain_node = sub_window.add_ao(OP_NODE_GAIN,
                                          parameters={'num_channels': num_channels},
                                          x_position=-325,
                                          y_position=0)
            for i in range(num_channels):
                in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-650, y_position=-250 + 150 * i)
                out_node = sub_window.add_ao(OP_NODE_DAC, x_position=0, y_position=-250 + 150 * i)
                in_node_output_socket = in_node.outputs[0]
                out_node_input_socket = out_node.inputs[0]
                sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                                  end_socket=gain_node.inputs[i],
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
                sub_window.view.dragging.add_edge(start_socket=gain_node.outputs[i],
                                                  end_socket=out_node_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)
        else:
            for i in range(2):
                in_node = sub_window.add_ao(OP_NODE_ADC, x_position=-650, y_position=-250 + 150 * i)
                out_node = sub_window.add_ao(OP_NODE_DAC, x_position=0, y_position=-250 + 150 * i)
                in_node_output_socket = in_node.outputs[0]
                out_node_input_socket = out_node.inputs[0]
                sub_window.view.dragging.add_edge(start_socket=in_node_output_socket,
                                                  end_socket=out_node_input_socket,
                                                  ignore_message_box=True,
                                                  ignore_drag_edge=True)

    def copy(self):
        """
            Copy text to clipboard
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.export.textEdit.toPlainText())
        if clipboard.text:
            QMessageBox.about(self, "Successful", "Copy Succeeded!")
        else:
            QMessageBox.about(self, "Failed", "Copy Failed!")

    def command_close(self):
        """
            close command window
        """
        self.exportDialogWidget.close()

    def config2cmd(self, path, target=Target.PC.value, export_type=ExportType.COMMAND.value):
        """
            Export command to dialog based on specified flw file path

            :param path: str, flw file path

            :param target: int, determines which platform is used,
                the value of parameter should be defined in Target.
                default:Target.PC.value

            :param export_type: int, determines which content should be outputted,
                the value of parameter should be defined in ExportType.
                default:ExportType.COMMAND.value
        """
        if target == Target.PC.value:
            self.export.textEdit.clear()
            self.export.progressBar.setValue(0)

        # Check .flw
        QApplication.setOverrideCursor(Qt.WaitCursor)
        is_export_success = self.onExportXML()
        QApplication.restoreOverrideCursor()

        if type(self.custom_message) is list:
            statement = 'SRC Check Fail, The following AO did not pass:'
            for ao in self.custom_message:
                statement += '\n   ● ' + ao
            self.settingDialog.onTerminateSocket('SRC Check Fail', statement)
            return

        if type(is_export_success) is tuple and is_export_success[1] == 'Design rule check failed':
            if hasattr(self.window, 'custom_message'):
                self.settingDialog.onTerminateSocket("invalid design", custom_message=self.custom_message)
                return
            self.settingDialog.onTerminateSocket("invalid design")
            return
        if type(is_export_success) is tuple and is_export_success[1] == 'Export failed':
            self.settingDialog.onTerminateSocket("config export failed")
            return
        self.config2cmd_progress_bar(target, 10)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        with open(path, 'r') as f:
            content = f.readline()
            result = Conversion().binary_to_str(input_binary=content)
            # Write to temp file
            try:
                with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.xml') as temp_file:
                    temp_file.write(result)
                    xml_temp_file_path = temp_file.name
            except PermissionError:
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Error code:{PERMISSION_ERROR_WHEN_CREATE_TEMP_FILE}'
                )
                return
        QApplication.restoreOverrideCursor()
        self.config2cmd_progress_bar(target, 20)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        special_types = ['PEQ', 'BIQUAD', 'LONG_APF', 'LPF_COMB_FILTER', 'PEQ_FP', 'BIQUAD_LOAD', 'FIR_LOAD']
        tree = ET.parse(xml_temp_file_path)
        root = tree.getroot()
        ao_list = root.findall('AO')
        is_special_type_present = any(ao.find('type').text in special_types for ao in ao_list)
        if is_special_type_present:
            # Open sub windows
            main_window = self.findMain().widget()
            current_window = self.getCurrentNodeEditorWidget()
            nodes_in_main = main_window.scene.nodes
            for node in nodes_in_main:
                if node.op_code == OP_NODE_SUBPATCH:
                    self.open_subwindow_in_subpatch_recursively(node.title)
                    self.setActiveSubWindow(current_window.parent())
        self.config2cmd_progress_bar(target, 30)

        allCmdList = []
        progress_index = 0

        lockAudioCmd = "setRoot/lockAudio/1/"
        clearLayoutCmd = "clearLayout/"
        initCmd = "init/" + str(len(ao_list)) + "/"
        reprepareCmd = "reprepare/"
        buildProcStepCmd = "buildProcStep/"
        unlockAudioCmd = "setRoot/lockAudio/0/"

        allCmdList.append(lockAudioCmd)
        allCmdList.append(clearLayoutCmd)
        allCmdList.append(initCmd)

        for AO in ao_list:
            # create obj commands
            Type = AO.find('type').text
            Id = AO.find("id").text
            Order = AO.find("order").text
            try:
                InCh = AO.attrib['in_ch']
                OutCh = AO.attrib['out_ch']
                Link = AO.attrib['link']
            except:
                InCh = -1
                OutCh = -1
                Link = -1

            paramDict = {}
            # build up a param name - val dict pair for later look up
            for param in AO.findall("param"):
                paramName = param.attrib['name']
                paramVal = param.attrib['val']
                paramDict[paramName] = paramVal

            if Type in special_types:
                tap_menu_parameter_name = None
                for window in self.mdiArea.subWindowList():
                    for node in window.widget().scene.nodes:
                        if f'{node.op_title}_{node.designator}' == Id:
                            tap_menu_parameter_name = node.tap_menu_parameter_name

                if Type == 'BIQUAD_LOAD':
                    tap_menu_parameter_name = 'maxBand' # e.g: obj/BIQUAD_LOAD/BIQUAD_LOAD_1/1/1/1/1/1/maxBand@1000
                if Type == 'FIR_LOAD':
                    tap_menu_parameter_name = 'maxTap' # e.g: obj/BIQUAD_LOAD/BIQUAD_LOAD_1/1/1/1/1/1/maxTap@1000

                objCmd = "obj/" + Type + "/" + Id + "/" + Order + "/" + str(InCh) + "/" + str(OutCh) + "/" + str(
                    Link) + f"/1/{tap_menu_parameter_name}@" + paramDict[tap_menu_parameter_name]
            else:
                objCmd = "obj/" + Type + "/" + Id + "/" + Order + "/" + str(InCh) + "/" + str(OutCh) + "/" + str(
                    Link) + "/0/"

            #         objCmds.append(objCmd)
            allCmdList.append(objCmd)
            # param commands
            for param in AO.findall("param"):
                paramName = param.attrib['name']
                if Debug.DEBUG_Low_Level.value: print(paramName)
                paramVal = param.attrib['val']
                try:
                    row = param.attrib['row']
                    col = param.attrib['col']
                except:
                    row = '0'
                    col = '0'

                paramNameSplit = paramName.split("_")

                if paramName == "ch" and int(paramVal) >= 1:
                    if Type == "MUX_ST":
                        paramCmd = "setCoord/" + Id + "/select/" + str(2 * int(paramDict['select'])) + "/0/0/"
                        allCmdList.append(paramCmd)
                        paramCmd = "setCoord/" + Id + "/select/" + str(2 * int(paramDict['select']) + 1) + "/0/1/"
                        allCmdList.append(paramCmd)
                    elif Type == "GAIN_ST":
                        paramCmd = "setCoord/" + Id + "/gain/" + paramDict['gain'] + "/0/1/"
                        allCmdList.append(paramCmd)
                    elif Type == "ATTEN_ST":
                        paramCmd = "setCoord/" + Id + "/gain/" + paramDict['gain'] + "/0/1/"
                        allCmdList.append(paramCmd)

                else:
                    try:
                        if paramNameSplit[0] == "Path":
                            paramCmd = "setStringCoord:#" + Id + ":#" + paramNameSplit[
                                0] + ":#" + paramVal + ":#" + row + ":#" + col + ":#"
                        else:
                            paramCmd = "setCoord/" + Id + "/" + paramNameSplit[
                                0] + "/" + paramVal + "/" + row + "/" + col + "/"
                    except:
                        None

                    if paramNameSplit[0] in ["tap", "Info"] and Type!="FIR": # skip those param names
                        None
                    else:
                        allCmdList.append(paramCmd)

            if Type == 'IIRCOEF':
                cmd = "setCoord/" + Id + "/ready/1/0/0/"
                allCmdList.append(cmd)

            progress_index = progress_index + 1
            self.config2cmd_progress_bar(target, 30 + progress_index / (len(ao_list)) * 30)
        if is_special_type_present:
            # close sub windows
            for window in self.mdiArea.subWindowList():
                if hasattr(window.widget(),
                           'encrypted') and window.widget().encrypted and not window.widget().already_input_password:
                    self.close_sub_window(window)
                if hasattr(window.widget(), 'close_if_no_problem') and window.widget().close_if_no_problem:
                    self.close_sub_window(window)

        allCmdList.append(reprepareCmd)
        allCmdList.append(buildProcStepCmd)
        progress_index = 0

        for AO in ao_list:
            Id = AO.find("id").text
            # create wire commands
            for dst in AO.findall("to"):
                dstCmd = Id + "@" + dst.attrib['index'] + "/" + dst.attrib['port'] + "@" + dst.attrib['dir'] + "/"
                wireCmd = "wire/" + dstCmd
                #             wireCmds.append(wireCmd)
                allCmdList.append(wireCmd)
            # create ctrlwire commands
            for dst in AO.findall("ctrlto"):
                dstCmd = Id + "@" + dst.attrib['index'] + "/" + dst.attrib['port'] + "@" + dst.attrib['dir'] + "/"
                wireCmd = "ctrlWire/" + dstCmd
                #             wireCmds.append(wireCmd)
                allCmdList.append(wireCmd)

            progress_index = progress_index + 1
            self.config2cmd_progress_bar(target, 60 + progress_index / len(ao_list) * 30)

        allCmdList.append(unlockAudioCmd)
        QApplication.restoreOverrideCursor()

        if target == Target.PC.value:
            if export_type == ExportType.COMMAND.value:
                for i in range(len(allCmdList)):
                    self.export.textEdit.append('FlowEngine_query_cmd(engine, "' + allCmdList[i] + '");')
        else:
            self.settingDialog.allCmdList = allCmdList
            self.config2cmd_progress_bar(target, 100)
            return
        # for i in range(len(allCmdList)):
        #     # print('FlowEngine_query_cmd(engine, "' + allCmdList[i] + '");')
        #     self.export.textEdit.append('FlowEngine_query_cmd(engine, "' + allCmdList[i] + '");')
        # print('----------- raw cmds ----------------------')
        if export_type == ExportType.RAW_COMMAND.value:
            for i in range(len(allCmdList)):
                self.export.textEdit.append(allCmdList[i])

        self.config2cmd_progress_bar(target, 100)

    def config2cmd_progress_bar(self, target, value):
        QApplication.processEvents()
        if target == Target.PC.value:
            self.export.progressBar.setValue(value)
        elif target == Target.S7.value:
            pass
        else:
            self.settingDialog.designUsbSelect.convert_bar.setValue(value)

    def upload_target(self):
        """upload design from current canvas to target device"""
        if Debug.DEBUG_COMMON.value: print("upload design from current canvas to target device")
        self.settingDialog.onUploadTarget()

    def download_target(self):
        """download design from target device to the current gui canvas"""
        if Debug.DEBUG_COMMON.value: print("download design from target device to the current gui canvas")
        # self.dialog.onDownloadTarget()

    def upload_flash(self):
        """upload flash from current canvas to target device"""
        qdialog = QDialog(self)
        self.settingDialog.designUsbSelect = Ui_usb_runtime_select_Dialog()
        self.settingDialog.designUsbSelect.setupUi(qdialog)
        self.settingDialog.designUsbSelect.flash.clicked.connect(lambda: self.settingDialog.onUSBUploadFlash(qdialog))
        self.settingDialog.designUsbSelect.upload.setVisible(False)
        self.settingDialog.designUsbSelect.only.setVisible(False)
        qdialog.exec()

    def onEditMode(self):
        """
            Toggle Edit Mode
        """
        if self.editmode:
            self.editmode = False
        else:
            self.editmode = True

    def updateQTabBarColor(self, editmode):
        """
            Toggle QTabBar Color

            :param editmode, Is it in editing status
        """
        if editmode:
            self.setStyleSheet("QMdiArea QTabBar::tab:!selected{background:#186A3B;}"
                               "QMdiArea QTabBar::tab:selected{background:#28B463;}")
        else:
            self.setStyleSheet("")

    def getDictByOP(self, node_op: int, nodes: list):
        """
            Filter and sort the nodes list

            :param node_op, op_code
            :param nodes, nodes list

            :return, Node Dictionary List
        """
        sortedDicts = []
        for node in nodes:
            if node['op_code'] == node_op:
                sortedDicts.append(node)
        sortedDicts = sorted(sortedDicts, key=operator.itemgetter('designator'))
        if Debug.DEBUG_Low_Level.value: print(sortedDicts)
        return sortedDicts

    def saveGroupWindows(self):
        activewnd = self.mdiArea.activeSubWindow()
        windows = self.mdiArea.subWindowList()
        windows.remove(activewnd)

        if activewnd.widget().getUserFriendlyFilename() in ['main.json', 'New FLOW', 'New FLOW*']:
            # if active window = main, save all the other window except active window

            # save them all
            for window in windows:
                window.widget().fileSave()
                window.widget().setTitle()
        else:
            # if active window = group window, save all the other window except active window and main window

            # search main, and remove it from list
            for window in windows:
                if window.widget().getUserFriendlyFilename() in ['main.json', 'New FLOW', 'New FLOW*']:
                    windows.remove(window)
                    break

            # rest element item in array will be group sub window, save them all
            for window in windows:
                window.widget().fileSave()
                window.widget().setTitle()

    def findMinimalConseqSequence(self, nodes: list):
        """
            Find the Minimal Conseq sequence of designer in the node list
        """
        n = len(nodes)
        count = 0
        res = 0

        if n == 0:
            return 1

        elif n == 1:
            if nodes[0]['designator'] == 1:
                return 2
            else:
                return 1

        for index in range(n):
            if (index > 0 and not nodes[index]['designator'] == nodes[index - 1]['designator'] + 1):
                return nodes[index - 1]['designator'] + 1
            elif (index > 0 and not index + 1 == nodes[index]['designator']):
                return index
            elif (index > 0 and nodes[index]['designator'] == nodes[index - 1]['designator'] + 1):
                count = count + 1
                res = nodes[index]['designator']

        return res + 1

    def getSelfWindow(self):
        """
            get settingDialog
        """
        return self.settingDialog

    def clear_sub_patchs_window_objects(self):
        """
            clear self.sub_patchs
        """
        self.sub_patchs = []

    # AO designator不能重複
    def prevent_conflict_name_and_designators(self):
        """
            AO designer cannot be duplicated
        """
        nodes_this_scene = self.getCurrentNodeEditorWidget().scene.nodes
        nodesSets = self.getCurrentNodeEditorWidget().collectNodesFromSubWnds(except_self=True)
        for node in nodes_this_scene:
            if node.op_code > 0 and node.op_code != OP_NODE_SUBPATCH:
                sortedNodes = self.getCurrentNodeEditorWidget().getNodesByOP(node.op_code, nodesSets)
                designator = self.getCurrentNodeEditorWidget().findMinimalConseqSequence(sortedNodes)
                node.designator = designator
                nodesSets.append(node)

    def reassign_designator(self, node, all_nodes):
        """
            Reassign node designer identity and update node titles

            :param node, select node
            :param all_nodes, all node list
        """
        sortedNodes = self.getDictByOP(node['op_code'], all_nodes)
        designator = self.findMinimalConseqSequence(sortedNodes)
        node['designator'] = designator
        node['title'] = node['type'] + '_' + str(designator)

    def decrypt_subpatch_recursively(self, input_subpatch_name, input_password, windows):
        # print(f'1 {input_subpatch_name} {input_password}')
        def dfs_decrypt_subpatch(subpatch_name, input_password, windows):
            is_subpatch_inside = False
            for sub_window in windows:
                sub_window_name = sub_window.widget().getPrettyFilename()
                if subpatch_name == sub_window_name:

                    if hasattr(sub_window.widget(), 'correct_password'):
                        if sub_window.widget().correct_password != input_password:
                            return
                        delattr(sub_window.widget(), 'correct_password')
                    if hasattr(sub_window.widget(), 'encrypted'):
                        delattr(sub_window.widget(), 'encrypted')
                    if hasattr(sub_window.widget(), 'already_input_password'):
                        delattr(sub_window.widget(), 'already_input_password')
                    subpatchs_inside = []
                    for node in sub_window.widget().scene.nodes:
                        if node.op_code == OP_NODE_SUBPATCH:
                            is_subpatch_inside = True
                            subpatchs_inside.append(node.title)

            if not is_subpatch_inside:
                return
            for subpatch_inside in subpatchs_inside:
                dfs_decrypt_subpatch(subpatch_inside, input_password, windows)
        dfs_decrypt_subpatch(input_subpatch_name, input_password, windows)

    def decrypt_file_not_recursively(self, file_name):
        with open(fr'{file_name}') as f:
            file_data = json.load(f)
            correct_password = AESOperation().decrypt_string(password=SECRET_KEY,
                                                             input_string=file_data['password'])
            decrypt_object = AESOperation().decrypt_string(password=correct_password,
                                                           input_string=file_data['object'])
            dic = json.loads(decrypt_object)
        with open(fr'{file_name}', 'w') as file:
            json.dump(dic, file)

    def encrypt_file_not_recursively(self, file_name, input_password):
        with open(fr'{file_name}') as f:
            file_data = json.load(f)
            # 原版檔案結構
            if 'object' not in file_data:
                encrypted_object = AESOperation().encrypt_string(password=input_password,
                                                                 input_string=json.dumps(file_data))
                encrypted_password = AESOperation().encrypt_string(password=SECRET_KEY,
                                                                   input_string=input_password)
                dic = {
                    'object': str(base64.b64encode(encrypted_object), 'utf-8'),
                    'password': str(base64.b64encode(encrypted_password), 'utf-8'),
                    'is_encrypted': True
                }
            # 新版檔案結構
            else:
                encrypted_object = AESOperation().encrypt_string(password=input_password,
                                                                 input_string=json.dumps(file_data['object']))
                encrypted_password = AESOperation().encrypt_string(password=SECRET_KEY,
                                                                   input_string=input_password)
                dic = {
                    'object': str(base64.b64encode(encrypted_object), 'utf-8'),
                    'password': str(base64.b64encode(encrypted_password), 'utf-8'),
                    'is_encrypted': True
                }
            # overwrite SUBPATCH file
            with open(fr'{file_name}', 'w') as file:
                json.dump(dic, file)

    def encrypt_subpatch_recursively(self, input_subpatch_name, input_password, windows):
        def dfs_encrypt_subpatch(subpatch_name, input_password, windows):
            is_subpatch_inside = False
            for sub_window in windows:
                sub_window_name = sub_window.widget().getPrettyFilename()
                if subpatch_name == sub_window_name:
                    sub_window.widget().encrypted = True
                    sub_window.widget().already_input_password = True
                    sub_window.widget().correct_password = input_password
                    subpatchs_inside = []
                    for node in sub_window.widget().scene.nodes:
                        if node.op_code == OP_NODE_SUBPATCH:
                            # 假如底下的subpatch沒有加密, 則要一起加密
                            if not node.is_encrypted():
                                is_subpatch_inside = True
                                subpatchs_inside.append(node.title)
            if not is_subpatch_inside:
                return
            for subpatch_inside in subpatchs_inside:
                dfs_encrypt_subpatch(subpatch_inside, input_password, windows)
        dfs_encrypt_subpatch(input_subpatch_name, input_password, windows)
        self.findMain().widget().scene.has_been_modified = True
        self.statusBar().showMessage('Added password successfully.', 3000)

    def add_node_in_subpatch_window(self, subpatch_name, node_op_code):
        current_window = self.getCurrentNodeEditorWidget()
        nodes = current_window.scene.nodes
        subpatch_node = None
        for node in nodes:
            if node.op_code == OP_NODE_SUBPATCH and node.title == subpatch_name:
                subpatch_node = node
                break
        self.open_subwindow_in_subpatch_recursively(subpatch_name)
        current_sub_windows = self.mdiArea.subWindowList()
        for sub_window in current_sub_windows:
            sub_window_name = sub_window.widget().getPrettyFilename()
            if sub_window_name == subpatch_name:
                if node_op_code == OP_NODE_INLET:
                    index = len(subpatch_node.inputlist)
                elif node_op_code == OP_NODE_OUTLET:
                    index = len(subpatch_node.outputlist)
                from flowstudio.nodes import INLET
                if node_op_code == OP_NODE_INLET:
                    node = INLET.FLOW_Node_INLET(sub_window.widget().scene)
                elif node_op_code == OP_NODE_OUTLET:
                    node = OUTLET.FLOW_Node_OUTLET(sub_window.widget().scene)
                node.designator = index + 1
                node.grNode.title += '_' + str(index + 1)
                node.title += '_' + str(index + 1)
                if node_op_code == OP_NODE_INLET:
                    node.setPos(-400, -150 + index * 150)
                elif node_op_code == OP_NODE_OUTLET:
                    node.setPos(400, -150 + index * 150)
                node_data = node.serialize()
                # 加入到subpatch window的所有history stamp
                for i in range(len(sub_window.widget().scene.history.history_stack)):
                    if node_data not in \
                            sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes']:
                        sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes'].append(
                            node_data)
        for sub_window in current_sub_windows:
            if hasattr(sub_window.widget(), 'close_if_no_problem'):
                if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                    self.close_sub_window(sub_window)
        self.setActiveSubWindow(current_window.parent())

    def delete_node_in_subpatch_window(self, subpatch_name, node_op_code):
        current_window = self.getCurrentNodeEditorWidget()
        self.open_subwindow_in_subpatch_recursively(subpatch_name)
        current_sub_windows = self.mdiArea.subWindowList()
        for sub_window in current_sub_windows:
            sub_window_name = sub_window.widget().getPrettyFilename()
            if sub_window_name == subpatch_name:
                nodes = sub_window.widget().scene.nodes
                all_specific_type_nodes = [node for node in nodes if node.op_code == node_op_code]
                max_specific_type_node_designator = all_specific_type_nodes[0].designator
                last_specific_node = all_specific_type_nodes[0]
                for inlet in all_specific_type_nodes:
                    if inlet.designator > max_specific_type_node_designator:
                        max_specific_type_node_designator = inlet.designator
                        last_specific_node = inlet
                node_data = last_specific_node.serialize()
                for i in range(len(sub_window.widget().scene.history.history_stack)):
                    if node_data in sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes']:
                        sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes'].remove(
                            node_data)
                last_specific_node.remove()
        for sub_window in current_sub_windows:
            if hasattr(sub_window.widget(), 'close_if_no_problem'):
                if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                    self.close_sub_window(sub_window)
        self.setActiveSubWindow(current_window.parent())

    def upload_project_info(self, action, content, project_name=None):
        """
            Upload project information to the server.

            Parameters:
                action (str): The action to be performed.
                content (dict): The content to be uploaded as a JSON dictionary.
                project_name (str, optional): The name of the project (default is 'temp' + formatted date and time).

            Returns:
                bool: True if the upload is successful, False otherwise.
        """
        now = datetime.datetime.now()
        formatted_date_time = now.strftime('%Y%m%d%H%M')
        if project_name is None:
            project_name = 'temp' + formatted_date_time
        try:
            res = requests.post(self.license_mechanism.add_project_info_url,
                                data=json.dumps(
                                    {'address': self.encrypt(self.license_mechanism.address).decode("utf-8"),
                                     'action': self.encrypt(action).decode("utf-8"),
                                     'content': self.encrypt(json.dumps(content)).decode("utf-8"),
                                     'projectName': self.encrypt(project_name).decode("utf-8")
                                     }
                                ),
                                headers={
                                    'Content-type': 'application/json'
                                },
                                timeout=4)
            if res.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

    def set_custom_menu_for_sub_window(self, sub_window):
        custom_menu = QMenu(sub_window)
        close_action = QAction('Close', self)
        close_action.triggered.connect(sub_window.widget().custom_hide)
        custom_menu.addAction(close_action)
        sub_window.setSystemMenu(custom_menu)

    def deselect_all_items(self):
        for window in self.mdiArea.subWindowList():
            for node in window.widget().scene.nodes:
                node.grNode.setSelected(False)
            for edge in window.widget().scene.edges:
                edge.grEdge.setSelected(False)


    def control_feature_by_license_tier(self, tier):
        """
            Control the features based on the license tier
        """
        if tier == "Free":
            combo_box = self.settingDialog.controlDialog.comboBox_targetdevice
            for i in range(combo_box.count()):
                item = combo_box.model().item(i)
                item.setEnabled(item.text() in ["PC", "Flow EVK", "TCP"])
            self.act_custom_ao_builder.setEnabled(False)
            self.act_import_custom_aos_settings.setEnabled(False)
            self.act_export_custom_aos_settings.setEnabled(False)
            # self.actQuickSignalFlowAi.setEnabled(False)
            self.editorDock.removeAction(self.actQuickSignalFlowAi)

            root = self.nodesListWidget.invisibleRootItem()
            for i in range(root.childCount()):
                if root.child(i).text(0) == "Custom":
                    root.child(i).setHidden(True)

        else:
            combo_box = self.settingDialog.controlDialog.comboBox_targetdevice
            for i in range(combo_box.count()):
                item = combo_box.model().item(i)
                item.setEnabled(item.text() not in ["Linux", "Linkplay A98"])
            self.act_custom_ao_builder.setEnabled(True)
            self.act_import_custom_aos_settings.setEnabled(True)
            self.act_export_custom_aos_settings.setEnabled(True)
            self.actQuickSignalFlowAi.setEnabled(True)
            self.editorDock.addAction(self.actQuickSignalFlowAi)

            root = self.nodesListWidget.invisibleRootItem()
            for i in range(root.childCount()):
                if root.child(i).text(0) == "Custom":
                    root.child(i).setHidden(False)

            for i in self.license_mechanism.custom_ao_list:
                self.license_mechanism.feature_permission_data[AO_TYPE_NAME].append(i)

    def set_AO_feature_edit_mode_change(self, mode):
        """
            Set special AO function when edit mode changes
        """
        windows = self.mdiArea.subWindowList()
        for window in windows:
            for i in range(len(window.widget().scene.nodes)):
                node = window.widget().scene.nodes[i]
                if node.op_code == OP_NODE_SRC:
                    node.is_enable_comboBox(mode)

class TempNode(object):
    def __init__(self):
        self.designator = 1

def smartCWD():
    current_path = os.getcwd()
    index = current_path.rsplit('\\', 1)
    target_path = index[0] + '\\' + 'bin'
    return target_path


class SignalFlowComparisonResultDialog(QWidget):
    def __init__(self, details, is_use_current_flow, orig_proj_file_path, chg_proj_file_path, parent=None):
        super(SignalFlowComparisonResultDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.setStyleSheet("background-color: #474747")
        self.details = details
        self.is_use_current_flow = is_use_current_flow
        self.setWindowTitle('Comparison result')
        self.setGeometry(100, 100, 600, 400)

        self.column_labels = ['NO.', 'type', 'details']

        self.table = QTableWidget(self)
        self.table.setStyleSheet('background-color:#212121;')
        self.table.setColumnCount(len(self.column_labels))
        self.table.setHorizontalHeaderLabels(self.column_labels)
        header_color = QColor('#2A2F2A')
        for column in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(column)
            if header_item is not None:
                header_item.setBackground(QBrush(header_color))
        self.table.setRowCount(len(details))
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout()
        orig_proj_label = QLabel('Original Project File Path:')
        orig_proj_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        orig_proj_path_label = QLabel(orig_proj_file_path)
        orig_proj_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(orig_proj_label)
        layout.addWidget(orig_proj_path_label)
        if not is_use_current_flow:
            chg_proj_label = QLabel('Changed Project File Path:')
            chg_proj_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            chg_proj_path_label = QLabel(chg_proj_file_path)
            chg_proj_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(chg_proj_label)
            layout.addWidget(chg_proj_path_label)
        else:
            label = QLabel('Use the currently edited flow as changed project')
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(label)
        export_button = QPushButton('Export')
        export_button.setFixedWidth(80)
        export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(export_button)
        layout.addWidget(self.table)
        self.setLayout(layout)
        content_color = QColor('#212121')
        row_no = 0
        for detail in details:
            index_item = QTableWidgetItem(str(detail['index']))
            index_item.setFlags(index_item.flags() ^ 2)
            index_item.setBackground(QBrush(content_color))
            type_item = QTableWidgetItem(detail['type'])
            type_item.setFlags(type_item.flags() ^ 2)
            type_item.setBackground(QBrush(content_color))
            details_item = QTableWidgetItem(detail['details'])
            details_item.setFlags(details_item.flags() ^ 2)
            details_item.setBackground(QBrush(content_color))
            # region Set font color based on type
            blue_color_code = QColor()
            blue_color_code.setNamedColor('#1496FC')
            red_color_code = QColor()
            red_color_code.setNamedColor('#FF3127')
            green_color_code = QColor()
            green_color_code.setNamedColor('#27D127')
            if detail['type'] == 'added':
                index_item.setForeground(blue_color_code)
                type_item.setForeground(blue_color_code)
                details_item.setForeground(blue_color_code)
            elif detail['type'] == 'deleted':
                index_item.setForeground(red_color_code)
                type_item.setForeground(red_color_code)
                details_item.setForeground(red_color_code)
            elif detail['type'] == 'changed':
                index_item.setForeground(green_color_code)
                type_item.setForeground(green_color_code)
                details_item.setForeground(green_color_code)
            # endregion
            self.table.setItem(row_no, 0, index_item)
            self.table.setItem(row_no, 1, type_item)
            self.table.setItem(row_no, 2, details_item)
            row_no += 1

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        if not is_use_current_flow:
            default_width = max(self.table.horizontalHeader().length(),
                            orig_proj_path_label.sizeHint().width(),
                            chg_proj_path_label.sizeHint().width()) + 25
        else:
            default_width = max(self.table.horizontalHeader().length(),
                            orig_proj_path_label.sizeHint().width()) + 25

        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.resize(default_width, self.height())
        self.move_to_center()

    def move_to_center(self):
        frame_geo = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geo.moveCenter(screen_center)
        self.move(frame_geo.topLeft())

    @pyqtSlot(QTableWidgetItem)
    def on_item_double_clicked(self, item):
        if self.is_use_current_flow:
            row = item.row()
            type_col_index = self.column_labels.index('type')
            type_val = self.table.item(row, type_col_index).text()
            if type_val == 'added' or type_val == 'changed':
                index = row + 1
                item_id = None
                item_type = None
                for detail in self.details:
                    if detail['index'] == index:
                        item_id = detail['id']
                        item_type = detail['ao_or_edge']
                        break
                main_window = self.parent().findMain().widget()
                current_window = self.parent().getCurrentNodeEditorWidget()
                nodes_in_main = main_window.scene.nodes
                for node in nodes_in_main:
                    if node.op_code == OP_NODE_SUBPATCH:
                        self.parent().open_subwindow_in_subpatch_recursively(node.title)
                        self.parent().setActiveSubWindow(current_window.parent())
                target_graphic = None
                target_x_position = None
                target_y_position = None
                target_scene = None
                for window in self.parent().mdiArea.subWindowList():
                    if item_type == 'ao':
                        for node in window.widget().scene.nodes:
                            if node.id == item_id:
                                target_scene = window.widget().scene
                                target_graphic = node.grNode
                                target_x_position = node.grNode.x()
                                target_y_position = node.grNode.y()
                                self.parent().setActiveSubWindow(window)
                                if hasattr(window.widget(), 'close_if_no_problem'):
                                    del window.widget().close_if_no_problem
                    elif item_type == 'edge':
                        for edge in window.widget().scene.edges:
                            if edge.id == item_id:
                                target_scene = window.widget().scene
                                target_graphic = edge.grEdge
                                target_x_position = edge.grEdge.path().elementAt(0).x
                                target_y_position = edge.grEdge.path().elementAt(0).y
                                self.parent().setActiveSubWindow(window)
                                if hasattr(window.widget(), 'close_if_no_problem'):
                                    del window.widget().close_if_no_problem
                    if hasattr(window.widget(), 'encrypted') and window.widget().encrypted and not window.widget().already_input_password:
                        self.parent().close_sub_window(window)
                    if hasattr(window.widget(), 'close_if_no_problem') and window.widget().close_if_no_problem:
                        self.parent().close_sub_window(window)
                self.parent().getCurrentNodeEditorWidget().view.centerOn(target_x_position, target_y_position)
                self.parent().deselect_all_items()
                target_graphic.setSelected(True)
                target_scene.onItemSelected()

    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', '(*.xlsx)')
        if file_path:
            data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                data.append(row_data)

            df = pd.DataFrame(data, columns=self.column_labels)
            df.to_excel(file_path, index=False)
            QMessageBox.about(self.parent(),
                              'Export successfully',
                              'Export successfully.')

    def closeEvent(self, event):
        self.parent().signal_flow_diff_q_widget.show()


class UserInputPasswordDialog(QDialog):
    data_entered = pyqtSignal(dict)

    def __init__(self, orig_passwords=None, chg_passwords=None, parent=None):
        super(UserInputPasswordDialog, self).__init__(parent)
        self.orig_passwords = orig_passwords
        self.chg_passwords = chg_passwords
        self.orig_input_passwords = {}
        self.chg_input_passwords = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.orig_labels = []
        self.orig_password_edits = []
        if self.orig_passwords:
            label = QLabel('Original project:')
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold")
            layout.addWidget(label)
            for file_name, correct_password in self.orig_passwords.items():
                label = QLabel("Enter password for file '{}':".format(file_name))
                password_edit = QLineEdit()
                password_edit.setEchoMode(QLineEdit.Password)
                self.orig_labels.append(label)
                self.orig_password_edits.append(password_edit)
                layout.addWidget(label)
                layout.addWidget(password_edit)
        self.chg_labels = []
        self.chg_password_edits = []
        if self.chg_passwords:
            label = QLabel('Changed project:')
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold")
            layout.addWidget(label)
            for file_name, correct_password in self.chg_passwords.items():
                label = QLabel("Enter password for file '{}':".format(file_name))
                password_edit = QLineEdit()
                password_edit.setEchoMode(QLineEdit.Password)
                self.chg_labels.append(label)
                self.chg_password_edits.append(password_edit)
                layout.addWidget(label)
                layout.addWidget(password_edit)
        button_layout = QVBoxLayout()
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')
        self.ok_button.clicked.connect(self.handle_ok_btn_clicked)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle('Input Password')
        self.setFixedSize(self.sizeHint())

    def handle_ok_btn_clicked(self):
        if self.orig_passwords:
            for i, file_name in enumerate(self.orig_passwords.keys()):
                entered_password = self.orig_password_edits[i].text()
                self.orig_input_passwords[file_name] = entered_password
        if self.chg_passwords:
            for i, file_name in enumerate(self.chg_passwords.keys()):
                entered_password = self.chg_password_edits[i].text()
                self.chg_input_passwords[file_name] = entered_password
        self.data_entered.emit(self.orig_input_passwords)
        self.data_entered.emit(self.chg_input_passwords)
        # check passwords correct or not
        problem_orig_files = []
        problem_chg_files = []
        for file_name, correct_password in self.orig_passwords.items():
            if self.orig_input_passwords[file_name] != correct_password:
                problem_orig_files.append(file_name)
        for file_name, correct_password in self.chg_passwords.items():
            if self.chg_input_passwords[file_name] != correct_password:
                problem_chg_files.append(file_name)
        if problem_orig_files or problem_chg_files:
            reminder_dialog = IncorrectPasswordReminderDialog(problem_orig_files, problem_chg_files, self)
            res = reminder_dialog.get_response()
            if not res:
                self.orig_input_passwords = {}
                self.chg_input_passwords = {}
                return
        self.close()

    def get_user_input_data(self):
        self.exec_()
        return self.orig_input_passwords, self.chg_input_passwords


class IncorrectPasswordReminderDialog(QDialog):
    def __init__(self, problem_orig_files=None, problem_chg_files=None, parent=None):
        super(IncorrectPasswordReminderDialog, self).__init__(parent)
        self.problem_orig_files = problem_orig_files
        self.problem_chg_files = problem_chg_files
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel('Incorrect passwords entered for the following files:')
        layout.addWidget(label)
        if self.problem_orig_files:
            label = QLabel('original project:')
            layout.addWidget(label)
            for problem_orig_file in self.problem_orig_files:
                label = QLabel(problem_orig_file)
                label.setStyleSheet("font-weight: bold")
                layout.addWidget(label)
        if self.problem_chg_files:
            if self.problem_orig_files:
                label = QLabel('')
                layout.addWidget(label)
            label = QLabel('changed project:')
            layout.addWidget(label)
            for problem_chg_file in self.problem_chg_files:
                label = QLabel(problem_chg_file)
                label.setStyleSheet("font-weight: bold")
                layout.addWidget(label)
        label = QLabel('Would you like to proceed and compare signal flows?')
        layout.addWidget(label)
        button_layout = QVBoxLayout()
        self.ok_button = QPushButton('Yes')
        self.cancel_button = QPushButton('No')
        self.ok_button.clicked.connect(self.handle_ok_btn_clicked)
        self.cancel_button.clicked.connect(self.handle_cancel_btn_clicked)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle('Reminder')
        self.setFixedSize(self.sizeHint())

    def handle_ok_btn_clicked(self):
        self.res = True
        self.close()

    def handle_cancel_btn_clicked(self):
        self.res = False
        self.close()

    def get_response(self):
        self.exec_()
        return self.res


class CustomTextComboBox(QComboBox):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.text = text

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().window())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)

    def showPopup(self):
        super().showPopup()
        # In order to show the popup below the combobox
        popup = self.view().parentWidget()
        popup.move(self.mapToGlobal(QtCore.QPoint(0, self.height())))


class CustomItemDelegate(QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease:
            if index.flags() & Qt.ItemIsUserCheckable:
                rect = option.rect
                if rect.contains(event.pos()):
                    current_value = index.data(Qt.CheckStateRole)
                    new_value = Qt.Checked if current_value != Qt.Checked else Qt.Unchecked
                    model.setData(index, new_value, Qt.CheckStateRole)
                    return True
        return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        item = index.model().itemFromIndex(index)
        if item and item.checkState() == Qt.PartiallyChecked:
            option.state |= QStyle.State_NoChange
        super().paint(painter, option, index)


class EditListDialog(QWidget):
    def __init__(self, initial_list, param_index, parent=None, flow_window=None, parameters_table_widget=None):
        super().__init__(parent)
        self.flow_window = flow_window
        self.parameters_table_widget = parameters_table_widget
        self.setWindowTitle('Edit List')
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.setStyleSheet("background-color: #474747")
        self.setGeometry(100, 100, 300, 400)


        self.layout = QVBoxLayout(self)

        self.param_index = param_index

        self.list_widget = QListWidget(self)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setStyleSheet('QListWidget { background-color: #272927; }')
        self.list_widget.addItems(initial_list)
        self.list_widget.itemSelectionChanged.connect(self.handle_item_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.edit_item)
        self.list_widget.model().rowsMoved.connect(self.handle_change_item_order)
        self.layout.addWidget(self.list_widget)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton('Add Item')
        self.add_button.clicked.connect(self.add_item)
        self.button_layout.addWidget(self.add_button)
        self.delete_button = QPushButton('Delete Selected Item')
        self.delete_button.setStyleSheet('background: #302E2E')
        self.delete_button.setDisabled(True)
        self.delete_button.clicked.connect(self.delete_item)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

    def handle_item_selection_changed(self):
        if self.list_widget.selectedItems():
            self.delete_button.setDisabled(False)
            self.delete_button.setStyleSheet('')
        else:
            self.delete_button.setDisabled(True)
            self.delete_button.setStyleSheet('background: #302E2E')

    def add_item(self):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        item_text, ok = QInputDialog.getText(self, 'Add Item', 'Item:')
        if ok and item_text:
            if item_text in window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.param_index]['value']:
                QMessageBox.warning(self, 'This addition is not possible',
                                    f'This value is already in the list, so it cannot be added.')
            else:
                window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value'].append(item_text)
                val = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value']
                self.list_widget.addItem(item_text)
                combo_box = self.parameters_table_widget.table.cellWidget(self.parameters_table_widget.p_value_index, 1)
                current_index = combo_box.currentIndex()
                combo_box.addItem(item_text)
                combo_box.setCurrentIndex(current_index)
                if item_text not in window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['options']:
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['options'].append(
                        item_text)
                self.parameters_table_widget.handle_value_of_param_under_tuning_param_changed(val, self.param_index)


    def edit_item(self, item):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        item_row = self.list_widget.row(item)
        item_text, ok = QInputDialog.getText(self, 'Edit Item', 'Item:', QLineEdit.Normal, item.text())
        if ok and item_text:
            if item_text != item.text() and item_text in \
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.param_index]['value']:
                QMessageBox.warning(self, 'This edit is not possible',
                                    f'This value is already in the list, so it cannot be added.')
            else:
                old_text = item.text()
                item.setText(item_text)
                window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value'][item_row] = item_text
                combo_box = self.parameters_table_widget.table.cellWidget(self.parameters_table_widget.p_value_index, 1)
                index = combo_box.findText(old_text)
                val = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value']
                if old_text != item_text and index != -1:
                    combo_box.setCurrentIndex(-1)
                    combo_box.setItemText(index, item_text)
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index][
                        'options'][index] = item_text
                self.parameters_table_widget.handle_value_of_param_under_tuning_param_changed(val, self.param_index)

    def delete_item(self):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            combo_box = self.parameters_table_widget.table.cellWidget(self.parameters_table_widget.p_value_index, 1)
            current_combo_box_text = combo_box.currentText()
            for item in selected_items:
                item_text = item.text()
                window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value'].remove(item_text)
                val = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.param_index]['value']
                self.list_widget.takeItem(self.list_widget.row(item))
                index = combo_box.findText(item_text)
                if index != -1:
                    combo_box.removeItem(index)
                if current_combo_box_text in [item.text() for item in selected_items]:
                    combo_box.setCurrentIndex(-1)
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['value'] = -1
                else:
                    index_to_set = combo_box.findText(current_combo_box_text)
                    combo_box.setCurrentIndex(index_to_set)
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['value'] = index_to_set
                if item_text in window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['options']:
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index]['options'].remove(
                        item_text)
                self.parameters_table_widget.handle_value_of_param_under_tuning_param_changed(val, self.param_index)

    def handle_change_item_order(self, parent, start, end, destination, row):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        item = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'][self.param_index]['value'].pop(start)
        if row > start:
            row -= 1
        window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'][self.param_index]['value'].insert(row, item)
        combo_box = self.parameters_table_widget.table.cellWidget(self.parameters_table_widget.p_value_index, 1)
        current_combo_box_text = combo_box.currentText()
        combo_box.clear()
        items = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'][self.param_index]['value']
        combo_box.addItems(items)
        window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index][
            'options'] = items
        index_to_set = combo_box.findText(current_combo_box_text)
        combo_box.setCurrentIndex(index_to_set)
        window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            current_selected_tuning_param_index]['parameters'][self.parameters_table_widget.p_value_index][
            'value'] = index_to_set


class ParametersTableWidget(QWidget):
    def __init__(self, tuning_parameter_index, parent=None, flow_window=None):
        super().__init__(parent)
        self.flow_window = flow_window
        self.tuning_parameter_index = tuning_parameter_index
        self.non_deletable_row_indices = set()
        self.layout = QVBoxLayout()

        self.table = QTableWidget(0, 2)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        # self.table.setHorizontalHeaderLabels(["Key", "Value"])
        self.table.itemSelectionChanged.connect(self.handle_table_item_selection_changed)
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add param")
        self.add_button.clicked.connect(self.add_parameter)
        # self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete selected param")
        self.delete_button.setDisabled(True)
        self.delete_button.setStyleSheet('background: #302E2E')
        self.delete_button.clicked.connect(self.delete_selected_parameter)
        # self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def handle_table_item_selection_changed(self):
        selected_cells = self.table.selectedIndexes()
        if selected_cells:
            if selected_cells[0].row() in self.non_deletable_row_indices:
                self.delete_button.setDisabled(True)
                self.delete_button.setStyleSheet('background: #302E2E')
            else:
                self.delete_button.setDisabled(False)
                self.delete_button.setStyleSheet('')
        else:
            self.delete_button.setDisabled(True)
            self.delete_button.setStyleSheet('background: #302E2E')

    def add_parameter(self):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        while True:
            # Create a custom input dialog
            dialog = QtWidgets.QInputDialog(window)
            dialog.setWindowTitle("Input key name of parameter")
            dialog.setLabelText("Please enter a key name:")
            dialog.resize(450, dialog.sizeHint().height())

            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                name = dialog.textValue()
            else:
                return  # User canceled

            if not name:  # Name is empty
                QtWidgets.QMessageBox.warning(self, "Empty Name",
                                              "The key name cannot be empty. Please enter a valid key name.")
                continue

            # Check if the name already exists
            parameters = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['parameters']

            existing_names = []

            for parameter in parameters:
                existing_names.append(parameter['key'])

            if name in existing_names:
                QtWidgets.QMessageBox.warning(self, "Duplicate Key Name",
                                              "The key name already exists. Please use a different key name.")
                continue

            break  # Valid name entered
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        key_edit = QLineEdit(name)
        key_edit.textChanged.connect(
            lambda key_val, row=row_position: self.handle_key_of_param_under_tuning_param_changed(key_val, row))
        self.table.setCellWidget(row_position, 0, key_edit)
        value_edit = QLineEdit('New Value')
        value_edit.textChanged.connect(
            lambda value_val, row=row_position: self.handle_value_of_param_under_tuning_param_changed(value_val, row))
        self.table.setCellWidget(row_position, 1, value_edit)
        window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['parameters'].append({'key': name,
                                                                       'value': 'New Value',
                                                                       'required': False})
    def handle_key_of_param_under_tuning_param_changed(self, key_val, row):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        parameters = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['parameters']
        existing_names = []
        for parameter in parameters:
            existing_names.append(parameter['key'])
        if key_val in existing_names:
            # Show error message box
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error: Duplicate key name. The value will revert to the original.")
            msg_box.setWindowTitle("Duplicate Key Name Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            # Revert to the original value
            original_name = parameters[row]['key']
            # Get the corresponding QLineEdit widget and set it back to the original value
            line_edit = window.custom_ao_builder_ui.tuning_parameters_table.cellWidget(self.tuning_parameter_index, 2).table.cellWidget(row, 0)
            line_edit.blockSignals(True)
            line_edit.setText(original_name)
            line_edit.blockSignals(False)
        else:
            # Update the value
            window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                self.tuning_parameter_index]['parameters'][row]['key'] = key_val

    def handle_value_of_param_under_tuning_param_changed(self, value_val, row):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        param_key_name = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                  self.tuning_parameter_index]['parameters'][row]['key']
        parameters_under_tuning_parameter = \
            window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                self.tuning_parameter_index]['parameters']
        if param_key_name == 'pDecimalPrecision':
            original_num_decimal_places = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                    self.tuning_parameter_index]['parameters'][row]['value']
            if value_val < original_num_decimal_places:
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pValue':
                        original_p_value = parameter_under_tuning_parameter['value']
                rounded_value = round(original_p_value, value_val)
                lost_information = original_p_value - rounded_value
                if lost_information != 0:
                    reply = QMessageBox.question(self, "Confirm pValue Change",
                                                f'Original pValue is {original_p_value},\n'
                                                f'After changing the number of decimal places to {value_val},\n'
                                                    f'pValue will be rounded to {rounded_value}\n'
                                                f'This action will result in information loss.\nDo you want to proceed?',
                                                QMessageBox.Yes | QMessageBox.No,
                                                QMessageBox.No)
                    if reply == QMessageBox.No:
                        self.table.cellWidget(row, 1).setValue(original_num_decimal_places)
                        return
            for index, parameter_under_tuning_parameter in enumerate(parameters_under_tuning_parameter):
                if parameter_under_tuning_parameter['key'] == 'pValue':
                    p_value_index = index
            self.table.cellWidget(p_value_index, 1).setDecimals(value_val)
        window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['parameters'][row]['value'] = value_val
        gui_type_no = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['gui_type_no']
        current_selected_custom_ao = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = current_selected_custom_ao['ao_name']
        tuning_parameter_name = current_selected_custom_ao['tuning_parameters'][
            self.tuning_parameter_index]['name']
        if gui_type_no == ControlType.SWITCH.value:
            label_text = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'label_text':
                    label_text = parameter_under_tuning_parameter['value']
            p_value = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pValue':
                    p_value = parameter_under_tuning_parameter['value']
            additional_parameters = {}
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] != 'label_text' and parameter_under_tuning_parameter['key'] != 'pValue':
                    additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter['value']
            AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                label_text=label_text,
                initial_val=p_value,
                is_preview=True,
                additional_parameters=additional_parameters)
            if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_label_text(label_text)
                return
        elif gui_type_no == ControlType.LABEL.value:
            label_text = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'label_text':
                    label_text = parameter_under_tuning_parameter['value']
            additional_parameters = {}
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] != 'label_text':
                    additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter[
                        'value']
            AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                initial_val=label_text,
                additional_parameters=additional_parameters)
            if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                widget = window.preview_popup.gui_manager.widgetSet[tuning_parameter_name]
                widget.set_label_text(label_text)
                return
        elif gui_type_no == ControlType.MENU.value:
            label_text = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'label_text':
                    label_text = parameter_under_tuning_parameter['value']
            p_list = []
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pList':
                    p_list = parameter_under_tuning_parameter['value']
            p_value = -1
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pValue':
                    p_value = parameter_under_tuning_parameter['value']
            additional_parameters = {}
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if (parameter_under_tuning_parameter['key'] != 'label_text' and
                        parameter_under_tuning_parameter['key'] != 'pList' and
                        parameter_under_tuning_parameter['key'] != 'pValue'):
                    additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter[
                        'value']
            AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                label_text=label_text,
                items=p_list,
                current_selected_item=p_list[p_value] if p_value >= 0 else None,
                is_preview=True,
                additional_parameters=additional_parameters)
            if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_label_text(label_text)
                window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_combo_box_items(p_list)
                window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_combo_box_current_index(p_value)
                return
        elif gui_type_no == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value:
            label_text = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'label_text':
                    label_text = parameter_under_tuning_parameter['value']
            p_max = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pMax':
                    p_max = parameter_under_tuning_parameter['value']
            p_min = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pMin':
                    p_min = parameter_under_tuning_parameter['value']
            p_value = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pValue':
                    p_value = parameter_under_tuning_parameter['value']
            is_slider_needed = True
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'is_slider_needed':
                    is_slider_needed = True if parameter_under_tuning_parameter['value'] == 'Yes' else False
            p_decimal_precision = 0
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pDecimalPrecision':
                    p_decimal_precision = parameter_under_tuning_parameter['value']
            additional_parameters = {}
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if (parameter_under_tuning_parameter['key'] != 'label_text' and
                        parameter_under_tuning_parameter['key'] != 'pValue' and
                        parameter_under_tuning_parameter['key'] != 'pMax' and
                        parameter_under_tuning_parameter['key'] != 'pMin' and
                        parameter_under_tuning_parameter['key'] != 'is_slider_needed' and
                        parameter_under_tuning_parameter['key'] != 'pDecimalPrecision'):
                    additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter[
                        'value']
            AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                label_text=label_text,
                max_value=p_max,
                min_value=p_min,
                initial_value=p_value,
                is_slider_needed=is_slider_needed,
                num_decimal_places=p_decimal_precision,
                additional_parameters=additional_parameters,
                is_preview=True)
            if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                widget = window.preview_popup.gui_manager.widgetSet[tuning_parameter_name]
                widget.set_label_text(label_text)
                widget.set_spinbox_max_value(p_max)
                widget.set_spinbox_min_value(p_min)
                widget.set_num_decimal_places(p_decimal_precision)
                widget.widget_value = p_value
                return
        elif (gui_type_no == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value
              or gui_type_no == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value
              or gui_type_no == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value):
            label_text = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'label_text':
                    label_text = parameter_under_tuning_parameter['value']
            p_max = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pMax':
                    p_max = parameter_under_tuning_parameter['value']
            p_min = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pMin':
                    p_min = parameter_under_tuning_parameter['value']
            p_value = ''
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if parameter_under_tuning_parameter['key'] == 'pValue':
                    p_value = parameter_under_tuning_parameter['value']
            additional_parameters = {}
            for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                if (parameter_under_tuning_parameter['key'] != 'label_text' and
                        parameter_under_tuning_parameter['key'] != 'pValue' and
                        parameter_under_tuning_parameter['key'] != 'pMax' and
                        parameter_under_tuning_parameter['key'] != 'pMin'):
                    additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter[
                        'value']
            AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                label_text=label_text,
                max_value=p_max,
                min_value=p_min,
                initial_value=p_value,
                additional_parameters=additional_parameters,
                is_preview=True)
            if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                widget = window.preview_popup.gui_manager.widgetSet[tuning_parameter_name]
                widget.set_label_text(label_text)
                widget.set_spinbox_max_value(p_max)
                widget.set_spinbox_min_value(p_min)
                widget.widget_value = p_value
                return
        window.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()

    def delete_selected_parameter(self):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        selected_cells = self.table.selectedIndexes()
        if selected_cells:
            row = selected_cells[0].row()
            self.table.removeRow(row)
            window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                current_selected_tuning_param_index]['parameters'].pop(row)

    def load_parameters(self, parameters):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        self.table.setRowCount(0)
        for param in parameters:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            key_edit = QLineEdit(param['key'])
            if 'required' in param and param['required']:
                key_edit.setReadOnly(True)  # Make the key item not editable
            if 'description' in param:
                key_edit.setToolTip(param['description'])  # Set tooltip for the key item
            key_edit.textChanged.connect(
                lambda key_val, row=row_position: self.handle_key_of_param_under_tuning_param_changed(key_val, row))
            self.table.setCellWidget(row_position, 0, key_edit)
            if 'options' in param:
                combo_box = QComboBox()
                combo_box.addItems(param['options'])
                if 'type' in param:
                    if param['type'] == 'index':
                        if param['value'] >= 0:
                            combo_box.setCurrentText(param['options'][param['value']])
                        else:
                            combo_box.setCurrentIndex(-1)
                        if param['key'] == 'pValue':
                            self.p_value_index = row_position
                        combo_box.currentIndexChanged.connect(
                            lambda index, row=row_position, cb=combo_box: self.combo_box_value_changed(cb, index, row, param['key'], param['type']))
                else:
                    combo_box.setCurrentText(param['value'])  # Set the current value based on param['value']
                    combo_box.currentIndexChanged.connect(
                        lambda index, row=row_position, cb=combo_box, key=param['key']: self.combo_box_value_changed(cb, index, row, key))
                self.table.setCellWidget(row_position, 1, combo_box)
            else:
                if isinstance(param['value'], int):
                    spin_box = QSpinBox()
                    if 'minimum' in param:
                        spin_box.setRange(param['minimum'], 2147483647)
                    else:
                        spin_box.setRange(-2147483648, 2147483647)
                    spin_box.setValue(param['value'])
                    spin_box.valueChanged.connect(
                        lambda value_val, row=row_position: self.handle_value_of_param_under_tuning_param_changed(
                            value_val, row))
                    self.table.setCellWidget(row_position, 1, spin_box)
                elif isinstance(param['value'], float):
                    gui_type = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        self.tuning_parameter_index]['gui_type_no']
                    spin_box = QDoubleSpinBox()
                    if gui_type == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value and param['key'] == 'pValue':
                        parameters = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                            self.tuning_parameter_index]['parameters']
                        for parameter in parameters:
                            if parameter['key'] == 'pDecimalPrecision':
                                decimal_precision = parameter['value']
                                break
                        spin_box.setDecimals(decimal_precision)
                    spin_box.setRange(-2147483648.0, 2147483647.0)
                    spin_box.setValue(param['value'])
                    spin_box.valueChanged.connect(
                        lambda value_val, row=row_position: self.handle_value_of_param_under_tuning_param_changed(
                            value_val, row))
                    self.table.setCellWidget(row_position, 1, spin_box)
                elif isinstance(param['value'], list):
                    button = QPushButton('Edit List')
                    available_choices = \
                    window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                        self.tuning_parameter_index]['parameters'][row_position]['value']
                    button.clicked.connect(lambda checked, index=row_position: self.edit_list(available_choices, index))
                    self.table.setCellWidget(row_position, 1, button)
                else:
                    value_edit = QLineEdit(str(param['value']))
                    value_edit.textChanged.connect(
                        lambda value_val, row=row_position: self.handle_value_of_param_under_tuning_param_changed(
                            value_val,
                            row))
                    self.table.setCellWidget(row_position, 1, value_edit)
            if 'required' in param and param['required']:
                self.non_deletable_row_indices.add(row_position)

    def combo_box_value_changed(self, cb, index, row_position, param_key_name, param_type=None):
        window = self.flow_window
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        gui_type_no = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
            self.tuning_parameter_index]['gui_type_no']
        parameters_under_tuning_parameter = \
            window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                self.tuning_parameter_index]['parameters']
        current_selected_custom_ao = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = current_selected_custom_ao['ao_name']
        tuning_parameter_name = current_selected_custom_ao['tuning_parameters'][
            self.tuning_parameter_index]['name']
        if param_type == 'index':
            for param in window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                self.tuning_parameter_index]['parameters']:
                if param['key'] == param_key_name:
                    param['value'] = index
            if gui_type_no == ControlType.MENU.value:
                label_text = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'label_text':
                        label_text = parameter_under_tuning_parameter['value']
                p_list = []
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pList':
                        p_list = parameter_under_tuning_parameter['value']
                p_value = -1
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pValue':
                        p_value = parameter_under_tuning_parameter['value']
                additional_parameters = {}
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if (parameter_under_tuning_parameter['key'] != 'label_text' and
                            parameter_under_tuning_parameter['key'] != 'pList' and
                            parameter_under_tuning_parameter['key'] != 'pValue'):
                        additional_parameters[parameter_under_tuning_parameter['key']] = parameter_under_tuning_parameter[
                            'value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    items=p_list,
                    current_selected_item=p_list[p_value] if p_value >= 0 else None,
                    is_preview=True,
                    additional_parameters=additional_parameters)
                if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                    window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_label_text(label_text)
                    window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_combo_box_items(p_list)
                    window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].set_combo_box_current_index(p_value)
                    return
        elif param_type is None:
            for param in window.temp_custom_aos_in_builder[current_selected_custom_ao_index]['tuning_parameters'][
                self.tuning_parameter_index]['parameters']:
                if param['key'] == param_key_name:
                    param['value'] = cb.itemText(index)
            if gui_type_no == ControlType.SWITCH.value:
                label_text = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'label_text':
                        label_text = parameter_under_tuning_parameter['value']
                p_value = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pValue':
                        p_value = parameter_under_tuning_parameter['value']
                additional_parameters = {}
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] != 'label_text' and parameter_under_tuning_parameter[
                        'key'] != 'pValue':
                        additional_parameters[parameter_under_tuning_parameter['key']] = \
                        parameter_under_tuning_parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    initial_val=p_value,
                    is_preview=True,
                    additional_parameters=additional_parameters)
                if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                    window.preview_popup.gui_manager.widgetSet[tuning_parameter_name].widget_value = [p_value]
                    return
            elif gui_type_no == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value:
                label_text = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'label_text':
                        label_text = parameter_under_tuning_parameter['value']
                p_max = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pMax':
                        p_max = parameter_under_tuning_parameter['value']
                p_min = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pMin':
                        p_min = parameter_under_tuning_parameter['value']
                p_value = ''
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pValue':
                        p_value = parameter_under_tuning_parameter['value']
                is_slider_needed = True
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'is_slider_needed':
                        is_slider_needed = True if parameter_under_tuning_parameter['value'] == 'Yes' else False
                p_decimal_precision = 0
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if parameter_under_tuning_parameter['key'] == 'pDecimalPrecision':
                        p_decimal_precision = parameter_under_tuning_parameter['value']
                additional_parameters = {}
                for parameter_under_tuning_parameter in parameters_under_tuning_parameter:
                    if (parameter_under_tuning_parameter['key'] != 'label_text' and
                            parameter_under_tuning_parameter['key'] != 'pValue' and
                            parameter_under_tuning_parameter['key'] != 'pMax' and
                            parameter_under_tuning_parameter['key'] != 'pMin' and
                            parameter_under_tuning_parameter['key'] != 'is_slider_needed' and
                            parameter_under_tuning_parameter['key'] != 'pDecimalPrecision'):
                        additional_parameters[parameter_under_tuning_parameter['key']] = \
                        parameter_under_tuning_parameter[
                            'value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter_name] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    max_value=p_max,
                    min_value=p_min,
                    initial_value=p_value,
                    is_slider_needed=is_slider_needed,
                    num_decimal_places=p_decimal_precision,
                    additional_parameters=additional_parameters,
                    is_preview=True)
                if hasattr(window, 'preview_popup') and window.preview_popup.isVisible():
                    widget = window.preview_popup.gui_manager.widgetSet[tuning_parameter_name]
                    widget.set_label_text(label_text)
                    widget.set_spinbox_max_value(p_max)
                    widget.set_spinbox_min_value(p_min)
                    widget.set_num_decimal_places(p_decimal_precision)
                    widget.widget_value = p_value
                    return
        window.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()

    def edit_list(self, current_list, param_index):
        dialog = EditListDialog(current_list, param_index, self.flow_window.custom_ao_builder_dialog,
                                flow_window=self.flow_window,
                                parameters_table_widget = self)
        dialog.show()

    def change_tuning_parameter_index(self, tuning_parameter_index):
        self.tuning_parameter_index = tuning_parameter_index


class PreviewPopupGUI(FLOW_GUI):
    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        window = self.node.flow_window
        window.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
        if hasattr(window.preview_node, 'widget'):
            window.preview_popup = window.preview_node.widget


class CustomNode(FLOW_Node):
    def __init__(self, scene, name,
                 is_collapsible,
                 is_popup_allowed,
                 type_ao_addition=TypeAOAddition.FIXED.value,
                 num_input_sockets=0,
                 num_output_sockets=0,
                 num_in_ctrl_sockets=0,
                 num_out_ctrl_sockets=0,
                 flow_window=None):
        self.flow_window = flow_window
        input_list = []
        output_list = []
        in_ctrl_list = []
        out_ctrl_list = []
        for _ in range(num_input_sockets):
            input_list.append(1)
        for _ in range(num_output_sockets):
            output_list.append(1)
        for _ in range(num_in_ctrl_sockets):
            in_ctrl_list.append(0)
        for _ in range(num_out_ctrl_sockets):
            out_ctrl_list.append(0)
        self.op_title = name
        self.content_label_objname = name
        self.is_temp_node = True
        self.inputs = input_list
        self.outputs = output_list
        self.inctrls = in_ctrl_list
        self.outctrls = out_ctrl_list
        self.expandable = is_collapsible
        self.openable = is_popup_allowed
        self.type_ao_addition = type_ao_addition
        super(CustomNode, self).__init__(scene, inputs=input_list, outputs=output_list, inctrls=in_ctrl_list,
                                         outctrls=out_ctrl_list)

    def initSettings(self):
        super().initSettings()
        self.outctrl_socket_position = RIGHT_BOTTOM

    def initInnerClasses(self):
        super().initInnerClasses()
        if self.openable:
            if hasattr(self.flow_window, 'preview_popup') and self.flow_window.preview_popup.isVisible():
                self.widget = self.flow_window.preview_popup
            else:
                self.widget = PreviewPopupGUI(self)
            if not hasattr(self.flow_window, 'preview_popup') or (
                    hasattr(self.flow_window, 'preview_popup') and not self.flow_window.preview_popup.isVisible()):
                self.flow_window.preview_popup = self.widget

    def onDoubleClicked(self, event):
        is_collapsible = self.expandable
        if not hasattr(self.flow_window, 'is_this_preview_node_to_be_processed') or (
                hasattr(self.flow_window, 'is_this_preview_node_to_be_processed') and not self.flow_window.is_this_preview_node_to_be_processed):
            self.flow_window.is_this_preview_node_to_be_processed = True
            if hasattr(self.flow_window, 'preview_popup') and self.flow_window.preview_popup.isVisible():
                self.flow_window.preview_popup.close()
                self.flow_window.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
            else:
                self.flow_window.custom_ao_builder_ui.preview_widget.load_custom_ao_settings()
                if is_collapsible:
                    if not self.expand:
                        self.flow_window.preview_node.collapseNode()
                self.flow_window.preview_node.onDoubleClicked(None)
        else:
            super().onDoubleClicked(event)
            self.flow_window.is_this_preview_node_to_be_processed = False


class PreviewWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent=None, flow_window=None):
        super(PreviewWidget, self).__init__(parent)
        self.flow_window = flow_window
        self.flow_scene = FLOW_Scene(is_draw_nothing=True, is_temp=True)
        self.setScene(self.flow_scene.grScene)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the border
        self.setStyleSheet('background: transparent;')  # Set the background to transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Set the scroll bar policy to display only when the content overflows
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def clear(self):
        self.scene().clear()

    def load_custom_ao_settings(self):
        window = self.flow_window
        if hasattr(window, 'trigger_from_preview') and window.trigger_from_preview:
            return
        self.scene().clear()
        current_selected_custom_ao_index = window.get_current_selected_custom_ao_index()
        current_selected_custom_ao = window.temp_custom_aos_in_builder[current_selected_custom_ao_index]
        ao_name = current_selected_custom_ao['ao_name']
        is_collapsible = current_selected_custom_ao['collapsible']
        is_popup_allowed = current_selected_custom_ao['is_popup_allowed']
        if ao_name not in AUDIO_OBJECT_TEMP:
            AUDIO_OBJECT_TEMP[ao_name] = OrderedDict()
        for tuning_parameter in current_selected_custom_ao['tuning_parameters']:
            gui_type_no = tuning_parameter['gui_type_no']
            parameters = tuning_parameter['parameters']
            if gui_type_no == ControlType.SWITCH.value:
                label_text = ''
                for parameter in parameters:
                    if parameter['key'] == 'label_text':
                        label_text = parameter['value']
                p_value = ''
                for parameter in parameters:
                    if parameter['key'] == 'pValue':
                        p_value = parameter['value']
                additional_parameters = {}
                for parameter in parameters:
                    if parameter['key'] != 'label_text' and parameter['key'] != 'pValue':
                        additional_parameters[parameter['key']] = parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter['name']] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    initial_val=p_value,
                    is_preview=True,
                    additional_parameters=additional_parameters)
            elif gui_type_no == ControlType.LABEL.value:
                label_text = ''
                for parameter in parameters:
                    if parameter['key'] == 'label_text':
                        label_text = parameter['value']
                additional_parameters = {}
                for parameter in parameters:
                    if parameter['key'] != 'label_text':
                        additional_parameters[parameter['key']] = parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter['name']] = CONTROLS_MAPPING[gui_type_no](
                    initial_val=label_text,
                    additional_parameters=additional_parameters)
            elif gui_type_no == ControlType.MENU.value:
                label_text = ''
                for parameter in parameters:
                    if parameter['key'] == 'label_text':
                        label_text = parameter['value']
                p_list = []
                for parameter in parameters:
                    if parameter['key'] == 'pList':
                        p_list = parameter['value']
                p_value = -1
                for parameter in parameters:
                    if parameter['key'] == 'pValue':
                        p_value = parameter['value']
                additional_parameters = {}
                for parameter in parameters:
                    if (parameter['key'] != 'label_text' and
                            parameter['key'] != 'pList' and
                            parameter['key'] != 'pValue'):
                        additional_parameters[parameter['key']] = parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter['name']] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    items=p_list,
                    current_selected_item=p_list[p_value] if p_value >= 0 else None,
                    is_preview=True,
                    additional_parameters=additional_parameters)
            elif gui_type_no == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value:
                label_text = ''
                for parameter in parameters:
                    if parameter['key'] == 'label_text':
                        label_text = parameter['value']
                p_max = ''
                for parameter in parameters:
                    if parameter['key'] == 'pMax':
                        p_max = parameter['value']
                p_min = ''
                for parameter in parameters:
                    if parameter['key'] == 'pMin':
                        p_min = parameter['value']
                p_value = ''
                for parameter in parameters:
                    if parameter['key'] == 'pValue':
                        p_value = parameter['value']
                is_slider_needed = True
                for parameter in parameters:
                    if parameter['key'] == 'is_slider_needed':
                        is_slider_needed = True if parameter['value'] == 'Yes' else False
                p_decimal_precision = ''
                for parameter in parameters:
                    if parameter['key'] == 'pDecimalPrecision':
                        p_decimal_precision = parameter['value']
                additional_parameters = {}
                for parameter in parameters:
                    if (parameter['key'] != 'label_text' and
                            parameter['key'] != 'pValue' and
                            parameter['key'] != 'pMax' and
                            parameter['key'] != 'pMin' and
                            parameter['key'] != 'is_slider_needed' and
                            parameter['key'] != 'pDecimalPrecision'):
                        additional_parameters[parameter['key']] = parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter['name']] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    max_value=p_max,
                    min_value=p_min,
                    initial_value=p_value,
                    is_slider_needed=is_slider_needed,
                    num_decimal_places=p_decimal_precision,
                    additional_parameters=additional_parameters,
                    is_preview=True)
            elif (gui_type_no == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value
                    or gui_type_no == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value
                    or gui_type_no == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value):
                label_text = ''
                for parameter in parameters:
                    if parameter['key'] == 'label_text':
                        label_text = parameter['value']
                p_max = ''
                for parameter in parameters:
                    if parameter['key'] == 'pMax':
                        p_max = parameter['value']
                p_min = ''
                for parameter in parameters:
                    if parameter['key'] == 'pMin':
                        p_min = parameter['value']
                p_value = ''
                for parameter in parameters:
                    if parameter['key'] == 'pValue':
                        p_value = parameter['value']
                additional_parameters = {}
                for parameter in parameters:
                    if (parameter['key'] != 'label_text' and
                            parameter['key'] != 'pValue' and
                            parameter['key'] != 'pMax' and
                            parameter['key'] != 'pMin'):
                        additional_parameters[parameter['key']] = parameter['value']
                AUDIO_OBJECT_TEMP[ao_name][tuning_parameter['name']] = CONTROLS_MAPPING[gui_type_no](
                    label_text=label_text,
                    max_value=p_max,
                    min_value=p_min,
                    initial_value=p_value,
                    additional_parameters=additional_parameters,
                    is_preview=True)
        type_ao_addition = current_selected_custom_ao['type_ao_addition']
        if type_ao_addition == TypeAOAddition.FIXED.value:
            num_input_sockets = current_selected_custom_ao['num_input_sockets']
            num_output_sockets = current_selected_custom_ao['num_output_sockets']
            num_in_ctrl_sockets = current_selected_custom_ao['num_inctrl_sockets']
            num_out_ctrl_sockets = current_selected_custom_ao['num_outctrl_sockets']
            window.preview_node = CustomNode(self.flow_scene, ao_name,
                                             is_collapsible,
                                             is_popup_allowed,
                                             num_input_sockets=num_input_sockets,
                                             num_output_sockets=num_output_sockets,
                                             num_in_ctrl_sockets=num_in_ctrl_sockets,
                                             num_out_ctrl_sockets=num_out_ctrl_sockets,
                                             flow_window=window)
        elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_CHANNELS.value:
            window.preview_node = CustomNode(self.flow_scene, ao_name,
                                             is_collapsible,
                                             is_popup_allowed,
                                             type_ao_addition=type_ao_addition,
                                             num_input_sockets=1,
                                             num_output_sockets=1,
                                             flow_window=window)
        elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value:
            window.preview_node = CustomNode(self.flow_scene, ao_name,
                                             is_collapsible,
                                             is_popup_allowed,
                                             type_ao_addition=type_ao_addition,
                                             num_input_sockets=1,
                                             num_output_sockets=1,
                                             flow_window=window)
        else:
            window.preview_node = CustomNode(self.flow_scene, ao_name, is_collapsible,
                                             is_popup_allowed,
                                             type_ao_addition=type_ao_addition,
                                             flow_window=window)
        window.preview_node.grNode.setPos(-90, -80)
        window.preview_node.grNode.setFlag(QGraphicsItem.ItemIsMovable, False)
        window.preview_node.grNode.setFlag(QGraphicsItem.ItemIsSelectable, False)
        window.preview_node.grNode.setAcceptHoverEvents(False)
        self.flow_scene.scene_width = window.preview_node.grNode.width + 110
        self.flow_scene.scene_height = window.preview_node.grNode.height + 100
        self.flow_scene.grScene.setGrScene(self.flow_scene.scene_width, self.flow_scene.scene_height)
        self.updateSceneRect(window.preview_node)
        current_selected_tuning_param_index = window.get_current_selected_tuning_param_index()
        if current_selected_tuning_param_index != -1:
            current_selected_tuning_param_name = window.custom_ao_builder_ui.tuning_parameters_table.cellWidget(
                current_selected_tuning_param_index, 0).text()
            for param_name, widget in window.preview_node.manager.widgetSet.items():
                if param_name == current_selected_tuning_param_name:
                    widget.trigger_preview_click_logic()
                    break

    def updateSceneRect(self, node):
        # Get the position and size of the node
        node_rect = node.grNode.sceneBoundingRect()

        # Extend the scene boundary to include the node
        current_scene_rect = self.scene().sceneRect()
        updated_scene_rect = current_scene_rect.united(node_rect)

        # Set the new scene boundary
        self.scene().setSceneRect(updated_scene_rect)


class CustomAOBuilderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def closeEvent(self, event):
        if not self.parent().is_ok_btn_clicked_in_custom_ao_builder:
            if not self.parent().is_same_between_changes_and_original_state_in_custom_ao_builder():
                reply = QMessageBox.question(self,
                                             'Discard Changes',
                                             'Do you want to discard the changes?',
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.parent().temp_custom_aos_in_builder = copy.deepcopy(self.parent().custom_aos_in_builder)
                else:
                    # If user clicks No, prevent dialog from closing
                    event.ignore()
                    return
        if hasattr(self.parent(), 'preview_popup') and self.parent().preview_popup.isVisible():
            self.parent().preview_popup.close()
        if hasattr(self.parent(), 'preview_popup'):
            del self.parent().preview_popup
        AUDIO_OBJECT_TEMP.clear()
        super().closeEvent(event)


class CodeTemplateGenerationThread(QThread):
    status_update = pyqtSignal(str, str)

    def __init__(self, current_custom_aos_setting, dir_path, parent=None):
        super().__init__(parent)
        self.current_custom_aos_setting = current_custom_aos_setting
        self.dir_path = dir_path

    def run(self):
        self.status_update.emit('Generating code templates...', 'white')
        # template_dir_path = '../project/AppOA/MAIN'
        # template_c_file = '../OA_template/Template_bak.c'
        # template_h_file = '../OA_template/Template_bak.h'
        # template_aoc_c_file = '../project/AppOA/AOCreationListCustom.c'
        # template_aoc_h_file = '../project/AppOA/AOCreationListCustom.h'

        # variable of copy revised .c and .h to new file
        exclude_block = False
        cur_start = False  # record start pivot

        template_dir_path = os.path.join(self.dir_path, 'project', 'AppOA', 'MAIN')
        template_c_file = '../OA_template/Template_bak.c'
        template_h_file = '../OA_template/Template_bak.h'
        template_aoc_c_file = os.path.join(self.dir_path, 'project', 'AppOA', 'AOCreationListCustom.c')
        template_aoc_h_file = os.path.join(self.dir_path, 'project', 'AppOA', 'AOCreationListCustom.h')
        project_CMake_txt = os.path.join(self.dir_path, 'project', 'AppOA', 'CMakeLists.txt')
        if os.path.exists(template_aoc_c_file):
            os.remove(template_aoc_c_file)
        if os.path.exists(template_aoc_h_file):
            os.remove(template_aoc_h_file)

        # dict_custome_aos_setting = cur_aos[0]
        # Copy Project to AppOA/project Folder
        OA_dest_dir = os.path.join(self.dir_path, 'project')

        copy_tree("../OA_template/project/", OA_dest_dir)
        shutil.copy2("../OA_template/project/CMakeLists.txt", OA_dest_dir)

        # shutil.copy2('../OA_template/AOCreationListCustom_bak.c', '../project/AppOA/AOCreationListCustom.c')
        # shutil.copy2('../OA_template/AOCreationListCustom_bak.h', '../project/AppOA/AOCreationListCustom.h')
        shutil.copy2('../OA_template/AOCreationListCustom_bak.c', template_aoc_c_file)
        shutil.copy2('../OA_template/AOCreationListCustom_bak.h', template_aoc_h_file)

        # search all .c file and put in delete list
        files_to_delete = []
        for root, dirs, files in os.walk(template_dir_path):
            for file in files:
                if file.startswith("C"):  # check file name is  CXXX
                    files_to_delete.append(file)

        ### Filter CTemplate files and remove it from CMakeList ###
        f = open(project_CMake_txt, 'r', encoding='utf-8')
        # Read CMakeLists.txt by line
        cmake_content = f.readlines()
        f.close()

        # Filter "Main/CTemplate.c" and "Main/CTemplate.h" line and remove it
        cmake_content = [line for line in cmake_content if
                         "Main/CTemplate.c" not in line and "Main/CTemplate.h" not in line]

        # Write back to CMakeLists.txt
        with open(project_CMake_txt, 'w', encoding='utf-8') as f:
            f.writelines(cmake_content)

        num_AOs = len(self.current_custom_aos_setting)
        for ao_input in range(num_AOs):
            dict_custome_aos_setting = self.current_custom_aos_setting[ao_input]
            # print(dict_custome_aos_setting)
            ao_name = dict_custome_aos_setting['ao_name']
            display_name = dict_custome_aos_setting['display_name']
            tuning_param = dict_custome_aos_setting['tuning_parameters']
            num_input_sockets = dict_custome_aos_setting['num_input_sockets']
            num_output_sockets = dict_custome_aos_setting['num_output_sockets']
            already_OA_files_exist = 0
            tuning_param_num = len(tuning_param)
            menu_idx_of_param = []    #reset index of menu type in parameters in every AO

            # remove special character and blank space, then concat string
            characters = "-_*&#$^%@'\/(){}""!?"
            for x in range(len(characters)):
                ao_name = ao_name.replace(characters[x], "")

            ao_name = ''.join(ao_name.split())

            characters = "-*&#^%$@'\/(){}""!?"
            for i in range(tuning_param_num):
                for x in range(len(characters)):
                    tuning_param[i]["name"] = tuning_param[i]["name"].replace(characters[x], "")
                tuning_param[i]["name"] = ''.join(tuning_param[i]["name"].split())

            #  1. remove exist same anme file 2. copy file
            # template_dir_path = '../project/AppOA/MAIN'
            # template_c_file = '../OA_template/Template_bak.c'
            # template_h_file = '../OA_template/Template_bak.h'
            # template_aoc_c_file = '../project/AppOA/AOCreationListCustom.c'
            # template_aoc_h_file = '../project/AppOA/AOCreationListCustom.h'
            ao_c_filename = 'C' + ao_name + '.c'
            ao_h_filename = 'C' + ao_name + '.h'
            cur_c_filepath = os.path.join(template_dir_path, ao_c_filename)
            cur_h_filepath = os.path.join(template_dir_path, ao_h_filename)
            #  declare changed AO temp file name from exist AO file
            user_ao_c_filename = 'UserTemplate_C' + ao_name + '.c'
            user_ao_h_filename = 'UserTemplate_C' + ao_name + '.h'
            user_template_c_file = os.path.join('../OA_template/', user_ao_c_filename) #'../OA_template/User_Template_bak.c'
            user_template_h_file = os.path.join('../OA_template/', user_ao_h_filename) #'../OA_template/User_Template_bak.h'

            # Add AO name to CMAKE List
            f = open(project_CMake_txt, 'r', encoding='utf-8')
            # 读取 CMakeLists.txt 的内容
            cmake_content = f.readlines()
            f.close()
            for i, line in enumerate(cmake_content):
                if line.strip() == 'set(CUSTOM_FILES':
                    # 在下一行插入文件
                    cmake_content.insert(i + 1, '"' + "MAIN/" + ao_c_filename + '"' + '\n')
                    cmake_content.insert(i + 1, '"' + "MAIN/" + ao_h_filename + '"' + '\n')
                    break
            f = open(project_CMake_txt, 'w+', encoding='utf-8')
            # 将更新后的内容写回到 CMakeLists.txt
            f.writelines(cmake_content)
            f.close()

            if os.path.exists(cur_c_filepath):
                # os.remove(cur_c_filepath)
                # remove current file name from delete list
                files_to_delete.remove(ao_c_filename)
                already_OA_files_exist = 1
            if os.path.exists(cur_h_filepath):
                # os.remove(cur_h_filepath)
                # remove current file name from delete list
                files_to_delete.remove(ao_h_filename)
                already_OA_files_exist = 1

            # copy CXXX.c and .h file to template user c file except Auto Gen code section
            if already_OA_files_exist == 1:
                f = open(cur_c_filepath, 'r')
                all_lines = f.readlines()
                f.close()
                f = open(user_template_c_file, 'w+')
                for everyline in all_lines:
                    CStatic_loc = everyline.find('declare param')
                    CParam_loc = everyline.find('construct params')
                    CRegister_loc = everyline.find('register the')
                    CDelete_loc = everyline.find('free param')
                    EndInit = everyline.find("END: AUTO GEN INIT")
                    EndNew = everyline.find("END: AUTO GEN NEW")
                    EndReg = everyline.find("END: AUTO GEN REGISTER")
                    EndFree = everyline.find("END: AUTO GEN FREE")
                    if CStatic_loc > -1 or CParam_loc > -1 or CRegister_loc > -1 or CDelete_loc > -1:
                        exclude_block = True
                        cur_start = True
                        f.writelines(everyline)
                    elif EndInit > -1 or EndNew > -1 or EndReg > -1 or EndFree > -1:
                        exclude_block = False
                        f.writelines(everyline)

                    if exclude_block == False and cur_start == False:
                        f.writelines(everyline)
                    if exclude_block == False:
                        cur_start = False

                f.close()

            if already_OA_files_exist == 1:
                f = open(cur_h_filepath, 'r')
                all_lines = f.readlines()
                f.close()
                f = open(user_template_h_file, 'w+')
                for everyline in all_lines:
                    CParam_loc = everyline.find('example, CParam*')
                    CEnum_loc = everyline.find('declare enum')
                    EndEnum = everyline.find("END: AUTO GEN DECLARE ENUM")
                    EndParam = everyline.find("END: AUTO GEN DECLARE PARAM")
                    if CEnum_loc > -1 or CParam_loc > -1:
                        exclude_block = True
                        cur_start = True
                        f.writelines(everyline)
                    elif EndEnum > -1 or EndParam > -1:
                        exclude_block = False
                        f.writelines(everyline)

                    if exclude_block == False and cur_start == False:
                        f.writelines(everyline)
                    if exclude_block == False:
                        cur_start = False

                f.close()

            # first time gen AO files, copy from template backup file. If not, copy from template User AO file
            if already_OA_files_exist == 0:
                shutil.copy2(template_c_file, cur_c_filepath)
                shutil.copy2(template_h_file, cur_h_filepath)
            elif already_OA_files_exist == 1:
                shutil.copy2(user_template_c_file, cur_c_filepath)
                shutil.copy2(user_template_h_file, cur_h_filepath)

            # replace AO name to template.c
            # f = open ("../docs/template/Template.c", 'r')
            f = open(cur_c_filepath, 'r')
            all_lines = f.readlines()
            f.close()
            # f = open ("../docs/template/Template.c", 'w+')
            f = open(cur_c_filepath, 'w+')
            for everyline in all_lines:
                x = re.sub('AOTemplate', ao_name, everyline)

                f.writelines(x)
                CStatic_loc = everyline.find('declare param')
                CParam_loc = everyline.find('construct params')
                CRegister_loc = everyline.find('register the')
                CDelete_loc = everyline.find('free param')

                # [WR] edit parameter info for initialization
                if (CStatic_loc > -1):
                    for i in range(tuning_param_num):
                        if tuning_param[i]["gui_type_no"] == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value or \
                                tuning_param[i][
                                    "gui_type_no"] == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value:
                            parameter_type = "kFloat"
                            step_val = "0.1"
                        if tuning_param[i]["gui_type_no"] == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value or \
                                tuning_param[i]["gui_type_no"] == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value or \
                                tuning_param[i]["gui_type_no"] == ControlType.MENU.value:
                            parameter_type = "kInt"
                            step_val = "1.0"
                            if tuning_param[i]["gui_type_no"] == ControlType.MENU.value:
                                menu_idx_of_param.append(i)
                        if tuning_param[i]["gui_type_no"] == ControlType.SWITCH.value:
                            parameter_type = "kBool"
                            step_val = "1.0"
                        inner_param_num = len(tuning_param[i]["parameters"])
                        for j in range(inner_param_num):
                            if tuning_param[i]["gui_type_no"] == ControlType.SWITCH.value:
                                if tuning_param[i]["parameters"][j]['key'] == "label_text":
                                    param_name = tuning_param[i]["name"]
                                elif tuning_param[i]["parameters"][j]['key'] == "pValue":
                                    if tuning_param[i]["parameters"][j]['value'] == "on":
                                        param_default = float(1)
                                    elif tuning_param[i]["parameters"][j]['value'] == "off":
                                        param_default = float(0)
                                param_max = float(1)
                                param_min = float(0)
                            elif tuning_param[i]["gui_type_no"] == ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value or \
                                    tuning_param[i][
                                        "gui_type_no"] == ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value or \
                                    tuning_param[i][
                                        "gui_type_no"] == ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value or \
                                    tuning_param[i][
                                        "gui_type_no"] == ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value:
                                if tuning_param[i]["parameters"][j]['key'] == "label_text":
                                    param_name = tuning_param[i]["name"]
                                elif tuning_param[i]["parameters"][j]['key'] == "pMax":
                                    param_max = float(tuning_param[i]["parameters"][j]['value'])
                                elif tuning_param[i]["parameters"][j]['key'] == "pMin":
                                    param_min = float(tuning_param[i]["parameters"][j]['value'])
                                elif tuning_param[i]["parameters"][j]['key'] == "pValue":
                                    param_default = float(tuning_param[i]["parameters"][j]['value'])
                            elif tuning_param[i]["gui_type_no"] == ControlType.MENU.value:
                                if tuning_param[i]["parameters"][j]['key'] == "label_text":
                                    param_name = tuning_param[i]["name"]
                                if tuning_param[i]["parameters"][j]['key'] == "pValue":
                                    def_item = tuning_param[i]["parameters"][j]['value']
                                    len_item = len(tuning_param[i]["parameters"][j]['options'])
                                    # remove special char in menu name
                                    for yy in range(len_item):
                                        temp_menu_name = tuning_param[i]["parameters"][j-1]['value'][yy]
                                        for x in range(len(characters)):
                                            temp_menu_name = temp_menu_name.replace(characters[x], "")
                                        tuning_param[i]["parameters"][j]['options'][yy] = ''.join(temp_menu_name.split())

                                    param_default = tuning_param[i]["parameters"][j]['options'][def_item]
                                    param_max = tuning_param[i]["parameters"][j]['options'][len_item-1]
                                    param_min = tuning_param[i]["parameters"][j]['options'][0]

                        if tuning_param[i]["gui_type_no"] == ControlType.MENU.value:
                            f.writelines(
                            "const ParamInfo _s" + tuning_param[i]["name"] + "  = { \"" + param_name + "\", (float)k" + str(
                                param_min) + ", (float)k" + str(param_max) + ", (float)k" + str(
                                param_default) + ", " + parameter_type + ", " + step_val + "f };\n")
                        else:
                            f.writelines(
                                "const ParamInfo _s" + tuning_param[i]["name"] + "  = { \"" + param_name + "\", " + str(
                                    param_min) + "f, " + str(param_max) + "f, " + str(
                                    param_default) + "f, " + parameter_type + ", " + step_val + "f };\n")
                        len_menu_param = len(menu_idx_of_param)

                # [WR] edit new parameter in CXXX_New()
                if (CParam_loc > -1):
                    for i in range(tuning_param_num):
                        f.writelines("\tme->_p" + tuning_param[i]["name"] + " = New(CParam, me, &_s" + tuning_param[i][
                            "name"] + ", numInChannels, numOutChannels);\n")
                        f.writelines(
                            "\tme->cao_base->AddParam(me->cao_base, me->_p" + tuning_param[i]["name"] + ");\n\n")

                # [WR] edit register handler in CXXX_New()
                if (CRegister_loc > -1):
                    for i in range(tuning_param_num):
                        f.writelines(
                            "\tme->_p" + tuning_param[i]["name"] + "->BindParamChangeHandler(me->_p" + tuning_param[i][
                                "name"] + ", C" + ao_name + "_" + ao_name + "ChangeHandler);\n")

                # [WR] edit free parameter memory in CXXX_Delete()
                if (CDelete_loc > -1):
                    for i in range(tuning_param_num):
                        f.writelines("\tDelete(CParam, obj->_p" + tuning_param[i]["name"] + ");\n")
            f.close()

            # replace AO name to template.h
            # f = open ("../docs/template/Template.h", 'r')
            f = open(cur_h_filepath, 'r')
            all_lines = f.readlines()
            f.close()
            # f = open ("../docs/template/Template.h", 'w+')
            f = open(cur_h_filepath, 'w+')
            for everyline in all_lines:
                x = re.sub('AOTemplate', ao_name, everyline)
                # print("l: ",everyline)
                CParam_loc = everyline.find('example, CParam*')
                CEnum_loc = everyline.find('declare enum')

                f.writelines(x)
                # [WR] edit declare parameter in struct _CXXX()
                if (CParam_loc > -1):
                    # print("l: ",everyline)
                    for i in range(tuning_param_num):
                        f.writelines("\tCParam* _p" + tuning_param[i]["name"] + ";\n")
                # [WR] edit new parameter in CXXX_New()
                if (CEnum_loc > -1):
                    for i in range(tuning_param_num):
                        for j in range(len_menu_param):
                            if menu_idx_of_param[j] == i:
                                len_item_param = len(tuning_param[i]["parameters"][2]['options'])
                                f.writelines("typedef enum e" + tuning_param[i]["name"] + "{\n")
                                for k in range(len_item_param):
                                    f.writelines("\tk" + tuning_param[i]["parameters"][2]['options'][k] + ",\n")

                                f.writelines("}e" + tuning_param[i]["name"] + ";\n\n")
            f.close()

            # replace AO name to AOCreationList.c
            f = open(template_aoc_c_file, 'r')
            all_lines = f.readlines()
            f.close()
            f = open(template_aoc_c_file, 'w+')
            for everyline in all_lines:
                CAOC_loc = everyline.find('Win32 OA')
                CAOC_h_loc = everyline.find("CustomerAO header")
                f.writelines(everyline)
                if (CAOC_loc > -1):
                    f.writelines(
                        "	{ \"" + ao_name + "\",				" + ao_name + "Creator_CreateAudioObject,	" + ao_name + "Creator_parseParam,  " + str(
                            num_input_sockets) + ", " + str(num_output_sockets) + ", NULL },\n")
                if (CAOC_h_loc > -1):
                    f.writelines("#include \"Main/C" + ao_name + ".h\"\n")
            f.close()

            # replace AO name to AOCreationList.h
            f = open(template_aoc_h_file, 'r')
            all_lines = f.readlines()
            f.close()
            f = open(template_aoc_h_file, 'w+')
            for everyline in all_lines:
                CAOC_loc = everyline.find('#define NUM_OF_FLOW_CUSTOM_AOS')
                # f.writelines(everyline)
                if (CAOC_loc > -1):
                    f.writelines("#define NUM_OF_FLOW_CUSTOM_AOS	" + str(num_AOs) + "\n");
                else:
                    f.writelines(everyline)
            f.close()

        # remove NOT current AO files
        for root, dirs, files in os.walk(template_dir_path):
            for file in files:
                if file in files_to_delete:  # check file in delete list
                    file_path = os.path.join(template_dir_path, file)  # get full file path
                    os.remove(file_path)  # remove unused files


        self.status_update.emit('Code templates generated successfully.', '#2ecc71')
        cmake_command = [
            "cmake",
            "-S", ".",  # Source directory
            "-B", "build",  # Build directory
            "-G", "Visual Studio 17 2022",
            "-A", "x64",
        ]
        self.status_update.emit('Generating Visual Studio solution...', 'white')
        # 使用 subprocess.Popen 啟動 CMake
        try:
            cmake_process = subprocess.Popen(cmake_command, cwd=OA_dest_dir, stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self.status_update.emit('Error: Visual Studio solution generation failed because CMake executable not found. Please install CMake and try again.', '#e37b7b')
            return
        # 等待 CMake 完成
        cmake_process.communicate()
        self.status_update.emit('Visual Studio solution generated successfully.', '#2ecc71')

        # # 確認解決方案文件的路徑
        # solution_path = os.path.abspath("../project/AppOA.sln")
        #
        # # 使用 msbuild 構建解決方案
        # try:
        #     result = subprocess.Popen(
        #         ["C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/Common7/IDE/devenv.exe", solution_path])
        # except FileNotFoundError:
        #     print("Warning: Visual Studio executable not found. Ignoring the error and continuing.")
        #
        # try:
        #     result = subprocess.Popen(
        #         ["C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional/Common7/IDE/devenv.exe", solution_path])
        # except FileNotFoundError:
        #     print("Warning: Visual Studio executable not found. Ignoring the error and continuing.")
        #
        # print(result.returncode)


class CustomAboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About Flow Studio {VERSION}")
        self.setFixedSize(800, 450)

        # Load background image
        self.background = QPixmap("../resources/about.png")

        # Create label with text
        self.label = QLabel(
            f"<span style='font-size: 14pt;'>v{VERSION}</span><br><br>" +
            "This application uses a 3D model by zsoltsulyok.<br>"
            "For more information please visit: <br>"
            "<a style='color: #FF69B4;' href='https://peerless-audio.com/flowdsp/'>https://peerless-audio.com/flowdsp/</a>"
        )
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
            }
            QLabel a:hover {
                color: #FFB6C1;
            }
        """)
        self.label.setOpenExternalLinks(True)

        # Position the label at bottom middle
        self.label.setParent(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Calculate center position
        label_width = 250  # Approximate width of the label
        x = (800 - label_width) // 2  # Center horizontally
        self.label.move(x, 330)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)
        super().paintEvent(event)


class LogWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Log')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black; color: white;")
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        layout = QVBoxLayout(self)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Calibri", 12))

        layout.addWidget(self.log_display)

    def append_log(self, text):
        self.log_display.append(text)