# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'group_io_select.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_io_select_Dialog(object):
    def setupUi(self, io_select_Dialog):
        io_select_Dialog.setObjectName("io_select_Dialog")
        io_select_Dialog.setEnabled(True)
        io_select_Dialog.resize(400, 120)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(io_select_Dialog.sizePolicy().hasHeightForWidth())
        io_select_Dialog.setSizePolicy(sizePolicy)
        io_select_Dialog.setMinimumSize(QtCore.QSize(400, 120))
        io_select_Dialog.setMaximumSize(QtCore.QSize(400, 120))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        io_select_Dialog.setFont(font)
        io_select_Dialog.setSizeGripEnabled(False)
        io_select_Dialog.setModal(False)
        self.layoutWidget = QtWidgets.QWidget(io_select_Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 383, 101))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout_1 = QtWidgets.QFormLayout()
        self.formLayout_1.setObjectName("formLayout_1")
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
        self.formLayout_1.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_1)
        self.comboBox_1 = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.comboBox_1.setFont(font)
        self.comboBox_1.setStyleSheet("QComboBox QAbstractItemView\n"
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
        self.comboBox_1.setObjectName("comboBox_1")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.formLayout_1.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setScaledContents(False)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.formLayout_1.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.comboBox_2.setFont(font)
        self.comboBox_2.setStyleSheet("QComboBox QAbstractItemView\n"
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
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.formLayout_1.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_2)
        self.verticalLayout.addLayout(self.formLayout_1)
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

        self.retranslateUi(io_select_Dialog)
        self.buttonBox.rejected.connect(io_select_Dialog.reject)
        self.buttonBox.accepted.connect(io_select_Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(io_select_Dialog)

    def retranslateUi(self, io_select_Dialog):
        _translate = QtCore.QCoreApplication.translate
        io_select_Dialog.setWindowTitle(_translate("io_select_Dialog", "Dialog"))
        self.label_1.setText(_translate("io_select_Dialog", "Group Input Select:"))
        self.comboBox_1.setItemText(0, _translate("io_select_Dialog", "1"))
        self.comboBox_1.setItemText(1, _translate("io_select_Dialog", "2"))
        self.comboBox_1.setItemText(2, _translate("io_select_Dialog", "3"))
        self.comboBox_1.setItemText(3, _translate("io_select_Dialog", "4"))
        self.comboBox_1.setItemText(4, _translate("io_select_Dialog", "5"))
        self.comboBox_1.setItemText(5, _translate("io_select_Dialog", "6"))
        self.comboBox_1.setItemText(6, _translate("io_select_Dialog", "7"))
        self.comboBox_1.setItemText(7, _translate("io_select_Dialog", "8"))
        self.label_2.setText(_translate("io_select_Dialog", "Group Output Select:"))
        self.comboBox_2.setItemText(0, _translate("io_select_Dialog", "1"))
        self.comboBox_2.setItemText(1, _translate("io_select_Dialog", "2"))
        self.comboBox_2.setItemText(2, _translate("io_select_Dialog", "3"))
        self.comboBox_2.setItemText(3, _translate("io_select_Dialog", "4"))
        self.comboBox_2.setItemText(4, _translate("io_select_Dialog", "5"))
        self.comboBox_2.setItemText(5, _translate("io_select_Dialog", "6"))
        self.comboBox_2.setItemText(6, _translate("io_select_Dialog", "7"))
        self.comboBox_2.setItemText(7, _translate("io_select_Dialog", "8"))
