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


class PEQ_GUI(FLOW_GUI):

    def __init__(self, node: 'Node'):
        super().__init__(node)
        self.setFixedSize(800, 330)
        self.iir = []
        self.decline = 0
        self.plotWidget = filter(self)
        self.initLayout()
        self.createDot()
        self.initPlot()
        for index in range(self.node.tap):
            self.enableCtrlOpt(index)
        self.gui_manager.widgetSet['rescale'].disableWidget(True)

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

        self.gui_manager.widgetSet["tap"].currentChanged.connect(self.updateSelectDot)

    def updateSelectDot(self):
        for child in self.plotWidget.viewbox.allChildren():
            if type(child) == plotDot:
                child.notSelected()
        if self.dot[self.gui_manager.widgetSet["tap"].currentIndex()] in self.plotWidget.viewbox.allChildren():
            self.dot[self.gui_manager.widgetSet["tap"].currentIndex()].selected()


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
            self.gui_manager.widgetSet['tap'].widget_value = [index, self.node.tap]
        else:
            self.gui_manager.widgetSet[fc].widget_value = 10**value[0]
            self.gui_manager.widgetSet[gain].widget_value = value[1]
            self.gui_manager.widgetSet['tap'].widget_value = [index, self.node.tap]

        self.dot[index].isDrag = False

    def numberBox_dotPos(self, key):
        index=int(key[-1])

        if not key.split('_')[0] == 'rescale':
            if "onoff" not in key and not self.gui_manager.widgetSet[key].spinbox.hasFocus():
                return

        self.setDotPos(index)
        self.updateSelectDot()
        if self.gui_manager.widgetSet['Auto Rescale'].widget_value[1] == 1 and self.decline >= 0:
            for index in range(self.node.tap):
                self.setDotPos(index)

    def setDotPos(self, index):
        kind = 'kind_' + str(index)
        fc = 'fc_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)

        if self.gui_manager.widgetSet[kind].widget_value[1] in [6, 7, 10, 11]:
            x = np.log10(self.gui_manager.widgetSet[fc].widget_value)
            y = self.gui_manager.widgetSet[boost].widget_value
        else:
            x = np.log10(self.gui_manager.widgetSet[fc].widget_value)
            y = self.gui_manager.widgetSet[gain].widget_value

        if self.gui_manager.widgetSet['Auto Rescale'].widget_value[1] == 1 and self.decline >= 0:
            y = y - self.decline

        if self.dot[index] in self.plotWidget.viewbox.allChildren():
            dot_pos = np.array([[x, y]], dtype=float)
            viewRange = self.dot[index].scatter.getViewBox().viewRange()
            if dot_pos[0][0] == viewRange[0][0]:
                dot_pos[0][0] = np.math.ceil(viewRange[0][0] * 100) / 100
            self.dot[index].setData(pos=dot_pos)
            self.dot[index].childItems()[1].setPos(x, y)

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

            vlayout = QVBoxLayout(self.gui_manager.widgetSet['tap'].__getattribute__(tab))
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
                gain = self.gui_manager.widgetSet[gain].widget_value,
                op_code=OP_NODE_PEQ_V2
            ))

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

        self.gui_manager.widgetSet['Auto Rescale'].toggle.toggled.connect(self.enableRescale)

        h2layout = QVBoxLayout()
        h2layout.addLayout(h1layout)
        h2layout.addWidget(self.gui_manager.widgetSet['Auto Rescale'], alignment=Qt.AlignLeft)
        h2layout.addWidget(self.gui_manager.widgetSet['rescale'], alignment=Qt.AlignLeft)
        h2layout.addWidget(self.gui_manager.widgetSet['tap'])
        h2layout.setContentsMargins(5, 5, 5, 5)
        h2layout.setSpacing(10)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(h2layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def enableRescale(self):
        self.updateCoef()

        for index in range(self.node.tap):
            if self.gui_manager.widgetSet['Auto Rescale'].widget_value[1] == 1:
                self.dot[index].noDrag = True
            else:
                self.dot[index].noDrag = False
            self.numberBox_dotPos('rescale_'+str(index))


    def enableCtrlOpt(self, index):
        kind = 'kind_' + str(index)
        Q = 'Q_' + str(index)
        boost = 'boost_' + str(index)
        gain = 'gain_' + str(index)
        slope = 'slope_' + str(index)
        if self.gui_manager.widgetSet[kind].widget_value[1] in [10, 11]:
            self.gui_manager.widgetSet[slope].hide()
            self.gui_manager.widgetSet[Q].show()
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
                if self.gui_manager.widgetSet["tap"].currentIndex() == int(key[-1]):
                    self.dot[int(key[-1])].selected()
                else:
                    self.dot[int(key[-1])].notSelected()
            else:
                self.plotWidget.viewbox.removeItem(self.dot[int(key[-1])])

            self.updateCoef()
            self.enableRescale()
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
        n = 1
        for index in range(self.node.tap):
            n = n * self.iir[index].h
        fr_amplitude = 20 * np.log10(abs(n))
        angle = np.angle(n)
        pr_amplitude = angle / np.pi * 40
        self.decline = max(fr_amplitude)

        for index in range(self.node.tap):
            h = h * self.iir[index].h
            amplitude = 20 * np.log10(abs(self.iir[index].h))
            if self.gui_manager.widgetSet['Auto Rescale'].widget_value[1] == 1 and self.decline >= 0:
                self.pr_plot_child[index].setFillLevel(-self.decline)
                self.pr_plot_child[index].setData(x=self.iir[index].w, y=amplitude-self.decline)
            else:
                self.pr_plot_child[index].setFillLevel(0)
                self.pr_plot_child[index].setData(x=self.iir[index].w, y=amplitude)


        if self.gui_manager.widgetSet['Auto Rescale'].widget_value[1] == 1 and self.decline >= 0:
            self.gui_manager.widgetSet['rescale'].spinbox.setValue(self.decline)
            fr_amplitude = fr_amplitude - self.decline
            pr_amplitude = pr_amplitude - self.decline
        else:
            self.gui_manager.widgetSet['rescale'].spinbox.setValue(0)


        self.fr_plot.setData(x=self.iir[0].w, y=fr_amplitude)
        self.pr_plot.setData(x=self.iir[0].w, y=pr_amplitude)

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

@register_node(OP_NODE_PEQ_V2)
class FlowNodePEQADV(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_PEQ_V2
    op_title = "PEQ_V2"
    content_label_objname = "PEQ_V2"
    display_name = 'Parametric EQ V2'
    info = 'PEQ_V2 audio object specify Q factor when defining Shelf filter instead of slope. And providing rescaling factor  that will off-set the EQ bank response to avoid overload in special case by reserving sufficient headroom.'
    expandable = True
    openable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value

    def __init__(self, scene, band, channel, control, list=None):
        if list is None:
            list = []
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

        self.iir1 = []
        for index in range(self.tap):
            kind = 'kind_' + str(index)
            fc = 'fc_' + str(index)
            boost = 'boost_' + str(index)
            gain = 'gain_' + str(index)
            Q = 'Q_' + str(index)
            slope = 'slope_' + str(index)

            self.iir1.append(IIR_Designer(
                filter_type=self.manager.widgetSet[kind].widget_value[1],
                frequency_cut=self.manager.widgetSet[fc].widget_value,
                magnitude=self.manager.widgetSet[boost].widget_value,
                Q=self.manager.widgetSet[Q].widget_value,
                slope=self.manager.widgetSet[slope].widget_value,
                gain=self.manager.widgetSet[gain].widget_value,
                op_code=OP_NODE_PEQ_V2
            ))

        self.manager.widgetSet['rescale'].disableWidget(True)
        self.manager.widgetSet['Auto Rescale'].toggle.toggled.connect(self.setRescale)
        for index in range(self.tap):
            self.manager.widgetSet['onoff_'+str(index)].toggle.toggled.connect(self.setRescale)
            self.manager.widgetSet['boost_'+str(index)].valueChanged.connect(self.setRescale)
            self.manager.widgetSet['kind_'+str(index)].valueChanged.connect(self.setRescale)
            self.manager.widgetSet['fc_'+str(index)].valueChanged.connect(self.setRescale)
            self.manager.widgetSet['gain_'+str(index)].valueChanged.connect(self.setRescale)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.manager.config['tap'].parameters['pSize'] = self.tap
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = PEQ_GUI(self)

        if self.lists != []:
            for li in self.lists:
                if 'fc' in li: return
                if li not in ["enable", "Auto Rescale", "rescale", 'tap']:
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
            self.manager.widgetSet[slope].disableWidget(True)
            self.manager.widgetSet[Q].disableWidget(False)
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

    def setRescale(self):
        n = 1
        for index in range(self.tap):
            self.iir1[index].bypass = not self.manager.widgetSet['onoff_' + str(index)].widget_value[1]
            self.iir1[index].filter_type = self.manager.widgetSet['kind_' + str(index)].widget_value[1]
            self.iir1[index].freq = self.manager.widgetSet['fc_' + str(index)].widget_value
            self.iir1[index].q = self.manager.widgetSet['Q_'+str(index)].widget_value
            self.iir1[index].magnitude = self.manager.widgetSet['boost_' + str(index)].widget_value
            self.iir1[index].slope = self.manager.widgetSet['slope_' + str(index)].widget_value
            self.iir1[index].gain = self.manager.widgetSet['gain_' + str(index)].widget_value
            n = n * self.iir1[index].h

        fr_amplitude = 20 * np.log10(abs(n))
        decline = max(fr_amplitude)

        if self.manager.widgetSet['Auto Rescale'].widget_value[1] == 1 and decline >= 0:
            self.manager.widgetSet['rescale'].numbox.setValue(decline)
        else:
            self.manager.widgetSet['rescale'].numbox.setValue(0)


    def tweaker(self, key):
        cmd = None
        if isinstance(key, str):
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name = key
            Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value

            if key == 'Auto Rescale':
                self.setRescale()
                cmd = "set/%s/%s/%s/" % (AO_Name, "rescale", self.manager.widgetSet["rescale"].widget_value)
            else:
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
