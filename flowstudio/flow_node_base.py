import time

from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER
from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import *

from flowstudio.flow_node_property import NODE_Propertys
from flowstudio.flow_scoket import FLOW_Socket
from flowstudio.flow_ctrl_manager import *
from flowstudio.flow_window_connection import *

from template.node_title_edit import Ui_nodetitleDialog

from functools import partial
from flowstudio import flow_conf

from flowstudio.functions.node_change_channel_imp import change_channel_implementation
from control.flow_control_widget import TapMenu as TapMenuUI

DEBUG = False
DEBUG_Content = False
DEBUG_Tweaker = False
DEBUG_Serialize = False

NODE_COLORS = [
    "#000000",
    "#FF7F00",
    "#00557F",
    "#AA0000",
    "#55AA00",
    "#0055FF",
    "#8B00FF",
    "#FF3131",
    "#571e50",
    "#233b52",
    "#182b22",
    "#662d27"
]

CO_NODE_COLORS = [
    "#000000",
    "#156082",
    "#aa0000",
    "#8b00ff",
    "#55aa00",
    "#f57a01"
]


class FLOW_GraphicsNode(QDMGraphicsNode):

    def initSizes(self):
        super().initSizes()
        self.title_height = 24.0
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10
        self.selected_time = 0
        if not self.node.is_temp_node:
            if self.node.manager.size == 0 and not self.node.content_label_objname == "SUBPATCH":
                self.height = 60
            elif self.node.content_label_objname in ["IN", "OUT"]:
                self.height = 60
                self.title_height = 48.0
            elif self.node.content_label_objname in ["MUX", "MUX_ST", 'MUX_FP']:
                max_val = lambda m, n: m if m > n else n
                height = self.title_height + 10 + (22 * max_val(len(self.node.inputlist), len(self.node.outputlist)))
                if height <= 200:
                    self.height = 200
                else:
                    self.height = height
                internal_height = self.node.manager.initPos()
                # we don't need internal height to process here...
            elif self.node.content_label_objname in ["SUBPATCH"]:
                max_val = lambda m, n: m if m > n else n
                height = 30 * max_val(len(self.node.inputlist), len(self.node.outputlist))
                if height <= 80:
                    self.height = 80
                else:
                    self.height = height
            elif self.node.op_code == flow_conf.OP_NODE_AI_BF:
                internal_height = self.node.manager.initPos()
                self.height = 100 + internal_height
            else:
                internal_height = self.node.manager.initPos()
                self.height = 60 + internal_height

            # self.width = 220 if self.node.manager.size else 100
            max_width = 80
            for widget in self.node.manager.widgetSet.values():
                if type(widget) is not TapMenuUI and widget.layout().maximumSize().width() > max_width:
                    max_width = widget.layout().maximumSize().width()

            if self.node.content_label_objname in ['GAIN', 'GAIN_FP']:
                if len(self.node.inputs) <= 8:
                    self.height = self.title_height + 200
                else:
                    self.height = self.title_height + len(self.node.inputs) * 22
                self.width = 140
                widget.setGeometry(0, 0, self.width, self.height - self.title_height)
            elif self.node.content_label_objname in ['LPF', 'HPF', 'HPF_FP', 'LPF_FP', 'IIRCOEF', 'FIR', 'ATTEN', 'POLARITY'
                                                     , 'CLIPPER', 'DELAY', 'DELAY_FP', 'IIRCEOF_FP', 'FIR_FP', 'CLIPPER_FP']:
                self.width = max_width + 20
                if len(self.node.inputs) <= 5:
                    self.height = self.title_height + 110
                else:
                    self.height = self.title_height + len(self.node.inputs) * 22
            elif self.node.content_label_objname in ['DEESSER']:
                self.width = max_width + 20
                if len(self.node.inputs) > 9:
                    self.height = self.title_height + len(self.node.inputs) * 22
            elif self.node.content_label_objname in ['GAME_EQ']:
                self.width = max_width + 20
                if len(self.node.inputs) > 4:
                    self.height = self.title_height + len(self.node.inputs) * 22 + 10
            elif self.node.content_label_objname in ['PEQ', 'LIMITER', 'COMP', 'PEQ_FP', 'LIMITER_FP', 'COMP_FP', 'PEQ_V2']:
                self.width = max_width + 20
                if len(self.node.inputs) > 14:
                    self.height = self.title_height + len(self.node.inputs)*22
            elif self.node.content_label_objname in ['GATE', 'SMART_GATE']:
                self.width = max_width + 20
                self.height = 365
                if len(self.node.inputs) > 14:
                    self.height = self.title_height + (len(self.node.inputs)+1)*22 +10
            elif self.node.content_label_objname in ['COMP']:
                self.width = max_width + 20
                if len(self.node.inputs) > 17:
                    self.height = self.title_height + len(self.node.inputs) * 22
            elif self.node.content_label_objname in ['COMP_Combo', 'COMP_Combo_FP']:
                self.width = max_width + 20
                if len(self.node.inputs) > 21:
                    self.height = self.title_height + len(self.node.inputs) * 22
            elif self.node.content_label_objname in ['MIXER', 'MIXER_FP']:
                self.width = max_width + 20
                self.height = self.title_height + 70 + len(self.node.inputs) * 30
            elif self.node.content_label_objname in ['METER', 'METER_FP']:
                self.width = max_width + 20
                self.height = self.title_height + len(self.node.inputs) * 22
            elif self.node.content_label_objname in ['BIQUAD', 'BIQUAD_LOAD', 'FIR_LOAD']:
                self.width = max_width + 45
            elif self.node.content_label_objname in ['NEGATOR', 'MERGER']:
                self.width = max_width + 30
            elif self.node.content_label_objname in ['MULTIPLIER', 'SUBPATCH']:
                self.width = max_width + 45
            elif self.node.content_label_objname in ['WAVPLAYER']:
                self.width = max_width + 20
                self.height = self.title_height + len(self.node.outputlist) * 22
            elif self.node.content_label_objname in ['CINGO', 'CINGO_SPK']:
                self.width = 100
                self.height = 40 + len(self.node.inputlist) * 22
            elif self.node.content_label_objname in ['SMART_EQ']:
                self.width = max_width + 20
                self.height = 190
            elif self.node.content_label_objname in ['MUTE']:
                self.width = max_width + 30
                self.height = self.title_height + 30 + len(self.node.outputlist) * 22
            elif self.node.content_label_objname in ['DIRAC']:
                self.width = max_width + 30
                self.height = self.title_height + 290 + len(self.node.outputlist) * 28
            elif self.node.type_ao_addition == flow_conf.TypeAOAddition.FIXED.value:
                self.height = self.node.manager.initPos() + self.title_height + 30
                self.width = max_width + 20
            else:
                if len(self.node.inputlist) >= 2 or len(self.node.outputlist) >= 2:
                    self.height += (max(len(self.node.inputlist), len(self.node.outputlist)) - 1) * 22
                if len(self.node.inctrllist) > 0 or len(self.node.outctrllist) >= 0:
                    self.height += (max(len(self.node.inctrllist), len(self.node.outctrllist)) - 1) * 22
                self.width = max_width + 20
        else:
            internal_height = self.node.manager.initPos()
            self.height = 60 + internal_height
            if len(self.node.inputs) >= 2 or len(self.node.outputs) >= 2:
                self.height += (max(len(self.node.inputs), len(self.node.outputs)) - 1) * 22
            if len(self.node.inctrls) > 0 or len(self.node.outctrls) >= 0:
                self.height += (max(len(self.node.inctrls), len(self.node.outctrls)) - 1) * 22
            max_width = 80
            for widget in self.node.manager.widgetSet.values():
                if type(widget) is not TapMenuUI and widget.layout().maximumSize().width() > max_width:
                    max_width = widget.layout().maximumSize().width()
            self.width = max_width + 20

    def initTitle(self):
        super().initTitle()
        self.designator_item = QGraphicsTextItem(self)
        self.designator_item.node = self.node
        self.designator_item.setDefaultTextColor(self._title_color)
        self.designator_item.setFont(self._title_font)
        self.designator_item.setPos(self.title_horizontal_padding, 24)
        self.designator_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def initAssets(self):
        super().initAssets()
        self._title_font = QFont("Calibri", 10, QFont.Bold)
        self.icons = QImage("../resources/dirty.png")
        self.not_supported_icon = QImage("../resources/not_support.png")

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        if self.isSelected():
            if self.selected_time == 0:
                self.selected_time = time.time()
        else:
            self.selected_time = 0

        offset = 24
        if self.node.isDirty() and self.node.showDirty:
            offset = 0.0

        if self.node.showDirty and (not self.node.is_supported() or not self.node.is_user_has_permission() or not self.node.is_support_feedback_path()):
            offset = 24
            painter.drawImage(
                QRectF(-10, -10, 24.0, 24.0),
                self.not_supported_icon,
                QRectF(0, 0, 24.0, 24.0)
            )

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class FLOW_Content(QDMNodeContentWidget):

    def __init__(self, node: 'Node', widget=None):
        super().__init__(node)
        self.node.manager.initNodeParam(self, True)

    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)
        if self.node.op_code == flow_conf.OP_NODE_SUBPATCH:
            for i in range(1, len(self.node.inputlist) + 1):
                label = QLabel(str(i), self)
                label.move(10, 10 + 21.5 * (i - 1))
            for i in range(1, len(self.node.outputlist) + 1):
                label = QLabel(str(i), self)
                label.move(105, 10 + 21.5 * (i - 1))
        elif self.node.op_code == flow_conf.OP_NODE_SMART_GATE:
            label = QLabel('VAD', self)
            height = 365
            if len(self.node.inputlist) > 14:
                height = 24 + (len(self.node.inputlist) + 1) * 22 + 10
            label.move(10, height - 48)

    def serialize(self):
        res = super().serialize()
        res.update(self.node.manager.Parameter)
        if Debug.DEBUG_SERIALIZE.value: print("Serialized FLOW_Content '%s'" % self.__class__.__name__, "res:", res)
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.node.manager.Parameter = data
            return True & res
        except Exception as e:
            dumpException(e)
        if Debug.DEBUG_SERIALIZE.value: print("Derialized FLOW_Content '%s'" % self.__class__.__name__, "res:", res)
        return res


