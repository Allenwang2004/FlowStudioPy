import math

from control.flow_widget_plot import drc_computer
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
from control.flow_widget_dot import plotDot
from utilities.iir_designer import *

thread_timeout = 50

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

class SMART_EQ_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node: 'Node'):
        super().__init__(node)
        self.setFixedSize(800, 600)
        self.iir = []
        self.initExtraWidget()
        self.initLayout()
        self.createDot()
        self.initPlot()
        self.initBoostLevelPlotWidget()
        self.isConnected = False
        self.boost_current = 0

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def createDot(self):
        self.dot = []
        fc = 'fc'

        x_pos = self.gui_manager.widgetSet[fc].widget_value
        y_pos = self.boostLevel.widget_value
        first_dot = plotDot(pos=[np.log10(x_pos), y_pos], texts='1')
        first_dot.noDrag = True
        self.dot.append(first_dot)

        self.gui_manager.widgetSet[fc].valueChanged.connect(partial(self.numberBox_dotPos, fc))
        self.boostLevel.valueChanged.connect(partial(self.numberBox_dotPos, 'boostLevel'))


    def numberBox_dotPos(self, key):
        fc = 'fc'

        x = np.log10(self.gui_manager.widgetSet[fc].widget_value)
        y = self.boostLevel.widget_value

        if self.dot[0] in self.plotWidget.viewbox.allChildren():
            dot_pos = np.array([[x, y]], dtype=float)
            range = self.dot[0].scatter.getViewBox().viewRange()
            if dot_pos[0][0] == range[0][0]:
                dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
            self.dot[0].setData(pos=dot_pos)
            self.dot[0].childItems()[1].setPos(x, y)
            self.dot[0].clicked()


    def initBoostLevelPlotWidget(self):
        y_axis = [[]]
        boost_value = - self.boostLevel.widget_value
        boost_max = math.ceil(boost_value + 18)
        boost_min = math.ceil(boost_value - 6)

        for i in [0, 1, 2, 3, 4, 5]:
            num = boost_min + 6 * i
            y_axis[0].append((num, str(num) + 'db'))

        self.boost_level_plot_widget.viewbox.setYRange(boost_min - 0.5, boost_max + 0.5, 0, True)
        self.boost_level_plot_widget.left_axis.setTicks(y_axis)

    def initPlot(self):
        self.pr_plot_child = []
        self.pr_plot_child.append(0)
        self.pr_plot_child[0] = self.plotWidget.plotItem.plot(pen=Color_Scheme[0], fillLevel=0,
                                                                  fillBrush=Color_Scheme[0], fillOutline=True)

        self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(120, 120, 120), style=Qt.DashLine, width=1.5))
        self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), width=3))

        self.boost_plot = self.boost_level_plot_widget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), width=2))

        self.boost_level_plot_y_data = []
        self.boost_level_plot_x_data = []
        for i in range(61):
            self.boost_level_plot_x_data.append(i)


    def paintBoostLevelPlot(self):
        self.boost_level_plot_y_data.append(float(self.boostdb_value.text()[:-2]))

        if len(self.boost_level_plot_y_data) <= 61:
            length = len(self.boost_level_plot_y_data)
        else:
            length = 61

        self.boost_plot.setData(x=self.boost_level_plot_x_data[:length], y=self.boost_level_plot_y_data[-length:])


    def initExtraWidget(self):
        self.plotWidget = filter(self)
        self.boost_level_plot_widget = boost_level(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        self.display = Switch('update', 'on').get_widget(self)
        self.display.toggle.clicked.connect(self.toggle)

        self.boostdb_value = QLabel(self)
        self.boostdb_value.setText("0db")
        self.boostdb_value.setStyleSheet("font-size:35px")

        self.boost_level_label = QLabel(self)
        self.boost_level_label.setText("Boost Level")
        self.boost_level_label.setStyleSheet("font-size:20px")

        self.reset = QPushButton(self)
        self.reset.setText("reset")
        self.reset.setStyleSheet("font-size:13px")
        self.reset.clicked.connect(self.onReset)

        self.calibrate = QPushButton(self)
        self.calibrate.setText("calibrate")
        self.calibrate.setStyleSheet("font-size:13px")
        self.calibrate.clicked.connect(self.onCalibrate)

        self.boostLevel = LabelDoubleNumberBox(self,
                                               {"label_text": "boostLevel", "pMax": 100, "pMin": -100, "pValue": 0,
                                                "pDecimalPrecision": 2})
        self.boostLevel.setHidden(True)

    def onReset(self):
        if self.isConnected:
            self.fetchData('reset')
        self.boostdb_value.setText("0db")
        self.gui_manager.widgetSet['fsboost'].widget_value = 0
        self.boostLevel.widget_value = 0
        self.ctrl2plot('onoff')

    def onCalibrate(self):
        if self.isConnected:
            self.fetchData('calibrate')
            self.fetchData('fsboost')
        self.ctrl2plot('onoff')

    def initLayout(self):
        layout1 = QVBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['slope'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['effthold'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ta'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['tr'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['tf'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['minboost'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['maxboost'], alignment=Qt.AlignLeft)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.boostdb_value, alignment=Qt.AlignCenter)
        layout2.addWidget(self.boost_level_label, alignment=Qt.AlignCenter)
        layout2.addWidget(self.reset, alignment=Qt.AlignCenter)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.gui_manager.widgetSet['fsboost'], alignment=Qt.AlignLeft)
        layout3.addWidget(self.calibrate)

        layout_left = QVBoxLayout()
        layout_left.addLayout(layout1, 4)
        layout_left.addWidget(self.display, 1, alignment=Qt.AlignLeft)
        layout_left.addLayout(layout2, 2)
        layout_left.addLayout(layout3, 1)
        layout_left.addStretch(2)
        layout_left.setContentsMargins(10, 0, 10, 10)

        layout_right = QVBoxLayout()
        layout_right.addWidget(self.plotWidget)
        layout_right.addWidget(self.boost_level_plot_widget)

        self.iir.append(IIR_Designer(
            filter_type=LOWSHELF,
            frequency_cut=self.gui_manager.widgetSet['fc'].widget_value,
            magnitude=self.boostLevel.widget_value,
            slope=self.gui_manager.widgetSet['slope'].widget_value))

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))
        self.boostLevel.valueChanged.connect(partial(self.ctrl2plot, 'boostLevel'))

        layout = QHBoxLayout(self)
        layout.addLayout(layout_right, 7)
        layout.addLayout(layout_left, 3)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def ctrl2plot(self, key):
        if 'onoff' in key:
            self.iir[0].bypass = not self.gui_manager.widgetSet[key].widget_value[1]

            if self.gui_manager.widgetSet[key].widget_value[1]:
                self.plotWidget.viewbox.addItem(self.dot[0])
                self.numberBox_dotPos(key)
            else:
                self.plotWidget.viewbox.removeItem(self.dot[0])

            self.updateCoef()
        elif 'fc' in key:
            self.iir[0].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif 'boostLevel' in key:
            self.iir[0].magnitude = self.boostLevel.widget_value
            self.updateCoef()
        elif 'slope' in key:
            self.iir[0].slope = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()

    def updateCoef(self):
        h = 1
        h = h * self.iir[0].h
        amplitude = 20 * np.log10(abs(self.iir[0].h))
        self.pr_plot_child[0].setData(x=self.iir[0].w, y=amplitude)

        amplitude = 20 * np.log10(abs(h))
        angle = np.angle(h)

        self.fr_plot.setData(x=self.iir[0].w, y=amplitude)
        self.pr_plot.setData(x=self.iir[0].w, y=angle / np.pi * 40)

    def refresh(self):
        """
            Refreshes the GUI and updates its state.
        """
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

    def toggle(self, bool):
        # if self.isConnected and not bool and self.socket.connection:
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout(index=1)
            self.timer.stop()
            # self.cleanPlot()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' %self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' %self.__class__.__name__)
        else:
            pass

    def fetchData(self, parameter=''):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            if parameter == 'reset':
                cmd = 'setCoord/SMART_EQ_1/reset/1/0/0/'
            elif parameter == 'calibrate':
                cmd = 'setCoord/SMART_EQ_1/calibrate/1/0/0/'
            elif parameter == 'fsboost':
                cmd = 'setCoord/SMART_EQ_1/fsboost/%s/0/0/' % self.gui_manager.widgetSet['fsboost'].widget_value
            else:
                Parameter_Name = "monitor/0/0"
                cmd = "getMeter/%s/%s/" % (AO_Name, Parameter_Name)
            self.client.setQueryTask(cmd, 16)
            self.client.start()
            if self.client.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value, Target.FLOW_APO.value]:
                self.client.wait(150)
            else:
                self.client.wait(thread_timeout)
            if self.client.result[0] == True and parameter == '':
                self.process()
            elif self.client.result[0] == False:
                self.toggle(False)
                self.display.toggle.setChecked(False)
        elif not self.cSocket.connection and self.isConnected:
            self.toggle(False)
            self.display.toggle.setChecked(False)
        elif self.client.isRunning():
            if Debug.DEBUG_THREAD.value: print('%s: current query is still running, skip this query.' %self.node)

    def process(self):
        self.boost_current = "{:.2f}".format(float(self.client.result[1].decode().split('\n')[0]))
        self.boostdb_value.setText(self.boost_current + "db")
        self.boostLevel.widget_value = float(self.boost_current) * -1
        self.initBoostLevelPlotWidget()
        self.paintBoostLevelPlot()

