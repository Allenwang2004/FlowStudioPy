from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


thread_timeout = 50
class ROOM_FIX_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(200, 400)
        self.initExtraWidget()
        self.initLayout()

        self.isConnected = False
        self.lastBPM = 120
        self.isBPMChanged = False

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def initExtraWidget(self):
        self.tempoIndicator = QLabel(self)
        self.tempoIndicator.setStyleSheet("background-color: white;"
                                          "font: 30pt Arial;")
        self.tempoIndicator.setAlignment(QtCore.Qt.AlignCenter)

        self.beatOnSetIndicator = QLabel(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        self.TempoTimer = QTimer(self)
        self.TempoTimer.timeout.connect(self.updateTempoIndicator)

        self.display = Switch('update', 'off').get_widget(self)
        self.display.toggle.toggled.connect(self.toggle)

    def initLayout(self):

        layout1 = QVBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['freeze'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['reset'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['fsboost'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['ta'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['tr'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['tf'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['slope'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['effthold'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.display, alignment=Qt.AlignLeft)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tempoIndicator)
        layout.addWidget(self.beatOnSetIndicator)
        layout.addWidget(self.display)
        layout.addLayout(layout1, 3)

    def toggle(self, bool):
        # if self.isConnected and not bool and self.socket.connection:
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout(index=1)
            self.timer.stop()
            self.TempoTimer.stop()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)
        else:
            pass

    def updateTempoIndicator(self):

        self.isBPMChanged = not self.isBPMChanged
        if (self.isBPMChanged):

            self.tempoIndicator.setStyleSheet("background-color: green;"
                                              "font: 30pt Arial;")
        else:
            self.tempoIndicator.setStyleSheet("background-color: white;"
                                              "font: 30pt Arial;")

    def fetchData(self):
        # if DEBUG: print('socket connection: %r' %self.socket.connection)
        # if DEBUG: print('is client socket running: %r' %self.client.isRunning())
        # if DEBUG: print('is main socket running: %r' %self.socket.mainSocket.isRunning())
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "monitor"
            cmd = "getSerialized/%s/%s/" % (AO_Name, Parameter_Name)
            self.client.setQueryTask(cmd, 16)
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
            if Debug.DEBUG_THREAD.value: print('%s: current query is still running, skip this query.' % self.node)

    def process(self):
        boostdB = float(self.client.result[1].decode().split('/')[0])
        ref_LF = float(self.client.result[1].decode().split('/')[1])
        ref_HF = float(self.client.result[1].decode().split('/')[2])
        mic_LF = float(self.client.result[1].decode().split('/')[3])
        mic_HF = float(self.client.result[1].decode().split('/')[4])
        if Debug.DEBUG_THREAD.value:
            print('%s:' % self.node)
            print(str(boostdB) + ', ' + str(ref_LF) + ', ' + str(ref_HF) + ', ' + str(mic_LF) + ', ' + str(mic_HF))

        self.tempoIndicator.setText(str(boostdB))

@register_node(OP_NODE_ROOM_FIX)
class FLOW_Node_ROOM_FIX(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_ROOM_FIX
    op_title = "ROOM_FIX"
    content_label_objname = "ROOM_FIX"
    expandable = True
    openable = True


    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = ROOM_FIX_GUI(self)