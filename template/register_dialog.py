# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'register_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Register")
        Form.resize(400, 230)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(60, 60, 54, 21))
        self.label.setLineWidth(1)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(120, 60, 180, 21))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.lineEdit.setDragEnabled(False)
        self.lineEdit.setObjectName("lineEdit")

        self.pushButton_send = QtWidgets.QPushButton(Form)
        self.pushButton_send.setGeometry(QtCore.QRect(310, 60, 40, 21))
        self.pushButton_send.setObjectName("pushButton_send")

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(80, 80, 300, 30))
        self.label_2.setLineWidth(1)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(60, 120, 54, 21))
        self.label_3.setLineWidth(1)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setWordWrap(False)
        self.label_3.setObjectName("label_3")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(120, 120, 100, 21))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.lineEdit_2.setDragEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(80, 140, 300, 30))
        self.label_4.setLineWidth(1)
        self.label_4.setTextFormat(QtCore.Qt.AutoText)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setWordWrap(False)
        self.label_4.setObjectName("label_4")

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(90, 190, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(250, 190, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Register"))
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font:Calibri; font-size:12pt; font-weight:600;\">email</span></p></body></html>"))
        self.label_2.setStyleSheet("color:red;")
        self.label_3.setText(_translate("Form",
                                      "<html><head/><body><p><span style=\" font:Calibri; font-size:12pt; font-weight:600;\">code</span></p></body></html>"))
        self.label_4.setStyleSheet("color:red;")
        self.pushButton_send.setText(_translate("Form", "send"))
        self.pushButton_send.setStyleSheet("font:Calibri; font-size:10pt;")
        self.pushButton.setText(_translate("Form", "register"))
        self.pushButton.setStyleSheet("font:Calibri; font-size:10pt;")
        self.pushButton_2.setText(_translate("Form", "quit"))
        self.pushButton_2.setStyleSheet("font:Calibri; font-size:10pt;")
