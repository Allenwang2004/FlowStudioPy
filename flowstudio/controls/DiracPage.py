from PyQt5 import QtWidgets

from control.flow_control_widget import widgetCompomentBase
from control.flow_widget_button import QTactileButton
from control.flow_widget_knob import *

class DiracMenu(object):

    def __init__(self, label_text, items):
        self.label_text = label_text
        self.parameters = {'pList': items,
                           'label_text': label_text}

    def get_widget(self, parent_widget, gui_type=None):
        return DiracMenuWidgets(parent_widget, self.parameters)

class DiracMenuWidgets(QWidget, widgetCompomentBase):

    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, parameters: dict):
        super(DiracMenuWidgets, self).__init__(widget)

        self.label = QLabel()
        self.label.setFixedWidth(80)
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])

        self.comboBox = QComboBox()
        self.comboBox.setFixedWidth(100)
        self.comboBox.setFont(self.grFont)
        self.comboBox.addItems(parameters['pList'])
        self.comboBox.setCurrentIndex(0)

        image_layout = QHBoxLayout()
        self.image_label = QLabel(self)
        pixmap = QPixmap('..\\resources\\Dirac2.png')
        scaled_pixmap = pixmap.scaledToWidth(220)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setFixedSize(scaled_pixmap.size())
        image_layout.addWidget(self.image_label)
        image_layout.setContentsMargins(0, 20, 0, 0)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignTop)
        layout.addWidget(self.comboBox, alignment=Qt.AlignTop)
        layout.addSpacing(20)
        layout.addLayout(image_layout)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.comboBox.currentIndexChanged.connect(self.menuChangeHandle)

    def menuChangeHandle(self):
        self.valueStored.emit()
        self.valueChanged.emit()

    @property
    def widget_value(self) -> list:
        return [self.comboBox.itemText(self.comboBox.currentIndex()), self.comboBox.currentIndex()]

    @widget_value.setter
    def widget_value(self, value: list):
        self.comboBox.setCurrentIndex(value[1])

class DiracEdit(object):

    def __init__(self, label_text, edit_text):
        self.label_text = label_text
        self.edit_text = edit_text

    def get_widget(self, parent_widget, gui_type=None):
        return DiracEditWidgets(parent_widget, self.label_text, self.edit_text)

class DiracEditWidgets(QWidget, widgetCompomentBase):

    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, label_text, edit_text):
        super(DiracEditWidgets, self).__init__(widget)

        self.label = QLabel()
        self.label.setFixedWidth(80)
        self.label.setFont(self.grFont)
        self.label.setText(label_text)

        self.textedit = QLineEdit()
        self.textedit.setFixedWidth(100)
        self.textedit.setStyleSheet("QLineEdit { background-color: #606060; color: white; }")
        self.textedit.setFont(self.grFont)
        self.textedit.setText(edit_text)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.textedit)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    @property
    def widget_value(self):
        return self.textedit.text()

    @widget_value.setter
    def widget_value(self, value):
        self.textedit.setText(value)

class DiracTab(object):

    def __init__(self):
        self.parameters = {}

    def get_widget(self, parent_widget, gui_type=None):
        return DiracTabWidgets(parent_widget)

class DiracTabWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget):
        super().__init__(widget)

        self.tabWidget = QTabWidget()
        self.tabWidth = 240
        self.tabHeight = 20
        self.tabOffset = 5
        self.tabWidget.setFixedWidth(self.tabWidth + self.tabOffset)
        self.tabWidget.setFixedHeight(self.tabHeight)

        self.tab_input = QtWidgets.QWidget()
        self.tab_input.setObjectName("tab_input")
        self.tabWidget.addTab(self.tab_input, "Input Info")

        self.tab_speaker = QtWidgets.QWidget()
        self.tab_speaker.setObjectName("tab_speaker")
        self.tabWidget.addTab(self.tab_speaker, "Speaker Info")
        self.tabWidget.setFont(self.grFont)

        self.setStyleSheet(("QTabWidget::pane { \n"
                            "top:-1px; \n"
                            "border: none;\n"
                            "}\n"
                            "QTabBar::tab {\n"
                            "border: 1px solid #7d7d7d; \n"
                            "color: #7d7d7d; \n"
                            "padding: 2px;\n"
                            "width: 110px;\n"
                            "}\n"
                            "QTabBar::tab:selected { \n"
                            "color: #ffffff;\n"
                            "background: #7d7d7d; \n"
                            "}"))

        self.save = QTactileButton()
        self.save.setFixedWidth(self.row_width[2])
        self.save.setFont(self.grFont)
        self.save.setText("Update")

        layout = QHBoxLayout(self)
        layout.addWidget(self.tabWidget)
        layout.addWidget(self.save)
        layout.setContentsMargins(90, 15, 0, 0)
        layout.setSpacing(self.row_spacing)

        self.tabWidget.currentChanged.connect(self.onTabChanged)

    def onTabChanged(self, index):
        self.valueChanged.emit()

    @property
    def widget_value(self):
        return self.tabWidget.currentIndex()

    @widget_value.setter
    def widget_value(self, value):
        self.tabWidget.setCurrentIndex(value)

