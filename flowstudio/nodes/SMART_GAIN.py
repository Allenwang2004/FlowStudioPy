from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import SocketType
from flowstudio.flow_node_base import *

thread_timeout = 50

class SMART_GAIN_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node: 'Node'):
        super().__init__(node)
        self.setFixedSize(200, 200)
        self.initExtraWidget()
        self.initLayout()

        self.isConnected = False

    def initExtraWidget(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

    def initLayout(self):
        self.display = Switch('update', 'off').get_widget(self)
        self.display.toggle.toggled.connect(self.toggle)

        layout = QVBoxLayout(self)
        layout.addWidget(self.gui_manager.widgetSet['range'], alignment=Qt.AlignCenter)
        layout.addWidget(self.gui_manager.widgetSet['target'], alignment=Qt.AlignCenter)
        layout.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignCenter)
        layout.addWidget(self.display, alignment=Qt.AlignCenter)
        layout.setSpacing(1)

    def toggle(self, bool):
        # if self.isConnected and not bool and self.socket.connection:
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout(index=1)
            self.timer.stop()
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

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "onoff"
            cmd = "get/%s/%s/" % (AO_Name, Parameter_Name)
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
        val = self.client.result[1].decode("utf-8").rstrip('\x00').replace('.', '')
        self.gui_manager.widgetSet['onoff'].numbox.setValue(int(val))


@register_node(OP_NODE_SMART_GAIN)
class FLOW_Node_SAMRT_GAIN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_SMART_GAIN
    op_title = "SMART_GAIN"
    content_label_objname = "SMART_GAIN"
    display_name = 'Smart Gain'
    info = 'SMART_GAIN is the algorithm that automatically controls the amplitude increase of an audio signal from original input to amplified output by VAD.'
    expandable = True
    openable = True

    def __init__(self, scene):
        self.inputs = [1]
        self.outputs = [1]
        self.inctrls = [SocketType.FLOAT.value]
        super().__init__(scene, inputs=self.inputs, outputs=self.outputs, inctrls=self.inctrls)
        self.initControl()
        self.eval()
        self.manager.widgetSet["onoff"].setHidden(True)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = SMART_GAIN_GUI(self)