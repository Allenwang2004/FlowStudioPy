from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
import scipy.signal

class IIRCOEF_GUI(FLOW_GUI):

    def __init__(self, node):
        super().__init__(node)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()

    def initExtraWidget(self):
        self.plotWidget = filter(self)

        self.phaseSwitch = Switch('Phase', 'on').get_widget(self)
        self.phaseSwitch.toggle.toggled.connect(self.control_phase_switch)

        self.gui_manager.widgetSet['File'].valueChanged.connect(partial(self.ctrl2plot, 'File'))
        self.gui_manager.widgetSet['File'].valueChanged.connect(partial(self.node.tweaker, 'File'))

    def control_phase_switch(self, turn_on):
        if turn_on:
            self.pr_plot.setPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5)
        else:
            self.pr_plot.setPen(None)

    def initLayout(self):
        layout1 = QVBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['File'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.phaseSwitch, alignment=Qt.AlignLeft)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(layout1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def initPlot(self):
        self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5))
        self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))

    def ctrl2plot(self, key):
        self.pr_plot.clear()
        self.fr_plot.clear()

        if self.gui_manager.widgetSet['File'].widget_value[0] and key == 'File':
            numerator = self.gui_manager.widgetSet['File'].widget_value[1][0]
            denominator = self.gui_manager.widgetSet['File'].widget_value[1][1]
            w, h = scipy.signal.freqz(numerator, denominator, worN=np.logspace(1, np.log(22000) / np.log(20), num=1024, base=20), whole=False, fs=44100)

            amplitude = 20 * np.log10(abs(h))
            angle = np.angle(h)
            self.fr_plot.setData(x=w, y=amplitude)
            self.pr_plot.setData(x=w, y=angle / np.pi * 40)

    def refresh(self):
        super().refresh()
        self.ctrl2plot('File')

@register_node(OP_NODE_IIRCOEF)
class FLOW_Node_IIRCOEF(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_IIRCOEF
    op_title = "IIRCOEF"
    content_label_objname = "IIRCOEF"
    display_name = 'Generic IIR filter'
    info = 'The IIRCOEF filter is an IIR filter directly executing the loaded coefficients and its order is up to 10.'
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

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = IIRCOEF_GUI(self)

    def tweaker(self, key):
        if key in ['onoff', 'ready']:
            super().tweaker(key)
        elif key == 'File' and self.manager.widgetSet[key].widget_value[0]:
            cmd = list()
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name_1 = 'b'
            numerator = self.manager.widgetSet[key].widget_value[1][0]

            Parameter_Name_2 = 'a'
            denominator = self.manager.widgetSet[key].widget_value[1][1]

            for index in range(len(numerator)):
                head_1 = "setCoord/%s/%s/%s/%s/0" % (AO_Name, Parameter_Name_1, numerator[index], index)
                head_2 = "setCoord/%s/%s/%s/%s/0" % (AO_Name, Parameter_Name_2, denominator[index], index)
                cmd.append(head_1)
                cmd.append(head_2)
            cmd.append("set/%s/ready/1/0/0" % AO_Name)

            if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

            if self.cSocket.connection:
                while self.cSocket.mainSocket.isRunning():
                    time.sleep(0.01)
                if not self.cSocket.mainSocket.isRunning():
                    self.cSocket.mainSocket.setQueryTasks(cmd, 32)
                    self.cSocket.mainSocket.start()
                    self.cSocket.mainSocket.wait()
                    if Debug.DEBUG_TWEAKER.value: print(self.cSocket.mainSocket.result)
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                else:
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))
