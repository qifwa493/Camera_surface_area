# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cameraMatrix.ui'
#
# Created by: PyQt5 UI code generator 5.13.0


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon


class Ui_createCamMatrixDialog(object):
    def setupUi(self, createCamMatrixDialog):
        createCamMatrixDialog.setObjectName("createCamMatrixDialog")
        createCamMatrixDialog.setWindowIcon(QIcon('exit.png'))
        createCamMatrixDialog.resize(430, 500)
        self.groupBox = QtWidgets.QGroupBox(createCamMatrixDialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 371, 371))
        self.groupBox.setObjectName("groupBox")
        self.camMatPicDirLabel = QtWidgets.QLabel(self.groupBox)
        self.camMatPicDirLabel.setGeometry(QtCore.QRect(10, 50, 351, 311))
        self.camMatPicDirLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.camMatPicDirLabel.setWordWrap(True)
        self.camMatPicDirLabel.setObjectName("camMatPicDirLabel")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 23, 351, 25))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.camMatImportButton = QtWidgets.QPushButton(self.layoutWidget)
        self.camMatImportButton.setObjectName("camMatImportButton")
        self.horizontalLayout.addWidget(self.camMatImportButton)
        spacerItem = QtWidgets.QSpacerItem(368, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.layoutWidget1 = QtWidgets.QWidget(createCamMatrixDialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(30, 400, 371, 41))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.camMatModelLineEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.camMatModelLineEdit.setObjectName("camMatModelLineEdit")
        self.verticalLayout.addWidget(self.camMatModelLineEdit)
        self.createCamMatButton = QtWidgets.QPushButton(createCamMatrixDialog)
        self.createCamMatButton.setGeometry(QtCore.QRect(30, 452, 261, 31))
        self.createCamMatButton.setObjectName("createCamMatButton")
        self.camMatCloseButton = QtWidgets.QPushButton(createCamMatrixDialog)
        self.camMatCloseButton.setGeometry(QtCore.QRect(330, 460, 75, 23))
        self.camMatCloseButton.setObjectName("camMatCloseButton")

        self.retranslateUi(createCamMatrixDialog)
        QtCore.QMetaObject.connectSlotsByName(createCamMatrixDialog)

    def retranslateUi(self, createCamMatrixDialog):
        _translate = QtCore.QCoreApplication.translate
        createCamMatrixDialog.setWindowTitle(_translate("createCamMatrixDialog", "Create Camera Matrix"))
        self.groupBox.setTitle(_translate("createCamMatrixDialog", "Import photos"))
        self.camMatPicDirLabel.setText(_translate("createCamMatrixDialog", "Please import at least 10 photos shot using the same camera. \n"
"Each photo should contain one and the same chessboard."))
        self.camMatImportButton.setText(_translate("createCamMatrixDialog", "Import"))
        self.label_2.setText(_translate("createCamMatrixDialog", "Camera Model"))
        self.createCamMatButton.setText(_translate("createCamMatrixDialog", "Create!"))
        self.camMatCloseButton.setText(_translate("createCamMatrixDialog", "Close"))
