from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from utilities.iir_designer import *
from control.flow_widget_plot import *

DEBUG = False
DEBUG_Content = False

Color_Scheme = [
[31, 119, 180, 100],
[255, 127, 14, 100],
[44, 160, 44, 100],
[214, 39, 40, 100],
[148, 103, 189, 100],
[140, 86, 75, 100],
[227, 119, 194, 100],
[188, 189, 34, 100],
[23, 190, 207, 100],
[127, 127, 127, 100]
]


class PEQ_FIXED_GUI(FLOW_GUI):

    def __init__(self, node: 'Node'):
        super().__init__(node)
        self.setFixedSize(800, 300)
        self.iir = []
        self.plotWidget = filter(self)
        self.initLayout()
        self.createDot()
        self.initPlot()
        for index in range(self.node.tap):
            self.enableCtrlOpt(index)

    def createDot(self):
        self.dot = []
        for index in range(self.node.tap):
            fc = 'fc_' + str(index)
            boost = 'boost_' + str(index)
            gain = 'gain_' + str(index)

            x_pos = self.gui_manager.widgetSet[fc].widget_value
            y_pos = self.gui_manager.widgetSet[boost].widget_value
            self.dot.append(plotDot(pos=[np.log10(x_pos), y_pos], texts=str(index + 1)))
            # self.dot[index].selected()

            self.dot[index].posChanged.connect(partial(self.dotPos_numberBox, index))

            self.gui_manager.widgetSet[fc].valueChanged.connect(partial(self.numberBox_dotPos, fc))
            self.gui_manager.widgetSet[boost].valueChanged.connect(partial(self.numberBox_dotPos, boost))
            self.gui_manager.widgetSet[gain].valueChanged.connect(partial(self.numberBox_dotPos, gain))

        self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].currentChanged.connect(self.updateSelectDot)

    def updateSelectDot(self):
        for child in self.plotWidget.viewbox.allChildren():
            if type(child) == plotDot:
                child.notSelected()
        if self.dot[self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].currentIndex()] in self.plotWidget.viewbox.allChildren():
            self.dot[self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].currentIndex()].selected()


    def dotPos_numberBox(self, index, value):
        if not self.dot[index].isDrag:
            return
        kind = 'kind_' + str(index)
        fc = 'fc_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)

        if self.gui_manager.widgetSet[kind].widget_value[1] in [6, 7, 10, 11]:
            self.gui_manager.widgetSet[fc].widget_value = 10**value[0]
            self.gui_manager.widgetSet[boost].widget_value = value[1]
            self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].widget_value = [index, self.node.tap]
        else:
            self.gui_manager.widgetSet[fc].widget_value = 10**value[0]
            self.gui_manager.widgetSet[gain].widget_value = value[1]
            self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].widget_value = [index, self.node.tap]

        self.dot[index].isDrag = False

    def numberBox_dotPos(self, key):
        index=int(key[-1])
        kind = 'kind_' + str(index)
        fc = 'fc_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)

        if "onoff" not in key and not self.gui_manager.widgetSet[key].spinbox.hasFocus():
            return

        if self.gui_manager.widgetSet[kind].widget_value[1] in [6, 7, 10, 11]:
            x = np.log10(self.gui_manager.widgetSet[fc].widget_value)
            y = self.gui_manager.widgetSet[boost].widget_value
        else:
            x = np.log10(self.gui_manager.widgetSet[fc].widget_value)
            y = self.gui_manager.widgetSet[gain].widget_value

        if self.dot[index] in self.plotWidget.viewbox.allChildren():
            dot_pos = np.array([[x, y]], dtype=float)
            range = self.dot[index].scatter.getViewBox().viewRange()
            if dot_pos[0][0] == range[0][0]:
                dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
            self.dot[index].setData(pos=dot_pos)
            self.dot[index].childItems()[1].setPos(x, y)
            self.dot[index].clicked()

    def control_phase_switch(self, turn_on):
        if turn_on:
            self.pr_plot.setPen(color=(120, 120, 120), style=Qt.DashLine, width=1.5)
        else:
            self.pr_plot.setPen(None)

    def initLayout(self):
        for index in range(self.node.tap):
            onoff = 'onoff_' + str(index)
            kind = 'kind_' + str(index)
            fc = 'fc_' + str(index)
            boost = 'boost_' + str(index)
            gain = 'gain_' + str(index)
            Q = 'Q_' + str(index)
            slope = 'slope_' + str(index)

            tab = 'tab' + str(index)

            vlayout = QVBoxLayout(self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].__getattribute__(tab))
            vlayout.addWidget(self.gui_manager.widgetSet[onoff], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[kind], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[fc], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[boost], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[gain], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[Q], alignment=Qt.AlignLeft)
            vlayout.addWidget(self.gui_manager.widgetSet[slope], alignment=Qt.AlignLeft)
            vlayout.setContentsMargins(0, 0, 0, 0)
            vlayout.setSpacing(0)

            self.iir.append(IIR_Designer(
                filter_type = self.gui_manager.widgetSet[kind].widget_value[1],
                frequency_cut = self.gui_manager.widgetSet[fc].widget_value,
                magnitude = self.gui_manager.widgetSet[boost].widget_value,
                Q = self.gui_manager.widgetSet[Q].widget_value,
                slope = self.gui_manager.widgetSet[slope].widget_value,
                gain = self.gui_manager.widgetSet[gain].widget_value))

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))
            if 'kind' in key:
                index = int(key[-1])
                self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.enableCtrlOpt, index))

        self.phaseSwitch = Switch('Phase', 'on').get_widget(self)
        self.phaseSwitch.toggle.toggled.connect(self.control_phase_switch)

        h1layout = QHBoxLayout()
        h1layout.addWidget(self.gui_manager.widgetSet['enable'], alignment=Qt.AlignLeft)
        h1layout.addWidget(self.phaseSwitch, alignment=Qt.AlignLeft)
        h1layout.setContentsMargins(0, 0, 0, 0)
        h1layout.setSpacing(0)

        h2layout = QVBoxLayout()
        h2layout.addLayout(h1layout)
        h2layout.addWidget(self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name])
        h2layout.setContentsMargins(0, 0, 0, 0)
        h2layout.setSpacing(0)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(h2layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def enableCtrlOpt(self, index):
        kind = 'kind_' + str(index)
        Q = 'Q_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)
        slope = 'slope_' + str(index)
        if self.gui_manager.widgetSet[kind].widget_value[1] in [10, 11]:
            self.gui_manager.widgetSet[slope].show()
            self.gui_manager.widgetSet[Q].hide()
            self.gui_manager.widgetSet[gain].hide()
            self.gui_manager.widgetSet[boost].show()
        elif self.gui_manager.widgetSet[kind].widget_value[1] in [6,7]:
            self.gui_manager.widgetSet[slope].hide()
            self.gui_manager.widgetSet[Q].show()
            self.gui_manager.widgetSet[gain].hide()
            self.gui_manager.widgetSet[boost].show()
        else:
            self.gui_manager.widgetSet[slope].hide()
            self.gui_manager.widgetSet[Q].show()
            self.gui_manager.widgetSet[gain].show()
            self.gui_manager.widgetSet[boost].hide()
        self.node.enableCtrlOpt(index)

    def ctrl2plot(self, key):
        if 'onoff' in key:
            self.iir[int(key[-1])].bypass = not self.gui_manager.widgetSet[key].widget_value[1]

            if self.gui_manager.widgetSet[key].widget_value[1]:
                self.plotWidget.viewbox.addItem(self.dot[int(key[-1])])
                self.numberBox_dotPos(key)
                if self.gui_manager.widgetSet[self.gui_manager.tap_menu_parameter_name].currentIndex() == int(key[-1]):
                    self.dot[int(key[-1])].selected()
                else:
                    self.dot[int(key[-1])].notSelected()
            else:
                self.plotWidget.viewbox.removeItem(self.dot[int(key[-1])])

            self.updateCoef()
        elif 'kind' in key:
            self.iir[int(key[-1])].filter_type = self.gui_manager.widgetSet[key].widget_value[1]
            self.updateCoef()
        elif 'fc' in key:
            self.iir[int(key[-1])].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif 'Q' in key:
            self.iir[int(key[-1])].q = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif 'boost' in key:
            self.iir[int(key[-1])].magnitude = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif 'slope' in key:
            self.iir[int(key[-1])].slope = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif 'gain' in key:
            self.iir[int(key[-1])].gain = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()

    def updateCoef(self):
        h = 1
        for index in range(self.node.tap):
            h = h * self.iir[index].h
            amplitude = 20 * np.log10(abs(self.iir[index].h))
            self.pr_plot_child[index].setData(x=self.iir[index].w, y=amplitude)

        amplitude = 20 * np.log10(abs(h))
        angle = np.angle(h)
        self.fr_plot.setData(x=self.iir[0].w, y=amplitude)
        self.pr_plot.setData(x=self.iir[0].w, y=angle/np.pi*40)

    def initPlot(self):
        self.pr_plot_child = []

        for index in range(self.node.tap):
            self.pr_plot_child.append(index)
            self.pr_plot_child[index] = self.plotWidget.plotItem.plot(pen=Color_Scheme[index], fillLevel=0, fillBrush=Color_Scheme[index], fillOutline=True)

        self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(120, 120, 120), style=Qt.DashLine, width=1.5))
        self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), width=3))

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

