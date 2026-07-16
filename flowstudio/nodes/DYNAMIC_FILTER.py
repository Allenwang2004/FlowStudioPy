from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_plot import *
from control.flow_widget_dot import plotDot
from utilities.iir_designer import *

Color_Scheme = [
    [31, 119, 180, 100],
    [255, 127, 14, 100],
    [44, 160, 44, 100],
    [214, 39, 40, 100],
    [148, 103, 189, 100],
    [140, 86, 75, 100],
    [227, 119, 194, 100],
    [188, 189, 34, 100],
    [23, 190, 207, 100],
    [127, 127, 127, 100]
]


class DYNAMIC_FILTER_GUI(FLOW_GUI):
    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        """
            Initializes the DYNAMIC_FILTER_GUI class.

            Parameters:
                node (FLOW_Node_DYNAMIC_FILTER): The node to which the GUI belongs.
        """
        super().__init__(node)
        self.setFixedSize(900, 500)
        self.high_iir = []
        self.low_iir = []
        self.high_plot_widget = filter(self)
        self.low_plot_widget = filter(self)
        self.initLayout()
        self.createDot()
        self.initPlot()

    def initLayout(self):
        """
            Initializes the layout of the GUI components.
        """
        outer_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        left_top_layout = QHBoxLayout()
        left_top_layout.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignCenter)
        left_top_layout.setContentsMargins(0, 0, 0, 0)
        left_top_layout.setSpacing(0)

        left_bottom_layout = QHBoxLayout()

        left_bottom_left_layout = QVBoxLayout()

        groupbox_detection = QGroupBox()
        groupbox_detection_layout = QVBoxLayout()
        left_bottom_label = QLabel('Detection')
        left_bottom_label.setStyleSheet("font:12pt;")
        groupbox_detection_layout.addWidget(left_bottom_label, alignment=Qt.AlignCenter)
        groupbox_detection_layout.addWidget(self.gui_manager.widgetSet['ta'], alignment=Qt.AlignLeft)
        groupbox_detection_layout.addWidget(self.gui_manager.widgetSet['hold'], alignment=Qt.AlignLeft)
        groupbox_detection_layout.addWidget(self.gui_manager.widgetSet['te'], alignment=Qt.AlignLeft)
        groupbox_detection_layout.addWidget(self.gui_manager.widgetSet['tr'], alignment=Qt.AlignLeft)
        groupbox_detection_layout.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignLeft)

        groupbox_detection_layout.setContentsMargins(10, 10, 10, 10)
        groupbox_detection_layout.setSpacing(5)

        groupbox_detection.setLayout(groupbox_detection_layout)
        groupbox_detection.setStyleSheet("QGroupBox { border: 1px solid gray; }")

        left_bottom_left_layout.addWidget(groupbox_detection)

        left_bottom_left_layout.setContentsMargins(0, 0, 0, 0)
        left_bottom_left_layout.setSpacing(0)
        middle_layout = QVBoxLayout()

        left_bottom_right_layout = QVBoxLayout()

        groupbox_threshold = QGroupBox()
        groupbox_threshold_layout = QVBoxLayout()
        middle_label = QLabel('Auto Mix Threshold')
        middle_label.setStyleSheet("font:12pt;")
        groupbox_threshold_layout.addWidget(middle_label, alignment=Qt.AlignCenter)
        groupbox_threshold_layout.addWidget(self.gui_manager.widgetSet['HiThresh'], alignment=Qt.AlignLeft)
        groupbox_threshold_layout.addWidget(self.gui_manager.widgetSet['LowThresh'], alignment=Qt.AlignLeft)
        groupbox_threshold_layout.setContentsMargins(10, 10, 10, 70)
        groupbox_threshold_layout.setSpacing(25)

        groupbox_threshold.setLayout(groupbox_threshold_layout)
        groupbox_threshold.setStyleSheet("QGroupBox { border: 1px solid gray; }")

        left_bottom_right_layout.addWidget(groupbox_threshold)

        left_bottom_right_layout.setContentsMargins(10, 0, 0, 0)
        left_bottom_right_layout.setSpacing(0)

        left_bottom_layout.addLayout(left_bottom_left_layout)
        left_bottom_layout.addLayout(left_bottom_right_layout)
        left_bottom_layout.setContentsMargins(0, 0, 0, 0)
        left_bottom_layout.setSpacing(0)

        left_layout.addLayout(left_top_layout)
        left_layout.addLayout(left_bottom_layout)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        right_layout = QVBoxLayout()
        right_top_layout = QVBoxLayout()

        right_top_second_layout = QHBoxLayout()
        right_top_second_layout.addWidget(self.high_plot_widget)

        groupbox_high_eq = QGroupBox()

        right_top_right_layout = QVBoxLayout()
        right_top_right_layout.addWidget(self.gui_manager.widgetSet['HiFc'], alignment=Qt.AlignLeft)
        right_top_right_layout.addWidget(self.gui_manager.widgetSet['HiPeakFc'], alignment=Qt.AlignLeft)
        right_top_right_layout.addWidget(self.gui_manager.widgetSet['boostH'], alignment=Qt.AlignLeft)
        right_top_right_layout.addWidget(self.gui_manager.widgetSet['QH'], alignment=Qt.AlignLeft)

        right_top_right_layout.setContentsMargins(5, 0, 10, 0)
        right_top_right_layout.setSpacing(0)

        groupbox_high_eq.setLayout(right_top_second_layout)
        groupbox_high_eq.setStyleSheet("QGroupBox { border: 1px solid gray; }")

        right_top_second_layout.addLayout(right_top_right_layout)
        right_top_second_layout.setContentsMargins(0, 0, 0, 0)
        right_top_second_layout.setSpacing(0)
        self.high_iir.append(IIR_Designer(
            filter_type=HIGHPASS1,
            frequency_cut=self.gui_manager.widgetSet['HiFc'].widget_value,
            magnitude=0))
        self.high_iir.append(IIR_Designer(
            filter_type=PEAKING,
            frequency_cut=self.gui_manager.widgetSet['HiPeakFc'].widget_value,
            magnitude=self.gui_manager.widgetSet['boostH'].widget_value,
            Q=self.gui_manager.widgetSet['QH'].widget_value))

        right_top_label = QLabel('High SPL EQ')
        right_top_label.setStyleSheet("font:12pt;")
        right_top_layout.addWidget(right_top_label, alignment=Qt.AlignCenter)
        right_top_layout.addWidget(groupbox_high_eq)
        right_top_layout.setContentsMargins(0, 0, 0, 0)
        right_top_layout.setSpacing(0)
        right_layout.addLayout(right_top_layout)

        right_bottom_layout = QVBoxLayout()

        right_bottom_label = QLabel('Low SPL EQ')
        right_bottom_label.setStyleSheet("font:12pt;")
        right_bottom_layout.addWidget(right_bottom_label, alignment=Qt.AlignCenter)

        right_bottom_second_layout = QHBoxLayout()
        right_bottom_second_layout.addWidget(self.low_plot_widget)

        groupbox_low_eq = QGroupBox()

        right_bottom_right_layout = QVBoxLayout()
        right_bottom_right_layout.addWidget(self.gui_manager.widgetSet['LowFc'], alignment=Qt.AlignLeft)
        right_bottom_right_layout.addWidget(self.gui_manager.widgetSet['LowPeakFc'], alignment=Qt.AlignLeft)
        right_bottom_right_layout.addWidget(self.gui_manager.widgetSet['boostL'], alignment=Qt.AlignLeft)
        right_bottom_right_layout.addWidget(self.gui_manager.widgetSet['QL'], alignment=Qt.AlignLeft)

        groupbox_low_eq.setLayout(right_bottom_second_layout)
        groupbox_low_eq.setStyleSheet("QGroupBox { border: 1px solid gray; }")

        right_bottom_right_layout.setContentsMargins(5, 0, 10, 0)
        right_bottom_right_layout.setSpacing(0)

        right_bottom_second_layout.addLayout(right_bottom_right_layout)

        self.low_iir.append(IIR_Designer(
            filter_type=HIGHPASS1,
            frequency_cut=self.gui_manager.widgetSet['LowFc'].widget_value,
            magnitude=0))
        self.low_iir.append(IIR_Designer(
            filter_type=PEAKING,
            frequency_cut=self.gui_manager.widgetSet['LowPeakFc'].widget_value,
            magnitude=self.gui_manager.widgetSet['boostL'].widget_value,
            Q=self.gui_manager.widgetSet['QL'].widget_value))

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))
        right_bottom_second_layout.setContentsMargins(0, 0, 0, 0)
        right_bottom_second_layout.setSpacing(0)
        right_bottom_layout.addWidget(groupbox_low_eq)
        right_bottom_layout.setContentsMargins(0, 0, 0, 0)
        right_bottom_layout.setSpacing(0)
        right_layout.addLayout(right_bottom_layout)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(0)
        outer_layout.addLayout(left_layout)
        outer_layout.addLayout(middle_layout)
        outer_layout.addLayout(right_layout)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(0)

    def createDot(self):
        """
            Creates and initializes dot objects for plotting purposes.
        """
        self.high_dots = []
        high_first_dot_x_pos = self.gui_manager.widgetSet['HiFc'].widget_value
        high_first_dot_y_pos = 0
        high_first_dot = plotDot(pos=[np.log10(high_first_dot_x_pos), high_first_dot_y_pos],
                                 texts='1')
        high_first_dot.disableY = True
        self.high_dots.append(high_first_dot)
        high_second_dot_x_pos = self.gui_manager.widgetSet['HiPeakFc'].widget_value
        high_second_dot_y_pos = self.gui_manager.widgetSet['boostH'].widget_value
        self.high_dots.append(plotDot(pos=[np.log10(high_second_dot_x_pos), high_second_dot_y_pos],
                                      texts='2'))
        for i in range(2):
            self.high_dots[i].posChanged.connect(partial(self.update_number_box_val_by_dot_pos,
                                                         'high',
                                                         i))
        self.gui_manager.widgetSet['HiFc'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                        'HiFc'))
        self.gui_manager.widgetSet['HiPeakFc'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                            'HiPeakFc'))
        self.gui_manager.widgetSet['boostH'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                          'boostH'))

        self.low_dots = []
        low_first_dot_x_pos = self.gui_manager.widgetSet['LowFc'].widget_value
        low_first_dot_y_pos = 0
        low_first_dot = plotDot(pos=[np.log10(low_first_dot_x_pos), low_first_dot_y_pos],
                                texts='1')
        low_first_dot.disableY = True
        self.low_dots.append(low_first_dot)
        low_second_dot_x_pos = self.gui_manager.widgetSet['LowPeakFc'].widget_value
        low_second_dot_y_pos = self.gui_manager.widgetSet['boostL'].widget_value
        self.low_dots.append(plotDot(pos=[np.log10(low_second_dot_x_pos), low_second_dot_y_pos],
                                     texts='2'))
        for i in range(2):
            self.low_dots[i].posChanged.connect(partial(self.update_number_box_val_by_dot_pos,
                                                        'low',
                                                        i))
        self.gui_manager.widgetSet['LowFc'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                         'LowFc'))
        self.gui_manager.widgetSet['LowPeakFc'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                             'LowPeakFc'))
        self.gui_manager.widgetSet['boostL'].valueChanged.connect(partial(self.update_dot_pos_by_number_box_val,
                                                                          'boostL'))

    def update_number_box_val_by_dot_pos(self, type_str, index, value):
        """
            Updates the value of the number box based on the position of the dot.

            Parameters:
                type_str (str): Type of dot (either 'high' or 'low').
                index (int): Index of the dot.
                value (tuple): The new position value of the dot.
        """
        if type_str == 'high':
            if not self.high_dots[index].isDrag:
                return
            if index == 0:
                self.gui_manager.widgetSet['HiFc'].widget_value = 10 ** value[0]
            elif index == 1:
                self.gui_manager.widgetSet['HiPeakFc'].widget_value = 10 ** value[0]
                self.gui_manager.widgetSet['boostH'].widget_value = value[1]
            self.high_dots[index].isDrag = False
        elif type_str == 'low':
            if not self.low_dots[index].isDrag:
                return
            if index == 0:
                self.gui_manager.widgetSet['LowFc'].widget_value = 10 ** value[0]
            elif index == 1:
                self.gui_manager.widgetSet['LowPeakFc'].widget_value = 10 ** value[0]
                self.gui_manager.widgetSet['boostL'].widget_value = value[1]
            self.low_dots[index].isDrag = False

    def update_dot_pos_by_number_box_val(self, key):
        """
            Updates the position of the dot based on the value of the number box.

            Parameters:
                key (str): Key corresponding to the GUI element.
        """
        if key != 'onoff' and not self.gui_manager.widgetSet[key].spinbox.hasFocus():
            return
        if key == 'HiFc':
            x = np.log10(self.gui_manager.widgetSet['HiFc'].widget_value)
            y = 0
            index = 0
            if self.high_dots[index] in self.high_plot_widget.viewbox.allChildren():
                dot_pos = np.array([[x, y]], dtype=float)
                range = self.high_dots[index].scatter.getViewBox().viewRange()
                if dot_pos[0][0] == range[0][0]:
                    dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
                self.high_dots[index].setData(pos=dot_pos)
                self.high_dots[index].childItems()[1].setPos(x, y)
                self.high_dots[index].clicked()
        elif key == 'HiPeakFc' or key == 'boostH':
            x = np.log10(self.gui_manager.widgetSet['HiPeakFc'].widget_value)
            y = self.gui_manager.widgetSet['boostH'].widget_value
            index = 1
            if self.high_dots[index] in self.high_plot_widget.viewbox.allChildren():
                dot_pos = np.array([[x, y]], dtype=float)
                range = self.high_dots[index].scatter.getViewBox().viewRange()
                if dot_pos[0][0] == range[0][0]:
                    dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
                self.high_dots[index].setData(pos=dot_pos)
                self.high_dots[index].childItems()[1].setPos(x, y)
                self.high_dots[index].clicked()
        elif key == 'LowFc':
            x = np.log10(self.gui_manager.widgetSet['LowFc'].widget_value)
            y = 0
            index = 0
            if self.low_dots[index] in self.low_plot_widget.viewbox.allChildren():
                dot_pos = np.array([[x, y]], dtype=float)
                range = self.low_dots[index].scatter.getViewBox().viewRange()
                if dot_pos[0][0] == range[0][0]:
                    dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
                self.low_dots[index].setData(pos=dot_pos)
                self.low_dots[index].childItems()[1].setPos(x, y)
                self.low_dots[index].clicked()
        elif key == 'LowPeakFc' or key == 'boostL':
            x = np.log10(self.gui_manager.widgetSet['LowPeakFc'].widget_value)
            y = self.gui_manager.widgetSet['boostL'].widget_value
            index = 1
            if self.low_dots[index] in self.low_plot_widget.viewbox.allChildren():
                dot_pos = np.array([[x, y]], dtype=float)
                range = self.low_dots[index].scatter.getViewBox().viewRange()
                if dot_pos[0][0] == range[0][0]:
                    dot_pos[0][0] = np.math.ceil(range[0][0] * 100) / 100
                self.low_dots[index].setData(pos=dot_pos)
                self.low_dots[index].childItems()[1].setPos(x, y)
                self.low_dots[index].clicked()

    def initPlot(self):
        """
            Instantiate all plot objects.
        """
        self.high_pr_plot_child = []

        for index in range(2):
            self.high_pr_plot_child.append(index)
            self.high_pr_plot_child[index] = self.high_plot_widget.plotItem.plot(pen=Color_Scheme[index],
                                                                                 fillLevel=0,
                                                                                 fillBrush=Color_Scheme[index],
                                                                                 fillOutline=True)

        self.high_pr_plot = self.high_plot_widget.plotItem.plot(
            pen=pg.mkPen(color=(120, 120, 120), style=Qt.DashLine, width=1.5))
        self.high_fr_plot = self.high_plot_widget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), width=3))

        self.low_pr_plot_child = []

        for index in range(2):
            self.low_pr_plot_child.append(index)
            self.low_pr_plot_child[index] = self.low_plot_widget.plotItem.plot(pen=Color_Scheme[index],
                                                                               fillLevel=0,
                                                                               fillBrush=Color_Scheme[index],
                                                                               fillOutline=True)

        self.low_pr_plot = self.low_plot_widget.plotItem.plot(
            pen=pg.mkPen(color=(120, 120, 120), style=Qt.DashLine, width=1.5))
        self.low_fr_plot = self.low_plot_widget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), width=3))

    def refresh(self):
        """
            Refreshes the GUI and updates its state.
        """
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)

    def updateCoef(self):
        """
            Updates the coefficients of the filters based on GUI inputs.
        """
        h = 1
        for i in range(len(self.high_iir)):
            h = h * self.high_iir[i].h
            amplitude = 20 * np.log10(abs(self.high_iir[i].h))
            self.high_pr_plot_child[i].setData(x=self.high_iir[i].w, y=amplitude)
        amplitude = 20 * np.log10(abs(h))
        angle = np.angle(h)
        self.high_fr_plot.setData(x=self.high_iir[0].w, y=amplitude)
        self.high_pr_plot.setData(x=self.high_iir[0].w, y=angle / np.pi * 40)

        h = 1
        for i in range(len(self.low_iir)):
            h = h * self.low_iir[i].h
            amplitude = 20 * np.log10(abs(self.low_iir[i].h))
            self.low_pr_plot_child[i].setData(x=self.low_iir[i].w, y=amplitude)
        amplitude = 20 * np.log10(abs(h))
        angle = np.angle(h)
        self.low_fr_plot.setData(x=self.low_iir[0].w, y=amplitude)
        self.low_pr_plot.setData(x=self.low_iir[0].w, y=angle / np.pi * 40)

    def ctrl2plot(self, key):
        """
            Updates the plot based on value changes of control.

            Parameters:
                key (str): Key corresponding to the GUI element.
        """
        if key == 'onoff':
            for i in range(len(self.high_iir)):
                self.high_iir[i].bypass = not self.gui_manager.widgetSet[key].widget_value[1]
            for i in range(len(self.low_iir)):
                self.low_iir[i].bypass = not self.gui_manager.widgetSet[key].widget_value[1]
            if self.gui_manager.widgetSet[key].widget_value[1]:
                for i in range(len(self.high_dots)):
                    self.high_plot_widget.viewbox.addItem(self.high_dots[i])
                for i in range(len(self.low_dots)):
                    self.low_plot_widget.viewbox.addItem(self.low_dots[i])
                self.update_dot_pos_by_number_box_val(key)
            else:
                for i in range(len(self.high_dots)):
                    self.high_plot_widget.viewbox.removeItem(self.high_dots[i])
                for i in range(len(self.low_dots)):
                    self.low_plot_widget.viewbox.removeItem(self.low_dots[i])
            self.updateCoef()
        elif key == 'HiFc':
            self.high_iir[0].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'HiPeakFc':
            self.high_iir[1].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'boostH':
            self.high_iir[1].magnitude = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'QH':
            self.high_iir[1].q = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'LowFc':
            self.low_iir[0].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'LowPeakFc':
            self.low_iir[1].freq = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'boostL':
            self.low_iir[1].magnitude = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()
        elif key == 'QL':
            self.low_iir[1].q = self.gui_manager.widgetSet[key].widget_value
            self.updateCoef()


@register_node(OP_NODE_DYNAMIC_FILTER)
class FLOW_Node_DYNAMIC_FILTER(FLOW_Node):
    op_code = OP_NODE_DYNAMIC_FILTER
    op_title = "DYNAMIC_FILTER"
    content_label_objname = "DYNAMIC_FILTER"
    display_name = 'Dynamic Filter'
    info = 'This dynamic filtering algorithm consists of two EQ blocks specifically designed for Low SPL and High SPL signals. These EQ blocks are connected through a mixer.<br>The algorithm uses the low-frequency energy of the detected input signal to determine the input range corresponding to a value between 0 and 1 through a threshold setting.<br>This range is then used to switch the mixer between each EQ block.'
    expandable = True
    openable = True

    def __init__(self, scene):
        """
            Initializes the FLOW_Node_DYNAMIC_FILTER class.

            Parameters:
                scene (QGraphicsScene): The scene in which the node will be added.
        """
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()
        self.grNode.height = 530

    def initInnerClasses(self):
        """
            Initializes inner classes and creates the GUI widget for the node.
        """
        super().initInnerClasses()
        self.widget = DYNAMIC_FILTER_GUI(self)
