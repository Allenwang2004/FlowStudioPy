from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from utilities.crossover_designer import *


class LPF_GUI(FLOW_GUI):

    def __init__(self, node):
        super().__init__(node)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()

        self.xover = Crossover_Designer(
            filter_type = LOW,
            filter_topology=self.gui_manager.widgetSet['kind'].widget_value[1],
            frequency_cut = self.gui_manager.widgetSet['fc'].widget_value)

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))

    def initExtraWidget(self):
        self.plotWidget = filter(self)

        fc = self.gui_manager.widgetSet['fc'].widget_value
        self.dot = plotDot([np.log10(fc), 0])
        self.dot.selected()
        self.dot.disableY = True
        self.dot.posChanged.connect(self.dotPos_numberBox)
        self.gui_manager.widgetSet['fc'].valueChanged.connect(self.numberBox_dotPos)

        self.phaseSwitch = Switch('Phase', 'on').get_widget(self)
        self.phaseSwitch.toggle.toggled.connect(self.control_phase_switch)

    def dotPos_numberBox(self, value):
        self.gui_manager.widgetSet['fc'].widget_value = 10**value[0]

    def numberBox_dotPos(self):
        x = np.log10(self.gui_manager.widgetSet['fc'].widget_value)
        dot_pos = np.array([[x, 0]], dtype=float)
        range = self.dot.scatter.getViewBox().viewRange()
        if dot_pos[0][0] == range[0][0]:
            dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
        self.dot.setData(pos=dot_pos)

    def control_phase_switch(self, turn_on):
        if turn_on:
            self.pr_plot.setPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5)
        else:
            self.pr_plot.setPen(None)

    def initLayout(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['Enable'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['kind'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.phaseSwitch, alignment=Qt.AlignLeft)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignHCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(layout1)
        layout.addWidget(self.plotWidget)
        layout.addLayout(layout2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def ctrl2plot(self, key):
        if key == 'Enable':
            self.xover.bypass = not self.gui_manager.widgetSet[key].widget_value[1]
        elif key =='kind':
            self.xover.filter_topology = self.gui_manager.widgetSet[key].widget_value[1]
        elif key =='fc':
            self.xover.freq = self.gui_manager.widgetSet[key].widget_value

        h1, h2, h3, h4 = self.xover.h
        amplitude = 20 * np.log10(abs(h1)) + 20 * np.log10(abs(h2)) + 20 * np.log10(abs(h3)) + 20 * np.log10(abs(h4))
        angle = np.angle(h1)+np.angle(h2)+np.angle(h3)+np.angle(h4)
        self.fr_plot.setData(x=self.xover.master[0].w, y=amplitude)
        self.pr_plot.setData(x=self.xover.master[0].w, y=angle/np.pi*40)

    def initPlot(self):
        self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5))

        self.plotWidget.viewbox.addItem(self.dot)

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

@register_node(OP_NODE_LPF)
class FLOW_Node_LPF(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_LPF
    op_title = "LPF"
    content_label_objname = "LPF"
    display_name = 'Low Pass Filter'
    info = 'This audio object allows the user to choose between a collection of low-pass filters of Butterworth, Bessel and Linkwitz-Riley'
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
        super().__init__(scene, self.inputs, self.outputs )
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = LPF_GUI(self)

    def serialize(self):
        res = super().serialize()
        res['content']['filter'] = 1
        return res