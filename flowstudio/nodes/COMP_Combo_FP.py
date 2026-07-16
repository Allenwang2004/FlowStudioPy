from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from utilities.drc_designer import *
from control.flow_widget_plot import *

thread_timeout = 50

class CompComboFPGUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(600, 400)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()
        self.env_volume = None
        self.isConnected = False

        self.COMP_Combo_FP = DRC_Designer(model=FUSION,
                                       threshold=self.gui_manager.widgetSet['thres1'].widget_value,
                                       threshold_2=self.gui_manager.widgetSet['thres2'].widget_value,
                                       noisegate=self.gui_manager.widgetSet['noisegate'].widget_value,
                                       ratio=self.gui_manager.widgetSet['ratio0'].widget_value,
                                       ratio_2=self.gui_manager.widgetSet['ratio1'].widget_value,
                                       ratio_3=self.gui_manager.widgetSet['ratio2'].widget_value,
                                       makeup=self.gui_manager.widgetSet['makeup'].widget_value)

        for key in self.gui_manager.widgetSet:
            if key in ['noisegate','thres1','thres2','onoff', 'ratio0','ratio1','ratio2','makeup']:
                self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))

        self.disableTrAndTaAndTe(self.gui_manager.widgetSet['type'].widget_value[0])
        self.gui_manager.widgetSet['type'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, self.gui_manager.widgetSet['type'].widget_value[0]))

    def disableTrAndTaAndTe(self, value):
        if value == self.gui_manager.widgetSet["type"].widget_value[0]:
            self.gui_manager.widgetSet["ta"].disableWidget(False)
            self.gui_manager.widgetSet["tr"].disableWidget(False)
            self.gui_manager.widgetSet["te"].disableWidget(False)
        else:
            self.gui_manager.widgetSet["tr"].disableWidget(False)
            self.gui_manager.widgetSet["ta"].disableWidget(False)
            self.gui_manager.widgetSet["te"].disableWidget(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def initExtraWidget(self):
        self.plotWidget = drc_computer(self)
        self.grWidget = gain_reduction(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        displayParameter = {"pMax":20, "pMin":-100, "pValue":0}
        self.display = Label_PushButton_DoubleNumber(self, displayParameter)
        self.display.label.setText('update')
        self.display.toggle.clicked.connect(self.toggle)

    def initLayout(self):
        layout1 = QVBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['type'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['thres1'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['thres2'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['noisegate'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ratio0'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ratio1'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ratio2'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ta'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['hold'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['td'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['te'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['tr'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['makeup'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.display, alignment=Qt.AlignLeft)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget, 6)
        layout.addWidget(self.grWidget, 1)
        layout.addLayout(layout1, 3)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def initPlot(self):
        self.dot = plotDot()

        self.dynamic_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.reduction_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((0,0,0,0), width=3), fillLevel = -120, fillOutline = True)

        self.fill = pg.FillBetweenItem(self.dynamic_plot, self.reduction_plot, brush=[26, 188, 156, 100])

        self.bar = pg.BarGraphItem(x=[1], height=[0], width=1,  brush=[188, 76, 26, 180])

    def ctrl2plot(self, key):
        if key == 'onoff':
            self.COMP_Combo_FP.bypass = not self.gui_manager.widgetSet['onoff'].widget_value[1]
        elif key == 'thres1':
            self.COMP_Combo_FP.threshold = self.gui_manager.widgetSet['thres1'].widget_value
        elif key == 'thres2':
            self.COMP_Combo_FP.threshold_2 = self.gui_manager.widgetSet['thres2'].widget_value
        elif key == 'noisegate':
            self.COMP_Combo_FP.noisegate = self.gui_manager.widgetSet['noisegate'].widget_value
        elif key == 'ratio0':
            self.COMP_Combo_FP.ratio = self.gui_manager.widgetSet['ratio0'].widget_value
        elif key == 'ratio1':
            self.COMP_Combo_FP.ratio_2 = self.gui_manager.widgetSet['ratio1'].widget_value
        elif key == 'ratio2':
            self.COMP_Combo_FP.ratio_3 = self.gui_manager.widgetSet['ratio2'].widget_value
        elif key == 'makeup':
            self.COMP_Combo_FP.makeup = self.gui_manager.widgetSet['makeup'].widget_value

        self.dynamic_plot.setData(x=self.COMP_Combo_FP.input, y=self.COMP_Combo_FP.output)

        if self.env_volume is not None: self.followUp()

    def followUp(self):
        idea_output = self.COMP_Combo_FP.location(self.env_volume)
        if self.gui_manager.widgetSet['onoff'].widget_value[1]:
            dot_pos = np.array([[self.env_volume, idea_output]], dtype=float)
        else:
            dot_pos = np.array([[self.env_volume, self.env_volume]], dtype=float)
        self.dot.setData(pos=dot_pos)

        index = self.COMP_Combo_FP.input_index(self.env_volume)

        if self.gui_manager.widgetSet['onoff'].widget_value[1]:
            x_data = [self.env_volume, self.env_volume]
            x_data = x_data + (self.COMP_Combo_FP.input[index:])

            y_data = [-120, idea_output]
            y_data = y_data + (self.COMP_Combo_FP.output[index:])
        else:
            x_data = [-120, 0]
            y_data = [-120, 0]

        self.reduction_plot.setData(x=x_data, y=y_data)

    def toggle(self, bool):
        if self.isConnected and not bool and self.cSocket.connection:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout(index=1)
            self.timer.stop()
            self.cleanPlotItem()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.addPlotItem()
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)
        else:
            pass

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "Env"
            cmd = "getSerialized/%s/%s/" % (AO_Name, Parameter_Name)
            self.client.setQueryTask(cmd, 64)
            self.client.start()
            self.client.wait(thread_timeout)
            if self.client.result[0] == True:
                self.process()
            elif self.client.result[0] == False:
                self.toggle(False)
                self.display.toggle.setChecked(False)
        elif not self.cSocket.connection and self.isConnected:
            self.toggle(False)
            self.display.toggle.setChecked(False)

    def process(self):
        raw = self.client.result[1].decode().split('/')

        self.env_volume = float(raw[0])
        self.display.spinbox.setValue(self.env_volume)
        self.followUp()

        reduction_volume = float(raw[1])
        self.bar.setOpts(height=-reduction_volume)

    def addPlotItem(self):
        self.grWidget.viewbox.addItem(self.bar)
        self.plotWidget.viewbox.addItem(self.dot)
        self.plotWidget.viewbox.addItem(self.reduction_plot)
        self.plotWidget.viewbox.addItem(self.fill)

    def cleanPlotItem(self):
        self.grWidget.viewbox.removeItem(self.bar)
        self.plotWidget.viewbox.removeItem(self.dot)
        self.plotWidget.viewbox.removeItem(self.reduction_plot)
        self.plotWidget.viewbox.removeItem(self.fill)

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

@register_node(OP_NODE_COMP_Combo_FP)
class FlowNodeCompComboFP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_COMP_Combo_FP
    op_title = "COMP_COMBO_FP"
    content_label_objname = "COMP_COMBO_FP"
    display_name = '3 section Compressor (fixed-point)'
    info = 'fixed-point version of COMP_Combo'
    expandable = True
    openable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    def __init__(self, scene, channel):
        self.inputs = []
        self.outputs = []
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()

        self.disableTrAndTaAndTe(self.manager.widgetSet['type'].widget_value[0])
        self.manager.widgetSet['type'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, self.manager.widgetSet['type'].widget_value[0]))

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = CompComboFPGUI(self)

    def disableTrAndTaAndTe(self,value):
        if value==self.manager.widgetSet["type"].widget_value[0]:
            self.manager.widgetSet["ta"].disableWidget(False)
            self.manager.widgetSet["tr"].disableWidget(False)
            self.manager.widgetSet["te"].disableWidget(False)
        else:
            self.manager.widgetSet["tr"].disableWidget(False)
            self.manager.widgetSet["ta"].disableWidget(False)
            self.manager.widgetSet["te"].disableWidget(True)