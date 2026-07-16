# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project_title_edit.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_projTitleDialog(object):
    def setupUi(self, projTitleDialog):
        projTitleDialog.setObjectName("projTitleDialog")
        projTitleDialog.setEnabled(True)
        projTitleDialog.resize(400, 80)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(projTitleDialog.sizePolicy().hasHeightForWidth())
        projTitleDialog.setSizePolicy(sizePolicy)
        projTitleDialog.setMinimumSize(QtCore.QSize(400, 80))
        projTitleDialog.setMaximumSize(QtCore.QSize(400, 80))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        projTitleDialog.setFont(font)
        projTitleDialog.setSizeGripEnabled(False)
        projTitleDialog.setModal(False)
        self.layoutWidget = QtWidgets.QWidget(projTitleDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 10, 382, 65))
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
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMaximumSize(QtCore.QSize(180, 24))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
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
        self.buttonBox.setStyleSheet("        QPushButton {\n"
"        font: 9pt \"Calibri\";\n"
"        width: 120px;\n"
"        color: black;\n"
"        border-color: darkGray;\n"
"        border-style: solid;\n"
"        border-radius: 2;\n"
"        padding: 5 px;\n"
"        background-color: lightGray;\n"
"        }\n"
"        QPushButton:hover {\n"
"        background-color: darkGray;\n"
"        }\n"
"        QPushButton:Pressed {\n"
"        background-color: darkGray;\n"
"        }\n"
"")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.RestoreDefaults|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(projTitleDialog)
        self.buttonBox.rejected.connect(projTitleDialog.reject)
        self.buttonBox.accepted.connect(projTitleDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(projTitleDialog)

    def retranslateUi(self, projTitleDialog):
        _translate = QtCore.QCoreApplication.translate
        projTitleDialog.setWindowTitle(_translate("projTitleDialog", "Dialog"))
        self.label_1.setText(_translate("projTitleDialog", "Project Name"))
        self.lineEdit.setText(_translate("projTitleDialog", "NEW_FLOW"))