class DiracInputInfo(object):

    def __init__(self):
        self.parameters = {}

    def get_widget(self, parent_widget, gui_type=None):
        return DiracInputInfoWidgets(parent_widget)

class DiracInputInfoWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget):
        super().__init__(widget)

        textedit_layout = QVBoxLayout()
        combobox_layout = QVBoxLayout()

        input_info_label = ['Front Left', 'Front Right', 'Center', 'Surround Left', 'Surround Right', 'Surround Back Left',
                            'Surround Back Right', 'Height Front Left', 'Height Front Right', 'Height Rear Left', 'Height Rear Right',
                            'Subwoofer_LFE']

        self.textedit_list = []
        self.combobox_list = []

        edit_label = QLabel()
        edit_label.setFont(self.grFont)
        edit_label.setText('name')
        textedit_layout.addWidget(edit_label, alignment=Qt.AlignCenter)

        for i in input_info_label:
            textedit = QLineEdit()
            textedit.setFixedWidth(160)
            textedit.setStyleSheet("QLineEdit { background-color: #606060; color: white; }")
            textedit.setFont(self.grFont)
            textedit.setText(i)
            self.textedit_list.append(textedit)
            textedit_layout.addWidget(textedit)
        textedit_layout.setContentsMargins(0, 0, 0, 0)
        textedit_layout.setSpacing(self.row_spacing)

        comboBox_label = QLabel()
        comboBox_label.setFont(self.grFont)
        comboBox_label.setText('type')
        combobox_layout.addWidget(comboBox_label, alignment=Qt.AlignCenter)

        for i in range(len(input_info_label)):
            comboBox = QComboBox()
            comboBox.setFixedWidth(180)
            comboBox.setFont(self.grFont)
            comboBox.addItems(["CHANNEL_TYPE_DEFAULT", "CHANNEL_TYPE_LFE"])
            self.combobox_list.append(comboBox)
            combobox_layout.addWidget(comboBox)
        combobox_layout.setContentsMargins(5, 0, 0, 0)
        combobox_layout.setSpacing(self.row_spacing)

        self.label = QLabel()
        self.label.setFixedWidth(480)
        self.label.setStyleSheet("font-size: 13px; font-family: Arial;")

        res_layout = QHBoxLayout()
        res_layout.addWidget(self.label)
        res_layout.setContentsMargins(10, 0, 0, 0)

        info_layout = QHBoxLayout()
        info_layout.addLayout(textedit_layout)
        info_layout.addLayout(combobox_layout)
        info_layout.setContentsMargins(25, 30, 0, 0)
        info_layout.setSpacing(self.row_spacing)

        layout = QVBoxLayout(self)
        layout.addLayout(info_layout)
        layout.addLayout(res_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

    @property
    def widget_value(self):
        text_list = []
        for textedit in self.textedit_list:
            text_list.append(textedit.text())
        combobox_text_list = []
        for combobox in self.combobox_list:
            combobox_text_list.append(combobox.currentText())
        return text_list, combobox_text_list

    @widget_value.setter
    def widget_value(self, value: list):
        for index, textedit in enumerate(self.textedit_list):
            textedit.setText(value[0][index])
        for index, combobox in enumerate(self.combobox_list):
            combobox.setCurrentText(value[1][index])

class DiracSpeakerInfo(object):

    def __init__(self):
        self.parameters = {}

    def get_widget(self, parent_widget, gui_type=None):
        return DiracSpeakerInfoWidgets(parent_widget, self.parameters, False)

class DiracSpeakerInfoWidgets(QWidget, widgetCompomentBase):
    valueStored = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, widget: QWidget, parameter: dict, rotate: bool):
        super().__init__(widget)

        textedit_layout = QVBoxLayout()
        combobox_layout = QVBoxLayout()
        combobox_id_layout = QVBoxLayout()
        index_layout = QVBoxLayout()

        speaker_info_label = ['Front Left', 'Front Right', 'Center', 'Surround Left', 'Surround Right', 'Surround Back Left',
                            'Surround Back Right', 'Height Front Left', 'Height Front Right', 'Height Rear Left', 'Height Rear Right',
                            'Subwoofer_LFE']
        type_list = ['FULLRANGE_SPEAKER', 'MIDRANGE_SPEAKER', 'WOOFER_SPEAKER', 'SUBWOOFER_SPEAKER', 'TWEETER_SPEAKER',
                     'BASS_MANAGED_SPEAKER', 'DOLBY_ATMOS_SPEAKER']
        id_list = ['0', '1', '2', '3', '4', '5', '6']
        index_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

        self.textedit_list = []
        self.combobox_list = []
        self.combobox_id_list = []
        self.index_list = []

        index_label = QLabel()
        index_label.setFont(self.grFont)
        index_label.setText('Assoc In')
        index_layout.addWidget(index_label, alignment=Qt.AlignCenter)

        for i in range(len(speaker_info_label)):
            comboBox = QComboBox()
            comboBox.setFixedWidth(45)
            comboBox.setFont(self.grFont)
            comboBox.addItems(index_list)
            comboBox.setCurrentIndex(i)
            self.index_list.append(comboBox)
            index_layout.addWidget(comboBox)
        index_layout.setContentsMargins(5, 0, 0, 0)
        index_layout.setSpacing(self.row_spacing)

        edit_label = QLabel()
        edit_label.setFont(self.grFont)
        edit_label.setText('name')
        textedit_layout.addWidget(edit_label, alignment=Qt.AlignCenter)

        for i in speaker_info_label:
            textedit = QLineEdit()
            textedit.setFixedWidth(150)
            textedit.setStyleSheet("QLineEdit { background-color: #606060; color: white; }")
            textedit.setFont(self.grFont)
            textedit.setText(i)
            self.textedit_list.append(textedit)
            textedit_layout.addWidget(textedit)
        textedit_layout.setContentsMargins(5, 0, 0, 0)
        textedit_layout.setSpacing(self.row_spacing)

        comboBox_label = QLabel()
        comboBox_label.setFont(self.grFont)
        comboBox_label.setText('type')
        combobox_layout.addWidget(comboBox_label, alignment=Qt.AlignCenter)

        for i in range(len(speaker_info_label)):
            comboBox = QComboBox()
            comboBox.setFixedWidth(150)
            comboBox.setFont(self.grFont)
            comboBox.addItems(type_list)
            comboBox.setCurrentIndex(0)
            self.combobox_list.append(comboBox)
            combobox_layout.addWidget(comboBox)
        combobox_layout.setContentsMargins(10, 0, 0, 0)
        combobox_layout.setSpacing(self.row_spacing)

        comboBox_id_label = QLabel()
        comboBox_id_label.setFont(self.grFont)
        comboBox_id_label.setText('group id')
        combobox_id_layout.addWidget(comboBox_id_label, alignment=Qt.AlignCenter)

        for i in range(len(speaker_info_label)):
            comboBox = QComboBox()
            comboBox.setFixedWidth(45)
            comboBox.setFont(self.grFont)
            comboBox.addItems(id_list)
            comboBox.setCurrentIndex(0)
            self.combobox_id_list.append(comboBox)
            combobox_id_layout.addWidget(comboBox)
        combobox_id_layout.setContentsMargins(5, 0, 0, 0)
        combobox_id_layout.setSpacing(self.row_spacing)

        self.label = QLabel()
        self.label.setFixedWidth(480)
        self.label.setStyleSheet("font-size: 13px; font-family: Arial;")

        res_layout = QHBoxLayout()
        res_layout.addWidget(self.label)
        res_layout.setContentsMargins(10, 0, 0, 0)

        info_layout = QHBoxLayout()
        info_layout.addLayout(index_layout)
        info_layout.addLayout(textedit_layout)
        info_layout.addLayout(combobox_layout)
        info_layout.addLayout(combobox_id_layout)
        info_layout.setContentsMargins(20, 0, 0, 0)
        info_layout.setSpacing(self.row_spacing)

        layout = QVBoxLayout(self)
        layout.addLayout(info_layout)
        layout.addLayout(res_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

    @property
    def widget_value(self):
        text_list = []
        for textedit in self.textedit_list:
            text_list.append(textedit.text())
        combobox_text_list = []
        for combobox in self.combobox_list:
            combobox_text_list.append(combobox.currentText())
        combobox_id_list = []
        for combobox_id in self.combobox_id_list:
            combobox_id_list.append(combobox_id.currentText())
        index_list = []
        for index in self.index_list:
            index_list.append(index.currentText())
        return text_list, combobox_text_list, combobox_id_list, index_list

    @widget_value.setter
    def widget_value(self, value: list):
        for index, textedit in enumerate(self.textedit_list):
            textedit.setText(value[0][index])
        for index, combobox in enumerate(self.combobox_list):
            combobox.setCurrentText(value[1][index])
        for index, combobox_id in enumerate(self.combobox_id_list):
            combobox_id.setCurrentText(value[2][index])
        for i, index in enumerate(self.index_list):
            index.setCurrentText(value[3][i])