# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        settingsDialog.setObjectName("settingsDialog")
        settingsDialog.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(settingsDialog.sizePolicy().hasHeightForWidth())
        settingsDialog.setSizePolicy(sizePolicy)
        settingsDialog.setMinimumSize(QtCore.QSize(400, 300))
        settingsDialog.setMaximumSize(QtCore.QSize(400, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../camera.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settingsDialog.setWindowIcon(icon)
        self.gridLayout_4 = QtWidgets.QGridLayout(settingsDialog)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.modeSelectionGroup = QtWidgets.QGroupBox(settingsDialog)
        self.modeSelectionGroup.setObjectName("modeSelectionGroup")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.modeSelectionGroup)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.atuoModeButton = QtWidgets.QRadioButton(self.modeSelectionGroup)
        self.atuoModeButton.setCheckable(True)
        self.atuoModeButton.setChecked(True)
        self.atuoModeButton.setAutoRepeat(True)
        self.atuoModeButton.setObjectName("atuoModeButton")
        self.gridLayout.addWidget(self.atuoModeButton, 0, 1, 1, 1)
        self.manualModeButton = QtWidgets.QRadioButton(self.modeSelectionGroup)
        self.manualModeButton.setObjectName("manualModeButton")
        self.gridLayout.addWidget(self.manualModeButton, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.modeSelectionGroup, 0, 0, 1, 2)
        self.curveFittingBox = QtWidgets.QCheckBox(settingsDialog)
        self.curveFittingBox.setObjectName("curveFittingBox")
        self.gridLayout_4.addWidget(self.curveFittingBox, 1, 0, 1, 1)
        self.maxSizeGroup = QtWidgets.QGroupBox(settingsDialog)
        self.maxSizeGroup.setObjectName("maxSizeGroup")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.maxSizeGroup)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.maxSizeSlider = QtWidgets.QSlider(self.maxSizeGroup)
        self.maxSizeSlider.setMinimum(1000)
        self.maxSizeSlider.setMaximum(5000)
        self.maxSizeSlider.setProperty("value", 3000)
        self.maxSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.maxSizeSlider.setObjectName("maxSizeSlider")
        self.gridLayout_3.addWidget(self.maxSizeSlider, 0, 0, 1, 1)
        self.maxSizeSpinBox = QtWidgets.QSpinBox(self.maxSizeGroup)
        self.maxSizeSpinBox.setMinimum(1000)
        self.maxSizeSpinBox.setMaximum(5000)
        self.maxSizeSpinBox.setProperty("value", 3000)
        self.maxSizeSpinBox.setObjectName("maxSizeSpinBox")
        self.gridLayout_3.addWidget(self.maxSizeSpinBox, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.maxSizeGroup, 2, 0, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(settingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_4.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(settingsDialog)
        self.buttonBox.accepted.connect(settingsDialog.accept)
        self.buttonBox.rejected.connect(settingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)

    def retranslateUi(self, settingsDialog):
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Settings"))
        self.modeSelectionGroup.setTitle(_translate("settingsDialog", "Area selection mode"))
        self.atuoModeButton.setText(_translate("settingsDialog", "Auto"))
        self.manualModeButton.setText(_translate("settingsDialog", "Manual"))
        self.curveFittingBox.setText(_translate("settingsDialog", "Curve fitting"))
        self.maxSizeGroup.setTitle(_translate("settingsDialog", "Max image size during processing"))
