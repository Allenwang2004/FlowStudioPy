# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'node_tap_select.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_node_tap_select(object):
    def setupUi(self, node_tap_select):
        node_tap_select.setObjectName("node_tap_select")
        node_tap_select.setEnabled(True)
        node_tap_select.resize(400, 80)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(node_tap_select.sizePolicy().hasHeightForWidth())
        node_tap_select.setSizePolicy(sizePolicy)
        node_tap_select.setMinimumSize(QtCore.QSize(400, 80))
        node_tap_select.setMaximumSize(QtCore.QSize(400, 80))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        node_tap_select.setFont(font)
        node_tap_select.setSizeGripEnabled(False)
        node_tap_select.setModal(False)
        self.layoutWidget = QtWidgets.QWidget(node_tap_select)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 10, 383, 65))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_1 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_1.setFont(font)
        self.label_1.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_1.setTextFormat(QtCore.Qt.AutoText)
        self.label_1.setScaledContents(False)
        self.label_1.setWordWrap(False)
        self.label_1.setObjectName("label_1")
        self.horizontalLayout.addWidget(self.label_1)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.comboBox.setFont(font)
        self.comboBox.setStyleSheet("QComboBox QAbstractItemView\n"
"{\n"
"     border: 1px solid rgb(161,161,161);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item\n"
"{\n"
"    height: 24px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:selected\n"
"{    \n"
"    background-color: rgba(54, 98, 180);\n"
"}")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setMinimumSize(QtCore.QSize(380, 30))
        self.buttonBox.setMaximumSize(QtCore.QSize(380, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.buttonBox.setFont(font)
        self.buttonBox.setAutoFillBackground(False)
        self.buttonBox.setStyleSheet("QDialogButtonBox {\n"
"    button-layout: 0;\n"
"}\n"
"\n"
"QPushButton{\n"
"    font: 75 9pt \"Calibri\";\n"
"    font-weight: bold;\n"
"    background: gray;\n"
"    color: white;\n"
"\n"
"    border-radius: 0px;\n"
"    \n"
"    width: 120px;\n"
"    height: 20px;\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    background:  #595959;\n"
"    color: gray;\n"
"}\n"
"\n"
"QPushButton:enabled {\n"
"    background: gray;\n"
"    color: white;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: gray;\n"
"    color: black;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: lightgray;\n"
"    color: black;\n"
"    border-width: 3px;\n"
"    border-style: solid;\n"
"    border-color: gray;\n"
"}\n"
"")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(node_tap_select)
        self.buttonBox.rejected.connect(node_tap_select.reject)
        self.buttonBox.accepted.connect(node_tap_select.accept)
        QtCore.QMetaObject.connectSlotsByName(node_tap_select)

    def retranslateUi(self, node_tap_select):
        _translate = QtCore.QCoreApplication.translate
        node_tap_select.setWindowTitle(_translate("node_tap_select", "Dialog"))
        self.label_1.setText(_translate("node_tap_select", "Tap"))
        self.comboBox.setItemText(0, _translate("node_tap_select", "1"))
        self.comboBox.setItemText(1, _translate("node_tap_select", "2"))
        self.comboBox.setItemText(2, _translate("node_tap_select", "3"))
        self.comboBox.setItemText(3, _translate("node_tap_select", "4"))
        self.comboBox.setItemText(4, _translate("node_tap_select", "5"))
        self.comboBox.setItemText(5, _translate("node_tap_select", "6"))
        self.comboBox.setItemText(6, _translate("node_tap_select", "7"))
        self.comboBox.setItemText(7, _translate("node_tap_select", "8"))
