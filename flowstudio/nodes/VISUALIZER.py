import numpy as np

from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from flowstudio.controls.Menu import Menu

thread_timeout = 100

class VISUALIZER_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(800, 350)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()
        self.onOverallMenuChanged()

        self.isConnected = False

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def initExtraWidget(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        self.plotWidget = signal_filter(self)

        # Overall Control
        self.overall_label = QLabel(self)
        self.overall_label.setText('Overall Control')

        self.overall_Menu = Menu('', ['Time', 'Freq'], 'Time').get_widget(self)
        self.overall_Menu.label.setFixedWidth(0)
        self.overall_Menu.comboBox.currentIndexChanged.connect(self.onOverallMenuChanged)

        self.display = Switch('Update', 'off').get_widget(self)
        self.display.label.setFixedWidth(100)
        self.display.toggle.toggled.connect(self.toggle)

        self.show_grid = Switch('Show Grid', 'on').get_widget(self)
        self.show_grid.label.setFixedWidth(100)
        self.show_grid.toggle.toggled.connect(self.onShowGrid)
        self.onShowGrid(True)

        # Y Axis
        self.y_axis_label = QLabel(self)
        self.y_axis_label.setText('Y Axis')

        self.y_axis_menu = Menu('', ['Linear', 'db10', 'db20'], 'Linear').get_widget(self)
        self.y_axis_menu.label.setFixedWidth(0)
        self.y_axis_menu.comboBox.currentIndexChanged.connect(self.onYAxisMenuChanged)
        self.y_axis_menu.comboBox.setStyleSheet("QComboBox\n"
                                                "{\n"
                                                "    color: black;\n"
                                                "}\n"
                                                "\n"
                                                "QComboBox::item:!enabled\n"
                                                "{\n"
                                                "    color: gray;\n"
                                                "}")

        self.y_auto_range = Switch('Auto Range', 'off').get_widget(self)
        self.y_auto_range.label.setFixedWidth(100)
        self.y_auto_range.toggle.toggled.connect(self.onYAxisAutoRange)

        # X Axis
        self.x_axis_label = QLabel(self)
        self.x_axis_label.setText('x Axis')

        self.x_axis_menu = Menu('', ['Linear', 'Logarithmic'], 'Linear').get_widget(self)
        self.x_axis_menu.label.setFixedWidth(0)
        self.x_axis_menu.comboBox.currentIndexChanged.connect(self.onXAxisMenuChanged)
        self.x_axis_menu.comboBox.setStyleSheet("QComboBox\n"
                                                "{\n"
                                                "    color: black;\n"
                                                "}\n"
                                                "\n"
                                                "QComboBox::item:!enabled\n"
                                                "{\n"
                                                "    color: gray;\n"
                                                "}")

        self.x_auto_range = Switch('Auto Range', 'off').get_widget(self)
        self.x_auto_range.label.setFixedWidth(100)
        self.x_auto_range.toggle.toggled.connect(self.onXAxisAutoRange)

    def initLayout(self):
        # Overall Control Layout
        overall_layout = QVBoxLayout()
        overall_layout.addWidget(self.overall_label, alignment=Qt.AlignLeft)
        overall_layout.addWidget(self.overall_Menu, alignment=Qt.AlignLeft)
        overall_layout.addWidget(self.display, alignment=Qt.AlignLeft)
        overall_layout.addWidget(self.show_grid, alignment=Qt.AlignLeft)

        # Y Axis Layout
        y_axis_layout = QVBoxLayout()
        y_axis_layout.addWidget(self.y_axis_label, alignment=Qt.AlignLeft)
        y_axis_layout.addWidget(self.y_axis_menu, alignment=Qt.AlignLeft)
        y_axis_layout.addWidget(self.y_auto_range, alignment=Qt.AlignLeft)

        # X Axis Layout
        x_axis_layout = QVBoxLayout()
        x_axis_layout.addWidget(self.x_axis_label, alignment=Qt.AlignLeft)
        x_axis_layout.addWidget(self.x_axis_menu, alignment=Qt.AlignLeft)
        x_axis_layout.addWidget(self.x_auto_range, alignment=Qt.AlignLeft)

        # Right Layout
        vlayout = QVBoxLayout()
        vlayout.addLayout(overall_layout)
        vlayout.addLayout(y_axis_layout)
        vlayout.addLayout(x_axis_layout)
        vlayout.setContentsMargins(10, 10, 10, 10)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plotWidget)
        layout.addLayout(vlayout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def onOverallMenuChanged(self):
        if self.overall_Menu.comboBox.currentText() == 'Time':
            self.y_axis_menu.comboBox.model().item(1).setEnabled(False)
            self.y_axis_menu.comboBox.model().item(2).setEnabled(False)
            self.x_axis_menu.comboBox.model().item(1).setEnabled(False)
            self.y_axis_menu.comboBox.setCurrentIndex(0)
            self.x_axis_menu.comboBox.setCurrentIndex(0)
        else:
            self.y_axis_menu.comboBox.model().item(1).setEnabled(True)
            self.y_axis_menu.comboBox.model().item(2).setEnabled(True)
            self.x_axis_menu.comboBox.model().item(1).setEnabled(True)


    def onShowGrid(self, bool):
        self.plotWidget.plotItem.showGrid(bool, bool, 0.2)

    def onYAxisMenuChanged(self):
        print(self.y_axis_menu.comboBox.currentText())

    def onYAxisAutoRange(self, bool):
        print(bool, 'YYY')

    def onXAxisMenuChanged(self):
        print(self.x_axis_menu.comboBox.currentText())

    def onXAxisAutoRange(self, bool):
        print(bool, 'XXX')

    def initPlot(self):
        self.plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((241, 196, 15), width=1))

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
            # self.cleanPlotItem()
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

            getInfo = "info/"
            getSize = "get/%s/fftsize/" % (AO_Name)
            self.client.setQueryTasks([getInfo, getSize], 64)
            self.client.start()
            self.client.wait()
            if not (False in self.client.result[0]):
                info = self.client.result[1][0]
                self.sampleRate = float(info.decode().split(',')[1])

            cmd = 'getMeterByte/%s/dump/1024/' % AO_Name
            self.client.setQueryTask(cmd, 2048)
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
        # 获取.raw数据 生成Y轴数据
        data = self.client.result[1]
        # 格式化数据
        raw_data = []
        for i in range(0, len(data), 2):
            raw_data.append(int.from_bytes(data[i:i + 2], byteorder='little', signed=True) / 32768)
        # 电脑采样率
        samplerate = self.sampleRate
        # x轴的数据
        x_data = []
        # y轴的数据
        y_data = []
        # x轴坐标轴
        x_axis = [[]]
        # y轴坐标
        y_axis = [[]]

        # Model Transformation
        if self.overall_Menu.comboBox.currentText() == 'Time':
            # 数据长度
            len_data = int(len(data)/2)
            # x轴的最大值
            x_max = (len_data / samplerate) * 1000
            # x轴间隔的值
            x_gap = (1/samplerate) * 1000
            # y轴数据
            y_data = raw_data

            # 利用 len_data数据长度和x_gap间隔值 生成x轴的数据
            for i in range(len_data):
                x_value = (i+1) * x_gap
                x_data.append(x_value)

            # 调整x轴坐标
            # 等份数量
            num_parts = 8
            # 每份的大小
            part_size = x_max / num_parts
            # 超出的宽度
            over_flow = part_size / 5

            for i in range(9):
                num = "{:.2f}".format(part_size * i)
                x_axis[0].append((float(num), str(num)))
            self.plotWidget.viewbox.setXRange(-over_flow, x_max + over_flow, 0, True)
            self.plotWidget.btm_axis.setTicks(x_axis)
            # 调整y轴坐标
            y_axis = [[(-2, '-2.0'), (-1, '-1.0'), (0, '0.0'), (1, '1.0'), (2, '2.0')]]
            self.plotWidget.viewbox.setYRange(-2.2, 2.2, 0, True)
            self.plotWidget.left_axis.setTicks(y_axis)
            self.plotWidget.btm_axis.setLabel('Millisecond')
        elif self.overall_Menu.comboBox.currentText() == 'Freq':
            # fft的y轴数据
            fft_data = np.abs(np.fft.fft(raw_data))
            for i in range(len(fft_data)):
                if i < len(raw_data)/2:
                    y_data.append(fft_data[i] / 512)
            # fft的x轴数据
            frequency = samplerate/2
            start = 0
            stop = frequency
            step = frequency / len(y_data)
            value = start
            while value < stop:
                value += step
                x_data.append(value)

            # 调整x轴坐标
            # 等份数量
            num_parts = 8
            # 每份的大小
            part_size = frequency / num_parts
            # 超出的宽度
            over_flow = part_size/5
            for i in range(9):
                num = part_size * i
                x_axis[0].append((num, str(num)))

            self.plotWidget.viewbox.setXRange(-over_flow, frequency + over_flow, 0, True)
            self.plotWidget.btm_axis.setTicks(x_axis)
            # 调整y轴坐标
            y_axis = [[(0, '0.0'), (0.25, '0.25'), (0.5, '0.5'), (0.75, '0.75'), (1, '1.0')]]
            self.plotWidget.viewbox.setYRange(-0.05, 1.05, 0, True)
            self.plotWidget.left_axis.setTicks(y_axis)
            self.plotWidget.btm_axis.setLabel('Frequency')

        # Y Axis Conversion Linear/db10/db20
        if self.overall_Menu.comboBox.currentText() == 'Freq':
            left_axis_label = self.y_axis_menu.comboBox.currentText()
            self.plotWidget.left_axis.setLabel(left_axis_label)
            if left_axis_label != 'Linear':
                data = y_data
                y_data = []
                if left_axis_label == 'db20':
                    for i in data:
                        y_data.append(20 * math.log10(i))
                elif left_axis_label == 'db10':
                    for i in data:
                        y_data.append(10 * math.log10(i))
                y_axis = [[(-144, '-144.0'), (-108, '-108.0'), (-72, '-72.0'), (-36, '-36.0'), (0, '0.0')]]
                self.plotWidget.viewbox.setYRange(-151.2, 7.2, 0, True)
                self.plotWidget.left_axis.setTicks(y_axis)
                self.plotWidget.btm_axis.setLabel('Frequency')

        # Y Axis Auto Range
        if self.y_auto_range.toggle.isChecked():
            # y轴坐标轴
            y_axis = [[]]
            y_max = max(y_data)
            y_min = min(y_data)
            if (y_max >= 0 and y_min >= 0) or (y_max <= 0 and y_min <= 0):
                y_length = abs(y_max - y_min)
            else:
                y_length = abs(y_max) + abs(y_min)

            part_size = y_length/4

            for i in range(5):
                num = "{:.2f}".format(y_min + part_size * i)
                y_axis[0].append((float(num), str(num)))

            self.plotWidget.viewbox.setYRange(y_min - part_size/5, y_max + part_size/5, 0, True)
            self.plotWidget.left_axis.setTicks(y_axis)

        # X Axis Conversion Linear/Logarithmic
        if self.overall_Menu.comboBox.currentText() == 'Freq':
            if self.x_axis_menu.comboBox.currentText() == 'Logarithmic':
                data = x_data
                x_data = []
                for i in data:
                    x_data.append(np.log10(i))

                x_axis = [[(np.log10(31.2), '31.2'), (np.log10(62.5), '62.5'), (np.log10(125), '125'), (np.log10(250), '250'), (np.log10(500), '500'),
                           (np.log10(1000), '1000'), (np.log10(2000), '2000'), (np.log10(4000), '4000'),
                           (np.log10(8000), '8000'), (np.log10(16000), '16000'), (np.log10(32000), '32000')
                         ]]
                self.plotWidget.viewbox.setXRange(np.log10(31.2)-0.06, np.log10(32000.0)+0.06, 0, True)
                self.plotWidget.btm_axis.setTicks(x_axis)

        # X Axis Auto Range
        if self.x_auto_range.toggle.isChecked():
            x_axis = [[]]
            x_max = max(x_data)
            x_min = min(x_data)
            if self.x_axis_menu.comboBox.currentText() == 'Logarithmic':
                max1 = float("{:.2f}".format(np.power(10, x_max)))
                min1 = float("{:.2f}".format(np.power(10, x_min)))
                x = min1
                num = "{:.2f}".format(x)
                x_axis[0].append((np.log10(float(num)), str(num)))
                while x <= max1:
                    x = x * 2
                    num = "{:.2f}".format(x)
                    x_axis[0].append((np.log10(float(num)), str(num)))
                gap = (x_axis[0][1][0] - x_axis[0][0][0])/5
                start = float("{:.2f}".format(np.log10(min1)-gap))
                end = float("{:.2f}".format(np.log10(max1)+gap))
                self.plotWidget.viewbox.setXRange(start, end, 0, True)
            else:
                if (x_min >= 0 and x_max >= 0) or (x_max <= 0 and x_min <= 0):
                    x_length = abs(x_max - x_min)
                else:
                    x_length = abs(x_max) + abs(x_min)
                part_size = x_length / 8
                for i in range(9):
                    num = "{:.2f}".format(x_min + part_size * i)
                    x_axis[0].append((float(num), str(num)))
                self.plotWidget.viewbox.setXRange(x_min - part_size / 5, x_max + part_size / 5, 0, True)
            self.plotWidget.btm_axis.setTicks(x_axis)

        # 画图
        self.plot.setData(x=x_data, y=y_data)

@register_node(OP_NODE_VISUALIZER)
class FLOW_Node_VISUALIZER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_VISUALIZER
    op_title = "VISUALIZER"
    content_label_objname = "VISUALIZER"
    display_name = 'Signal Visualizer'
    info = 'User can use a signal visualizer AO to visualize the audio samples in time domain. It will be useful for user to realize the current audio condition.'
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = VISUALIZER_GUI(self)