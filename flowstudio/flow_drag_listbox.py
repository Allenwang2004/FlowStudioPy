from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import CATE_CONTROL_MAPPING
from nodeeditor.utils import dumpException
from functools import partial

class QDMDragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()


    def addMyItems(self):
        keys = list(FLOW_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)


    def addMyItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self) # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)


    def startDrag(self, *args, **kwargs):

        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.UserRole))


            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e: dumpException(e)

    def updateItemsFlag(self,editmode):
        for i in range(self.count()):
            if editmode:
                self.item(i).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                self.item(i).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

class QDMDragTreebox(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.column_dicts = CATE_AO_MAPPING.keys()
        self.column_number = 0
        self.column_item = None
        self.items = list()
        self.subPatch_item=None
        self.input_item = None
        self.output_item = None
        self.setColumnCount(2)
        self.setColumnWidth(0, 255)
        self.setColumnWidth(1, 10)
        self.initUI()

    def initUI(self):
        # init
        self.font = QFont("Calibri")
        self.setHeaderHidden(True)
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.setMinimumHeight(210)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setIndentation(16)
        self.setIconSize(QSize(28, 28))
        # self.setStyleSheet("QTreeView::branch{border-image: none;image: url(../resources/cut.png);height:10px;width:10px;}")

    def focusOutEvent(self, event):
        """失去焦点时取消选中"""
        self.clearSelection()
        super().focusOutEvent(event)

    def addMyItems(self, category_name=None):
        for key, values in CATE_AO_MAPPING.items():
            if category_name is not None and key != category_name:
                continue
            category = self.add_item(name=key)
            if key == 'Technology Provider':
                category.setForeground(0, QBrush(QColor(110, 190, 255)))
            for value in values:
                if type(value) is Company:
                    company_item = self.add_item(name=value.name, icon=value.icon_path, parent_item=category,
                                                 is_self_parent=True)
                    if (hasattr(self.parent.license_mechanism, 'technical_provider_info_data') and
                            value.db_name in self.parent.license_mechanism.technical_provider_info_data):
                        value.description = self.parent.license_mechanism.technical_provider_info_data[value.db_name]
                    info_button = QToolButton(self)
                    info_button.setIcon(QIcon("../resources/info-icon.png"))
                    info_button.setStyleSheet("border-radius: 30px;")
                    info_button.clicked.connect(partial(self.handle_info_button_clicked, f'{value.name} Info',
                                                        value.description))
                    self.setItemWidget(company_item, 1, info_button)
                    if type(value.ao_list) is list:
                        for ao_no in value.ao_list:
                            node = get_class_from_opcode(ao_no)
                            ao_item = self.add_item(name=node.display_name, icon=node.icon, op_code=node.op_code,
                                                    parent_item=company_item)
                            if (hasattr(self.parent.license_mechanism, 'ao_info_data') and
                                    node.op_code in self.parent.license_mechanism.ao_info_data):
                                node.description = self.parent.license_mechanism.ao_info_data[node.op_code]
                            info_button = QToolButton(self)
                            info_button.setIcon(QIcon("../resources/info-icon.png"))
                            info_button.setStyleSheet("border-radius: 30px;")
                            info_button.clicked.connect(partial(self.handle_info_button_clicked, f'{node.display_name} Info',
                                                                node.description))
                            self.setItemWidget(ao_item, 1, info_button)
                    elif type(value.ao_list) is dict:
                        for key, values in value.ao_list.items():
                            if key:
                                category = self.add_item(name=key, parent_item=company_item,
                                                         is_self_parent=True)
                                for ao_no in values:
                                    node = get_class_from_opcode(ao_no)
                                    ao_item = self.add_item(name=node.display_name, icon=node.icon, op_code=node.op_code,
                                                            parent_item=category)
                                    if (hasattr(self.parent.license_mechanism, 'ao_info_data') and
                                            node.op_code in self.parent.license_mechanism.ao_info_data):
                                        node.description = self.parent.license_mechanism.ao_info_data[node.op_code]
                                    info_button = QToolButton(self)
                                    info_button.setIcon(QIcon("../resources/info-icon.png"))
                                    info_button.setStyleSheet("border-radius: 30px;")
                                    info_button.clicked.connect(
                                        partial(self.handle_info_button_clicked, f'{node.display_name} Info',
                                                node.description))
                                    self.setItemWidget(ao_item, 1, info_button)
                            else:
                                for ao_no in values:
                                    node = get_class_from_opcode(ao_no)
                                    ao_item = self.add_item(name=node.display_name, icon=node.icon, op_code=node.op_code,
                                                            parent_item=company_item)
                                    if (hasattr(self.parent.license_mechanism, 'ao_info_data') and
                                            node.op_code in self.parent.license_mechanism.ao_info_data):
                                        node.description = self.parent.license_mechanism.ao_info_data[node.op_code]
                                    info_button = QToolButton(self)
                                    info_button.setIcon(QIcon("../resources/info-icon.png"))
                                    info_button.setStyleSheet("border-radius: 30px;")
                                    info_button.clicked.connect(
                                        partial(self.handle_info_button_clicked, f'{node.display_name} Info',
                                                node.description))
                                    self.setItemWidget(ao_item, 1, info_button)
                else:
                    node = get_class_from_opcode(value)
                    ao_item = self.add_item(name=node.display_name, icon=node.icon, op_code=node.op_code,
                                            parent_item=category)
                    if (hasattr(self.parent.license_mechanism, 'ao_info_data') and
                            node.op_code in self.parent.license_mechanism.ao_info_data):
                        node.description = self.parent.license_mechanism.ao_info_data[node.op_code]
                    info_button = QToolButton(self)
                    info_button.setIcon(QIcon("../resources/info-icon.png"))
                    info_button.setStyleSheet("border-radius: 30px;")
                    info_button.clicked.connect(partial(self.handle_info_button_clicked,
                                                        f'{node.display_name} Info',
                                                        node.description))
                    self.setItemWidget(ao_item, 1, info_button)

    def addControlItems(self):
        for key, values in CATE_CONTROL_MAPPING.items():
            category = self.add_item(name=key)
            for value in values:
                if type(value) is Company:
                    return
                else:
                    node = get_class_from_opcode(value)
                    ao_item = self.add_item(name=node.display_name, icon=node.icon, op_code=node.op_code,
                                            parent_item=category)
                    # if (hasattr(self.parent.license_mechanism, 'ao_info_data') and
                    #         node.op_code in self.parent.license_mechanism.ao_info_data):
                    #     node.description = self.parent.license_mechanism.ao_info_data[node.op_code]
                    info_button = QToolButton(self)
                    info_button.setIcon(QIcon("../resources/info-icon.png"))
                    info_button.setStyleSheet("border-radius: 30px;")
                    info_button.clicked.connect(partial(self.handle_info_button_clicked,
                                                        f'{node.display_name} Info',
                                                        node.info))
                    self.setItemWidget(ao_item, 1, info_button)

    def handle_info_button_clicked(self, title, text):
        """
            Handle the click event of the information button.

            This function hides all GUI windows in the parent's list of window objects, displays an information message box
            with the provided 'title' and 'text' content, and then shows all GUI windows again.

            Args:
                title (str): The title of the information message box.
                text (str): The text content of the information message box.

            Returns:
                None
        """
        for gui_window in self.parent.all_window_objects:
            gui_window.hide()
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec_()
        for gui_window in self.parent.all_window_objects:
            gui_window.show()

    def add_item(self, name, icon=None, op_code=0, parent_item=None, is_self_parent=False):
        """
            Add an item to the hierarchical tree structure.

            This method creates and adds an item with the specified attributes to a hierarchical tree structure.

            Args:
                name (str): The name of the item.
                icon (str, optional): The path to an icon for the item. Default is None.
                op_code (int, optional): A number associated with the item. Default is 0.
                parent_item (QTreeWidgetItem, optional): The parent item to which this item should be added. Default is None.
                is_self_parent (bool, optional): Indicates whether this item is considered a parent item itself. Default is False.

            Returns:
                QTreeWidgetItem: The created and added item.

            Note:
                - If `parent_item` is None, the item is added as the first layer in the hierarchy.
                - If `parent_item` is provided, the item is added as a child of `parent_item`.
                - If `is_self_parent` is True, the item is considered a parent item and is added to the `items` list.
        """
        if parent_item is None:  # first layer
            item = QTreeWidgetItem(self)
            item.setText(self.column_number, name)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setFont(self.column_number, self.font)
            item.setSizeHint(self.column_number, QSize(32, 32))
        else:  # not first layer
            item = QTreeWidgetItem(parent_item)
            pixmap = QPixmap(icon if icon is not None else ".")
            item.setText(self.column_number, name)
            item.setIcon(self.column_number, QIcon(pixmap))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setFont(self.column_number, self.font)
            item.setSizeHint(self.column_number, QSize(32, 32))
            item.setToolTip(self.column_number, name)

            if not is_self_parent:  # this is audio object
                self.items.append(item)
                if op_code == OP_NODE_SUBPATCH:
                    self.subPatch_item = item
                if op_code == OP_NODE_ADC:
                    self.input_item = item
                if op_code == OP_NODE_DAC:
                    self.output_item = item
                item.setData(self.column_number, Qt.UserRole, pixmap)
                item.setData(self.column_number, Qt.UserRole + 1, op_code)

        return item

    def update(self):
        self.items.clear()
        super().update()

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()

            op_code = item.data(self.currentColumn(),Qt.UserRole + 1)

            pixmap = QPixmap(item.data(self.currentColumn(),Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text(self.currentColumn()))

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)


            drag.exec_(Qt.MoveAction)

        except Exception as e: dumpException(e)

    def updateItemsFlag(self,editmode):
        for item in self.items:
            if editmode:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

    def HiddenSubPatchItem(self, hidden):
        if not hidden:
            self.subPatch_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.subPatch_item.setHidden(False)
        else:
            self.subPatch_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.subPatch_item.setHidden(True)

    def HiddenInOutItem(self, hidden, in_ao_is_supported, out_ao_is_supported):
        from flowstudio.flow_conf import AO_TYPE_NAME, OP_NODE_ADC, OP_NODE_DAC, CATE_AO_MAPPING
        feature_permission_data = self.parent.license_mechanism.feature_permission_data

        if not hidden:
            if OP_NODE_ADC in feature_permission_data[AO_TYPE_NAME]:
                self.input_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            else:
                self.input_item.setFlags(self.input_item.flags() & ~Qt.ItemIsEnabled)
            self.input_item.setHidden(False)
            if OP_NODE_DAC in feature_permission_data[AO_TYPE_NAME]:
                self.output_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            else:
                self.output_item.setFlags(self.input_item.flags() & ~Qt.ItemIsEnabled)
            self.output_item.setHidden(False)
        else:
            self.input_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.input_item.setHidden(True)
            self.output_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.output_item.setHidden(True)

        # When in_ao_is_supported is False, IN AO is not supported
        if not in_ao_is_supported:
            self.input_item.setFlags(self.input_item.flags() & ~Qt.ItemIsEnabled)

        # When out_ao_is_supported is False, OUT AO is not supported
        if not out_ao_is_supported:
            self.output_item.setFlags(self.input_item.flags() & ~Qt.ItemIsEnabled)