# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon


class Ui_openDialog(object):
    def setupUi(self, openDialog):
        openDialog.setObjectName("openDialog")
        openDialog.setWindowIcon(QIcon('app_icon.png'))
        openDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(openDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox = QtWidgets.QCheckBox(openDialog)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
        self.cameraGroupBox = QtWidgets.QGroupBox(openDialog)
        self.cameraGroupBox.setObjectName("cameraGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.cameraGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cameraMatrixDirLabel = QtWidgets.QLabel(self.cameraGroupBox)
        self.cameraMatrixDirLabel.setText("")
        self.cameraMatrixDirLabel.setWordWrap(True)
        self.cameraMatrixDirLabel.setObjectName("cameraMatrixDirLabel")
        self.verticalLayout.addWidget(self.cameraMatrixDirLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.importCamMatrixButton = QtWidgets.QPushButton(self.cameraGroupBox)
        self.importCamMatrixButton.setObjectName("importCamMatrixButton")
        self.horizontalLayout.addWidget(self.importCamMatrixButton)
        spacerItem = QtWidgets.QSpacerItem(278, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.cameraGroupBox, 1, 0, 1, 2)
        self.photoGroupBox = QtWidgets.QGroupBox(openDialog)
        self.photoGroupBox.setObjectName("photoGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.photoGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.photoDirLabel = QtWidgets.QLabel(self.photoGroupBox)
        self.photoDirLabel.setText("")
        self.photoDirLabel.setWordWrap(True)
        self.photoDirLabel.setObjectName("photoDirLabel")
        self.verticalLayout_2.addWidget(self.photoDirLabel)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.importPhotoButton = QtWidgets.QPushButton(self.photoGroupBox)
        self.importPhotoButton.setObjectName("importPhotoButton")
        self.horizontalLayout_2.addWidget(self.importPhotoButton)
        spacerItem1 = QtWidgets.QSpacerItem(278, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.photoGroupBox, 2, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(285, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(openDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(openDialog)
        self.buttonBox.accepted.connect(openDialog.accept)
        self.buttonBox.rejected.connect(openDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(openDialog)

    def retranslateUi(self, openDialog):
        _translate = QtCore.QCoreApplication.translate
        openDialog.setWindowTitle(_translate("openDialog", "Open"))
        self.checkBox.setText(_translate("openDialog", "Calibrate camera"))
        self.cameraGroupBox.setTitle(_translate("openDialog", "Camera Matrix"))
        self.importCamMatrixButton.setText(_translate("openDialog", "Import"))
        self.photoGroupBox.setTitle(_translate("openDialog", "Photo"))
        self.importPhotoButton.setText(_translate("openDialog", "Import"))