class FLOW_GUI(QWidget):

    def __init__(self, node: 'Node'):
        super().__init__(parent=node.scene.getView().window())
        self.node = node
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.initInnerClasses()
        self.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.setStyleSheet("QLabel{color:#e0e0e0;}")

    def initInnerClasses(self):
        self.gui_manager = FLOW_Ctrl_Manager(None, **self.node.manager.config)
        self.gui_manager.initNodeParam(self, False)
        self.mapping()
        self.gui_manager.initPos()

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self in FLOW_Window_Connection.show_window_objects:
            FLOW_Window_Connection.show_window_objects.remove(self)
        super().closeEvent(a0)

    def initExtraWidget(self):
        '''
        Instantiate the extra widget in the GUI window, such as plot widget, dot widget, control widget...
        create the signal/slot connection between extra widgets object and child method.

        :return:
        '''
        raise NotImplemented()

    def initPlot(self):
        '''
        Instantiate all plot objects inside this method.

        :return:
        '''
        raise NotImplemented()

    def initLayout(self):
        '''
        Implement vertical and horizontal layout in this method.

        :return:
        '''
        raise NotImplemented()

    def ctrl2plot(self, key):
        '''
        Implement the link between parameter control and graphic plot here.

        :param key: to retrieve the data in GUI widgetSet(:type GUI widgetSet: dict)
        :type key: str
        :return:
        '''
        raise NotImplemented()

    def followUp(self):
        '''
        You need to implement this method when the incoming data needed to be coupled with the algorithm model.
        take COMP as example: when the user is adjusting the parameter with an updating dot,
        the updating dot will be un-linked with the dynamic range control plot,
        due to low-level has a slower response for parameter changed.
        when we changed parameter, property/value assigned by fetchData will be called to this method,
        in order to keep the communication response align with our algorithm model.

        :return:
        '''
        raise NotImplemented()

    def addPlotItem(self):
        '''
        Add item in viewbox

        :return:
        '''
        raise NotImplemented()

    def cleanPlotItem(self):
        '''
        Remove item in viewbox

        :return:
        '''
        raise NotImplemented()

    def fetchData(self):
        '''
        Query the raw data from low-levle server.

        :return:
        '''
        raise NotImplemented()

    def process(self):
        '''
        Process raw data from the socket's thread and update the plot.

        :return:
        '''
        raise NotImplemented()

    def phaseVisible(self):
        '''
        Handle to enable/disable phase plot.

        :return:
        '''
        raise NotImplemented()

    def mapping(self):
        '''
        Mapping the value from GUI widgetSet to the value in Node widgetSet, using the valueStored signal.

        :return:
        '''
        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.valueGUI_valueNode, key))

    def valueGUI_valueNode(self, key):
        self.node.manager.widgetSet[key].widget_value = self.gui_manager.widgetSet[key].widget_value

    def refresh(self):
        '''
        This method will be called before opening GUI window,
        copy the value from Node widgetSet to GUI widgetSet without triggering valueChanged and valueStored.

        :return:
        '''
        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].widget_value = self.node.manager.widgetSet[key].widget_value


