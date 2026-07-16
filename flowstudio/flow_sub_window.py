import json
import operator

from flowstudio.flow_conf_co import *
from flowstudio.functions.track_worker import TrackManager
from template.co_socket_type_and_num_select import Ui_co_socket_type_and_num_select
from template.co_socket_type_select import Ui_co_socket_type_select
from template.node_band_select import Ui_node_band_select
from template.node_channel_select import Ui_node_channel_select
from template.node_configure_dialog import Ui_node_configure_dialog
from template.node_in_out_select import Ui_node_in_out_select
from template.node_out_select import Ui_node_out_select
from template.node_tap_select import *
from template.group_io_select import *
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_file_converter import *
from flowstudio.flow_view import FLOW_View
from flowstudio.flow_scene import FLOW_Scene

from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER, EDGE_TYPE_SQUARE
from nodeeditor.node_graphics_view import MODE_EDGE_DRAG
from nodeeditor.utils import dumpException
from utilities.utils import getFileDialogDirectory, getFileDialogFilter
from flowstudio.functions.aes_operation import AESOperation
from flowstudio.functions.conversion import Conversion
from flowstudio.functions.common import *
DEBUG = False
DEBUG_Context = False
DEBUG_Linked_List = False


class FLOW_Sub_Window(NodeEditorWidget):
    editmode = False
    Scene_class = FLOW_Scene
    GraphicsView_class = FLOW_View

    def __init__(self):
        from flowstudio.flow_conf import CATE_AO_MAPPING
        super().__init__()
        self.ao_categories = CATE_AO_MAPPING.keys()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    def getNodeClassFromData(self, data):
        if 'op_code' not in data: return Node
        if data['op_code'] not in FLOW_NODES:
            # When audio object must be captured using the type
            return get_class_from_type(data['type'])
        else:
            return get_class_from_opcode(data['op_code'])


    def onEval(self):
        for node in self.scene.nodes:
            node.eval()

    def onHistoryRestored(self):
        # print("onHistoryRestored")
        self.onEval()

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New FLOW"
        return name + ("*" if self.isModified() else "")

    def getPrettyFilename(self):
        name = self.getUserFriendlyFilename()
        if name.endswith('*'):
            name = name[:-1]
            if name.endswith('.json'):
                name = name[:-5]
        else:
            name = name[:-5]
        return name

    def fileLoad(self, filename):
        if super().fileLoad(filename):
            self.onEval()
            return True

        return False

    def fileSave(self, filename: str = None):
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True

    def exportXML(self, sub_window, flw_file_path=None, is_to_binary=True):
        """
            export flw file which is for FlowEngine to use

            :param sub_window: FLOW_Sub_Window instance of main sub window,
            :param flw_file_path: str, flw file path that you want to output;
                default:None, if no parameter value provided,
                file will be stored in location which is specified by system
            :param is_to_binary: bool, default:True, if True, convert xml to binary format;

        """
        current_window = self.window().getCurrentNodeEditorWidget()
        nodes_in_main = sub_window.scene.nodes
        for node in nodes_in_main:
            if node.op_code == OP_NODE_SUBPATCH:
                self.window().open_subwindow_in_subpatch_recursively(node.title)
                self.window().setActiveSubWindow(current_window.parent())
        raw_data = json.dumps(sub_window.scene.serialize(), indent=4)
        data = json.loads(raw_data)

        rate = self.window().settingDialog.controlDialog.comboBox_sr_list.currentText()
        converter = FLOW_File_Convert(copy.deepcopy(data), windows=self.window().mdiArea.subWindowList(), rate=rate)
        # convert process
        result, not_support_nodes = converter.process()

        if not_support_nodes:
            self.window().custom_message = not_support_nodes

        # region if hasn't saved, store flw file under userPath
        if flw_file_path is None:
            if sub_window.filename is None:
                flw_file_path = self.window().userPath + '/' + 'default_config.flw'
            else:
                flw_file_path = os.path.join(self.window().temp_folder_path, 'default_config.flw')

        # xml to binary
        if is_to_binary:
            result = Conversion().str_to_binary(input_str=result)

        for window in self.window().mdiArea.subWindowList():
            if hasattr(window.widget(), 'close_if_no_problem'):
                if window.widget().close_if_no_problem:
                    self.window().close_sub_window(window)
            if hasattr(window.widget(), 'encrypted'):
                if window.widget().encrypted and not window.widget().already_input_password:
                    self.window().close_sub_window(window)
        # save .flw to /bin/temp directory
        with open(flw_file_path, "w") as file:
            file.write(result)
            self.has_been_modified = False

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(FLOW_NODES.keys())
        keys.sort()
        for key in keys:
            node = FLOW_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.display_name)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        from flowstudio.flow_conf import CATE_AO_MAPPING, NOT_SUPPORT_AOS, Company, AO_TYPE_NAME
        if 'Custom' in CATE_AO_MAPPING:
            for ao_number in CATE_AO_MAPPING['Custom']:
                self.node_actions[ao_number] = QAction(QIcon(FLOW_NODES[ao_number].icon), FLOW_NODES[ao_number].display_name)
                self.node_actions[ao_number].setData(ao_number)
        feature_permission_data = self.view.window().license_mechanism.feature_permission_data
        context_menu = QMenu(self)
        for ao_category in self.ao_categories:
            # add separator line
            if ao_category == 'Technology Provider':
                separator = context_menu.addSeparator()
            submenu = context_menu.addMenu(add_ampersand_before_and(ao_category))
            if CATE_AO_MAPPING[ao_category]:
                if type(CATE_AO_MAPPING[ao_category][0]) is Company:
                    for company in CATE_AO_MAPPING[ao_category]:
                        company_menu = submenu.addMenu(company.name)
                        if type(company.ao_list) is list:
                            if len(company.ao_list) == 0:
                                submenu.addAction(company.name)
                            for ao_no in company.ao_list:
                                if (FLOW_NODES[ao_no].is_float_point and
                                        not self.window().float_point_aos_checkbox.isChecked()):
                                    continue
                                if (not FLOW_NODES[ao_no].is_float_point and
                                        not self.window().fixed_point_aos_checkbox.isChecked()):
                                    continue
                                company_menu.addAction(self.node_actions[ao_no])
                        elif type(company.ao_list) is dict:
                            for cate, ao_nos in company.ao_list.items():
                                if cate:
                                    sub_sub_menu = company_menu.addMenu(add_ampersand_before_and(cate))
                                    for ao_no in ao_nos:
                                        if (FLOW_NODES[ao_no].is_float_point and
                                                not self.window().float_point_aos_checkbox.isChecked()):
                                            continue
                                        if (not FLOW_NODES[ao_no].is_float_point and
                                                not self.window().fixed_point_aos_checkbox.isChecked()):
                                            continue
                                        sub_sub_menu.addAction(self.node_actions[ao_no])
                                    all_child_hidden = True
                                    for action in sub_sub_menu.actions():
                                        if action.isVisible():
                                            all_child_hidden = False
                                            break
                                    if all_child_hidden:
                                        sub_sub_menu.menuAction().setVisible(False)
                                else:
                                    for ao_no in ao_nos:
                                        if (FLOW_NODES[ao_no].is_float_point and
                                                not self.window().float_point_aos_checkbox.isChecked()):
                                            continue
                                        if (not FLOW_NODES[ao_no].is_float_point and
                                                not self.window().fixed_point_aos_checkbox.isChecked()):
                                            continue
                                        company_menu.addAction(self.node_actions[ao_no])
                        all_child_hidden = True
                        for action in company_menu.actions():
                            if action.isVisible():
                                all_child_hidden = False
                                break
                        if all_child_hidden:
                            company_menu.menuAction().setVisible(False)
                else:
                    for ao_number in CATE_AO_MAPPING[ao_category]:
                        # region it's not allowed to use IN and OUT inside subpatch
                        from flowstudio.flow_sub_group import FLOW_Sub_Group
                        if type(self) == FLOW_Sub_Group:
                            if ao_number == OP_NODE_ADC or ao_number == OP_NODE_DAC:
                                continue
                        # endregion
                        if FLOW_NODES[ao_number].is_float_point and not self.window().float_point_aos_checkbox.isChecked():
                            continue
                        if not FLOW_NODES[ao_number].is_float_point and not self.window().fixed_point_aos_checkbox.isChecked():
                            continue
                        submenu.addAction(self.node_actions[ao_number])
            all_child_hidden = True
            for action in submenu.actions():
                if action.isVisible():
                    all_child_hidden = False
                    break
            if all_child_hidden:
                submenu.menuAction().setVisible(False)
            if ao_category == list(CATE_AO_MAPPING.keys())[-1]:
                if not submenu.isVisible():
                    context_menu.removeAction(separator)
        if self.view.window().target in NOT_SUPPORT_AOS:
            for key, value in self.node_actions.items():
                if key in NOT_SUPPORT_AOS[self.view.window().target]:
                    self.node_actions[key].setEnabled(False)
                else:
                    if key in feature_permission_data[AO_TYPE_NAME]:
                        self.node_actions[key].setEnabled(True)
                    else:
                        self.node_actions[key].setEnabled(False)
        else:
            for key, value in self.node_actions.items():
                if key in feature_permission_data[AO_TYPE_NAME]:
                    self.node_actions[key].setEnabled(True)
                else:
                    self.node_actions[key].setEnabled(False)
        return context_menu

    def setTitle(self):
        """
            Set the FLOW_Sub_Window title and the FLOW_Window title based on the file name and modification status.

            Returns:
                No return value.
        """
        from flowstudio.flow_window import FLOW_Window
        if self.isFilenameSet():
            project_name = self.window().project_name
            title = project_name
            window_title = f'Flow Studio - {project_name}'
        else:
            title = 'NEW'
            window_title = 'Flow Studio - New File'
        if self.isModified():
            self.setWindowTitle(f'{title}*')
            self.view.window().setWindowTitle(f'{window_title}*')
        else:
            self.setWindowTitle(f'{title}')
            if type(self.view.window()) is FLOW_Window:
                self.view.window().setWindowTitle(f'{window_title}')

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)

        if event.isAccepted():
            nodes = self.scene.nodes

            # close the open widget while subwnd is closed
            for node in nodes:
                if node.openable:
                    node.widget.close()

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Shift:
            if Debug.DEBUG_Low_Level.value: print('Key ID: %s Pressed' % event.key())
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Shift:
            if Debug.DEBUG_Low_Level.value: print('Key ID: %s Released' % event.key())
            self.view.setDragMode(QGraphicsView.RubberBandDrag)

    def add_ao(self, ao_code, x_position=0, y_position=0, parameters=None):
        """
            Add an audio object to the sub window.

            :param ao_code: int, the code of the audio object to be added.
            :param x_position: float, optional, the x-position on the screen where the audio object should be added.
                Defaults to 0.
            :param y_position: float, optional, the y-position on the screen where the audio object should be added.
                Defaults to 0.
            :param parameters: dict, optional, for automated testing parameters,
                the necessary arguments are passed directly without requiring user input for parameter values.
                Defaults to None.

            :return: Returns instance of audio object if the audio object is successfully added, otherwise returns None.
        """
        try:
            current_window = self.parent().window().getCurrentNodeEditorWidget()
            nodesSets = self.collectNodesFromSubWnds()
            self.parent().window().setActiveSubWindow(current_window.parent())
            sortedNodes = self.getNodesByOP(ao_code, nodesSets)
            designator = self.findMinimalConseqSequence(sortedNodes)
            new_node = self.initNewNodeCondition(ao_code, parameters)
            if new_node:
                new_node.designator = designator
                new_node.setPos(x_position, y_position)

                # Rename the title with designator at the first time create the node
                new_node.title = new_node.title + '_' + str(designator)
                self.view.window().adjust_title_of_new_in_out_ao(new_node)

                if ao_code == OP_NODE_SUBPATCH:
                    self.window().onEnterGroupFile(new_node)

                if self.scene.getView().mode == MODE_EDGE_DRAG:
                    if Debug.DEBUG_Low_Level.value: print("its MODE_EDGE_DRAG")
                    # if we were dragging an edge...
                    self.scene.getView().dragging.edgeDragEnd(new_node.inputs[0].grSocket)
                    new_node.doSelect(True)
                else:
                    if ao_code == OP_NODE_SUBPATCH:
                        new_node.cwd = new_node.title
                    self.scene.history.storeHistory(f"Created {new_node.__class__.__name__}-{new_node.title}",
                                                    setModified=True)
                    self.view.window().statusBar().clearMessage()
                    self.view.window().statusBar().showMessage("Created Node: %s" % new_node.title, 3000)
                    self.scene.has_been_modified = True
                    self.setFocus()
                return new_node

        except Exception as e:
            dumpException(e)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if Debug.DEBUG_Low_Level.value: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            self.add_ao(ao_code=op_code, x_position=scene_position.x(), y_position=scene_position.y())

            event.setDropAction(Qt.MoveAction)
            event.accept()

            # Track user action "drag AO into Canvas"
            self.tracker = TrackManager()
            self.tracker.track_user_action(action=3, license=self.view.window().license_mechanism)
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()



    def initNewNodeCondition(self, input_data, parameters=None):
        """
            Return the corresponding audio object instance based on the given parameters.

            :param input_data: int, the code of the audio object.
            :param parameters: dict, optional, for automated testing parameters,
                the necessary arguments are passed directly without requiring user input for parameter values.
                Defaults to None.

            :return: If there are no exceptional cases, return the corresponding audio object.
                If there are exceptional cases, return None.
        """
        try:
            self.input_data = input_data
            type_ao_addition = get_class_from_opcode(input_data).type_ao_addition
            if type_ao_addition == TypeAOAddition.FIXED.value:
                result = get_class_from_opcode(input_data)(self.scene)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_CHANNELS.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_channels'])
                else:
                    self.defaultNodeChannel = 0
                    self.selectChannelDialog()
                    if self.defaultNodeChannel >= 1 and input_data == OP_NODE_NTTS_AGC:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeChannel+1)
                    elif self.defaultNodeChannel >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeChannel)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_in_channels'],
                                                               parameters['num_out_channels'])
                else:
                    self.defaultNodeIn = 0
                    self.defaultNodeOut = 0
                    self.selectInOutDialog()
                    if self.defaultNodeIn >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeIn, self.defaultNodeOut)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_bands'],
                                                               parameters['num_channels'], parameters['control'])
                else:
                    self.defaultNodeBand = 0
                    self.defaultNodeChannel = 0
                    self.defaultControl = False
                    self.selectBandDialog()
                    if self.defaultNodeBand >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeBand,
                                                                   self.defaultNodeChannel, self.defaultControl)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_TAPS.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_taps'])
                else:
                    self.defaultNodeTap = 0
                    self.selectTapDialog()
                    if self.defaultNodeTap >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeTap)
            elif type_ao_addition == TypeAOAddition.SPECIAL_ACTION.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['configure'])
                else:
                    self.defaultNodeConfigure = 0
                    self.node_configure_dialog(input_data)
                    if self.defaultNodeConfigure != 0:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeConfigure)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_NUM_OUTPUTS_AND_FOUR_TIMES_INPUTS.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_out_channels'])
                else:
                    self.defaultNodeOut = 0
                    self.selectOutDialog()
                    if self.defaultNodeOut >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultNodeOut)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_SOCKET_TYPE.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_channels'])
                else:
                    self.defaultSocketType = 0
                    self.CO_socket_type_select_dialog(input_data)
                    if self.defaultSocketType >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultSocketType)
            elif type_ao_addition == TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value:
                if parameters is not None:
                    result = get_class_from_opcode(input_data)(self.scene, parameters['num_channels'])
                else:
                    self.defaultSocketType = 0
                    self.defaultSocketNum = 0
                    self.CO_socket_type_num_select_dialog(input_data)
                    if self.defaultSocketType >= 1 and self.defaultSocketNum >= 1:
                        result = get_class_from_opcode(input_data)(self.scene, self.defaultSocketType, self.defaultSocketNum)

            return result

        except Exception as e:
            if Debug.DEBUG_Low_Level.value:
                dumpException(e)

    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos())
            if Debug.DEBUG_Low_Level.value: print(item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                if hasattr(item, 'node'):
                    expandable = item.node.expandable
                    if expandable:
                        expand = item.node.expand
                    else:
                        expand = False
                    openable = item.node.openable
                    if hasattr(item.node, 'widget'):
                        if item.node.widget.isVisible() is True:
                            expandable = False
                            openable = False
                    if item.node.content_label_objname == "SUBPATCH":
                        group = True
                    else:
                        group = False
                    self.handleNodeContextMenu(event, expandable, openable, expand, group)
            elif self.editmode:
                if Debug.DEBUG_Low_Level.value: print("sub window disable right click handle")
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            # elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dumpException(e)

    def handleNodeContextMenu(self, event, expandable=False, openable=False, expand=False, group=False):

        selected = None
        item = self.scene.getItemAt(event.pos())
        if type(item) == QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node

        if hasattr(item, 'socket'):
            selected = item.socket.node

        if Debug.DEBUG_Low_Level.value: print("got item:", selected)

        if Debug.DEBUG_Low_Level.value: print("CONTEXT: NODE")

        context_menu = QMenu(self)
        renameNodeAct = context_menu.addAction("Rename")

        deleteNodeAct = context_menu.addAction("Delete")

        chageColorAct = context_menu.addAction("Recolor")

        propertyAct = context_menu.addAction("Property")

        context_menu.addSeparator()
        feedbackChannel = context_menu.addAction("feedback")
        feedbackChannel.setCheckable(True)
        feedbackChannel.setChecked(selected.is_feedback)
        context_menu.addSeparator()

        context_menu.addSeparator()

        addChannel = context_menu.addAction("add channel")

        reduceChannel = context_menu.addAction("reduce channel")

        addCtrlChannel = context_menu.addAction("add control channel")

        reduceCtrlChannel = context_menu.addAction("reduce control channel")

        add_inlet = context_menu.addAction("add inlet")

        reduce_inlet = context_menu.addAction("reduce inlet")

        add_outlet = context_menu.addAction("add outlet")

        reduce_outlet = context_menu.addAction("reduce outlet")

        addTap = context_menu.addAction("add band")

        reduceTap = context_menu.addAction("reduce band")

        addInputChannel = context_menu.addAction("add input")

        reduceInputChannel = context_menu.addAction("reduce input")

        addOutPutChannel = context_menu.addAction("add output")

        reduceOutPutChannel = context_menu.addAction("reduce output")

        context_menu.addSeparator()

        if selected.op_code in [OP_NODE_CO_ADD, OP_NODE_CO_MULTIPLY, OP_NODE_CO_INVERSE, OP_NODE_CO_POWER, OP_NODE_CO_SQRT,
                                OP_NODE_CO_LOG, OP_NODE_CO_EXP, OP_NODE_CO_CLAMP, OP_NODE_CO_OR, OP_NODE_CO_AND, OP_NODE_CO_NOT,
                                OP_NODE_CO_DELAY, OP_NODE_CO_METER]:
            control_channel_number_max, control_channel_number_min = self.get_node_control_channel_number(selected.op_code)
            if len(selected.inctrls) >= control_channel_number_max:
                addCtrlChannel.setEnabled(False)
            else:
                addCtrlChannel.setEnabled(True)

            if len(selected.inctrls) <= control_channel_number_min:
                reduceCtrlChannel.setEnabled(False)
            else:
                reduceCtrlChannel.setEnabled(True)

            if self.window().editmode:
                addCtrlChannel.setEnabled(False)
                reduceCtrlChannel.setEnabled(False)
        else:
            addCtrlChannel.setVisible(False)
            reduceCtrlChannel.setVisible(False)


        if selected.op_code in [OP_NODE_BIQUAD, OP_NODE_BIQUAD_LOAD, OP_NODE_PEQ, OP_NODE_LPF, OP_NODE_HPF, OP_NODE_IIRCOEF, OP_NODE_FIR,
                                OP_NODE_GAIN, OP_NODE_GAIN_FP, OP_NODE_HPF_FP, OP_NODE_LPF_FP, OP_NODE_PEQ_FP,
                                OP_NODE_ATTEN, OP_NODE_POLARITY, OP_NODE_LIMITER, OP_NODE_COMP, OP_NODE_AUTO_COMP,
                                OP_NODE_COMP_Combo, OP_NODE_COMP_FP, OP_NODE_LIMITER_FP, OP_NODE_DELAY_FP, OP_NODE_DYNAMIC_EQ,
                                OP_NODE_CLIPPER, OP_NODE_GATE, OP_NODE_MUX, OP_NODE_DELAY, OP_NODE_MUTE,
                                OP_NODE_DEESSER, OP_NODE_AGC, OP_NODE_SRC, OP_NODE_VBASS, OP_NODE_METER_FP, OP_NODE_IIRCOEF_FP,
                                OP_NODE_DBASS, OP_NODE_METER, OP_NODE_DLOUDNESS, OP_NODE_MUX_FP, OP_NODE_FIR_FP,
                                OP_NODE_COMP_Combo_FP, OP_NODE_CLIPPER_FP, OP_NODE_NTTS_AGC, OP_NODE_PEQ_V2,
                                OP_NODE_FIR_LOAD, OP_NODE_GAME_EQ,
                                OP_NODE_FIR_LOAD]:

            channel_number_max, channel_number_min = self.get_node_channel_number(selected.op_code)

            if len(selected.inputs) >= channel_number_max:
                addChannel.setEnabled(False)
            else:
                addChannel.setEnabled(True)

            if len(selected.inputs) <= channel_number_min:
                reduceChannel.setEnabled(False)
            else:
                reduceChannel.setEnabled(True)

            if self.window().editmode:
                addChannel.setEnabled(False)
                reduceChannel.setEnabled(False)
        else:
            addChannel.setVisible(False)
            reduceChannel.setVisible(False)

        def subpatch_inlet_outlet_operation():
            if selected.op_code == OP_NODE_SUBPATCH:
                max_num = 8
                min_num = 1
                if len(selected.inputs) >= max_num:
                    add_inlet.setEnabled(False)
                else:
                    add_inlet.setEnabled(True)

                if len(selected.inputs) <= min_num:
                    reduce_inlet.setEnabled(False)
                else:
                    reduce_inlet.setEnabled(True)
                if len(selected.outputs) >= max_num:
                    add_outlet.setEnabled(False)
                else:
                    add_outlet.setEnabled(True)

                if len(selected.outputs) <= min_num:
                    reduce_outlet.setEnabled(False)
                else:
                    reduce_outlet.setEnabled(True)
            else:
                add_inlet.setVisible(False)
                reduce_inlet.setVisible(False)
                add_outlet.setVisible(False)
                reduce_outlet.setVisible(False)




        if selected.op_code in [OP_NODE_BIQUAD, OP_NODE_PEQ, OP_NODE_PEQ_FP, OP_NODE_PEQ_V2]:
            band_min = 1
            if selected.op_code == OP_NODE_BIQUAD_LOAD:
                band_max = 10000
            else:
                band_max = 10

            if selected.tap <= band_min:
                reduceTap.setEnabled(False)
            else:
                reduceTap.setEnabled(True)

            if selected.tap >= band_max:
                addTap.setEnabled(False)
            else:
                addTap.setEnabled(True)

            if self.window().editmode:
                addTap.setEnabled(False)
                reduceTap.setEnabled(False)

        else:
            addTap.setVisible(False)
            reduceTap.setVisible(False)

        if selected.op_code in [OP_NODE_MIXER]:
            in_min, in_max, out_min, out_max = self.getNodeChannelMaxAndMin(selected.op_code)
            if len(selected.inputs) >= in_max:
                addInputChannel.setEnabled(False)
            else:
                addInputChannel.setEnabled(True)

            if len(selected.inputs) <= in_min:
                reduceInputChannel.setEnabled(False)
            else:
                reduceInputChannel.setEnabled(True)

            if len(selected.outputs) >= out_max:
                addOutPutChannel.setEnabled(False)
            else:
                addOutPutChannel.setEnabled(True)

            if len(selected.outputs) <= out_min:
                reduceOutPutChannel.setEnabled(False)
            else:
                reduceOutPutChannel.setEnabled(True)

            if self.window().editmode:
                addInputChannel.setEnabled(False)
                reduceInputChannel.setEnabled(False)
                addOutPutChannel.setEnabled(False)
                reduceOutPutChannel.setEnabled(False)

        else:
            addInputChannel.setVisible(False)
            reduceInputChannel.setVisible(False)
            addOutPutChannel.setVisible(False)
            reduceOutPutChannel.setVisible(False)

        availableStatus = "Collapse" if expand else "Expand"
        expandcollapseAct = context_menu.addAction(availableStatus)
        expandcollapseAct.setEnabled(expandable)

        openAct = context_menu.addAction("Open")
        openAct.setEnabled(openable)
        # openAct.setEnabled(False)
        addPassword = context_menu.addAction("Add Password")
        modifyPassword = context_menu.addAction("Modify Password")
        removePassword = context_menu.addAction("Remove Password")
        if selected.op_code in [OP_NODE_SUBPATCH]:
            if not selected.is_encrypted():
                addPassword.setVisible(True)
                modifyPassword.setVisible(False)
                removePassword.setVisible(False)
                subpatch_inlet_outlet_operation()
            else:
                renameNodeAct.setEnabled(False)
                addPassword.setVisible(False)
                modifyPassword.setVisible(True)
                removePassword.setVisible(True)
                add_inlet.setEnabled(False)
                reduce_inlet.setEnabled(False)
                add_outlet.setEnabled(False)
                reduce_outlet.setEnabled(False)
                # 加密狀態並且有輸過密碼 則可以改名
                for ele in self.window().sub_patchs:
                    if ele.title == selected.title or ele.title == selected.title + '.json':
                        if hasattr(ele, 'already_input_password'):
                            if ele.already_input_password:
                                renameNodeAct.setEnabled(True)
                                subpatch_inlet_outlet_operation()
                # 上層subpatch還是加密的況下 下層的subpatch不能刪除密碼
                current_widget = self.window().getCurrentNodeEditorWidget()
                from flowstudio.flow_sub_group import FLOW_Sub_Group
                if type(current_widget) == FLOW_Sub_Group:
                    upper_subpatch_title = current_widget.getPrettyFilename()
                    # print(current_widget.getPrettyFilename())
                    sub_windows = self.window().mdiArea.subWindowList()
                    for sub_window in sub_windows:
                        for i in range(len(sub_window.widget().scene.nodes)):
                            node = sub_window.widget().scene.nodes[i]
                            if node.op_code == OP_NODE_SUBPATCH and node.title == upper_subpatch_title:
                                if node.is_encrypted():
                                    removePassword.setVisible(False)
            if self.window().editmode:
                add_inlet.setEnabled(False)
                reduce_inlet.setEnabled(False)
                add_outlet.setEnabled(False)
                reduce_outlet.setEnabled(False)
        else:
            addPassword.setVisible(False)
            modifyPassword.setVisible(False)
            removePassword.setVisible(False)

            add_inlet.setVisible(False)
            reduce_inlet.setVisible(False)
            add_outlet.setVisible(False)
            reduce_outlet.setVisible(False)


        if selected.op_code in [OP_NODE_FEEDBACK]:
            feedbackChannel.setVisible(False)


        if group: enterGroupAct = context_menu.addAction("Enter Group")

        if self.editmode:
            renameNodeAct.setEnabled(False)
            deleteNodeAct.setEnabled(False)
            # if expandable:
            #     if expand:
            #         openAct.setEnabled(False)
            #     else:
            #         openAct.setEnabled(True)
            # else:
            #     openAct.setEnabled(False)
            # expandcollapseAct.setEnabled(False)

        # markDirtyAct = context_menu.addAction("Mark Dirty")
        # markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        # markInvalidAct = context_menu.addAction("Mark Invalid")
        # unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        # evalAct = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        # if selected and action == markDirtyAct: selected.markDirty()
        # if selected and action == markDirtyDescendantsAct: selected.markDescendantsDirty()
        # if selected and action == markInvalidAct: selected.markInvalid()
        # if selected and action == unmarkInvalidAct: selected.markInvalid(False)

        if selected and action == renameNodeAct: selected.renameNode()
        if selected and action == expandcollapseAct: selected.expandcollapseNode()
        if selected and action == openAct:
            selected.collapseNode()
            selected.openNodeGUIWidget()

        if selected and action == deleteNodeAct:
            selected.on_delete_node()

        if selected and action == chageColorAct:
            selected.onColorSelect()

        if selected and action == propertyAct:
            selected.openNodePropertyWidget()

        if selected and action == addChannel:
            selected.addChannel()

        if selected and action == reduceChannel:
            selected.reduceChannel()

        if selected and action == addCtrlChannel:
            selected.addChannel()

        if selected and action == reduceCtrlChannel:
            selected.reduceChannel()

        if selected and action == feedbackChannel:
            selected.feedbackChannel()

        if selected and action == add_inlet:
            selected.addChannel(add_inlet=True, add_outlet=False)

        if selected and action == reduce_inlet:
            selected.reduceChannel(reduce_inlet=True, reduce_outlet=False)

        if selected and action == add_outlet:
            selected.addChannel(add_inlet=False, add_outlet=True)

        if selected and action == reduce_outlet:
            selected.reduceChannel(reduce_inlet=False, reduce_outlet=True)

        if selected and action == addTap:
            selected.Tap(0)

        if selected and action == reduceTap:
            selected.Tap(1)

        if selected and action == addInputChannel:
            selected.addOneSignChannel('Input', selected.op_code)

        if selected and action == reduceInputChannel:
            selected.reduceOneSignChannel('Input', selected.op_code)

        if selected and action == addOutPutChannel:
            selected.addOneSignChannel('Output', selected.op_code)

        if selected and action == reduceOutPutChannel:
            selected.reduceOneSignChannel('Output', selected.op_code)

        if selected and action == addPassword:
            selected.add_password()
        if selected and action == removePassword:
            selected.remove_password()
        if selected and action == modifyPassword:
            selected.modify_password()

        if group and selected and action == enterGroupAct: self.window().onEnterGroupFile(selected)

        # if selected and action == evalAct:
        #     val = selected.eval()
        #     if DEBUG_CONTEXT: print("EVALUATED:", val)

    def handleEdgeContextMenu(self, event):
        if Debug.DEBUG_Low_Level.value: print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        squareAct = context_menu.addAction("Squre Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_TYPE_DIRECT
        if selected and action == squareAct:  selected.edge_type = EDGE_TYPE_SQUARE

    def handleNewNodeContextMenu(self, event):
        if Debug.DEBUG_Low_Level.value: print("CONTEXT: EMPTY SPACE")
        context_menu = self.initNodesContextMenu()
        all_child_hidden = True
        for action in context_menu.actions():
            if action.isVisible():
                all_child_hidden = False
                break
        if all_child_hidden:
            return
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            op_code = action.data()
            if op_code is None:
                return
            current_window = self.parent().window().getCurrentNodeEditorWidget()
            nodesSets = self.collectNodesFromSubWnds()
            self.parent().window().setActiveSubWindow(current_window.parent())
            sortedNodes = self.getNodesByOP(op_code, nodesSets)

            designator = self.findMinimalConseqSequence(sortedNodes)
            new_node = self.initNewNodeCondition(op_code)
            new_node.designator = designator
            new_node.title = new_node.title + '_' + str(designator)
            scene_pos = self.scene.getView().mapToScene(event.pos())

            new_node.setPos(scene_pos.x(), scene_pos.y())
            if Debug.DEBUG_Low_Level.value: print("Selected node:", new_node)

            if op_code == OP_NODE_SUBPATCH:
                self.window().onEnterGroupFile(new_node)

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                if Debug.DEBUG_Low_Level.value: print("its MODE_EDGE_DRAG")
                # if we were dragging an edge...
                self.scene.getView().dragging.edgeDragEnd(new_node.inputs[0].grSocket)
                new_node.doSelect(True)
            else:
                if op_code == OP_NODE_SUBPATCH:
                    new_node.cwd = new_node.title
                self.scene.history.storeHistory(f"Created {new_node.__class__.__name__}-{new_node.title}", setModified=True)
                self.view.window().statusBar().clearMessage()
                self.view.window().statusBar().showMessage("Created Node: %s" % new_node.title, 3000)

            self.parent().window().setActiveSubWindow(current_window.parent())



        self.scene.has_been_modified = True

    def selectTapDialog(self):
        qdialog = QDialog(self.view.window())
        self.node_tap_select = Ui_node_tap_select()
        self.node_tap_select.setupUi(qdialog)
        self.node_tap_select.buttonBox.clicked.connect(self.onTapDialogOption)
        qdialog.exec()

    def selectOutDialog(self):
        qdialog = QDialog(self.view.window())
        self.node_out_select = Ui_node_out_select()
        self.node_out_select.setupUi(qdialog)
        self.node_out_select.buttonBox.clicked.connect(self.onOutDialogOption)
        qdialog.exec()

    def selectBandDialog(self):
        qdialog = QDialog(self.view.window())
        self.node_band_select = Ui_node_band_select()
        self.node_band_select.setupUi(qdialog)

        # if op_code in [OP_NODE_PEQ, OP_NODE_PEQ_FP]:
        self.node_band_select.comboBox.addItem('9')
        self.node_band_select.comboBox.addItem('10')
        validator = QIntValidator(0, 10000, self)
        self.node_band_select.lineEdit_2.setValidator(validator)

        if self.input_data in [OP_NODE_BIQUAD_LOAD, OP_NODE_FIR_LOAD]:
            self.node_band_select.label_1.setVisible(False)
            self.node_band_select.comboBox.setVisible(False)
        else:
            self.node_band_select.label_3.setVisible(False)
            self.node_band_select.lineEdit_2.setVisible(False)

        if self.input_data in [OP_NODE_FIR_LOAD]:
            self.node_band_select.label_3.setText('max taps')

        if self.input_data not in [OP_NODE_PEQ]:
            self.node_band_select.comboBox_2.setVisible(False)
            self.node_band_select.label_4.setVisible(False)
            qdialog.setFixedHeight(140)

        self.node_band_select.pushButton_2.clicked.connect(self.onBandDialogOptionPlus)
        self.node_band_select.pushButton.clicked.connect(self.onBandDialogOptionReduce)
        self.node_band_select.buttonBox.clicked.connect(self.onBandDialogOption)
        qdialog.exec()

    def selectChannelDialog(self):
        qdialog = QDialog(self.view.window())
        self.node_channel_select = Ui_node_channel_select()
        self.node_channel_select.setupUi(qdialog)

        channel_number_max, channel_number_min = self.get_node_channel_number(self.input_data)
        if self.input_data == OP_NODE_NTTS_AGC:
            self.node_channel_select.label_1.setText('Audio Input')
        self.node_channel_select.lineEdit.setText(str(channel_number_min))
        validator = QRegExpValidator()
        if channel_number_max < 10: validator.setRegExp(QRegExp("^[%s-%s]$" % (channel_number_min, channel_number_max)))
        if channel_number_max > 10: validator.setRegExp(QRegExp("^(%s|[1-2][0-9]|%s)$" % (channel_number_min, channel_number_max)))
        self.node_channel_select.lineEdit.setValidator(validator)

        self.node_channel_select.pushButton_2.clicked.connect(lambda: self.onChannelDialogOptionPlus(channel_number_max))
        self.node_channel_select.pushButton.clicked.connect(lambda: self.onChannelDialogOptionReduce(channel_number_min))
        self.node_channel_select.buttonBox.clicked.connect(self.onChannelDialogOption)
        qdialog.exec()

    def selectInOutDialog(self):
        qdialog = QDialog(self.view.window())
        self.node_in_out_select = Ui_node_in_out_select()
        self.node_in_out_select.setupUi(qdialog)

        in_min, in_max, out_min, out_max = self.getNodeChannelMaxAndMin(self.input_data)
        if self.input_data == OP_NODE_UPHEAR_VQE:
            self.node_in_out_select.label_1.setText('    MIC')
            self.node_in_out_select.label_2.setText('    REF')
        self.node_in_out_select.lineEdit.setText(str(in_min))
        self.node_in_out_select.lineEdit_2.setText(str(out_min))
        validator = QRegExpValidator()
        validator.setRegExp(QRegExp("^[%s-%s]$" % (in_min, in_max)))
        self.node_in_out_select.lineEdit.setValidator(validator)
        validator = QRegExpValidator()
        validator.setRegExp(QRegExp("^[%s-%s]$" % (out_min, out_max)))
        self.node_in_out_select.lineEdit_2.setValidator(validator)

        self.node_in_out_select.pushButton_2.clicked.connect(lambda: self.onInDialogOptionPlus(in_max))
        self.node_in_out_select.pushButton.clicked.connect(lambda: self.onInDialogOptionReduce(in_min))

        self.node_in_out_select.pushButton_4.clicked.connect(lambda: self.onOutDialogOptionPlus(out_max))
        self.node_in_out_select.pushButton_3.clicked.connect(lambda: self.onOutDialogOptionReduce(out_min))
        self.node_in_out_select.buttonBox.clicked.connect(self.onInOutDialogOption)
        qdialog.exec()

    def node_configure_dialog(self, op_code):
        qdialog = QDialog(self.view.window())
        self.node_configure_select = Ui_node_configure_dialog()
        self.node_configure_select.setupUi(qdialog)
        if op_code == OP_NODE_DIRAC:
            items = ["2.0", "5.1.2", "7.1.4"]
            self.node_configure_select.comboBox.addItems(items)
        elif op_code == OP_NODE_CINGO:
            qdialog.setWindowTitle("Channel")
            items = ["2.0", "7.1"]
            self.node_configure_select.comboBox.addItems(items)
            self.node_configure_select.label_1.setText("Audio Format")
        self.node_configure_select.buttonBox.clicked.connect(self.on_node_configure_dialog_option)
        qdialog.exec()

    def CO_socket_type_select_dialog(self, op_code):
        qdialog = QDialog(self.view.window())
        self.socket_type_select = Ui_co_socket_type_select()
        self.socket_type_select.setupUi(qdialog)

        items = self.get_co_node_socket_type_list(op_code)
        self.socket_type_select.socket_type_comboBox.addItems(items)

        self.socket_type_select.buttonBox.accepted.connect(qdialog.accept)
        self.socket_type_select.buttonBox.rejected.connect(qdialog.reject)
        self.socket_type_select.buttonBox.clicked.connect(
            partial(self.on_socket_type_select_dialog_option, include_num=False))

        qdialog.exec()

    def CO_socket_type_num_select_dialog(self, op_code):
        qdialog = QDialog(self.view.window())
        self.socket_type_and_num_select = Ui_co_socket_type_and_num_select()
        self.socket_type_and_num_select.setupUi(qdialog)

        channel_number_max = 32
        channel_number_min = 1

        items = self.get_co_node_socket_type_list(op_code)
        self.socket_type_and_num_select.socket_type_comboBox.addItems(items)

        self.socket_type_and_num_select.socket_num_edit.textChanged.connect(
            lambda: self.socket_type_and_num_select_dialog_validate_input(channel_number_max, channel_number_min))
        self.socket_type_and_num_select.channel_number_add.clicked.connect(
            lambda: self.socket_type_and_num_select_dialog_socket_num_add(channel_number_max))
        self.socket_type_and_num_select.socket_num_reduce.clicked.connect(
            lambda: self.socket_type_and_num_select_dialog_socket_num_reduce(channel_number_min))
        self.socket_type_and_num_select.buttonBox.accepted.connect(qdialog.accept)
        self.socket_type_and_num_select.buttonBox.rejected.connect(qdialog.reject)
        self.socket_type_and_num_select.buttonBox.clicked.connect(
            partial(self.on_socket_type_select_dialog_option, include_num=True))

        qdialog.exec()

    def get_co_node_socket_type_list(self, op_code):
        items = []
        if op_code in [OP_NODE_CO_HW_IN, OP_NODE_CO_HW_OUT]:
            items = ['bool', 'int', 'float', 'string']
        elif op_code in [OP_NODE_CO_ADD, OP_NODE_CO_MULTIPLY, OP_NODE_CO_CLAMP, OP_NODE_CO_THRESHOLD,
                         OP_NODE_CO_LOOKUP_TABLE]:
            items = ['int', 'float']
        elif op_code in [OP_NODE_CO_CONSTANT, OP_NODE_CO_DELAY, OP_NODE_CO_METER]:
            items = ['bool', 'int', 'float']
        elif op_code in [OP_NODE_CO_INVERSE, OP_NODE_CO_POWER, OP_NODE_CO_SQRT, OP_NODE_CO_LOG, OP_NODE_CO_EXP]:
            items = ['float']
        elif op_code in [OP_NODE_CO_OR, OP_NODE_CO_AND, OP_NODE_CO_XOR, OP_NODE_CO_NOT]:
            items = ['bool']
        return items

    def onChannelDialogOptionPlus(self, num_max):
        num = self.node_channel_select.lineEdit.text()
        if int(num) < num_max:
            self.node_channel_select.lineEdit.setText(str(int(num) + 1))

    def onChannelDialogOptionReduce(self, num_mix):
        num = self.node_channel_select.lineEdit.text()
        if int(num) > num_mix:
            self.node_channel_select.lineEdit.setText(str(int(num) - 1))

    def selectNum(self):
        if self.input_data == 81:
            return 8
        else:
            return 32

    def onInDialogOptionPlus(self, max):
        num = self.node_in_out_select.lineEdit.text()
        if int(num) < max:
            self.node_in_out_select.lineEdit.setText(str(int(num) + 1))

    def onInDialogOptionReduce(self, min):
        num = self.node_in_out_select.lineEdit.text()
        if int(num) > min:
            self.node_in_out_select.lineEdit.setText(str(int(num) - 1))

    def onOutDialogOptionPlus(self, max):
        num = self.node_in_out_select.lineEdit_2.text()
        if int(num) < max:
            self.node_in_out_select.lineEdit_2.setText(str(int(num) + 1))

    def onOutDialogOptionReduce(self, min):
        num = self.node_in_out_select.lineEdit_2.text()
        if int(num) > min:
            self.node_in_out_select.lineEdit_2.setText(str(int(num) - 1))

    def onBandDialogOptionPlus(self):
        num = self.node_band_select.lineEdit.text()
        if int(num) < 32:
            self.node_band_select.lineEdit.setText(str(int(num) + 1))

    def onBandDialogOptionReduce(self):
        num = self.node_band_select.lineEdit.text()
        if int(num) > 1:
            self.node_band_select.lineEdit.setText(str(int(num) - 1))

    def onTapDialogOption(self, input_data):
        sb = self.node_tap_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            self.defaultNodeTap = int(self.node_tap_select.comboBox.currentText())
        else:
            self.defaultNodeTap = 0

    def on_node_configure_dialog_option(self, input_data):
        sb = self.node_configure_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            self.defaultNodeConfigure = str(self.node_configure_select.comboBox.currentText())
        else:
            self.defaultNodeConfigure = 0

    def on_socket_type_select_dialog_option(self, input_data, include_num=False):
        dialog_component = self.socket_type_and_num_select if include_num else self.socket_type_select

        sb = dialog_component.buttonBox.standardButton(input_data)
        socket_type = {"bool": 7, 'int': 8, 'float': 9, 'string': 10}

        if sb == QDialogButtonBox.Ok:
            self.defaultSocketType = socket_type[dialog_component.socket_type_comboBox.currentText()]
            if include_num:
                self.defaultSocketNum = int(dialog_component.socket_num_edit.text())
        else:
            self.defaultSocketType = 0
            if include_num:
                self.defaultSocketNum = 0

    def socket_type_and_num_select_dialog_socket_num_add(self, num_max):
        num = self.socket_type_and_num_select.socket_num_edit.text()
        if int(num) < num_max:
            self.socket_type_and_num_select.socket_num_edit.setText(str(int(num) + 1))

    def socket_type_and_num_select_dialog_socket_num_reduce(self, num_mix):
        num = self.socket_type_and_num_select.socket_num_edit.text()
        if int(num) > num_mix:
            self.socket_type_and_num_select.socket_num_edit.setText(str(int(num) - 1))

    def socket_type_and_num_select_dialog_validate_input(self, num_max, num_mix):
        line_edit = self.socket_type_and_num_select.socket_num_edit
        num = line_edit.text()
        if num.isdigit():
            num = int(num)
            if num < num_mix:
                line_edit.setText(str(num_mix))
            elif num > num_max:
                line_edit.setText(str(num_max))
        else:
            line_edit.setText(str(num_mix))

    def onOutDialogOption(self, input_data):
        sb = self.node_out_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            self.defaultNodeOut = int(self.node_out_select.comboBox.currentText())
        else:
            self.defaultNodeOut = 0

    def onChannelDialogOption(self, input_data):
        sb = self.node_channel_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            num = int(self.node_channel_select.lineEdit.text())
            channel_number_max, channel_number_min = self.get_node_channel_number(self.input_data)
            if num > channel_number_max or num < channel_number_min:
                statement = "Please enter the correct range(%s-%s)" % (channel_number_min, channel_number_max)
                QMessageBox.about(self.window(), "Refused", "%s" % statement)
            else:
                self.defaultNodeChannel = num
        else:
            self.defaultNodeChannel = 0

    def onInOutDialogOption(self, input_data):
        sb = self.node_in_out_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            num = int(self.node_in_out_select.lineEdit.text())
            num2 = int(self.node_in_out_select.lineEdit_2.text())
            self.defaultNodeIn = num
            self.defaultNodeOut = num2
        else:
            self.defaultNodeChannel = 0

    def onBandDialogOption(self, input_data):
        sb = self.node_band_select.buttonBox.standardButton(input_data)
        if sb == QDialogButtonBox.Ok:
            num = int(self.node_band_select.lineEdit.text())
            if num > 32 or num < 1:
                statement = "Please enter the correct range(1-32)"
                QMessageBox.about(self.window(), "Refused", "%s" % statement)
            else:
                self.defaultNodeChannel = num
                self.defaultControl = (self.node_band_select.comboBox_2.currentIndex() == 1)
                if self.input_data in [OP_NODE_BIQUAD_LOAD, OP_NODE_FIR_LOAD]:
                    self.defaultNodeBand = int(self.node_band_select.lineEdit_2.text())
                else:
                    self.defaultNodeBand = int(self.node_band_select.comboBox.currentText())
        else:
            self.defaultNodeTap = 0

    def get_node_channel_number(self, op_code):
        channel_number_max = 32
        channel_number_min = 1

        if op_code == OP_NODE_METER or op_code == OP_NODE_METER_FP:
            channel_number_max = 16
        elif op_code == OP_NODE_MUX or op_code == OP_NODE_MUX_FP:
            channel_number_max = 16
            channel_number_min = 4
        elif op_code == OP_NODE_NTTS_AGC:
            channel_number_max = 2
            channel_number_min = 1

        return channel_number_max, channel_number_min


    def getNodeChannelMaxAndMin(self, op_code):
        in_min = 1
        in_max = 8
        out_min = 1
        out_max = 8

        if op_code == OP_NODE_UPHEAR_VQE:
            out_min = 0
            out_max = 8

        return in_min, in_max, out_min, out_max

    def getNodesByOP(self, node_op: int, nodes: list):
        sortedNodes = []
        for node in nodes:
            if node.op_code == node_op:
                sortedNodes.append(node)
        sortedNodes = sorted(sortedNodes, key=operator.attrgetter('designator'))
        if Debug.DEBUG_Low_Level.value: print(sortedNodes)
        return sortedNodes

    def get_node_control_channel_number(self, op_code):
        control_channel_number_max = 16
        control_channel_number_min = 1

        return control_channel_number_max, control_channel_number_min

    # return index in self.window().sub_patchs
    def exist_in_sub_patchs_obj_index(self, title):
        index = -1
        sub_patchs_objs = self.window().sub_patchs
        for i in range(len(sub_patchs_objs)):
            if sub_patchs_objs[i].title == title and sub_patchs_objs[i].closed:
                index = i
        return index

    def collectNodesFromSubWnds(self, except_self=False):
        # 把所有視窗打開
        for node in self.window().findMain().widget().scene.nodes:
            if node.op_code == OP_NODE_SUBPATCH:
                self.window().open_subwindow_in_subpatch_recursively(node.title)
        windows = self.window().mdiArea.subWindowList()
        nodesSets = []
        for index in range(len(windows)):
            if except_self:
                if windows[index].widget() == self:
                    continue
            nodesSet = windows[index].widget().scene.nodes
            nodesSets = nodesSets + nodesSet
            if hasattr(windows[index].widget(), 'close_if_no_problem'):
                if windows[index].widget().close_if_no_problem:
                    self.window().close_sub_window(windows[index])
                if hasattr(windows[index].widget(), 'already_input_password'):
                    for sub_window in self.window().sub_patchs:
                        if (sub_window.title == windows[index].widget().title or sub_window.title == windows[index].widget().title + '.json'):
                            sub_window.already_input_password = windows[index].widget().already_input_password
                if hasattr(windows[index].widget(), 'correct_password'):
                    for sub_window in self.window().sub_patchs:
                        if (sub_window.title == windows[index].widget().title or sub_window.title == windows[index].widget().title + '.json'):
                            sub_window.correct_password = windows[index].widget().correct_password
                if hasattr(windows[index].widget(), 'encrypted'):
                    for sub_window in self.window().sub_patchs:
                        if (sub_window.title == windows[index].widget().title or sub_window.title == windows[index].widget().title + '.json'):
                            sub_window.encrypted = windows[index].widget().encrypted
        return nodesSets

    def findMinimalConseqSequence(self, nodes: list):
        n = len(nodes)
        count = 0
        res = 0

        if n == 0:
            return 1

        elif n == 1:
            if nodes[0].designator == 1:
                return 2
            else:
                return 1

        for index in range(n):
            if (index > 0 and not nodes[index].designator == nodes[index - 1].designator + 1):
                return nodes[index - 1].designator + 1
            elif (index > 0 and not index + 1 == nodes[index].designator):
                return index
            elif (index > 0 and nodes[index].designator == nodes[index - 1].designator + 1):
                count = count + 1
                res = nodes[index].designator

        return res + 1

    def showEvent(self, event):
        super().showEvent(event)
        # Set the attributes for QMdiSubWindow objects to improve the performance.
        if type(self.parentWidget()) == QMdiSubWindow:
            self.parentWidget().setAttribute(Qt.WA_OpaquePaintEvent)
            self.parentWidget().setAttribute(Qt.WA_NoSystemBackground)
