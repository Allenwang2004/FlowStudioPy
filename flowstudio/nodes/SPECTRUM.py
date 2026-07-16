from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from utilities.utils import circular, getReleaseTime
from flowstudio.controls.Menu import Menu

thread_timeout = 50

class SPECTRUM_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(800, 400)
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
        self.plotWidget = spectrum(self)

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
        layout1 = QVBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['fftsize'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['window'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.decay, alignment=Qt.AlignLeft)
        layout1.addWidget(self.display, alignment=Qt.AlignLeft)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(layout1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def initPlot(self):
        self.plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=1), fillLevel = -160, fillBrush = [26, 188, 156, 100], fillOutline = True)
        # self.plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=1))

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
            Parameter_Name = "Mag"

            getInfo = "info/"
            getSize = "get/%s/fftsize/" % (AO_Name)
            self.client.setQueryTasks([getInfo, getSize], 64)
            self.client.start()
            self.client.wait()
            if not (False in self.client.result[0]):
                info = self.client.result[1][0]
                self.sampleRate = float(info.decode().split(',')[1])
                size = self.client.result[1][1]
                self.fftSize = float(size.decode().strip(b'\n\x00'.decode()))
                index = self.gui_manager.widgetSet['fftsize'].comboBox.findText(str(int(self.fftSize)))
                self.gui_manager.widgetSet['fftsize'].widget_value = [int(self.fftSize), index]

            Parameter_Arg = self.gui_manager.widgetSet['fftsize'].widget_value[0]
            cmd = "getSerializedAmount/%s/%s/%s/" % (AO_Name, Parameter_Name, int(Parameter_Arg)/2)

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

        if hasattr(self, 'sampleRate') and hasattr(self, 'fftSize'):
            y_data = mag[0:-1].astype(np.float)
            x_data = np.linspace(1, self.sampleRate / 2, num=int(len(y_data)), endpoint=True)

            minimum = int(self.sampleRate / self.fftSize)
            if minimum <= 20: minimum = 20
            maximum = int(self.sampleRate / 2)

            self.plotWidget.viewbox.setXRange(np.log10(minimum), np.log10(maximum), 0, True)

            if len(self.frame) == 1:
                if len(self.frame[0]) == len(y_data):
                    y_rms = self.releaseTime * self.frame[0] + (1 - self.releaseTime) * y_data
                    self.frame = circular(self.frame, y_rms, 1)
                    if len(y_rms) == len(x_data):
                        self.plot.setData(x=x_data, y=y_rms)
                        self.display.spinbox.setValue(len(raw)-1)
                else:
                    self.frame = circular(self.frame, y_data, 1)
            else:
                self.frame = circular(self.frame, y_data, 1)

    def timeSelect(self):
        text = self.decay.comboBox.currentText()
        self.releaseTime = getReleaseTime(int(text))

    def cleanPlotItem(self):
        self.plot.clear()

@register_node(OP_NODE_SPECTRUM)
class FLOW_Node_SPECTRUM(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SPECTRUM
    op_title = "SPECTRUM"
    content_label_objname = "SPECTRUM"
    display_name = 'Spectrum Analyzer'
    info = 'FFT based spectrum analyzer, analyze the frequency bin up to 16384 and featuring different kind of analysis window and averaging time(Decay) for better spectrum visualization.'
    expandable = True
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = SPECTRUM_GUI(self)

    def tweaker(self, key):
        if not key == 'fftsize':
            super().tweaker(key)
        else:
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name = key
            Parameter_Value = self.manager.widgetSet[key].widget_value[0]
            cmd = "set/%s/%s/%s/" % (AO_Name, Parameter_Name, Parameter_Value)

            if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

            if self.cSocket.connection:
                if not self.cSocket.mainSocket.isRunning():
                    self.cSocket.mainSocket.setQueryTask(cmd, 32)
                    self.cSocket.mainSocket.start()
                    self.cSocket.mainSocket.wait()
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                else:
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))