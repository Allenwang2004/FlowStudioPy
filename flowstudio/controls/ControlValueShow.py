from control.flow_control_widget import widgetCompomentBase
from control.flow_widget_button import QToggleSwitch
from control.flow_widget_knob import *

class ControlValueShow(object):

    def __init__(self, label_text):
        self.label_text = label_text
        self.parameters = {'label_text': self.label_text}

    def get_widget(self, parent_widget, gui_type=None):
        return ControlValueShowWidgets(parent_widget, self.parameters)

class ControlValueShowWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, parameter: dict):
        super(ControlValueShowWidgets, self).__init__(widget)
        grFont = QFont("Arial", 10)

        self.label = QLabel()
        self.label.setFixedWidth(40)
        self.label.setText(parameter['label_text'])
        self.label.setFont(grFont)

        self.label_value = QLabel()
        self.label_value.setFixedWidth(40)
        self.label_value.setFont(grFont)

        image_layout = QHBoxLayout(self)
        image_layout.addWidget(self.label)
        image_layout.addWidget(self.label_value)
        image_layout.setContentsMargins(10, 8, 0, 0)

    @property
    def widget_value(self):
        widget_value = 0
        return widget_value

    @widget_value.setter
    def widget_value(self, data: str):
        self.label_value.setText(str(data))
