# -*- coding: utf-8 -*-
import os
import shutil
import sys
import zipfile

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox,QInputDialog,QFileDialog



class Ui_Form(object):
  def setupUi(self, Form):
    Form.setObjectName("Form")
    Form.resize(500, 150)
    self.widget = QtWidgets.QWidget(Form)
    self.widget.setGeometry(QtCore.QRect(50, 10, 400, 100))
    self.widget.setObjectName("widget")
    self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
    self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.openFileButton = QtWidgets.QPushButton(self.widget)
    self.openFileButton.setObjectName("openFileButton")
    self.horizontalLayout.addWidget(self.openFileButton)
    self.filePathlineEdit = QtWidgets.QTextEdit(self.widget)
    self.filePathlineEdit.setFixedHeight(100)
    self.filePathlineEdit.setFixedWidth(250)
    self.filePathlineEdit.setObjectName("filePathlineEdit")
    self.horizontalLayout.addWidget(self.filePathlineEdit)
    self.retranslateUi(Form)
    QtCore.QMetaObject.connectSlotsByName(Form)
  def retranslateUi(self, Form):
    _translate = QtCore.QCoreApplication.translate
    Form.setWindowTitle(_translate("Form", "Convert File"))
    self.openFileButton.setText(_translate("Form", "Select File"))


class MyMainForm(QMainWindow, Ui_Form):
  def __init__(self, parent=None):
    super(MyMainForm, self).__init__(parent)
    self.setupUi(self)
    self.openFileButton.clicked.connect(self.openFile)

  def get_zip(self, dirpath, outFullName):
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
      fpath = path.replace(dirpath, '')
      for filename in filenames:
        print(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


  def openFile(self):

    try:
      get_filename_path, ok = QFileDialog.getOpenFileName(self,
                    "Select a single file",
                    "D:\TYM\FlowStudioPy",
                    "All Files (*);;Text Files (*.txt)")

      # Get path
      fi = QFileInfo(get_filename_path)
      file_name = fi.fileName()
      file_name1 = fi.fileName().split(".")[0]
      file_path = fi.absolutePath()

      # Rename
      new_file = os.path.join(file_path, "main.json")
      os.rename(file_path+"/"+file_name, new_file)

      # Create a file and move
      os.mkdir(file_path + "/file")
      old_file = file_path + "/main.json"
      new_file = file_path + "/file/main.json"
      shutil.move(old_file, new_file)

      # zip
      self.get_zip(file_path + "/file",file_path+"/"+file_name1+".zip")

      # rename
      newname = os.path.join(file_path,file_name1 + '.proj')
      os.rename(file_path+"/"+file_name1+".zip", newname)

      # Remove folders
      shutil.rmtree(file_path + "/file")

      self.filePathlineEdit.setText("Save : "+newname)
    except Exception as e:
      print(e)
      self.filePathlineEdit.setText("Fail : " + str(e))


if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWin = MyMainForm()
  myWin.show()
  sys.exit(app.exec_())