@register_node(OP_NODE_SMART_EQ)
class FLOW_Node_SAMRT_EQ(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SMART_EQ
    op_title = "SMART_EQ"
    content_label_objname = "SMART_EQ"
    display_name = 'Smart Equalizer'
    info = 'Adaptive correction using built-in Mic, no user calibration required. In offensive compensation for wall & corner loading.<br>The bass boost level aligns with expectation can potentially fix bass boosting due to room acoustics, but could not fix higher frequencies, therefore the resulting sound would maybe still be tonally incorrect. Best for ‘carry-around’ speakers.'
    expandable = True
    openable = True

    def __init__(self, scene):
        self.inputs = [1, 1]
        self.outputs = [1]
        super().__init__(scene, inputs=self.inputs, outputs=self.outputs)
        self.initControl()
        self.eval()
        self.manager.widgetSet["slope"].setHidden(True)
        self.manager.widgetSet["effthold"].setHidden(True)
        self.manager.widgetSet["ta"].setHidden(True)
        self.manager.widgetSet["tr"].setHidden(True)
        self.manager.widgetSet["tf"].setHidden(True)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = SMART_EQ_GUI(self)

    def initSocketTooltip(self):
        self.inputs[0].grSocket.setToolTip("input")
        self.inputs[1].grSocket.setToolTip("mic input")
        self.outputs[0].grSocket.setToolTip("output")