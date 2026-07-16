from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTreeWidget, \
    QAbstractItemView, QTreeWidgetItem

class NODE_Propertys(QDialog):
    def __init__(self,node):
        super().__init__()
        self.node=node
        self.dict={}
        self.setWindowTitle(self.node.op_title + " property")
        self.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.setFixedSize(250,400)
        self.serializeFile()
        self.propertyWidget=Node_Property_Widget()
        self.propertyWidget.dict_value=self.dict
        self.propertyWidget.setParent(self)
        self.propertyWidget.setFixedSize(250,400)

    def serializeFile(self):
        self.dict=self.node.serialize()

#TODO: when we have multiple FLOW_Sub_Window,if we switch,Node_Property_Widget need to changed.
class Node_Property_Widget(QTreeWidget):

    @property
    def dict_value(self):
        return self.dict

    @dict_value.setter
    def dict_value(self,dict:dict):
        self.dict=dict
        self.updateData()

    def __init__(self):
        super().__init__()
        self.dict = {}
        self.setStyleSheet("background:#212121;font: 75 12pt \"Calibri\";color:#dddddd;")
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.setMinimumHeight(100)
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setIndentation(16)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.initLayout()

    def focusOutEvent(self, event):
        """失去焦点时取消选中"""
        self.clearSelection()
        super().focusOutEvent(event)

    def initLayout(self):

        self.initGeneralSubLayout()
        self.initContentSubLayout()
        self.initInputsOrOutputsSubLayout("inputs")
        self.initInputsOrOutputsSubLayout("outputs")
        self.initInputsOrOutputsSubLayout('inctrls')
        self.initInputsOrOutputsSubLayout('outctrls')

    def initGeneralSubLayout(self):
        generalItems = QTreeWidgetItem(self)
        generalItems.setText(0,"general")
        generalItems.setExpanded(False)
        try:
            # id = QTreeWidgetItem(generalItems)
            # id.setText(0, "id:  " + str(self.dict["id"]))
            title = QTreeWidgetItem(generalItems)
            title.setText(0, "name:  " + str(self.dict["title"]))
            # posX = QTreeWidgetItem(generalItems)
            # posX.setText(0, "pos_x:  " + str(self.dict["pos_x"]))
            # posY = QTreeWidgetItem(generalItems)
            # posY.setText(0, "pos_y:  " + str(self.dict["pos_y"]))

            # op_code = QTreeWidgetItem(generalItems)
            # op_code.setText(0, "op_code:  " + str(self.dict["op_code"]))
            # type = QTreeWidgetItem(generalItems)
            # type.setText(0, "type:  " + str(self.dict["type"]))
            # designator = QTreeWidgetItem(generalItems)
            # designator.setText(0, "designator:  " + str(self.dict["designator"]))
            control_id = QTreeWidgetItem(self)
            control_id.setText(0, "control_id:  " + str(self.dict["type"]) + "_" + str(self.dict["designator"]))
            color = QTreeWidgetItem(generalItems)
            color.setText(0, "color:  " + str(self.dict["color"]))

            expand = QTreeWidgetItem(generalItems)
            if "expand" in self.dict:
                expand.setText(0, "expand:  " + str(self.dict["expand"]))
            else:
                expand.setText(0, "expand:  disabled")
        except Exception:
            generalItems.takeChild(generalItems.childCount()-1)

    def initInputsOrOutputsSubLayout(self,key:str):
        ioWidget = QTreeWidgetItem(self)
        ioWidget.setText(0, key)
        ioWidget.setExpanded(False)
        try:
            count = 0
            for i in self.dict[key]:
                ioItems = QTreeWidgetItem(ioWidget)
                ioItems.setText(0, key + "_" + str(count) + ":  ")
                for j, k in i.items():
                    ioItem = QTreeWidgetItem(ioItems)
                    ioItem.setText(0, j + ":  " + str(k))
                count = count + 1
        except Exception:
            return

    def initContentSubLayout(self):
        contentItems = QTreeWidgetItem(self)
        contentItems.setText(0, "parameter")
        contentItems.setExpanded(True)
        try:
            tap_flag = False
            tap_index = 0
            if self.dict['tap_menu_parameter_name'] in self.dict["content"].keys():
                for j, k in self.dict["content"].items():
                    if j == self.dict['tap_menu_parameter_name']:
                        tap_flag = True
                        continue
                    if tap_flag:
                        if int(j[-1]) + 1 != tap_index:
                            tap_index = tap_index + 1
                            tapItem = QTreeWidgetItem(contentItems)
                            tapItem.setText(0, "" + str(tap_index) + ":  ")
                        tapInner_Item = QTreeWidgetItem(tapItem)
                        tapInner_Item.setText(0, j[:-1] + str(tap_index) + ":  " + str(k[0] if type(k) is list else k))
                    else:
                        tapAbove_Item = QTreeWidgetItem(contentItems)
                        tapAbove_Item.setText(0, j + ":  " + str(k[0] if type(k) is list else k))
            else:
                for j, k in self.dict["content"].items():
                    if self.dict['type'] == 'SMART_GATE':
                        if j == 'thres': break;
                    other_Item = QTreeWidgetItem(contentItems)
                    other_Item.setText(0, j + ":  " + str(k[0] if type(k) is list else k))
        except Exception:
            return

    def updateData(self):
        self.clear()
        self.initLayout()