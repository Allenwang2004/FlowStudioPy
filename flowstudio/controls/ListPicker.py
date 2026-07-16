from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QDialog,
                             QListWidget, QLineEdit, QListWidgetItem, QVBoxLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont

from control.flow_control_widget import widgetCompomentBase
from flowstudio.flow_window_connection import FLOW_Window_Connection


class ListPicker(object):
    """列表选择器"""

    def __init__(self, label_text, items, default_index):
        self.label_text = label_text
        self.parameters = {
            'label_text': label_text,
            'pList': items,
            'pValue': default_index
        }

    def get_widget(self, parent_widget, gui_type=None):
        return ListPickerWidgets(parent_widget, self.parameters)


class ListPickerWidgets(QWidget, widgetCompomentBase):
    """列表选择器组件"""

    valueChanged = pyqtSignal()
    valueStored = pyqtSignal()

    def __init__(self, widget: QWidget, parameters: dict):
        super(ListPickerWidgets, self).__init__(widget)

        self.parent_widget = widget
        self.items = parameters.get('pList', [])
        self.current_index = parameters.get('pValue', 0)
        self.current_text = self.items[self.current_index] if self.items else "None"

        # 标签
        self.label = QLabel()
        self.label.setFont(self.grFont)
        self.label.setText(parameters['label_text'])
        self.label.setFixedWidth(self.row_width[1])

        # 显示当前选中项的标签
        self.display_label = QLabel(self.current_text)
        self.display_label.setFixedWidth(self.row_width[3])
        self.display_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
            }
        """)

        # 选择按钮
        self.select_btn = QPushButton("...")
        self.select_btn.setFixedWidth(self.row_width[2])
        self.select_btn.setFixedHeight(25)
        self.select_btn.clicked.connect(self.buttonSelect)

        # 布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.display_label)
        layout.addWidget(self.select_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.row_spacing)

    @property
    def widget_value(self) -> list:
        """返回 [文本, 索引]"""
        return [self.current_text, self.current_index]

    @widget_value.setter
    def widget_value(self, value: list):
        """设置值 [文本, 索引]"""
        if isinstance(value, list) and len(value) >= 2:
            self.setCurrentIndex(value[1])

    def setCurrentIndex(self, index):
        """设置当前选中索引"""
        if 0 <= index < len(self.items):
            self.current_index = index
            self.current_text = self.items[index]
            self.display_label.setText(self.current_text)

    def buttonSelect(self):
        """显示选择对话框"""
        # 创建对话框
        self.qdialog = QDialog(self.parent_widget.node.scene.getView().window())
        self.qdialog.setWindowTitle('Select Game Profile')

        # 创建选择界面
        self.selectorUI = ListSelectorUI()
        self.selectorUI.setupUi(self.qdialog, self.items, self.current_index)

        # 连接信号
        self.selectorUI.itemSelected.connect(self.on_item_selected)

        # 隐藏其他窗口
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()

        # 显示对话框
        self.qdialog.exec_()

        # 恢复其他窗口
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def on_item_selected(self, item_text, index):
        """选择项改变时"""
        self.current_text = item_text
        self.current_index = index
        self.display_label.setText(item_text)
        self.valueChanged.emit()
        self.valueStored.emit()


from PyQt5.QtCore import QObject, pyqtSignal


class ListSelectorUI(QObject):
    """列表选择器UI"""

    itemSelected = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()

    def setupUi(self, dialog, items, current_index=0):
        """设置UI"""
        self.dialog = dialog
        self.items = items
        self.current_index = current_index
        self.selected_item = None
        self.selected_index = -1

        # 设置对话框
        dialog.setModal(True)
        dialog.setGeometry(400, 200, 500, 600)
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        # 主布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题
        title_label = QLabel("Select Item")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setFixedHeight(35)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 5px;
                font-size: 13px;
                background-color: #2b2b2b;
                color: white;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.search_box.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_box)

        # 列表
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.setFocusPolicy(Qt.StrongFocus)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #555;
                border-radius: 5px;
                outline: none;
                background-color: #2b2b2b;
                color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)

        # 添加项目
        for i, item in enumerate(items):
            list_item = QListWidgetItem(f"{i + 1}. {item}")
            self.list_widget.addItem(list_item)

        # 设置当前选中项
        if 0 <= current_index < len(items):
            self.list_widget.setCurrentRow(current_index)
            self.list_widget.scrollToItem(self.list_widget.item(current_index))

        # 双击选择
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.list_widget)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(self.cancel_btn)

        # 确定按钮
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedSize(100, 35)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

        # 设置焦点到搜索框
        self.search_box.setFocus()

    def filter_items(self, text):
        """过滤列表项"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_text = item.text().split('. ', 1)[1] if '. ' in item.text() else item.text()
            if text.lower() in item_text.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def on_item_double_clicked(self, item):
        """双击项目时"""
        self.accept()

    def accept(self):
        """确认选择"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.selected_index = current_row
            self.selected_item = self.items[current_row]
            self.itemSelected.emit(self.selected_item, self.selected_index)
        self.dialog.accept()