class FLOW_Node(Node):
    GraphicsNode_class = QDMGraphicsNode
    NodeContent_class = QDMNodeContentWidget
    Socket_class = FLOW_Socket

    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "flow_node_bg"
    display_name = ''
    expandable = False
    openable = False
    showDirty = False
    is_feedback = False
    linkType = 0
    node_type = "AO"
    _designator = 0
    description = ''
    info = ''
    is_float_point = True
    type_ao_addition = flow_conf.TypeAOAddition.FIXED.value
    is_temp_node = False
    cSocket = FLOW_Window_Connection.client

    def __init__(self, scene, inputs=None, outputs=None, inctrls=None, outctrls=None, mic=0, ref=0, rule_check_mode=-1):
        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        if inctrls is None:
            inctrls = []
        if outctrls is None:
            outctrls = []
        self.inputlist = inputs
        self.outputlist = outputs
        self.inctrllist = inctrls
        self.outctrllist = outctrls
        self.mic = mic
        self.ref = ref
        self.scene = scene
        self.rule_check_mode = rule_check_mode
        super().__init__(scene, self.op_title, inputs, outputs, inctrls, outctrls)
        if self.expandable: self.expand = True
        self.initNodeColor()
        self.initSocketTooltip()
        # it's really important to mark all nodes Dirty by default
        self.markDirty()
        self.tap_menu_parameter_name = self.manager.tap_menu_parameter_name

    def __del__(self):
        if self.openable:
            try:
                if self.widget.isVisible(): self.widget.close()
            except:
                if Debug.DEBUG_Low_Level.value: print('%s node has been deleted'%(self.content_label_objname))

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname, self.is_temp_node)
        if hasattr(self, 'tap'):
            self.manager.config[self.manager.tap_menu_parameter_name].parameters['pSize'] = self.tap

        self.content = FLOW_Content(self)

        self.grNode = FLOW_GraphicsNode(self)
        if self.openable: self.widget = FLOW_GUI(self)

    def initNodeColor(self):
        """Initialize node color based on node type and operation code"""
        if self.node_type == "AO":
            index = self.get_ao_category_index()
            color = NODE_COLORS[index]
        else:
            index = self.get_control_category_index()
            color = CO_NODE_COLORS[index]

        # Set node color
        self.grNode._brush_title = QBrush(QColor(color))
        self.title_background_color = color

    def get_ao_category_index(self):
        """Get category index for AO type nodes"""
        categories = list(flow_conf.CATE_AO_MAPPING.keys())

        for category, values in flow_conf.CATE_AO_MAPPING.items():
            if not values:
                continue

            # Check if it's a Company type
            if isinstance(values[0], flow_conf.Company):
                for company in values:
                    if self.op_code in company.ao_list:
                        return categories.index(category)
            else:
                if self.op_code in values:
                    return categories.index(category)

        return 0  # Default to first category index

    def get_control_category_index(self):
        """Get category index for control type nodes"""
        import flowstudio.flow_conf_co as flow_conf_co
        categories = list(flow_conf_co.CATE_CONTROL_MAPPING.keys())

        for category, values in flow_conf_co.CATE_CONTROL_MAPPING.items():
            if self.op_code in values:
                return categories.index(category)

        return 0 # Default to first category index

    def initSocketTooltip(self):
        control_socket_type_list = {1: '', 7: "bool", 8: 'int', 9: 'float', 10: 'string'}
        for socket in (self.outputs + self.inputs + self.inctrls + self.outctrls):
            socket.setSocketPositionHorizontal()

        for input in self.inputs:
            input.grSocket.setToolTip("input")

        for output in self.outputs:
            output.grSocket.setToolTip("output")

        for inctrl in self.inctrls:
            inctrl.grSocket.setToolTip(f"input ({control_socket_type_list[int(inctrl.socket_type)]})")

        for outctrl in self.outctrls:
            outctrl.grSocket.setToolTip(f"output ({control_socket_type_list[int(outctrl.socket_type)]})")

    @property
    def designator(self):
        return self._designator

    @designator.setter
    def designator(self, input_data):
        self._designator = input_data
        # if self.content_label_objname == "IN" or self.content_label_objname == "OUT":
        #     self.grNode.designator_item.setPlainText(self.content_label_objname + '_' + str(input_data))

    def initControl(self):
        if self.manager.config.get(self.manager.tap_menu_parameter_name):
            keylist = [*self.manager.config[self.manager.tap_menu_parameter_name].parameters['cParameter']]
        else:
            keylist = []

        for key in self.manager.widgetSet:
            if any([name in key for name in keylist]):
                new_key = key.split('_')
                key_name = new_key[0]
                key_index = new_key[1]
                self.manager.widgetSet[key].valueChanged.connect(partial(self.tweaker, [key_index, key_name, key]))
            elif key == self.manager.tap_menu_parameter_name:
                pass
            else:

                self.manager.widgetSet[key].valueChanged.connect(partial(self.tweaker, key))

    def tweaker(self, key):

        cmd = None
        if isinstance(key, str):
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name = key
            Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
            cmd = "set/%s/%s/%s/" % (AO_Name, Parameter_Name, Parameter_Value)

        elif isinstance(key, list):
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Index = key[0]
            Parameter_Name = key[1]
            Parameter_Value = self.manager.widgetSet[key[2]].widget_value[1] if isinstance(
                self.manager.widgetSet[key[2]].widget_value, list) else self.manager.widgetSet[key[2]].widget_value
            cmd = "setCoord/%s/%s/%s/%s/0" % (AO_Name, Parameter_Name, Parameter_Value, Parameter_Index)

        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        if self.node_type == "AO":
            self.inctrl_socket_position = LEFT_BOTTOM
            self.outctrl_socket_position = RIGHT_BOTTOM
        else:
            self.inctrl_socket_position = LEFT_TOP
            self.outctrl_socket_position = RIGHT_TOP

    def evalImplementation(self):
        inputFlag = self.dynamicRuleCheck(self.rule_check_mode if len(self.inputs) else [], self.inputs)
        outputFlag = self.dynamicRuleCheck(self.rule_check_mode if len(self.outputs) else [], self.outputs)
        res = inputFlag and outputFlag
        if self.rule_check_mode == -1:
            if hasattr(self, 'input_connected_indices') and hasattr(self, 'output_connected_indices') and \
                    len(self.inputs) == len(self.outputs):
                self.input_connected_indices.sort()
                self.output_connected_indices.sort()
                if self.input_connected_indices != self.output_connected_indices:
                    res = False
        if res:
            self.grNode.setToolTip("")
            self.markInvalid(False)
            self.markDirty(False)
        else:
            self.markDirty()

    def getOutputWithSocket(self, index: int = 0) -> [('Node', 'Socket'), (None, None)]:
        """
        Get the **first**  `Node` connected to the Output specified by `index` and the connection `Socket`

        :param index: Order number of the `Output Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node_node.Node` and :class:`~nodeeditor.node_socket.Socket` which
            is connected to the specified `Output` or ``None`` if there is no connection of index is out of range
        :rtype: (:class:`~nodeeditor.node_node.Node`, :class:`~nodeeditor.node_socket.Socket`)
        """
        try:
            output_socket = self.outputs[index]
            if len(output_socket.edges) == 0: return None, None
            connecting_edge = output_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.outputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            dumpException(e)
            return None, None

    def getIOWithSocket(self, index, input_or_output):
        '''
        :param index: socket index in node object
        :type index: int
        :param input_or_output: select self.inputs/self.outputs to check
        :type input_or_output: list
        :return: list; while self.inputs selected, "source of node" and "source of socket" returned as a list
        :return: list; while self.outputs selected, "destination of node" and "destination of socket" returned as a list
        '''
        if input_or_output == self.inputs:
            src_node, src_socket = self.getInputWithSocket(index)
            try:
                return (src_node, src_socket.is_output)
            except:
                return (False, False)
        elif input_or_output == self.outputs:
            dst_node, dst_socket = self.getOutputWithSocket(index)
            try:
                return (dst_node, dst_socket.is_input)
            except:
                return (False, False)
        else:
            pass

    def dynamicRuleCheck(self, socket_list, io_list):
        '''
        :param socket_list: -1, return True while one of the sockets connected
        :param socket_list: -2, return True while all of the sockets connected
        :param socket_list: [], return True while specific socket connected
        :type socket_list: list or integer
        :param io_list: select self.inputs/self.outputs to check
        :type io_list: list
        :return: bool
        '''
        if socket_list == -1:
            res = False
            if io_list == self.inputs:
                type_channel = 'input'
                self.input_connected_indices = []
            if io_list == self.outputs:
                type_channel = 'output'
                self.output_connected_indices = []
            for socket in io_list:
                index = socket.index
                node, socket = self.getIOWithSocket(index, io_list)
                if node and socket:
                    if type_channel == 'input':
                        self.input_connected_indices.append(index)
                    elif type_channel == 'output':
                        self.output_connected_indices.append(index)
                    res = True
            return res


        elif socket_list == -2:
            flag = []
            for socket in io_list:
                node, socket = self.getIOWithSocket(socket.index, io_list)
                if not (node and socket):
                    return False
                else:
                    flag.append(True)
                    if len(flag) == len(io_list): return True

        elif isinstance(socket_list, list):
            flag = []
            if len(socket_list):
                for index in socket_list:
                    node, socket = self.getIOWithSocket(index, io_list)
                    if not (node and socket):
                        return False
                    else:
                        flag.append(True)
                        if len(flag) == len(socket_list): return True
            elif len(io_list):
                if self.dynamicRuleCheck(-1, io_list):
                    return False
                else:
                    return True
            else:
                return True

    def getChildrenNodes(self) -> 'List[Node]':
        return super().getChildrenNodes()

    def getParentNodes(self) -> 'List[Node]':
        """
        Retreive all first-level children connected to this `Node` `Outputs`

        :return: list of `Nodes` connected to this `Node` from all `Outputs`
        :rtype: List[:class:`~nodeeditor.node_node.Node`]
        """
        if self.inputs == []: return []
        other_nodes = []
        for ix in range(len(self.inputs)):
            for edge in self.inputs[ix].edges:
                other_node = edge.getOtherSocket(self.inputs[ix]).node
                other_nodes.append(other_node)
        return other_nodes

    def eval(self, index=0):
        if not self.isDirty() and not self.isInvalid():
            if Debug.DEBUG_Low_Level.value: print(" _> returning cached %s" % self.__class__.__name__)
        try:
            self.evalImplementation()
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def evalChildren(self):
        super().evalChildren()

    def evalParents(self):
        """Evaluate all children of this `Node`"""
        for node in self.getParentNodes():
            node.eval()

    def onInputChanged(self, new_edge):
        if Debug.DEBUG_Low_Level.value: print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def onOutputChanged(self, new_edge):
        if Debug.DEBUG_Low_Level.value: print("%s::__onOutputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def renameNode(self):
        qdialog = QDialog(self.scene.getView().window())
        qdialog.setWindowTitle('Rename Node')
        self.renameDialog = Ui_nodetitleDialog()
        self.renameDialog.setupUi(qdialog)

        regexp = QRegExp("[a-z-A-Z-0-9_]+")
        validator = QRegExpValidator(regexp, self.renameDialog.lineEdit)
        self.renameDialog.lineEdit.setValidator(validator)

        self.renameDialog.lineEdit.setText(self.grNode.title)
        self.renameDialog.buttonBox.clicked.connect(self.onDialogOption)

        qdialog.setWindowTitle("Rename Node")
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def on_delete_node(self):
        self.grNode.setSelected(True)
        self.scene.getView().window().onEditDelete()

    def onColorSelect(self):
        tempWidget = QMainWindow()
        tempWidget.setStyleSheet("font:11pt Calibri;")
        tempWidget.setWindowIcon(QIcon("../resources/main-theme.png"))

        colorSelector = QColorDialog()
        color = colorSelector.getColor(initial=QColor(self.title_background_color), parent=tempWidget)
        if color.isValid():
            self.grNode._brush_title = QBrush(QColor(color.name()))
            self.title_background_color = color.name()

    def Tap(self, isPlus, op=''):
        self.lists = self.manager.Parameter
        hashmap = {}
        history_stamp = self.scene.history.history_stack[self.scene.history.history_current_step]
        edges = history_stamp['snapshot']['edges']
        edge = []
        x = self.pos.x()
        y = self.pos.y()
        title = self.title
        self.grNode.node.remove()
        if isPlus == 0:
            self.tap += 1
        elif isPlus == 1:
            self.tap -= 1
        self.initInnerClasses()
        node_data = dict(self.serialize())
        if op == 'MIXER':
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')),
                                                                  len(node_data.get('outputs')))
        elif op == 'MUX':
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('outputs')))
        elif op == 'METER':
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')))
        elif self.op_title == 'BIQUAD':
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data['content'][node_data['tap_menu_parameter_name']][1],
                                                                  len(node_data.get('inputs')))

        elif op == '':
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data['content'][node_data['tap_menu_parameter_name']][1],
                                                                  len(node_data.get('inputs')),self.lists)

        new_node.deserialize(node_data, hashmap, True)
        new_node.setPos(x, y)
        new_node.setTitle = title
        for hash in hashmap:
            for edge_data in edges:
                if edge_data['start'] == hash:
                    edge.append(edge_data)

                if edge_data['end'] == hash:
                    edge.append(edge_data)

        for node in self.scene.nodes:
            for out in node.outputs:
                for edge_data in edge:
                    if out.id == edge_data['start']:
                        for node1 in self.scene.nodes:
                            for input in node1.inputs:
                                if input.id == edge_data['end']:
                                    Edge(self.scene, out, input, EDGE_TYPE_BEZIER)

        for i in range(len(self.scene.nodes)):
            self.scene.nodes[i].setDirty()

        self.scene.history.storeHistory(f"Add/Reduce Band Node-{self.__class__.__name__}-{self.title}",
                                        setModified=True)

    def addChannel(self, add_inlet=True, add_outlet=True):
        if self.node_type == 'CO':
            self.co_input_list_output_list_adjust(self.inctrllist, self.outctrllist, True)
        else:
            if self.content_label_objname == 'MUX':
                for i in range(4):
                    self.inputlist.append(1)
                self.outputlist.append(1)
            elif self.content_label_objname == 'METER':
                self.inputlist.append(1)
            else:
                if add_inlet:
                    self.inputlist.append(1)
                if add_outlet:
                    self.outputlist.append(1)

        index = []
        input_edges = []
        input_node = []
        for i in range(len(self.grNode.node.inputs)):
            input_edges.append(self.grNode.node.inputs[i].edges)
            input_node.append(self.grNode.node.inputs[i])
            index.append(i)
            # if self.grNode.node.inputs[i].edges != []:
            #     input_edges.append(self.grNode.node.inputs[i].edges)
            #     input_node.append(self.grNode.node.inputs[i])
            #     index.append(i)
        out_edges = []
        out_node = []
        outdex = []
        for i in range(len(self.grNode.node.outputs)):
            out_edges.append(self.grNode.node.outputs[i].edges)
            out_node.append(self.grNode.node.outputs[i])
            outdex.append(i)
            # if self.grNode.node.outputs[i].edges != []:
            #     out_edges.append(self.grNode.node.outputs[i].edges)
            #     out_node.append(self.grNode.node.outputs[i])
            #     outdex.append(i)
        inctrl_edges = []
        inctrl_nodes = []
        inctrldex = []
        for i in range(len(self.grNode.node.inctrls)):
            inctrl_edges.append(self.grNode.node.inctrls[i].edges)
            inctrl_nodes.append(self.grNode.node.inctrls[i])
            inctrldex.append(i)
        outctrl_edges = []
        outctrl_nodes = []
        outctrldex = []
        for i in range(len(self.grNode.node.outctrls)):
            outctrl_edges.append(self.grNode.node.outctrls[i].edges)
            outctrl_nodes.append(self.grNode.node.outctrls[i])
            outctrldex.append(i)

        self.adjust_sockets(original_inputs=self.inputs, input_list=self.inputlist,
                            original_outputs=self.outputs, output_list=self.outputlist,
                            original_inctrls=self.inctrls, inctrl_list=self.inctrllist,
                            original_outctrls=self.outctrls, outctrl_list=self.outctrllist)

        for i in range(len(input_edges)):
            self.grNode.node.inputs[index[i]].edges = input_edges[i]
            socket = self.grNode.node.inputs[index[i]].grSocket
            self.grNode.node.inputs[index[i]] = input_node[i]
            self.grNode.node.inputs[index[i]].grSocket = socket

        for i in range(len(out_edges)):
            self.grNode.node.outputs[outdex[i]].edges = out_edges[i]
            socket = self.grNode.node.outputs[outdex[i]].grSocket
            self.grNode.node.outputs[outdex[i]] = out_node[i]
            self.grNode.node.outputs[outdex[i]].grSocket = socket

        for i in range(len(inctrl_edges)):
            self.grNode.node.inctrls[inctrldex[i]].edges = inctrl_edges[i]
            socket = self.grNode.node.inctrls[inctrldex[i]].grSocket
            self.grNode.node.inctrls[inctrldex[i]] = inctrl_nodes[i]
            self.grNode.node.inctrls[inctrldex[i]].grSocket = socket

        for i in range(len(outctrl_edges)):
            self.grNode.node.outctrls[outctrldex[i]].edges = outctrl_edges[i]
            socket = self.grNode.node.outctrls[outctrldex[i]].grSocket
            self.grNode.node.outctrls[outctrldex[i]] = outctrl_nodes[i]
            self.grNode.node.outctrls[outctrldex[i]].grSocket = socket

        self.grNode.initSizes()
        for socket in (self.grNode.node.outputs + self.grNode.node.inputs + self.grNode.node.inctrls + self.grNode.node.outctrls):
            socket.setSocketPosition()
        self.updateConnectedEdges()
        self.content.setFixedHeight(self.grNode.height)

        if self.content_label_objname == 'MUX':
            self.Tap(3, 'MUX')
        elif self.content_label_objname == 'METER':
            self.Tap(3, 'METER')
        elif self.content_label_objname == 'UpHear_VQE':
            self.initInnerClasses()

        if self.op_code == flow_conf.OP_NODE_SUBPATCH:
            current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
            self.update_self_node_display()
            self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
            # self.scene.getView().window().setActiveSubWindow(current_window.parent())
            current_sub_windows = self.scene.getView().window().mdiArea.subWindowList()
            for sub_window in current_sub_windows:
                sub_window_name = sub_window.widget().getPrettyFilename()
                if sub_window_name == self.title:
                    if add_inlet and not add_outlet:
                        index = len(self.inputlist) - 1
                    elif not add_inlet and add_outlet:
                        index = len(self.outputlist) - 1
                    from flowstudio.nodes import INLET
                    from flowstudio.nodes import OUTLET
                    if add_inlet and not add_outlet:
                        node = INLET.FLOW_Node_INLET(sub_window.widget().scene)
                    elif not add_inlet and add_outlet:
                        node = OUTLET.FLOW_Node_OUTLET(sub_window.widget().scene)
                    node.designator = index + 1
                    node.grNode.title += '_' + str(index + 1)
                    node.title += '_' + str(index + 1)
                    if add_inlet and not add_outlet:
                        node.setPos(-400, -150 + index * 150)
                    elif not add_inlet and add_outlet:
                        node.setPos(400, -150 + index * 150)
                    node_data = node.serialize()
                    # 加入到subpatch window的所有history stamp
                    for i in range(len(sub_window.widget().scene.history.history_stack)):
                        if node_data not in \
                                sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes']:
                            sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes'].append(node_data)
            for sub_window in current_sub_windows:
                if hasattr(sub_window.widget(), 'close_if_no_problem'):
                    if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                        self.scene.getView().window().close_sub_window(sub_window)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
        if add_inlet and add_outlet:
            self.scene.history.storeHistory(f"Add Channel Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)
        elif add_inlet and not add_outlet:
            self.scene.history.storeHistory(f"Add Inlet Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)
        elif not add_inlet and add_outlet:
            self.scene.history.storeHistory(f"Add Outlet Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)

    def adjust_sockets(self, original_inputs, input_list, original_outputs, output_list,
                       original_inctrls=None, inctrl_list=None,
                       original_outctrls=None, outctrl_list=None):
        if len(input_list) > len(original_inputs):
            diff = len(input_list) - len(original_inputs)
            for i in range(len(original_inputs), len(original_inputs) + diff):
                node_side = 2
                for item in input_list[len(original_inputs):]:
                    socket = self.__class__.Socket_class(
                        node=self, index=i, position=self.input_socket_position,
                        socket_type=item, multi_edges=self.input_multi_edged,
                        count_on_this_node_side=node_side, is_input=True
                    )
                    self.inputs.append(socket)
        elif len(input_list) < len(original_inputs):
            diff = len(original_inputs) - len(input_list)
            for i in range(diff):
                socket_to_remove = self.inputs.pop()
                self.scene.grScene.removeItem(socket_to_remove.grSocket)

        if len(output_list) > len(original_outputs):
            diff = len(output_list) - len(original_outputs)
            for i in range(len(original_outputs), len(original_outputs) + diff):
                node_side = 2
                for item in output_list[len(original_outputs):]:
                    socket = self.__class__.Socket_class(
                        node=self, index=i, position=self.output_socket_position,
                        socket_type=item, multi_edges=self.output_multi_edged,
                        count_on_this_node_side=node_side, is_input=False
                    )
                    self.outputs.append(socket)
        elif len(output_list) < len(original_outputs):
            diff = len(original_outputs) - len(output_list)
            for i in range(diff):
                socket_to_remove = self.outputs.pop()
                self.scene.grScene.removeItem(socket_to_remove.grSocket)

        if len(inctrl_list) > len(original_inctrls) and original_inctrls is not None and inctrl_list is not None:
            diff = len(inctrl_list) - len(original_inctrls)
            for i in range(len(original_inctrls), len(original_inctrls) + diff):
                node_side = 2
                for item in inctrl_list[len(original_inctrls):]:
                    socket = self.__class__.Socket_class(
                        node=self, index=i, position=self.inctrl_socket_position,
                        socket_type=item, multi_edges=self.output_multi_edged,
                        count_on_this_node_side=node_side, is_input=True
                    )
                    self.inctrls.append(socket)
        elif len(inctrl_list) < len(original_inctrls):
            diff = len(original_inctrls) - len(inctrl_list)
            for i in range(diff):
                socket_to_remove = self.inctrls.pop()
                self.scene.grScene.removeItem(socket_to_remove.grSocket)

        if len(outctrl_list) > len(original_outctrls) and original_outctrls is not None and outctrl_list is not None:
            diff = len(outctrl_list) - len(original_outctrls)
            for i in range(len(original_outctrls), len(original_outctrls) + diff):
                node_side = 2
                for item in outctrl_list[len(original_outctrls):]:
                    socket = self.__class__.Socket_class(
                        node=self, index=i, position=self.outctrl_socket_position,
                        socket_type=item, multi_edges=self.output_multi_edged,
                        count_on_this_node_side=node_side, is_input=False
                    )
                    self.outctrls.append(socket)
        elif len(outctrl_list) < len(original_outctrls):
            diff = len(original_outctrls) - len(outctrl_list)
            for i in range(diff):
                socket_to_remove = self.outctrls.pop()
                self.scene.grScene.removeItem(socket_to_remove.grSocket)

    def reduceChannel(self, reduce_inlet=True, reduce_outlet=True):
        if self.node_type == 'CO':
            self.co_input_list_output_list_adjust(self.inctrllist, self.outctrllist, False)
        else:
            if self.content_label_objname == 'MUX':
                for i in range(4):
                    self.inputlist.pop()
                self.outputlist.pop()
            elif self.content_label_objname == 'METER':
                self.inputlist.pop()
            else:
                if reduce_inlet:
                    self.inputlist.pop()
                if reduce_outlet:
                    self.outputlist.pop()

        index = []
        input_edges = []
        input_node = []
        for i in range(len(self.grNode.node.inputs)):
            if len(self.inputlist) <= i:
                if self.grNode.node.inputs[i].edges != []:
                    self.grNode.node.inputs[i].edges[0].remove()
            else:
                input_edges.append(self.grNode.node.inputs[i].edges)
                input_node.append(self.grNode.node.inputs[i])
                index.append(i)

        out_edges = []
        out_node = []
        outdex = []
        for i in range(len(self.grNode.node.outputs)):
            if len(self.outputlist) == i:
                if self.grNode.node.outputs[i].edges != []:
                    self.grNode.node.outputs[i].edges[0].remove()
            else:
                out_edges.append(self.grNode.node.outputs[i].edges)
                out_node.append(self.grNode.node.outputs[i])
                outdex.append(i)

        inctrl_edges = []
        inctrl_nodes = []
        inctrldex = []
        for i in range(len(self.grNode.node.inctrls)):
            if len(self.inctrllist) == i:
                if self.grNode.node.inctrls[i].edges != []:
                    self.grNode.node.inctrls[i].edges[0].remove()
            else:
                inctrl_edges.append(self.grNode.node.inctrls[i].edges)
                inctrl_nodes.append(self.grNode.node.inctrls[i])
                inctrldex.append(i)

        outctrl_edges = []
        outctrl_nodes = []
        outctrldex = []
        for i in range(len(self.grNode.node.outctrls)):
            if len(self.outctrllist) == i:
                if self.grNode.node.outctrls[i].edges != []:
                    self.grNode.node.outctrls[i].edges[0].remove()
            else:
                outctrl_edges.append(self.grNode.node.outctrls[i].edges)
                outctrl_nodes.append(self.grNode.node.outctrls[i])
                outctrldex.append(i)

        self.adjust_sockets(original_inputs=self.inputs, input_list=self.inputlist,
                            original_outputs=self.outputs, output_list=self.outputlist,
                            original_inctrls=self.inctrls, inctrl_list=self.inctrllist,
                            original_outctrls=self.outctrls, outctrl_list=self.outctrllist)

        for i in range(len(input_edges)):
            self.grNode.node.inputs[index[i]].edges = input_edges[i]
            socket = self.grNode.node.inputs[index[i]].grSocket
            self.grNode.node.inputs[index[i]] = input_node[i]
            self.grNode.node.inputs[index[i]].grSocket = socket

        for i in range(len(out_edges)):
            self.grNode.node.outputs[outdex[i]].edges = out_edges[i]
            socket = self.grNode.node.outputs[outdex[i]].grSocket
            self.grNode.node.outputs[outdex[i]] = out_node[i]
            self.grNode.node.outputs[outdex[i]].grSocket = socket

        for i in range(len(inctrl_edges)):
            self.grNode.node.inctrls[inctrldex[i]].edges = inctrl_edges[i]
            socket = self.grNode.node.inctrls[inctrldex[i]].grSocket
            self.grNode.node.inctrls[inctrldex[i]] = inctrl_nodes[i]
            self.grNode.node.inctrls[inctrldex[i]].grSocket = socket

        for i in range(len(outctrl_edges)):
            self.grNode.node.outctrls[outctrldex[i]].edges = outctrl_edges[i]
            socket = self.grNode.node.outctrls[outctrldex[i]].grSocket
            self.grNode.node.outctrls[outctrldex[i]] = outctrl_nodes[i]
            self.grNode.node.outctrls[outctrldex[i]].grSocket = socket

        self.grNode.initSizes()
        for socket in (self.grNode.node.outputs + self.grNode.node.inputs + self.grNode.node.inctrls + self.grNode.node.outctrls):
            socket.setSocketPosition()
        self.updateConnectedEdges()
        self.content.setFixedHeight(self.grNode.height)

        if self.content_label_objname == 'MUX':
            self.Tap(3, 'MUX')
        elif self.content_label_objname == 'METER':
            self.Tap(3, 'METER')
        if self.op_code == flow_conf.OP_NODE_SUBPATCH:
            current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
            self.update_self_node_display()
            self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
            current_sub_windows = self.scene.getView().window().mdiArea.subWindowList()
            for sub_window in current_sub_windows:
                sub_window_name = sub_window.widget().getPrettyFilename()
                if sub_window_name == self.title:
                    nodes = sub_window.widget().scene.nodes
                    if reduce_inlet and not reduce_outlet:
                        all_specific_type_nodes = [node for node in nodes if node.op_code == flow_conf.OP_NODE_INLET]
                    if not reduce_inlet and reduce_outlet:
                        all_specific_type_nodes = [node for node in nodes if node.op_code == flow_conf.OP_NODE_OUTLET]
                    max_specific_type_node_designator = all_specific_type_nodes[0].designator
                    last_specific_type_node = all_specific_type_nodes[0]
                    for specific_type_node in all_specific_type_nodes:
                        if specific_type_node.designator > max_specific_type_node_designator:
                            max_specific_type_node_designator = specific_type_node.designator
                            last_specific_type_node = specific_type_node
                    node_data = last_specific_type_node.serialize()
                    for i in range(len(sub_window.widget().scene.history.history_stack)):
                        if node_data in sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes']:
                            sub_window.widget().scene.history.history_stack[i]['snapshot']['nodes'].remove(
                                node_data)
                    last_specific_type_node.remove()
            for sub_window in current_sub_windows:
                if hasattr(sub_window.widget(), 'close_if_no_problem'):
                    if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                        self.scene.getView().window().close_sub_window(sub_window)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
        if reduce_inlet and reduce_outlet:
            self.scene.history.storeHistory(f"Reduce Channel Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)
        elif reduce_inlet and not reduce_outlet:
            self.scene.history.storeHistory(f"Reduce Inlet Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)
        elif not reduce_inlet and reduce_outlet:
            self.scene.history.storeHistory(f"Reduce Outlet Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)

    def co_input_list_output_list_adjust(self, inctrllist, outctrllist, is_add):
        if self.op_title in ["ADD", "MULTIPLY", "OR", "AND", "CO_METER"]:
            if is_add:
                self.inctrllist.append(inctrllist[0])
            else:
                self.inctrllist.pop()
        elif self.op_title in ["INVERSE", "POWER", "SQRT", "LOG", "EXP", "CLAMP", "NOT", "CO_DELAY"]:
            if is_add:
                self.inctrllist.append(inctrllist[0])
                self.outctrllist.append(outctrllist[0])
            else:
                self.inctrllist.pop()
                self.outctrllist.pop()

    def feedbackChannel(self):
        self.is_feedback = not self.is_feedback

        if self.is_feedback:
            input_position = RIGHT_TOP
            output_position = LEFT_TOP
            edge_type = 3
        else:
            input_position = LEFT_TOP
            output_position = RIGHT_TOP
            edge_type = 2

        # 更新 socket 位置
        for socket in self.inputs:
            socket.position = input_position
            socket.setSocketPosition()

        for socket in self.outputs:
            socket.position = output_position
            socket.setSocketPosition()

        for input in self.inputs:
            edges = input.edges
            for edge in edges:
                edge.remove()

        for output in self.outputs:
            edges = output.edges
            for edge in edges:
                edge.remove()

        # 调用更新
        self.updateConnectedEdges()

        self.scene.history.storeHistory(f"Feedback Node-{self.__class__.__name__}-{self.title}",
                                        setModified=True)

    def update_self_node_display(self):
        hashmap = {}
        history_stamp = self.scene.history.history_stack[self.scene.history.history_current_step]
        edges = history_stamp['snapshot']['edges']
        edges_connected_to_this_node = []
        x = self.pos.x()
        y = self.pos.y()

        node_data = dict(self.serialize())
        new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')), len(node_data.get('outputs')))
        new_node.deserialize(node_data, hashmap, True)

        new_node.setPos(x, y)
        self.remove()
        # region restore edges which connected to this node
        for key in hashmap:
            for edge in edges:
                if edge['start'] == key:
                    edges_connected_to_this_node.append(edge)

                if edge['end'] == key:
                    edges_connected_to_this_node.append(edge)
        edges_hash_map = {}
        for edge_connected_to_this_node in edges_connected_to_this_node:
            for node in self.scene.nodes:
                for output_socket in node.outputs:
                    if output_socket.id == edge_connected_to_this_node['start']:
                        edges_hash_map[edge_connected_to_this_node['id']] = [output_socket]
        for edge_connected_to_this_node in edges_connected_to_this_node:
            for node in self.scene.nodes:
                for input_socket in node.inputs:
                    if input_socket.id == edge_connected_to_this_node['end']:
                        edges_hash_map[edge_connected_to_this_node['id']].append(input_socket)
        for edge_id, sockets in edges_hash_map.items():
            Edge(self.scene, sockets[0], sockets[1], EDGE_TYPE_BEZIER)
        # endregion

        for i in range(len(self.scene.nodes)):
            self.scene.nodes[i].eval()

    def addOneSignChannel(self, str, op_code):
        if str == 'Input':
            self.inputlist.append(1)
        elif str == 'Output':
            self.outputlist.append(1)

        index = []
        input_edges = []
        input_node = []
        out_edges = []
        out_node = []
        for i in range(len(self.grNode.node.inputs)):
            if self.grNode.node.inputs[i].edges != []:
                input_edges.append(self.grNode.node.inputs[i].edges)
                input_node.append(self.grNode.node.inputs[i])
                index.append(i)
        outdex = []
        for i in range(len(self.grNode.node.outputs)):
            if self.grNode.node.outputs[i].edges != []:
                out_edges.append(self.grNode.node.outputs[i].edges)
                out_node.append(self.grNode.node.outputs[i])
                outdex.append(i)

        self.adjust_sockets(original_inputs=self.inputs, input_list=self.inputlist,
                            original_outputs=self.outputs, output_list=self.outputlist)

        for i in range(len(input_edges)):
            self.grNode.node.inputs[index[i]].edges = input_edges[i]
            socket = self.grNode.node.inputs[index[i]].grSocket
            self.grNode.node.inputs[index[i]] = input_node[i]
            self.grNode.node.inputs[index[i]].grSocket = socket

        for i in range(len(out_edges)):
            self.grNode.node.outputs[outdex[i]].edges = out_edges[i]
            socket = self.grNode.node.outputs[outdex[i]].grSocket
            self.grNode.node.outputs[outdex[i]] = out_node[i]
            self.grNode.node.outputs[outdex[i]].grSocket = socket

        self.grNode.initSizes()
        for socket in (self.grNode.node.outputs + self.grNode.node.inputs):
            socket.setSocketPosition()
        self.content.setFixedHeight(self.grNode.height)

        if self.content_label_objname == 'upHear VQE':
            change_channel_implementation().VQE_change_channel(self.manager, len(self.inputs) - self.ref)


        if op_code == 66:
            if str == 'Output':
                self.Tap(0, 'MIXER')

            if str == 'Input':
                for i in range(len(self.inputs)):
                    for j in range(len(self.outputs)):
                        str = 'MixGain_%s_%s' % (i, j)
                        self.manager.widgetSet[str].label.setText('gain %s' % (i + 1))
                        self.manager.widgetSet[str].setVisible(True)

        self.scene.history.storeHistory(f"Add Channel Node-{self.__class__.__name__}-{self.title}",
                                        setModified=True)

    def reduceOneSignChannel(self, str, op_code):
        if str == 'Input':
            self.inputlist.pop()
        elif str == 'Output':
            self.outputlist.pop()

        index = []
        input_edges = []
        input_node = []
        out_edges = []
        out_node = []
        for i in range(len(self.grNode.node.inputs)):
            if self.grNode.node.inputs[i].edges != []:
                if len(self.inputlist) == i:
                    self.grNode.node.inputs[i].edges[0].remove()
                else:
                    input_edges.append(self.grNode.node.inputs[i].edges)
                    input_node.append(self.grNode.node.inputs[i])
                    index.append(i)

        outdex = []
        for i in range(len(self.grNode.node.outputs)):
            if self.grNode.node.outputs[i].edges != []:
                if len(self.outputlist) == i:
                    self.grNode.node.outputs[i].edges[0].remove()
                else:
                    out_edges.append(self.grNode.node.outputs[i].edges)
                    out_node.append(self.grNode.node.outputs[i])
                    outdex.append(i)

        self.adjust_sockets(original_inputs=self.inputs, input_list=self.inputlist,
                            original_outputs=self.outputs, output_list=self.outputlist)

        for i in range(len(input_edges)):
            self.grNode.node.inputs[index[i]].edges = input_edges[i]
            socket = self.grNode.node.inputs[index[i]].grSocket
            self.grNode.node.inputs[index[i]] = input_node[i]
            self.grNode.node.inputs[index[i]].grSocket = socket

        for i in range(len(out_edges)):
            self.grNode.node.outputs[outdex[i]].edges = out_edges[i]
            socket = self.grNode.node.outputs[outdex[i]].grSocket
            self.grNode.node.outputs[outdex[i]] = out_node[i]
            self.grNode.node.outputs[outdex[i]].grSocket = socket

        self.grNode.initSizes()
        for socket in (self.grNode.node.outputs + self.grNode.node.inputs):
            socket.setSocketPosition()
        self.updateConnectedEdges()
        self.content.setFixedHeight(self.grNode.height)

        if self.content_label_objname == 'upHear VQE':
            change_channel_implementation().VQE_change_channel(self.manager, len(self.inputs) - self.ref)


        if op_code == 66:
            if str == 'Output':
                self.Tap(1, 'MIXER')

            if str == 'Input':
                i = len(self.grNode.node.inputs)
                for j in range(len(self.grNode.node.outputs)):
                    str = 'MixGain_%s_%s' % (i, j)
                    self.manager.widgetSet[str].label.setText('gain %s' % (i + 1))
                    self.manager.widgetSet[str].setVisible(False)

        self.scene.history.storeHistory(f"Reduce Channel Node-{self.__class__.__name__}-{self.title}",
                                        setModified=True)

    def openNodePropertyWidget(self):
        self.property_widget = NODE_Propertys(self)
        self.property_widget.exec()

    def rename(self, new_name, ignore_message_box=False):
        """
            Rename the audio object to the given new name.

            :param new_name: The new name to assign to the audio object.
            :param ignore_message_box: Optional. Default: False.
                   A boolean value indicating whether to ignore displaying the message box or not.
            :return: Returns True if the renaming operation is successful, otherwise returns False.
        """
        current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
        sub_windows = self.scene.getView().window().mdiArea.subWindowList()
        if self.op_code == flow_conf.OP_NODE_SUBPATCH:
            nodes = self.scene.getView().window().getCurrentNodeEditorWidget().collectNodesFromSubWnds()
            dict = []
            for node in nodes:
                dict.append(node.serialize())
            same_type_nodes = self.scene.getView().window().getDictByOP(self.op_code, dict)
            for i in range(len(same_type_nodes)):
                if same_type_nodes[i]['id'] == self.id:
                    target_index = i
            same_type_nodes.pop(target_index)
            titles_of_other_same_nodes = []
            for node in same_type_nodes:
                titles_of_other_same_nodes.append(node['title'])
            if new_name in titles_of_other_same_nodes:
                if not ignore_message_box:
                    QMessageBox.warning(self.scene.getView().window(), 'Same subpatch name conflicted',
                                        f'"{new_name}" is not allowed, because other subpatch also has this name')
                return False
            else:
                subpatch_objects = self.scene.getView().window().sub_patchs
                for subpatch_object in subpatch_objects:
                    if (subpatch_object.title == self.title or subpatch_object.title == self.title + '.json') and \
                            subpatch_object.closed:
                        subpatch_object.title = new_name
                        subpatch_object.scene.has_been_modified = True
                        subpatch_object.renamed = True
                for sub_window in sub_windows:
                    sub_window_name = sub_window.widget().getPrettyFilename()
                    if sub_window_name == self.title:
                        sub_window.widget().scene.has_been_modified = True
                        sub_window.widget().renamed = True
                        sub_window.widget().title = new_name
                        sub_window.widget().setWindowTitle(new_name + '*')
                original_title = self.title
                new_title = new_name
                self.grNode.title = new_name
                self.title = new_name
                self.scene.history.storeHistory(f"Rename SubPatch {original_title} to {new_title}",
                                                setModified=True)
                self.scene.getView().window().setActiveSubWindow(current_window.parent())
        else:
            self.grNode.title = new_name
            self.title = new_name
            self.scene.history.storeHistory(f"Rename Node-{self.__class__.__name__}-{self.title}",
                                            setModified=True)
        return True

    def onDialogOption(self, button):
        sb = self.renameDialog.buttonBox.standardButton(button)
        if sb == QDialogButtonBox.Save:
            textboxValue = self.renameDialog.lineEdit.text()
            self.rename(new_name=textboxValue)
            if Debug.DEBUG_Low_Level.value:
                print("Save Clicked")
        elif sb == QDialogButtonBox.RestoreDefaults:
            self.renameDialog.lineEdit.setText(self.op_title)
            if Debug.DEBUG_Low_Level.value:
                print("Reset Clicked")
        elif sb == QDialogButtonBox.Cancel:
            if Debug.DEBUG_Low_Level.value:
                print("Cancel Clicked")

    def nodeUIUpdate(self):
        """
            When node expand or collapse, the size of the UI changes
        """
        if self.grNode.title_item.boundingRect().height() > self.grNode.title_height:
            self.grNode.height += self.grNode.title_item.boundingRect().height() - 24
            self.grNode.title_height = self.grNode.title_item.boundingRect().height()
        self.grNode.initContent()
        for socket in (self.outputs + self.inputs + self.inctrls + self.outctrls):
            socket.setSocketPosition()
        self.updateConnectedEdges()

    def expandcollapseNode(self):
        if self.expand == True:
            self.collapseNode()
        else:
            self.expandNode()

    def expandNode(self, deserialize=False):
        self.grNode.prepareGeometryChange()
        self.grNode.initSizes()
        self.grNode.title_item.setTextWidth(
            self.grNode.width
            - 2 * self.grNode.title_horizontal_padding
        )
        self.grNode.designator_item.setTextWidth(
            self.grNode.width
            - 2 * self.grNode.title_horizontal_padding
        )

        self.nodeUIUpdate()
        self.content.setVisible(True)
        self.expand = True
        if self.openable and self.widget.isVisible(): self.widget.close()
        if not self.is_temp_node:
            if not deserialize: self.scene.history.storeHistory("Expand Node",
                                                                setModified=True)

    def collapseNode(self, deserialize=False):
        self.grNode.prepareGeometryChange()
        self.grNode.width = 100
        num = 0
        if len(self.grNode.node.inputs) >= len(self.grNode.node.outputs):
            num = len(self.grNode.node.inputs) + len(self.grNode.node.inctrls)
        else:
            num = len(self.grNode.node.outputs) + len(self.grNode.node.outctrls)
        self.grNode.height = 22 * num + 32
        self.grNode.title_item.setTextWidth(
            self.grNode.width
            - 2 * self.grNode.title_horizontal_padding
        )
        self.grNode.designator_item.setTextWidth(
            self.grNode.width
            - 2 * self.grNode.title_horizontal_padding
        )
        self.nodeUIUpdate()
        self.content.setVisible(False)
        self.expand = False
        if not self.is_temp_node:
            if not deserialize: self.scene.history.storeHistory("Collapse Node",
                                                                setModified=True)

    def openNodeGUIWidget(self):
        # self.widget.setWindowTitle(self.grNode.designator_item.toPlainText())
        self.widget.setWindowTitle(self.grNode.title)
        if not self.is_temp_node:
            self.widget.refresh()
        self.widget.show()
        FLOW_Window_Connection.show_window_objects.append(self.widget)

    def onDoubleClicked(self, event):
        if self.expandable == True:
            if self.expand == True:
                self.collapseNode()
                if self.openable == True:
                    self.openNodeGUIWidget()
            else:
                self.expandNode()
        else:
            if self.openable == True:
                self.openNodeGUIWidget()
        if self.op_code == flow_conf.OP_NODE_SUBPATCH:
            self.scene.getView().window().onEnterGroupFile(self)

    def deserializeFromExpand(self, data: dict, deserialize: bool):
        if self.expandable:
            if data['expand'] == True and self.expand == False:
                self.expandNode(deserialize)
            elif data['expand'] == False and self.expand == True:
                self.collapseNode(deserialize)
            else:
                pass

    def deserializeFromColor(self, data: dict):
        try:
            self.grNode._brush_title = QBrush(QColor(data['color']))
            self.title_background_color = data['color']
        except Exception:
            self.initNodeColor()

    def serialize(self):
        res = super().serialize()

        res["op_code"] = self.__class__.op_code
        res["type"] = self.__class__.content_label_objname
        res["linktype"] = self.__class__.linkType
        res["color"] = self.title_background_color
        res["designator"] = self.designator
        res["linktype"] = self.__class__.linkType
        res["mic"] = self.mic
        res["ref"] = self.ref
        res["node_type"] = self.node_type
        if self.tap_menu_parameter_name:
            res["tap_menu_parameter_name"] = self.tap_menu_parameter_name
        if self.expandable: res["expand"] = self.expand
        if self.inctrls != []: res["control"] = True

        if Debug.DEBUG_SERIALIZE.value: print("Serialized FLOW_Node '%s'" % self.__class__.__name__, "res:", res)
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        self.designator = data["designator"]
        self.deserializeFromExpand(data, res)
        self.deserializeFromColor(data)

        if Debug.DEBUG_SERIALIZE.value: print("Deserialized FLOW_Node '%s'" % self.__class__.__name__, "res:", res)
        return res

    def is_supported(self):
        window = self.scene.getView().window()
        target = window.target
        if self.op_code == flow_conf.OP_NODE_SUBPATCH:
            def is_unsupported_ao_under(subpatch_name):
                for open_window in window.mdiArea.subWindowList():
                    if open_window.widget().getPrettyFilename() == subpatch_name:
                        for node_in_open_window in open_window.widget().scene.nodes:
                            if node_in_open_window.op_code != flow_conf.OP_NODE_SUBPATCH \
                                    and target in flow_conf.NOT_SUPPORT_AOS and \
                                    node_in_open_window.op_code in flow_conf.NOT_SUPPORT_AOS[target]:
                                return True
                        for node_in_open_window in open_window.widget().scene.nodes:
                            if node_in_open_window.op_code == flow_conf.OP_NODE_SUBPATCH:
                                return is_unsupported_ao_under(node_in_open_window.title)
                for sub_patch_window in window.sub_patchs:
                    if sub_patch_window.closed and (
                            sub_patch_window.title == subpatch_name or sub_patch_window.title == subpatch_name + '.json'):
                        for node_in_sub_patch_window in sub_patch_window.scene.history.history_stack[
                            sub_patch_window.scene.history.history_current_step]['snapshot']['nodes']:
                            if node_in_sub_patch_window['op_code'] != flow_conf.OP_NODE_SUBPATCH \
                                    and target in flow_conf.NOT_SUPPORT_AOS and \
                                    node_in_sub_patch_window['op_code'] in flow_conf.NOT_SUPPORT_AOS[target]:
                                return True
                for sub_patch_window in window.sub_patchs:
                    if sub_patch_window.closed and (
                            sub_patch_window.title == subpatch_name or sub_patch_window.title == subpatch_name + '.json'):
                        for node_in_sub_patch_window in sub_patch_window.scene.history.history_stack[
                            sub_patch_window.scene.history.history_current_step]['snapshot']['nodes']:
                            if node_in_sub_patch_window['op_code'] == flow_conf.OP_NODE_SUBPATCH:
                                return is_unsupported_ao_under(node_in_sub_patch_window['title'])
                return False

            return False if is_unsupported_ao_under(self.title) else True

        while 11 in flow_conf.NOT_SUPPORT_AOS[target]:
            flow_conf.NOT_SUPPORT_AOS[target].remove(11)

        if target in flow_conf.NOT_SUPPORT_AOS and self.op_code in flow_conf.NOT_SUPPORT_AOS[target]:
            return False
        return True

    def is_user_has_permission(self):
        """
            Check if the user has permission to use this audio object.

            Returns:
                bool: True if the user has permission to use this audio object, False otherwise.
        """
        if self.op_code == flow_conf.OP_NODE_INLET or self.op_code == flow_conf.OP_NODE_OUTLET:
            return True
        if self.node_type == 'CO':
            return True
        window = self.scene.getView().window()
        available_aos = window.license_mechanism.feature_permission_data[flow_conf.AO_TYPE_NAME]
        return self.op_code in available_aos

    def onControlChanged(self, socket_type, value):
        pass

    def is_support_feedback_path(self):
        """
            Check if the feedback path is supported for this audio object.
            1. The feedback path must have 'feedback' AO
            2. The feedback path should start from "feedback" AO
            Returns:
                bool: True if the feedback path is supported, False otherwise.
        """
        if not self.is_feedback:
            return True

        if self.isDirty():
            return True

        feedback_path_ao = []
        for node in self.scene.nodes:
            if node.is_feedback:
                feedback_path_ao.append(node.op_code)

        if OP_NODE_FEEDBACK not in feedback_path_ao:
            return False

        for edge in self.scene.edges:
            if edge.edge_type == 3:
                if edge.end_socket.node.op_code == OP_NODE_FEEDBACK:
                    if not edge.start_socket.node.is_feedback:
                        return True
                    else:
                        return False

class FlowFixedPointNode(FLOW_Node):
    is_float_point = False
