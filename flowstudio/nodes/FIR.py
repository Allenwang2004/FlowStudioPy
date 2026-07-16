from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
import scipy.signal

class FIR_GUI(FLOW_GUI):

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(800, 300)
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
            self.pr_plot.setPen(color=(87, 101, 116), style=Qt.DashLine, width=1)
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
        self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(87, 101, 116), style=Qt.DashLine, width=1))
        self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((254, 202, 87), width=3))

    def ctrl2plot(self, key):
        self.pr_plot.clear()
        self.fr_plot.clear()

        if self.gui_manager.widgetSet['File'].widget_value[0] and key == 'File':
            numerator = self.gui_manager.widgetSet['File'].widget_value[1][0]
            denominator = 1
            w, h = scipy.signal.freqz(numerator, denominator, worN=np.logspace(1, np.log(22000) / np.log(20), num=1024, base=20), whole=False, fs=44100)

            amplitude = 20 * np.log10(abs(h))
            angle = np.angle(h)
            self.fr_plot.setData(x=w, y=amplitude)
            self.pr_plot.setData(x=w, y=(angle / np.pi * 40))

    def refresh(self):
        super().refresh()
        self.ctrl2plot('File')

@register_node(OP_NODE_FIR)
class FLOW_Node_FIR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_FIR
    op_title = "FIR"
    content_label_objname = "FIR"
    display_name = 'FIR filter'
    info = 'As the name implies, this audio object will provide a finite impulse response filter to the user. The user needs to load manually the FIR coefficients in the coefficients space of the design window. There needs to be a single coefficient per line in the coefficients space. The maximum number of taps that the FIR filter supports is 1024.'
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
        # TODO: we need to initControl in the future...
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = FIR_GUI(self)

    def tweaker(self, key):
        if key == 'onoff':
            super().tweaker(key)
        elif key == 'File' and self.manager.widgetSet[key].widget_value[0]:
            cmd = list()

            coefArray = self.manager.widgetSet[key].widget_value[1][0]
            # if len(coefArray) / 2 > len(coefArray) >> 1:
            #     size = (len(coefArray) >> 1) + 1
            # else:
            #     size = len(coefArray) >> 1
            size = len(coefArray)
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            for index in range(size):
                # start = index * 2
                # end = len(coefArray) if (index+1) * 2 > len(coefArray) else (index+1) * 2
                coefs = coefArray[index]
                # head = "setSerializeCoord/%s/b/%s/%s/0/" % (AO_Name, start, end-1)
                head = "setCoord/%s/b/%s/%s/0/" % (AO_Name, str(coefs), str(index))

                # for coef in coefs:
                #     head = head + str(coef) + '/'

                cmd.append(head)

            tapConstruct = "set/%s/%s/%s/" % (AO_Name, 'tap', len(coefArray))
            # cmd.insert(0, tapConstruct)
            cmd.append(tapConstruct)
            # cmdToSend = np.transpose(cmd)

            if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

            if self.cSocket.connection:
                while self.cSocket.mainSocket.isRunning():
                    time.sleep(0.01)
                if not self.cSocket.mainSocket.isRunning():

                    self.cSocket.mainSocket.setQueryTasks(cmd, 64)
                    self.cSocket.mainSocket.client.settimeout(5)
                    QApplication.setOverrideCursor(Qt.WaitCursor)
                    self.cSocket.mainSocket.start()
                    self.cSocket.mainSocket.wait()
                    self.cSocket.mainSocket.client.settimeout(1)
                    QApplication.restoreOverrideCursor()
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                else:
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))
