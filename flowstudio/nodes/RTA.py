from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from utilities.utils import circular, getReleaseTime
from flowstudio.controls.Menu import Menu

thread_timeout = 50

class RTA_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(900, 400)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()

        self.frame = list()
        self.isConnected = False

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def initExtraWidget(self):
        self.plotWidget = octaveBandAnalyzer(self)

        y = np.linspace(0, 0, num=31)
        x = np.linspace(1, 31, num=31)

        self.bar = pg.BarGraphItem(x=x, height=y, width=1, pen=pg.mkPen((23, 122, 166), width=1), brush=[23, 122, 166, 200])
        self.plotWidget.viewbox.addItem(self.bar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        displayParameter = {"pMax": 16384, "pMin": 0, "pValue": 0}
        self.display = Label_PushButton_DoubleNumber(self, displayParameter)
        self.display.label.setText('update')
        self.display.toggle.toggled.connect(self.toggle)

        self.decay = Menu('decay', ['50', '100', '200', '500', '1000', '2000', '5000'], '200').get_widget(self)
        self.decay.comboBox.currentIndexChanged.connect(self.timeSelect)

        self.timeSelect()

    def initLayout(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.decay, alignment=Qt.AlignLeft)
        layout1.addWidget(self.display, alignment=Qt.AlignLeft)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(layout1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def initPlot(self):
        self.plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=1), fillLevel = -160, fillBrush = [150,150,105,100], fillOutline = True)

    def toggle(self, bool):
        '''
        the following behavior will be triggered by toggle.

        :param bool: toggle status
        :type bool: bool
        :return:
        '''
        # if self.isConnected and not bool and self.socket.connection:
        if self.isConnected and not bool:
            # terminate the thread
            self.client.terminate()
            # set the timeout of the thread to process
            self.client.wait(thread_timeout)
            # disconnect client from server
            self.client.logout(index=1)
            # stop timer to fetch data
            self.timer.stop()
            # clean the ploy
            self.cleanPlotItem()
            # set connected flag into False
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            # create client
            self.client = self.cSocket.createClient()
            # connect client to server
            self.client.login()
            # start timer to fetch data
            self.timer.start(thread_timeout)
            # set connected flag into True
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)
        else:
            pass

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "rta"
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
        elif self.client.isRunning():
            if Debug.DEBUG_THREAD.value: print('%s: current query is still running, skip this query.' %self.node)

    def process(self):
        raw = self.client.result[1].decode().split('/')
        mag = np.array(raw)
        y_data = mag[0:-1].astype(np.float)
        x_data = np.linspace(1, 31, num=int(31), endpoint=True)

        if len(self.frame) == 1:
            if len(self.frame[0]) == len(y_data):
                y_rms = self.releaseTime * self.frame[0] + (1 - self.releaseTime) * y_data
                self.frame = circular(self.frame, y_rms, 1)
                if len(y_rms) == len(x_data):
                    self.bar.setOpts(height = y_rms+120)
                    self.display.spinbox.setValue(len(raw)-1)
            else:
                self.frame = circular(self.frame, y_data, 1)
        else:
            self.frame = circular(self.frame, y_data, 1)

    def timeSelect(self):
        text = self.decay.comboBox.currentText()
        self.releaseTime = getReleaseTime(int(text))

    def cleanPlotItem(self):
        y = np.linspace(0, 0, num=31)
        self.bar.setOpts(height=y)
        self.plot.clear()

@register_node(OP_NODE_RTA)
class FLOW_Node_RTA(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_RTA
    op_title = "RTA"
    content_label_objname = "RTA"
    display_name = 'Real Time Analyzer'
    info = 'RTA is the 1/3 octave band analyzer to analyze the frequency response of the signal'
    expandable = False
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = RTA_GUI(self)


