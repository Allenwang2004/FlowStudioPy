from control.flow_control_widget import widgetCompomentBase
from control.flow_widget_button import QToggleSwitch
from control.flow_widget_knob import *

class LabelToggle(object):

    def __init__(self, left_text, right_text, label_width):
        self.left_text = left_text
        self.right_text = right_text
        self.label_width = label_width
        self.parameters = {'left_text': self.left_text,
                           'right_text': self.right_text,
                           'label_width': self.label_width}

    def get_widget(self, parent_widget, gui_type=None):
        return LabelToggleWidgets(parent_widget, self.parameters)

class LabelToggleWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, parameter: dict):
        super(LabelToggleWidgets, self).__init__(widget)
        self.left_label = QLabel()
        self.left_label.setFixedWidth(parameter['label_width'])
        self.left_label.setFont(self.grFont)
        self.left_label.setText(parameter['left_text'])

        self.toggle = QToggleSwitch()
        self.toggle.setFont(self.grFont)
        self.toggle.setCheckable(True)

        self.right_label = QLabel()
        self.right_label.setFixedWidth(parameter['label_width'])
        self.right_label.setFont(self.grFont)
        self.right_label.setText(parameter['right_text'])


        image_layout = QHBoxLayout(self)
        image_layout.addWidget(self.left_label)
        image_layout.addWidget(self.toggle)
        image_layout.addWidget(self.right_label)
        image_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def widget_value(self):
        widget_value = 1 if self.toggle.isChecked() else 0
        return widget_value

    @widget_value.setter
    def widget_value(self, data: str):
        self.toggle.setChecked(data == 1)