@register_node(OP_NODE_PEQ_FP)
class FLOW_Node_PEQ_FP(FlowFixedPointNode):
    # icon = "icons/in.png"
    op_code = OP_NODE_PEQ_FP
    op_title = "PEQ_FP"
    content_label_objname = "PEQ_FP"
    display_name = 'Parametric EQ (fixed-point)'
    info = 'Fixed-point version of PEQ'
    expandable = True
    openable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value

    def __init__(self, scene, band, channel, control, list = []):
        self.tap = band
        self.inputs = []
        self.outputs = []
        # parameter lists
        self.lists = list
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()
        for index in range(self.tap):
            self.enableCtrlOpt(index)

        for key in self.manager.widgetSet:
            if 'kind' in key:
                index = int(key[-1])
                self.manager.widgetSet[key].valueChanged.connect(partial(self.enableCtrlOpt, index))



    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.manager.config[self.manager.tap_menu_parameter_name].parameters['pSize'] = self.tap
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = PEQ_FIXED_GUI(self)

        if self.lists != []:
            for li in self.lists:

                if 'fc' in li: return
                
                if li not in ["enable", self.manager.tap_menu_parameter_name]:
                    if int(li[-1]) != self.tap:
                        if li[0:-2] not in ['onoff','kind']:
                            self.manager.widgetSet[li].widget_value = self.lists[li]
                        else:
                            value = self.lists[li]
                            self.manager.widgetSet[li].widget_value = value
                elif li == "enable":
                    value = self.lists[li]
                    self.manager.widgetSet[li].widget_value = value

    def enableCtrlOpt(self,index):
        kind = 'kind_' + str(index)
        Q = 'Q_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)
        slope = 'slope_' + str(index)
        if self.manager.widgetSet[kind].widget_value[1] in [10, 11]:
            self.manager.widgetSet[slope].disableWidget(False)
            self.manager.widgetSet[Q].disableWidget(True)
            self.manager.widgetSet[gain].disableWidget(True)
            self.manager.widgetSet[boost].disableWidget(False)
        elif self.manager.widgetSet[kind].widget_value[1] in [6, 7]:
            self.manager.widgetSet[slope].disableWidget(True)
            self.manager.widgetSet[Q].disableWidget(False)
            self.manager.widgetSet[gain].disableWidget(True)
            self.manager.widgetSet[boost].disableWidget(False)
        else:
            self.manager.widgetSet[slope].disableWidget(True)
            self.manager.widgetSet[Q].disableWidget(False)
            self.manager.widgetSet[gain].disableWidget(False)
            self.manager.widgetSet[boost].disableWidget(True)
