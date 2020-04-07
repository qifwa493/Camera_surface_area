# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'areaDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon


class Ui_areaDialog(object):
    def setupUi(self, areaDialog):
        areaDialog.setObjectName("areaDialog")
        areaDialog.setWindowIcon(QIcon('camera.png'))
        areaDialog.resize(280, 160)
        self.verticalLayout = QtWidgets.QVBoxLayout(areaDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(areaDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(298, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.areaLineEdit = QtWidgets.QLineEdit(areaDialog)
        self.areaLineEdit.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.areaLineEdit.setFont(font)
        self.areaLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.areaLineEdit.setReadOnly(True)
        self.areaLineEdit.setObjectName("areaLineEdit")
        self.horizontalLayout_2.addWidget(self.areaLineEdit)
        self.label_2 = QtWidgets.QLabel(areaDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(153, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.areaOKButton = QtWidgets.QPushButton(areaDialog)
        self.areaOKButton.setObjectName("areaOKButton")
        self.horizontalLayout_3.addWidget(self.areaOKButton)
        spacerItem2 = QtWidgets.QSpacerItem(153, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(areaDialog)
        QtCore.QMetaObject.connectSlotsByName(areaDialog)

    def retranslateUi(self, areaDialog):
        _translate = QtCore.QCoreApplication.translate
        areaDialog.setWindowTitle(_translate("areaDialog", "Area"))
        self.label.setText(_translate("areaDialog", "The area is:"))
        self.areaLineEdit.setText(_translate("areaDialog", "12345"))
        self.label_2.setText(_translate("areaDialog",
                                        "<html><head/><body><p>m<span style=\" vertical-align:super;\">2</span></p></body></html>"))
        self.areaOKButton.setText(_translate("areaDialog", "OK"))

