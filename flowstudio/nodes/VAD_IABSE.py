from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import SocketType
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.controls.SpecialFloatSpinBox import SpecialFloatSpinBox

thread_timeout = 50


class VAD_IABSE_GUI(FLOW_GUI):
    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(140, 150)
        self.initExtraWidget()
        self.initLayout()
        self.isConnected = False

    def initLayout(self):
        outer_layout = QHBoxLayout(self)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
        inner_layout.addWidget(self.gui_manager.widgetSet['Sensit'], alignment=Qt.AlignLeft)
        self.vad = SpecialFloatSpinBox('VAD', 1, 0, 0).get_widget(self.node.content)
        inner_layout.addWidget(self.vad, alignment=Qt.AlignLeft)
        inner_layout.addWidget(self.display, alignment=Qt.AlignLeft)

        outer_layout.addLayout(inner_layout, 2)
        outer_layout.setContentsMargins(0, 0, 0, 0)

    def initExtraWidget(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        self.display = Switch('update', 'off').get_widget(self)
        self.display.toggle.clicked.connect(self.toggle)

    def toggle(self, bool):
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout()
            self.timer.stop()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "Flag"
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
        self.vad.numbox.setValue(int(val))


@register_node(OP_NODE_VAD_IABSE)
class FLOW_Node_VAD_IABSE(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_VAD_IABSE
    op_title = "VAD_IABSE"
    content_label_objname = "VAD_IABSE"
    display_name = 'VAD'
    info = 'Voice activity detection (VAD) is the method to distinguish the human speech segments from digital signal.<br>The audio object provides traditional method rather than AI to save memory size.<br>It includes improved entropy-based endpoint detection algorithm, adaptive band-partitioning spectral entropy and zero-crossing rate method.'
    expandable = True
    openable = True

    def __init__(self, scene):
        self.inputs = [1]
        self.outctrls = [SocketType.FLOAT.value]
        super().__init__(scene, inputs=self.inputs, outctrls=self.outctrls)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        super().initInnerClasses()
        self.widget = VAD_IABSE_GUI(self)
