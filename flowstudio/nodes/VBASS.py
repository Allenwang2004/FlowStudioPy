from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
from flowstudio.flow_window_connection import *
from utilities.crossover_designer import *

class VBassGUI(FLOW_GUI):

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(800, 320)
        self.init_extra_widget()
        self.init_layout()
        self.init_plot()

        self.vbass_blue = Crossover_Designer(
            filter_type=LOW,
            filter_topology=3,
            frequency_cut=self.gui_manager.widgetSet['fcReson'].widget_value)

        self.vbass_yellow_right = Crossover_Designer(
            filter_type=LOW,
            filter_topology=3,
            frequency_cut=self.gui_manager.widgetSet['fcLBPF'].widget_value)

        self.vbass_yellow_left = Crossover_Designer(
            filter_type=HIGH,
            filter_topology=3,
            frequency_cut=self.gui_manager.widgetSet['fcReson'].widget_value)

        self.vbass_green = Crossover_Designer(
            filter_type=HIGH,
            filter_topology=3,
            frequency_cut=self.gui_manager.widgetSet['fcReson'].widget_value)

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))

    def init_extra_widget(self):
        self.plotWidget = VBassFilter(self)

    def init_layout(self):
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['fcReson'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['fcLBPF'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['LPGain'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['VBGain'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['HPGain'], alignment=Qt.AlignCenter)
        right_layout.addWidget(self.gui_manager.widgetSet['intens'], alignment=Qt.AlignCenter)
        right_layout.setSpacing(1)

        image_label = QLabel()
        image = QPixmap('../../resources/ship.png')  # 替换为您的图片路径
        image_label.setPixmap(image)

        layout = QHBoxLayout(self)
        layout.addWidget(image_label)
        layout.addWidget(self.plotWidget, 8)
        layout.addLayout(right_layout, 2)
        layout.addWidget(image_label)

    def ctrl2plot(self, key):
        fcReson = self.gui_manager.widgetSet['fcReson'].widget_value
        fcLBPF = self.gui_manager.widgetSet['fcLBPF'].widget_value
        if fcReson > fcLBPF:
            statement = "FcReson must be lower than fcLBPF, please try again"
            QMessageBox.about(self.window(), "Note", "%s" % statement)
            if key == 'fcReson':
                self.gui_manager.widgetSet['fcReson'].widget_value = self.gui_manager.widgetSet['fcLBPF'].widget_value
            elif key == 'fcLBPF':
                self.gui_manager.widgetSet['fcLBPF'].widget_value = self.gui_manager.widgetSet['fcReson'].widget_value
            return

        if key =='fcReson':
            self.vbass_blue.freq = self.gui_manager.widgetSet[key].widget_value
            self.vbass_green.freq = self.gui_manager.widgetSet[key].widget_value
            self.vbass_yellow_left.freq = self.gui_manager.widgetSet[key].widget_value
        elif key =='fcLBPF':
            self.vbass_yellow_right.freq = self.gui_manager.widgetSet[key].widget_value

        h1_LF, h2_LF, h3_LF, h4_LF = self.vbass_blue.h
        amplitude = 20 * np.log10(abs(h1_LF)) + 20 * np.log10(abs(h2_LF)) + 20 * np.log10(abs(h3_LF)) + 20 * np.log10(abs(h4_LF))
        amplitude = np.array(amplitude, dtype=float) + self.gui_manager.widgetSet['LPGain'].widget_value
        self.fr_plot_blue.setData(x=self.vbass_blue.master[0].w, y=amplitude)

        h1_LF, h2_LF, h3_LF, h4_LF = self.vbass_green.h
        amplitude = 20 * np.log10(abs(h1_LF)) + 20 * np.log10(abs(h2_LF)) + 20 * np.log10(abs(h3_LF)) + 20 * np.log10(
            abs(h4_LF))
        amplitude = np.array(amplitude, dtype=float) + self.gui_manager.widgetSet['HPGain'].widget_value
        self.fr_plot_green.setData(x=self.vbass_green.master[0].w, y=amplitude)

        h1_LF, h2_LF, h3_LF, h4_LF = self.vbass_yellow_left.h
        amplitude_left = list(20 * np.log10(abs(h1_LF)) + 20 * np.log10(abs(h2_LF)) + 20 * np.log10(abs(h3_LF)) + 20 * np.log10(
            abs(h4_LF)))

        h1_LF, h2_LF, h3_LF, h4_LF = self.vbass_yellow_right.h
        amplitude_right = 20 * np.log10(abs(h1_LF)) + 20 * np.log10(abs(h2_LF)) + 20 * np.log10(abs(h3_LF)) + 20 * np.log10(
            abs(h4_LF))
        diff_mix_index = self.find_min_diff_index(amplitude_left, amplitude_right)
        amplitude_right = list(amplitude_left[0:diff_mix_index+1]) + list(amplitude_right[diff_mix_index+1:1024])
        amplitude = np.array(amplitude_right, dtype=float) + self.gui_manager.widgetSet['VBGain'].widget_value
        self.fr_plot_yellow.setData(x=self.vbass_yellow_right.master[0].w, y=amplitude)


    def init_plot(self):
        legend = self.plotWidget.addLegend(offset=(1, 1))
        legend.mouseDragEvent = lambda *args, **kwargs: None
        legend.hoverEvent = lambda *args, **kwargs: None
        self.fr_plot_blue = self.plotWidget.plotItem.plot(pen=pg.mkPen((39, 192, 210), width=3), name='Original Bass',
                                                          fillLevel=-80, fillBrush=[31, 119, 180, 100], fillOutline=False)
        self.fr_plot_green = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3), name='Input + HPF',
                                                           fillLevel=-80, fillBrush=[26, 188, 156, 100], fillOutline=False)
        self.fr_plot_yellow = self.plotWidget.plotItem.plot(pen=pg.mkPen((219, 186, 68), width=3), name='Virtual Bass',
                                                            fillLevel=-80, fillBrush=[138, 113, 40, 100], fillOutline=False)


    def find_min_diff_index(self, arr1, arr2):
        # 计算两个数组中对应位置的值的差的绝对值
        abs_differences = [(abs(arr1[i] - arr2[i]), i) for i in range(len(arr1))]

        # 找出最小值以及其索引
        min_difference = min(abs_differences, key=lambda x: x[0])
        min_index = min_difference[1]

        return min_index

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)


@register_node(OP_NODE_VBASS)
class FLOW_Node_VBASS(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_VBASS
    op_title = "VBASS"
    content_label_objname = "VBASS"
    display_name = 'Virtual Bass'
    info = 'Virtual bass utilizes band extension method to reproduce low pitched signal by psychoacoustic phenomena effect. This application is great for small speaker'
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
        self.widget = VBassGUI(self)