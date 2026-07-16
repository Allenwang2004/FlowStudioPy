from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from utilities.drc_designer import *
from control.flow_widget_plot import *
from flowstudio.controls.TapMenu import TapMenu as TapMenuControl
from control.flow_control_widget import TapMenu as TapMenuUI

thread_timeout = 50


class LIMITER_MB_GUI(FLOW_GUI):
    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(600, 600)
        self.initExtraWidget()
        self.initLayout()
        self.initPlot()

        self.env_volume = list([None, None, None, None])
        self.isConnected = False

        self.limiterLF = DRC_Designer(model=LIMITER,
                                      knee=self.gui_manager.widgetSet['kneeLF'].widget_value,
                                      threshold=self.gui_manager.widgetSet['thresholdLF'].widget_value)

        self.limiterHF = DRC_Designer(model=LIMITER,
                                      knee=self.gui_manager.widgetSet['kneeHF'].widget_value,
                                      threshold=self.gui_manager.widgetSet['thresholdHF'].widget_value)

        for key in self.gui_manager.widgetSet:
            self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))

        self.disableTrAndTaAndTe('typeLF', self.gui_manager.widgetSet['typeLF'].widget_value[0])
        self.disableTrAndTaAndTe('typeHF', self.gui_manager.widgetSet['typeHF'].widget_value[0])
        self.gui_manager.widgetSet['typeLF'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, 'typeLF', self.gui_manager.widgetSet['typeLF'].widget_value[0]))
        self.gui_manager.widgetSet['typeHF'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, 'typeHF', self.gui_manager.widgetSet['typeHF'].widget_value[0]))

    def disableTrAndTaAndTe(self, name, value):
        taName = "taLF"
        trName = "trLF"
        teName = "teLF"
        if name == 'typeHF':
            taName = "taHF"
            trName = "trHF"
            teName = "teHF"
        if value == self.gui_manager.widgetSet[name].widget_value[0]:
            self.gui_manager.widgetSet[taName].disableWidget(False)
            self.gui_manager.widgetSet[trName].disableWidget(False)
            self.gui_manager.widgetSet[teName].disableWidget(False)
        else:
            self.gui_manager.widgetSet[taName].disableWidget(False)
            self.gui_manager.widgetSet[trName].disableWidget(False)
            self.gui_manager.widgetSet[teName].disableWidget(True)

    def initInnerClasses(self):
        self.gui_manager = LIMITER_MB_Ctrl_Manager(None, **self.node.manager.config)
        self.gui_manager.initNodeParam(self, False)
        self.mapping()
        self.gui_manager.initPos()

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        self.display.toggle.setChecked(False)

    def initExtraWidget(self):
        self.plotWidgetLF = drc_computer(self)
        self.grWidgetLF = gain_reduction(self)

        self.plotWidgetHF = drc_computer(self)
        self.grWidgetHF = gain_reduction(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        self.display = Label_PushButton_DoubleNumber(self, {"pMax": 20, "pMin": -100, "pValue": 0})
        self.display.label.setText('update')
        self.display.toggle.clicked.connect(self.toggle)

    def initLayout(self):
        layout1 = QVBoxLayout()
        layout1.addWidget(self.display, alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignLeft)
        layout1.addWidget(self.gui_manager.widgetSet['LFHFtap'], alignment=Qt.AlignLeft)
        layout1.setContentsMargins(10, 0, 0, 0)
        layout1.setSpacing(0)

        layoutLF = QHBoxLayout()
        layoutLF.addWidget(self.plotWidgetLF, 6)
        layoutLF.addWidget(self.grWidgetLF, 1)

        layoutHF = QHBoxLayout()
        layoutHF.addWidget(self.plotWidgetHF, 6)
        layoutHF.addWidget(self.grWidgetHF, 1)

        layoutDRC = QVBoxLayout()
        layoutDRC.addLayout(layoutLF)
        layoutDRC.addLayout(layoutHF)

        layout = QHBoxLayout(self)
        layout.addLayout(layoutDRC)
        layout.addLayout(layout1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def initPlot(self):
        self.dotLF = plotDot()

        self.dynamic_plotLF = self.plotWidgetLF.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.reduction_plotLF = self.plotWidgetLF.plotItem.plot(pen=pg.mkPen((0, 0, 0, 0), width=3), fillLevel=-120,
                                                                fillOutline=True)

        self.fillLF = pg.FillBetweenItem(self.dynamic_plotLF, self.reduction_plotLF, brush=[26, 188, 156, 100])

        self.barLF = pg.BarGraphItem(x=[1], height=[0], width=1, brush=[188, 76, 26, 180])

        self.dotHF = plotDot()

        self.dynamic_plotHF = self.plotWidgetHF.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
        self.reduction_plotHF = self.plotWidgetHF.plotItem.plot(pen=pg.mkPen((0, 0, 0, 0), width=3), fillLevel=-120,
                                                                fillOutline=True)

        self.fillHF = pg.FillBetweenItem(self.dynamic_plotHF, self.reduction_plotHF, brush=[23, 122, 166, 100])

        self.barHF = pg.BarGraphItem(x=[1], height=[0], width=1, brush=[188, 76, 26, 180])

    def ctrl2plot(self, key):
        if key == 'EnableLF':
            self.limiterLF.bypass = not self.gui_manager.widgetSet['EnableLF'].widget_value[1]
        elif key == 'thresholdLF':
            self.limiterLF.threshold = self.gui_manager.widgetSet['thresholdLF'].widget_value
        elif key == 'kneeLF':
            self.limiterLF.knee = self.gui_manager.widgetSet['kneeLF'].widget_value
        elif key == 'EnableHF':
            self.limiterHF.bypass = not self.gui_manager.widgetSet['EnableHF'].widget_value[1]
        elif key == 'thresholdHF':
            self.limiterHF.threshold = self.gui_manager.widgetSet['thresholdHF'].widget_value
        elif key == 'kneeHF':
            self.limiterHF.knee = self.gui_manager.widgetSet['kneeHF'].widget_value

        self.dynamic_plotLF.setData(x=self.limiterLF.input, y=self.limiterLF.output)
        self.dynamic_plotHF.setData(x=self.limiterHF.input, y=self.limiterHF.output)

        if not (self.env_volume[0] and self.env_volume[1] and self.env_volume[2] and self.env_volume[
            3]) == None: self.followUp()

    def followUp(self):
        idea_output_LF = self.limiterLF.location(self.env_volume[0])
        idea_output_HF = self.limiterHF.location(self.env_volume[2])

        if self.gui_manager.widgetSet['EnableLF'].widget_value[1]:
            dot_pos_LF = np.array([[self.env_volume[0], idea_output_LF]], dtype=float)
        else:
            dot_pos_LF = np.array([[self.env_volume[0], self.env_volume[0]]], dtype=float)
        self.dotLF.setData(pos=dot_pos_LF)

        if self.gui_manager.widgetSet['EnableHF'].widget_value[1]:
            dot_pos_HF = np.array([[self.env_volume[2], idea_output_HF]], dtype=float)
        else:
            dot_pos_HF = np.array([[self.env_volume[2], self.env_volume[2]]], dtype=float)
        self.dotHF.setData(pos=dot_pos_HF)

        index_LF = self.limiterLF.input_index(self.env_volume[0])
        index_HF = self.limiterHF.input_index(self.env_volume[2])

        if self.gui_manager.widgetSet['EnableLF'].widget_value[1]:
            x_data = [self.env_volume[0], self.env_volume[0]]
            x_data = x_data + (self.limiterLF.input[index_LF:])

            y_data = [-120, idea_output_LF]
            y_data = y_data + (self.limiterLF.output[index_LF:])
        else:
            x_data = [-120, 0]
            y_data = [-120, 0]

        self.reduction_plotLF.setData(x=x_data, y=y_data)

        if self.gui_manager.widgetSet['EnableHF'].widget_value[1]:
            x_data = [self.env_volume[2], self.env_volume[2]]
            x_data = x_data + (self.limiterHF.input[index_HF:])

            y_data = [-120, idea_output_HF]
            y_data = y_data + (self.limiterHF.output[index_HF:])
        else:
            x_data = [-120, 0]
            y_data = [-120, 0]

        self.reduction_plotHF.setData(x=x_data, y=y_data)

    def toggle(self, bool):
        # if self.isConnected and not bool and self.socket.connection:
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout(index=1)
            self.timer.stop()
            self.cleanPlotItem()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.addPlotItem()
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)
        else:
            pass

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "Meter"
            cmd = "getSerialized/%s/%s/" % (AO_Name, Parameter_Name)
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
        raw = self.client.result[1].decode().split('/')

        self.env_volume[0] = float(raw[0])
        self.env_volume[1] = float(raw[1])
        self.env_volume[2] = float(raw[2])
        self.env_volume[3] = float(raw[3])

        if self.gui_manager.widgetSet['LFHFtap'].widget_value[0] == 0:
            self.display.spinbox.setValue(self.env_volume[0])
        elif self.gui_manager.widgetSet['LFHFtap'].widget_value[0] == 1:
            self.display.spinbox.setValue(self.env_volume[2])

        self.followUp()

        reduction_volume = float(raw[1])
        self.barLF.setOpts(height=-reduction_volume)

        reduction_volume = float(raw[3])
        self.barHF.setOpts(height=-reduction_volume)

    def addPlotItem(self):
        self.grWidgetLF.viewbox.addItem(self.barLF)
        self.grWidgetHF.viewbox.addItem(self.barHF)
        self.plotWidgetLF.viewbox.addItem(self.dotLF)
        self.plotWidgetHF.viewbox.addItem(self.dotHF)
        self.plotWidgetLF.viewbox.addItem(self.reduction_plotLF)
        self.plotWidgetHF.viewbox.addItem(self.reduction_plotHF)
        self.plotWidgetLF.viewbox.addItem(self.fillLF)
        self.plotWidgetHF.viewbox.addItem(self.fillHF)

    def cleanPlotItem(self):
        self.grWidgetLF.viewbox.removeItem(self.barLF)
        self.grWidgetHF.viewbox.removeItem(self.barHF)
        self.plotWidgetLF.viewbox.removeItem(self.dotLF)
        self.plotWidgetHF.viewbox.removeItem(self.dotHF)
        self.plotWidgetLF.viewbox.removeItem(self.reduction_plotLF)
        self.plotWidgetHF.viewbox.removeItem(self.reduction_plotHF)
        self.plotWidgetLF.viewbox.removeItem(self.fillLF)
        self.plotWidgetHF.viewbox.removeItem(self.fillHF)

        self.display.spinbox.clear()

    def refresh(self):
        super().refresh()
        for key in self.gui_manager.widgetSet:
            self.ctrl2plot(key)


class LIMITER_MB_Ctrl_Manager(FLOW_Ctrl_Manager):
    # TODO: we need fix config in flow engine in the future to prevent manual code

    def initNodeParam(self, parent: QWidget, parameterStored: bool):
        parameter = TapMenuControl({},
                                   parameters={"pSize": 2, "cSize": 10, "cParameter": {}}).parameters
        self.tap = TapMenuUI(parent, parameter, False)
        self.tap.setTabText(0, 'LF')
        self.tap.setTabText(1, 'HF')
        self.widgetSet['LFHFtap'] = self.tap

        self.content = parent

        res = self.createControlInterface('fc', self.config['fc'], parent)
        res.label.setText('fc')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['fc'] = res

        res = self.createControlInterface('EnableLF', self.config['EnableLF'], self.tap.widget(0))
        res.label.setText('enable')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['EnableLF'] = res

        res = self.createControlInterface('typeLF', self.config['typeLF'], self.tap.widget(0))
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['typeLF'] = res

        res = self.createControlInterface('kneeLF', self.config['kneeLF'], self.tap.widget(0))
        res.label.setText('knee')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['kneeLF'] = res

        res = self.createControlInterface('thresholdLF', self.config['thresholdLF'], self.tap.widget(0))
        res.label.setText('thresh')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['thresholdLF'] = res

        res = self.createControlInterface('taLF', self.config['taLF'], self.tap.widget(0))
        res.label.setText('ta')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['taLF'] = res

        res = self.createControlInterface('holdLF', self.config['holdLF'], self.tap.widget(0))
        res.label.setText('hold')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['holdLF'] = res

        res = self.createControlInterface('tdLF', self.config['tdLF'], self.tap.widget(0))
        res.label.setText('td')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['tdLF'] = res

        res = self.createControlInterface('teLF', self.config['teLF'], self.tap.widget(0))
        res.label.setText('te')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['teLF'] = res

        res = self.createControlInterface('trLF', self.config['trLF'], self.tap.widget(0))
        res.label.setText('tr')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['trLF'] = res

        res = self.createControlInterface('makeupLF', self.config['makeupLF'], self.tap.widget(0))
        res.label.setText('makeup')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['makeupLF'] = res

        res = self.createControlInterface('EnableHF', self.config['EnableHF'], self.tap.widget(1))
        res.label.setText('enable')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['EnableHF'] = res

        res = self.createControlInterface('typeHF', self.config['typeHF'], self.tap.widget(1))
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['typeHF'] = res

        res = self.createControlInterface('kneeHF', self.config['kneeHF'], self.tap.widget(1))
        res.label.setText('knee')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['kneeHF'] = res

        res = self.createControlInterface('thresholdHF', self.config['thresholdHF'], self.tap.widget(1))
        res.label.setText('thresh')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['thresholdHF'] = res

        res = self.createControlInterface('taHF', self.config['taHF'], self.tap.widget(1))
        res.label.setText('ta')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['taHF'] = res

        res = self.createControlInterface('holdHF', self.config['holdHF'], self.tap.widget(1))
        res.label.setText('hold')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['holdHF'] = res

        res = self.createControlInterface('tdHF', self.config['tdHF'], self.tap.widget(1))
        res.label.setText('td')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['tdHF'] = res

        res = self.createControlInterface('teHF', self.config['teHF'], self.tap.widget(1))
        res.label.setText('te')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['teHF'] = res

        res = self.createControlInterface('trHF', self.config['trHF'], self.tap.widget(1))
        res.label.setText('tr')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['trHF'] = res

        res = self.createControlInterface('makeupHF', self.config['makeupHF'], self.tap.widget(1))
        res.label.setText('makeup')
        if parameterStored: res.valueStored.connect(self.parameterStored)
        self.widgetSet['makeupHF'] = res

    def initPos(self):
        self.widgetSet["fc"].move(10, 10)

        self.tap.move(10, 40)

        self.widgetSet["EnableLF"].move(0, 10)
        self.widgetSet["typeLF"].move(0, 40)
        self.widgetSet["kneeLF"].move(0, 70)
        self.widgetSet["thresholdLF"].move(0, 100)
        self.widgetSet["taLF"].move(0, 130)
        self.widgetSet["holdLF"].move(0, 160)
        self.widgetSet["tdLF"].move(0, 190)
        self.widgetSet["teLF"].move(0, 220)
        self.widgetSet["trLF"].move(0, 250)
        self.widgetSet["makeupLF"].move(0, 280)

        self.widgetSet["EnableHF"].move(0, 10)
        self.widgetSet["typeHF"].move(0, 40)
        self.widgetSet["kneeHF"].move(0, 70)
        self.widgetSet["thresholdHF"].move(0, 100)
        self.widgetSet["taHF"].move(0, 130)
        self.widgetSet["holdHF"].move(0, 160)
        self.widgetSet["tdHF"].move(0, 190)
        self.widgetSet["teHF"].move(0, 220)
        self.widgetSet["trHF"].move(0, 250)
        self.widgetSet["makeupHF"].move(0, 280)

        return 360


@register_node(OP_NODE_LIMITER_MB)
class FLOW_Node_LIMITER_MB(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_LIMITER_MB
    op_title = "LIMITER_MB"
    content_label_objname = "LIMITER_MB"
    display_name = '2 Band Limiter'
    info = 'A 2 band limiter has two separate limiters processing for high/low frequency bands divided by its built-in crossover.<br>Thus it can apply different attack/release time for different frequency band, so as to have better response to each band.'
    expandable = True
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()

        self.disableTrAndTaAndTe('typeLF', self.manager.widgetSet['typeLF'].widget_value[0])
        self.disableTrAndTaAndTe('typeHF', self.manager.widgetSet['typeHF'].widget_value[0])
        self.manager.widgetSet['typeLF'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, 'typeLF', self.manager.widgetSet['typeLF'].widget_value[0]))

        self.manager.widgetSet['typeHF'].valueChanged.connect(
            partial(self.disableTrAndTaAndTe, 'typeHF', self.manager.widgetSet['typeHF'].widget_value[0]))

    def initInnerClasses(self):
        self.manager = LIMITER_MB_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = LIMITER_MB_GUI(self)

    def disableTrAndTaAndTe(self, name, value):
        taName = "taLF"
        trName = "trLF"
        teName = "teLF"
        if name == 'typeHF':
            taName = "taHF"
            trName = "trHF"
            teName = "teHF"
        if value == self.manager.widgetSet[name].widget_value[0]:
            self.manager.widgetSet[taName].disableWidget(False)
            self.manager.widgetSet[trName].disableWidget(False)
            self.manager.widgetSet[teName].disableWidget(False)
        else:
            self.manager.widgetSet[taName].disableWidget(False)
            self.manager.widgetSet[trName].disableWidget(False)
            self.manager.widgetSet[teName].disableWidget(True)
