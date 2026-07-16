from control.flow_widget_dot import plotDot
from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_matplotlib_graphical import *
from utilities.iir_designer import *
from control.flow_widget_plot import *

DEBUG = False
DEBUG_Content = False


# class BIQUAD_GUI(FLOW_GUI):
#
#     def __init__(self, node):
#         super().__init__(node)
#         self.initExtraWidget()
#         self.initLayout()
#         self.initPlot()
#
#         self.iir = IIR_Designer(
#             filter_type = self.gui_manager.widgetSet['kind'].widget_value[1],
#             frequency_cut = self.gui_manager.widgetSet['fc'].widget_value,
#             magnitude = self.gui_manager.widgetSet['boost'].widget_value,
#             Q = self.gui_manager.widgetSet['Q'].widget_value,
#             slope = self.gui_manager.widgetSet['slope'].widget_value)
#
#         for key in self.gui_manager.widgetSet:
#             self.gui_manager.widgetSet[key].valueChanged.connect(partial(self.ctrl2plot, key))
#
#         self.gui_manager.widgetSet['kind'].valueChanged.connect(self.disableSlopeQ)
#         self.disableSlopeQ()
#
#     def initExtraWidget(self):
#         self.plotWidget = filter(self)
#
#         fc = self.gui_manager.widgetSet['fc'].widget_value
#         self.dot = plotDot([np.log10(fc), 0])
#         self.dot.selected()
#         self.dot.posChanged.connect(self.dotPos_numberBox)
#         self.gui_manager.widgetSet['fc'].valueChanged.connect(self.numberBox_dotPos)
#         self.gui_manager.widgetSet['boost'].valueChanged.connect(self.numberBox_dotPos)
#
#         self.phaseSwitch = Switch('Phase', 'on').get_widget(self)
#         self.phaseSwitch.valueChanged.connect(self.phaseVisible)
#
#     def dotPos_numberBox(self, value):
#         self.gui_manager.widgetSet['fc'].widget_value = 10**value[0]
#         self.gui_manager.widgetSet['boost'].widget_value = value[1]
#
#     def numberBox_dotPos(self):
#         x = np.log10(self.gui_manager.widgetSet['fc'].widget_value)
#         y = self.gui_manager.widgetSet['boost'].widget_value
#         dot_pos = np.array([[x, y]], dtype=float)
#         self.dot.setData(pos=dot_pos)
#
#     def phaseVisible(self):
#         if self.phaseSwitch.widget_value[1] == 1:
#             self.pr_plot.setPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5)
#         else:
#             self.pr_plot.setPen(None)
#
#     def initLayout(self):
#         layout1 = QHBoxLayout()
#         layout1.addWidget(self.gui_manager.widgetSet['onoff'], alignment=Qt.AlignLeft)
#         layout1.addWidget(self.gui_manager.widgetSet['kind'], alignment=Qt.AlignLeft)
#         layout1.addWidget(self.phaseSwitch, alignment=Qt.AlignLeft)
#
#         layout2 = QHBoxLayout()
#         layout2.addWidget(self.gui_manager.widgetSet['fc'], alignment=Qt.AlignHCenter)
#         layout2.addWidget(self.gui_manager.widgetSet['boost'], alignment=Qt.AlignHCenter)
#         layout2.addWidget(self.gui_manager.widgetSet['Q'], alignment=Qt.AlignHCenter)
#         layout2.addWidget(self.gui_manager.widgetSet['slope'], alignment=Qt.AlignHCenter)
#
#         layout = QVBoxLayout(self)
#         layout.addLayout(layout1)
#         layout.addWidget(self.plotWidget)
#         layout.addLayout(layout2)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0)
#
#     def disableSlopeQ(self):
#         if self.gui_manager.widgetSet['kind'].widget_value[1] in [10, 11]:
#             self.gui_manager.widgetSet['Q'].hide()
#             self.gui_manager.widgetSet['slope'].show()
#         else:
#             self.gui_manager.widgetSet['Q'].show()
#             self.gui_manager.widgetSet['slope'].hide()
#
#     def ctrl2plot(self, key):
#         if key == 'onoff':
#             self.iir.bypass = not self.gui_manager.widgetSet[key].widget_value[1]
#             if self.gui_manager.widgetSet[key].widget_value[1]:
#                 self.plotWidget.viewbox.addItem(self.dot)
#             else:
#                 self.plotWidget.viewbox.removeItem(self.dot)
#         elif key =='kind':
#             self.iir.filter_type = self.gui_manager.widgetSet[key].widget_value[1]
#         elif key =='fc':
#             self.iir.freq = self.gui_manager.widgetSet[key].widget_value
#         elif key =='Q':
#             self.iir.q = self.gui_manager.widgetSet[key].widget_value
#         elif key =='boost':
#             self.iir.magnitude = self.gui_manager.widgetSet[key].widget_value
#         elif key =='slope':
#             self.iir.slope = self.gui_manager.widgetSet[key].widget_value
#
#         amplitude = 20 * np.log10(abs(self.iir.h))
#         angle = np.angle(self.iir.h)
#         self.fr_plot.setData(x=self.iir.w, y=amplitude)
#         self.pr_plot.setData(x=self.iir.w, y=angle/np.pi*40)
#
#     def initPlot(self):
#         self.fr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen((139, 176, 164), width=3))
#         self.pr_plot = self.plotWidget.plotItem.plot(pen=pg.mkPen(color=(210, 210, 210), style=Qt.DashLine, width=1.5))
#
#         self.plotWidget.viewbox.addItem(self.dot)
#
#     def refresh(self):
#         super().refresh()
#         for key in self.gui_manager.widgetSet:
#             self.ctrl2plot(key)

@register_node(OP_NODE_BIQUAD_LOAD)
class FLOW_Node_BIQUAD_LOAD(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_BIQUAD_LOAD
    op_title = "BIQUAD_LOAD"
    content_label_objname = "BIQUAD_LOAD"
    display_name = 'Biquad filter loading simulator'
    info = 'BIQUQD allow users to input arbitrary filter coefficient for the standard IIR biquad filter processing'
    expandable = True
    # openable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value

    def __init__(self, scene, band, channel, control):
        self.inputs = []
        self.outputs = []
        for i in range(channel):
            self.inputs.append(1)
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()
        self.manager.widgetSet['num'].slider.setMaximum(band)
        self.manager.widgetSet['num'].slider.setMinimum(0)
        self.manager.widgetSet['num'].numbox.setMinimum(band)
        self.manager.widgetSet['num'].numbox.setMinimum(0)
        self.manager.widgetSet['num'].numbox.setValue(1)
        self.manager.widgetSet['maxBand'].widget_value = band
        self.manager.widgetSet['maxBand'].label.setVisible(False)
        self.manager.widgetSet['maxBand'].slider.setVisible(False)
        self.manager.widgetSet['maxBand'].numbox.setVisible(False)
