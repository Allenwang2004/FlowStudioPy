from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
from flowstudio.flow_window_connection import *
from utilities.crossover_designer import *
from flowstudio.controls.TapMenu import TapMenu as TapMenuControl
from control.flow_control_widget import TapMenu as TapMenuUI


class XOverGUI(FLOW_GUI):

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(800, 300)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()

        self.xoverLF = Crossover_Designer(
            filter_type=LOW,
            filter_topology=self.gui_manager.widgetSet['kindLF'].widget_value[1],
            frequency_cut=self.gui_manager.widgetSet['fcLF'].widget_value)

        self.xoverHF = Crossover_Designer(
            filter_type=HIGH,
            filter_topology=self.gui_manager.widgetSet['kindHF'].widget_value[1],
            frequency_cut=self.gui_manager.widgetSet['fcHF'].widget_value)

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))

    def initExtraWidget(self):
        self.plotWidget = filter(self)

        fcLF = self.gui_manager.widgetSet['fcLF'].widget_value
        self.dotLF = plotDot([np.log10(fcLF), 0], '0')
        self.dotLF.selected()
        self.dotLF.disableY = True
        # self.dotLF.posChanged.connect(self.dotPos_numberBox_LF)
        self.gui_manager.widgetSet['fcLF'].valueChanged.connect(self.numberBox_dotPos_LF)

        fcHF = self.gui_manager.widgetSet['fcHF'].widget_value
        self.dotHF = plotDot([np.log10(fcHF), 0], '1')
        self.dotHF.selected()
        self.dotHF.disableY = True
        # self.dotHF.posChanged.connect(self.dotPos_numberBox_HF)
        self.gui_manager.widgetSet['fcHF'].valueChanged.connect(self.numberBox_dotPos_HF)

        self.phaseSwitchLF = Switch('PhaseLF', 'on').get_widget(self)
        self.phaseSwitchLF.toggle.toggled.connect(self.control_phase_switch_lf)

        self.phaseSwitchHF = Switch('PhaseHF', 'on').get_widget(self)
        self.phaseSwitchHF.toggle.toggled.connect(self.control_phase_switch_hf)

    def dotPos_numberBox_LF(self, value):
        self.gui_manager.widgetSet['fcLF'].widget_value = 10 ** value[0]

    def numberBox_dotPos_LF(self):
        x = np.log10(self.gui_manager.widgetSet['fcLF'].widget_value)
        dot_pos = np.array([[x, 0]], dtype=float)
        range = self.dotLF.scatter.getViewBox().viewRange()
        if dot_pos[0][0] == range[0][0]:
            dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
        self.dotLF.setData(pos=dot_pos)
        self.dotLF.childItems()[1].setPos(dot_pos[0][0], dot_pos[0][1])
        self.dotLF.clicked()

    def dotPos_numberBox_HF(self, value):
        self.gui_manager.widgetSet['fcHF'].widget_value = 10 ** value[0]

    def numberBox_dotPos_HF(self):
        x = np.log10(self.gui_manager.widgetSet['fcHF'].widget_value)
        dot_pos = np.array([[x, 0]], dtype=float)
        range = self.dotHF.scatter.getViewBox().viewRange()
        if dot_pos[0][0] == range[0][0]:
            dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
        self.dotHF.setData(pos=dot_pos)
        self.dotHF.childItems()[1].setPos(dot_pos[0][0], dot_pos[0][1])
        self.dotHF.clicked()

    def control_phase_switch_lf(self, turn_on):
        if turn_on:
            self.pr_plot_LF.setPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5)
        else:
            self.pr_plot_LF.setPen(None)

    def control_phase_switch_hf(self, turn_on):
        if turn_on:
            self.pr_plot_HF.setPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5)
        else:
            self.pr_plot_HF.setPen(None)

    def initLayout(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.gui_manager.widgetSet['EnableLF'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['EnableHF'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['kindLF'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['kindHF'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.phaseSwitchLF, alignment=Qt.AlignLeft)
        layout1.addWidget(self.phaseSwitchHF, alignment=Qt.AlignLeft)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.gui_manager.widgetSet['fcLF'], alignment=Qt.AlignHCenter)
        layout2.addWidget(self.gui_manager.widgetSet['fcHF'], alignment=Qt.AlignHCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(layout1)
        layout.addWidget(self.plotWidget)
        layout.addLayout(layout2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def ctrl2plot(self, key):
        if key == 'EnableLF':
            self.xoverLF.bypass = not self.gui_manager.widgetSet[key].widget_value[1]
        elif key == 'kindLF':
            self.xoverLF.filter_topology = self.gui_manager.widgetSet[key].widget_value[1]
        elif key == 'fcLF':
            self.xoverLF.freq = self.gui_manager.widgetSet[key].widget_value
        elif key == 'EnableHF':
            self.xoverHF.bypass = not self.gui_manager.widgetSet[key].widget_value[1]
        elif key == 'kindHF':
            self.xoverHF.filter_topology = self.gui_manager.widgetSet[key].widget_value[1]
        elif key == 'fcHF':
            self.xoverHF.freq = self.gui_manager.widgetSet[key].widget_value

        h1_LF, h2_LF, h3_LF, h4_LF = self.xoverLF.h
        amplitude = 20 * np.log10(abs(h1_LF)) + 20 * np.log10(abs(h2_LF)) + 20 * np.log10(abs(h3_LF)) + 20 * np.log10(
            abs(h4_LF))
        angle = np.angle(h1_LF) + np.angle(h2_LF) + np.angle(h3_LF) + np.angle(h4_LF)
        self.fr_plot_LF.setData(x=self.xoverLF.master[0].w, y=amplitude)
        self.pr_plot_LF.setData(x=self.xoverLF.master[0].w, y=angle / np.pi * 40)

        h1_HF, h2_HF, h3_HF, h4_HF = self.xoverHF.h
        amplitude = 20 * np.log10(abs(h1_HF)) + 20 * np.log10(abs(h2_HF)) + 20 * np.log10(abs(h3_HF)) + 20 * np.log10(
            abs(h4_HF))
        angle = np.angle(h1_HF) + np.angle(h2_HF) + np.angle(h3_HF) + np.angle(h4_HF)
        self.fr_plot_HF.setData(x=self.xoverHF.master[0].w, y=amplitude)
        self.pr_plot_HF.setData(x=self.xoverHF.master[0].w, y=angle / np.pi * 40)

    def initPlot(self):
        self.fr_plot_LF = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.pr_plot_LF = self.plotWidget.plotItem.plot(
            pen=pg.mkPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5))

        self.fr_plot_HF = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.pr_plot_HF = self.plotWidget.plotItem.plot(
            pen=pg.mkPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5))

        self.plotWidget.viewbox.addItem(self.dotLF)
        self.plotWidget.viewbox.addItem(self.dotHF)

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

class XOverCtrlManager(FLOW_Ctrl_Manager):
    # TODO: we need fix config in flow engine in the future to prevent manual code

    def initNodeParam(self, parent: QWidget, parameterStored: bool):
        parameter = TapMenuControl({},
                                   parameters={"pSize" : 2, "cSize": 3, "cParameter":{}}).parameters
        self.tap = TapMenuUI(parent, parameter, False)
        self.tap.setTabText(0,'LF')
        self.tap.setTabText(1,'HF')

        self.content = parent

        res = self.createControlInterface('EnableLF', self.config['EnableLF'], self.tap.widget(0))
        res.label.setText('enable')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['EnableLF'] = res

        res = self.createControlInterface('fcLF', self.config['fcLF'], self.tap.widget(0))
        res.label.setText('fc')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['fcLF'] = res

        res = self.createControlInterface('kindLF', self.config['kindLF'], self.tap.widget(0))
        res.label.setText('kind')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['kindLF'] = res

        res = self.createControlInterface('EnableHF', self.config['EnableHF'], self.tap.widget(1))
        res.label.setText('enable')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['EnableHF'] = res

        res = self.createControlInterface('fcHF', self.config['fcHF'], self.tap.widget(1))
        res.label.setText('fc')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['fcHF'] = res

        res = self.createControlInterface('kindHF', self.config['kindHF'], self.tap.widget(1))
        res.label.setText('kind')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['kindHF'] = res

    def initPos(self):
        self.tap.move(10, 10)

        self.widgetSet['EnableLF'].move(0, 10)
        self.widgetSet['kindLF'].move(0, 40)
        self.widgetSet['fcLF'].move(0, 70)

        self.widgetSet['EnableHF'].move(0, 10)
        self.widgetSet['kindHF'].move(0, 40)
        self.widgetSet['fcHF'].move(0, 70)

        return 120
        

@register_node(OP_NODE_XOVER_FP)
class FlowNodeXOverFP(FlowFixedPointNode):
    #icon = "icons/in.png"
    op_code = OP_NODE_XOVER_FP
    op_title = "XOVER_FP"
    content_label_objname = "XOVER_FP"
    display_name = '2-way crossover (fixed-point)'
    info = 'Fixed-point version of XOVER'
    expandable = True
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1, 1], rule_check_mode=-2)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = XOverCtrlManager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = XOverGUI(self)

    def initSocketTooltip(self):
        self.inputs[0].grSocket.setToolTip("input")
        self.outputs[0].grSocket.setToolTip("LF output")
        self.outputs[1].grSocket.setToolTip("HF output")