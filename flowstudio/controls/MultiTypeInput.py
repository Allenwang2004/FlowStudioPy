from control.flow_control_widget import widgetCompomentBase
from control.flow_widget_button import QToggleSwitch
from control.flow_widget_knob import *

class MultiTypeInput(object):

    def __init__(self, label_text, label_width, is_input=False):
        self.label_text = label_text
        self.label_width = label_width
        self.is_input = is_input
        self.parameters = {'label_text': self.label_text,
                           'is_input': self.is_input,
                           'label_width': self.label_width}

    def get_widget(self, parent_widget, gui_type=None):
        return MultiTypeInputWidgets(parent_widget, self.parameters)

class MultiTypeInputWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, parameter: dict):
        super(MultiTypeInputWidgets, self).__init__(widget)
        if parameter['is_input']:
            self.socket_type = widget.node.inctrllist[0]
        else:
            self.socket_type = widget.node.outctrllist[0]

        self.label = QLabel()
        self.label.setFixedWidth(parameter['label_width'])
        self.label.setFont(self.grFont)
        self.label.setText(parameter['label_text'])

        self.dy_widget = None
        if self.socket_type == 7:
            self.dy_widget = QToggleSwitch()
            self.dy_widget.setFont(self.grFont)
            self.dy_widget.setCheckable(True)
            self.dy_widget.toggled.connect(self.on_value_changed)
        elif self.socket_type == 8:
            self.dy_widget = QSpinBox()
            self.dy_widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.dy_widget.setFont(self.grFont)
            self.dy_widget.setFixedWidth(50)
            self.dy_widget.setRange(-2147483647, 2147483647)
            self.dy_widget.valueChanged.connect(self.on_value_changed)
        elif self.socket_type == 9:
            self.dy_widget = QDoubleSpinBox()
            self.dy_widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.dy_widget.setFont(self.grFont)
            self.dy_widget.setFixedWidth(70)
            self.dy_widget.setDecimals(4)
            self.dy_widget.setRange(-1e20, 1e20)
            self.dy_widget.valueChanged.connect(self.on_value_changed)

        image_layout = QHBoxLayout(self)
        image_layout.addWidget(self.label)
        image_layout.addWidget(self.dy_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def widget_value(self):
        widget_value = 0
        if self.socket_type == 7:
            widget_value = 1 if self.dy_widget.isChecked() else 0
        elif self.socket_type == 8:
            widget_value = self.dy_widget.value()
        elif self.socket_type == 9:
            widget_value = self.dy_widget.value()
        return widget_value

    @widget_value.setter
    def widget_value(self, data: str):
        if self.socket_type == 7:
            self.dy_widget.setChecked(data == 1)
        elif self.socket_type == 8:
            self.dy_widget.setValue(float(data))
        elif self.socket_type == 9:
            self.dy_widget.setValue(int(data))

    def on_value_changed(self, value):
        self.valueChanged.emit()
        self.valueStored.emit()
        # """值改变时的处理"""
        # if self.socket_type == 7:
        #     # 开关状态 (bool)
        #     print(f"开关状态: {'开' if value else '关'}")
        # elif self.socket_type == 8:
        #     # 整数值 (int)
        #     print(f"整数值: {value}")
        # elif self.socket_type == 9:
        #     # 浮点数值 (float)
        #     print(f"浮点数值: {value:.4f}")