# -*- coding: utf-8 -*-

__version__ = '1.4'
__appID__ = 'CameraSurfaceArea.version_' + __version__

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from Components.UI.UI_mainWindow import *
from Components.UI.UI_openDialog import *
from Components.UI.UI_areaDialog import *
from Components.UI.UI_cameraMatrix import *
from Components.UI.UI_settingsDialog import *

from Components.py_preprocess import *
from Components.py_getContour import findContours
from Components.py_traceTheContour import *
from Components.py_getArea import *
from Components.py_cameraMatrix import *
from Components.py_lineFitting import contourFitting
import cv2
import numpy as np
import json

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__appID__)
print(__appID__)


# This dialog changes settings
class mySettingsDialog(QDialog):
    def __init__(self, parent=None):
        # Initialize the dialog
        self.parent = parent
        super().__init__()
        self.settingsDialogUI = Ui_settingsDialog()
        self.settingsDialogUI.setupUi(self)

        self.curveFittingState = self.parent._CurveFitting
        self.selectionModeState = self.parent._SelectionMode
        self.maxImgSizeState = self.parent._MaxImageSize

        # Set the current state
        if self.curveFittingState:
            self.settingsDialogUI.curveFittingBox.setChecked(True)
        else:
            self.settingsDialogUI.curveFittingBox.setChecked(False)

        if self.selectionModeState == 1:
            self.settingsDialogUI.atuoModeButton.setChecked(True)
        if self.selectionModeState == 2:
            self.settingsDialogUI.manualModeButton.setChecked(True)

        self.settingsDialogUI.maxSizeSlider.setValue(self.maxImgSizeState)
        self.settingsDialogUI.maxSizeSpinBox.setValue(self.maxImgSizeState)

        # Define state change events
        self.settingsDialogUI.curveFittingBox.stateChanged.connect(self.curveFittingClicked)
        self.settingsDialogUI.atuoModeButton.toggled.connect(self.modeButtonClicked)
        self.settingsDialogUI.manualModeButton.toggled.connect(self.modeButtonClicked)
        self.settingsDialogUI.maxSizeSlider.valueChanged.connect(self.maxSizeSliderChanged)
        self.settingsDialogUI.maxSizeSpinBox.valueChanged.connect(self.maxSizeSpinChanged)

    # Choose whether curve fitting will be performed
    def curveFittingClicked(self):
        if self.settingsDialogUI.curveFittingBox.isChecked():
            self.curveFittingState = True
            # print('Curve fitting')
        else:
            self.curveFittingState = False
            # print('No curve fitting')

    # Change area selection mode, 1 = Auto, 2 = Manual
    def modeButtonClicked(self):
        if self.settingsDialogUI.atuoModeButton.isChecked():
            self.selectionModeState = 1
            # print('Auto mode')

        if self.settingsDialogUI.manualModeButton.isChecked():
            self.selectionModeState = 2
            # print('Manual mode')

    # Change max image size set by slider bar
    def maxSizeSliderChanged(self):
        self.maxImgSizeState = self.settingsDialogUI.maxSizeSlider.value()
        self.settingsDialogUI.maxSizeSpinBox.setValue(self.maxImgSizeState)

    # Change max image size set by spin box
    def maxSizeSpinChanged(self):
        self.maxImgSizeState = self.settingsDialogUI.maxSizeSpinBox.value()
        self.settingsDialogUI.maxSizeSlider.setValue(self.maxImgSizeState)

    # Return the values and close the dialog
    def accept(self):
        self.parent._CurveFitting = self.curveFittingState
        self.parent._SelectionMode = self.selectionModeState
        self.parent._MaxImageSize = self.maxImgSizeState

        # Save the changes in the settings file
        settingsContent = json.dumps(dict(CurveFitting=self.curveFittingState,
                                          SelectionMode=self.selectionModeState,
                                          MaxImageSize=self.maxImgSizeState), indent=4)

        with open('settings.txt', 'w') as f:
            f.write(settingsContent)

        self.close()


# This dialog shows the final result
class myShowAreaDialog(QDialog):
    def __init__(self, Area):
        # Initialize the dialog
        super().__init__()
        self.showAreaDialogUI = Ui_areaDialog()
        self.showAreaDialogUI.setupUi(self)

        # Display the area with only 3 decimal points
        self.showAreaDialogUI.areaLineEdit.setText('{:.3f}'.format(Area))

        self.showAreaDialogUI.areaOKButton.clicked.connect(self.close)


# This dialog imports Camera Matrix and Photo
class myOpenFilesDialog(QDialog):
    def __init__(self, parent=None):
        # Initialize the dialog
        self.parent = parent
        super().__init__()
        self.openDialogUI = Ui_openDialog()
        self.openDialogUI.setupUi(self)
        self.cameraMatrixDir = None
        self.pictureDir = None
        self.calibrateCam = True

        self.openDialogUI.importCamMatrixButton.clicked.connect(self.importCameraMatrix)
        self.openDialogUI.importPhotoButton.clicked.connect(self.importTargetPicture)

        self.openDialogUI.checkBox.stateChanged.connect(self.checkCamCal)

    # Choose whether to calibrate camera or not
    def checkCamCal(self):
        if self.openDialogUI.checkBox.isChecked():
            self.openDialogUI.importCamMatrixButton.setEnabled(True)
            self.calibrateCam = True
        else:
            self.openDialogUI.importCamMatrixButton.setEnabled(False)
            self.calibrateCam = False

    # Display a dialog to import Camera Matrix
    def importCameraMatrix(self):
        # Accept '.p' files as camera matrix
        fname = QFileDialog.getOpenFileName(self, 'Import Camera Matrix', filter='P (*.P)\n All Formats (*.*)')

        if fname[0]:
            self.cameraMatrixDir = fname[0]
            self.openDialogUI.cameraMatrixDirLabel.setText(fname[0])

    # Display a dialog to import target picture
    def importTargetPicture(self):
        # Accept '.jpeg' & '.png' files
        fname = QFileDialog.getOpenFileName(self, 'Import picture', filter='JPEG (*.JPG; *.JPEG)\n PNG (*.PNG)\n All '
                                                                           'Formats (*.*)')

        if fname[0]:
            self.pictureDir = fname[0]
            self.openDialogUI.photoDirLabel.setText(fname[0])

    def accept(self):
        if self.calibrateCam:
            # Import both Camera Matrix and photo
            if self.cameraMatrixDir is None or self.pictureDir is None:
                QMessageBox.information(self, 'Incomplete import',
                                        'Please import both Camera Matrix and Photo',
                                        buttons=QMessageBox.Ok)
            # Store the directory of both files and return '10'
            else:
                self.parent._CamMatrixDir = self.cameraMatrixDir
                self.parent._PhotoDir = self.pictureDir
                self.done(10)
        else:
            # Import only photo
            if self.pictureDir is None:
                QMessageBox.information(self, 'Incomplete import',
                                        'Please import a photo',
                                        buttons=QMessageBox.Ok)
            # Store the directory and return '5'
            else:
                self.parent._PhotoDir = self.pictureDir
                self.done(5)


# This dialog creates the camera matrix
class myCreateCamMatrix(QDialog):
    def __init__(self):
        super().__init__()
        self.CreateCamMatrixUI = Ui_createCamMatrixDialog()
        self.CreateCamMatrixUI.setupUi(self)

        # Define key elements
        self._PhotosDir = ([], '')
        self._CameraModel = None

        # Define buttons
        self.CreateCamMatrixUI.camMatImportButton.clicked.connect(self.importCamMatPics)
        self.CreateCamMatrixUI.createCamMatButton.clicked.connect(self.startCreatingMatrix)
        self.CreateCamMatrixUI.camMatCloseButton.clicked.connect(self.close)

    def importCamMatPics(self):
        self._PhotosDir = QFileDialog.getOpenFileNames(self, 'Import photos',
                                                       filter='JPEG (*.JPG; *.JPEG)\nPNG (*.PNG)\nAll Formats (*.*)')
        if self._PhotosDir[1] is not '':
            temp = ''
            for picDirs in self._PhotosDir[0]:
                temp += picDirs.split('/')[-2] + '/' + picDirs.split('/')[-1] + '\n'
            self.CreateCamMatrixUI.camMatPicDirLabel.setText(temp)

    def startCreatingMatrix(self):
        if self._PhotosDir[1] == '' or self.CreateCamMatrixUI.camMatModelLineEdit.text() == '':
            QMessageBox.information(self, 'Incomplete information',
                                    'Please import at least 10 photos and enter the camera model!',
                                    buttons=QMessageBox.Ok)
        else:
            self._CameraModel = self.CreateCamMatrixUI.camMatModelLineEdit.text()
            self.CreateCamMatrixUI.createCamMatButton.setText('Creating...')
            self.CreateCamMatrixUI.createCamMatButton.setEnabled(False)
            cv2.waitKey(1)
            try:
                calibrate_camera(self._PhotosDir[0], self._CameraModel)
                location = self._PhotosDir[0][0][
                           :-len(self._PhotosDir[0][0].split('/')[-1])] + self._CameraModel + '_Matrix.p '
                self.CreateCamMatrixUI.createCamMatButton.setText('Create')
                self.CreateCamMatrixUI.createCamMatButton.setEnabled(True)
                QMessageBox.information(self, 'Completed',
                                        'Camera matrix created at: ' + location,
                                        buttons=QMessageBox.Ok)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error creating camera matrix',
                                    'Error when creating camera matrix.\nTry again with different photos.',
                                    buttons=QMessageBox.Ok)


# This is the graphic scene for drawing contour
class myPainting(QGraphicsScene):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()

        self.drawingFlag = False
        self.lineStart = None
        self.myLine = None

    # Override the mousePressEvent
    def mousePressEvent(self, event):
        # print(event.scenePos())
        if event.button() & Qt.LeftButton:
            if self.parent._ContourRedraw is None:
                self.parent._ContourRedraw = np.array([(int(event.scenePos().y()),
                                                        int(event.scenePos().x()))], dtype=np.uint32)
            else:
                self.parent._ContourRedraw = np.vstack((self.parent._ContourRedraw, (0, 0)))
                self.parent._ContourRedraw = np.vstack((self.parent._ContourRedraw,
                                                        [int(event.scenePos().y()),
                                                         int(event.scenePos().x())]))
            self.drawingFlag = True
            self.lineStart = event.scenePos()
            self.myLine = QGraphicsLineItem(QtCore.QLineF(self.lineStart, event.scenePos()))

    # Override the mouseMoveEvent
    def mouseMoveEvent(self, event):
        if self.drawingFlag:
            try:
                self.removeItem(self.myLine)
            finally:
                self.myLine = QGraphicsLineItem(QtCore.QLineF(self.lineStart, event.scenePos()))
                self.myLine.setPen(QPen(Qt.red, 1))
                self.addItem(self.myLine)

    # Override the mouseReleaseEvent
    def mouseReleaseEvent(self, event):
        # print(event.scenePos())
        self.drawingFlag = False
        self.parent._ContourRedraw = np.vstack(
            (self.parent._ContourRedraw, [int(event.scenePos().y()), int(event.scenePos().x())]))


# This is the graphic scene for area selection
class mySelection(QGraphicsScene):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()

        # Define variables
        self.rectStart = None
        self.myRect = None
        self.lineStart = None
        self.myLine = None
        self.lineLocations = None
        self.lineType = None
        self.grabCutMask = None
        self.grabCutTemp = None
        self.grabCutOutput = None
        self.bgdmodel = np.zeros((1, 65), np.float64)
        self.fgdmodel = np.zeros((1, 65), np.float64)
        self.drawingRatio = None

        # setting up flags
        self.rect = (0, 0, 1, 1)
        self.drawing = False
        self.rectangle = False

    # Override the mousePressEvent
    def mousePressEvent(self, event):
        # Draw the rectangle
        if self.myRect is None:
            if event.button() & Qt.LeftButton:
                self.rectangle = True
                self.rectStart = event.scenePos()

        # Draw touch-up lines
        else:
            if event.button() & Qt.LeftButton:
                # Draw foreground
                self.lineType = 1
            if event.button() & Qt.RightButton:
                # Draw background
                self.lineType = 0

            # Start line drawing
            self.drawing = True
            self.lineStart = event.scenePos()
            self.lineLocations = np.array([(int(self.lineStart.x()), int(self.lineStart.y()))], dtype=np.uint32)

    # Override the mouseMoveEvent
    def mouseMoveEvent(self, event):
        # Draw the rectangle
        if self.rectangle:
            try:
                self.removeItem(self.myRect)
            finally:
                self.myRect = QGraphicsRectItem(QtCore.QRectF(self.rectStart, event.scenePos()))
                self.myRect.setPen(QPen(Qt.blue, 1))
                self.addItem(self.myRect)

        # Draw touch-up lines
        else:
            if self.drawing:
                self.myLine = self.myLine = QGraphicsLineItem(QtCore.QLineF(self.lineStart, event.scenePos()))
                self.lineStart = event.scenePos()
                self.lineLocations = np.vstack((self.lineLocations,
                                                (int(event.scenePos().x()), int(event.scenePos().y()))))

                # Foreground lines
                if self.lineType == 1:
                    self.myLine.setPen(QPen(Qt.white, 5))
                # Background lines
                if self.lineType == 0:
                    self.myLine.setPen(QPen(Qt.black, 5))

                self.addItem(self.myLine)

    # Override the mouseReleaseEvent
    def mouseReleaseEvent(self, event):
        # Store the rectangle and perform first grab cut
        if self.rectangle:
            self.rectangle = False
            self.drawingRatio = self.parent._DrawingRatio
            ix, iy = int(self.rectStart.x() * self.drawingRatio), int(self.rectStart.y() * self.drawingRatio)
            x, y = int(event.scenePos().x() * self.drawingRatio), int(event.scenePos().y() * self.drawingRatio)

            self.rect = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))
            print('Grab Cut rectangle:', self.rect)

            # Create a black mask
            mainSize = self.parent._MainImage.shape[:2]
            self.grabCutMask = np.zeros(mainSize, dtype=np.uint8)

            # Copy the original image
            self.grabCutTemp = self.parent._MainImage.copy()

            # Grab cut
            self.parent.MainUI.statusbar.showMessage('Processing...')
            self.parent.MainUI.progressBar.setValue(30)
            cv2.waitKey(1)
            cv2.grabCut(self.grabCutTemp, self.grabCutMask, self.rect, self.bgdmodel, self.fgdmodel, 1,
                        cv2.GC_INIT_WITH_RECT)
            self.parent.MainUI.progressBar.setValue(80)
            cv2.waitKey(1)

            # Apply the mask on the image
            mask2 = np.where((self.grabCutMask == 1) + (self.grabCutMask == 3), 255, 0).astype('uint8')
            self.parent._GrabCutResult = mask2
            self.grabCutOutput = cv2.bitwise_and(self.grabCutTemp, self.grabCutTemp, mask=mask2)
            self.grabCutOutput = cv2.rectangle(self.grabCutOutput, (self.rect[0], self.rect[1]),
                                               (self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]),
                                               (255, 0, 0), int(self.drawingRatio))

            # Store the image for displaying
            self.grabCutOutput = cv2.addWeighted(self.grabCutTemp, 0.3, self.grabCutOutput, 0.8, 0)
            cv2.imwrite('grabCutOutput.jpg', self.grabCutOutput)
            self.parent.MainUI.progressBar.setValue(90)
            cv2.waitKey(1)

            # Display background image
            self.clear()
            w, h = self.parent.MainUI.graphicsView.width(), self.parent.MainUI.graphicsView.height()
            grabCutTemp = QtGui.QPixmap('grabCutOutput.jpg').scaled(w, h, Qt.KeepAspectRatio)
            self.addItem(QGraphicsPixmapItem(grabCutTemp))

            # Enable button
            self.parent.MainUI.redrawButton.setText('Next')
            self.parent.MainUI.redrawButton.setEnabled(True)

            # Display message
            self.parent.MainUI.statusbar.showMessage('Left mouse button to mark foreground, right mouse button to '
                                                     'mark background, press \'Next\' to continue')
            self.parent.MainUI.progressBar.setValue(100)

        # Draw touch-up lines and perform grab cut
        else:
            if self.drawing:
                self.drawing = False

                # Disable button
                self.parent.MainUI.redrawButton.setEnabled(False)

                # Draw the lines to the mask
                temp = self.lineLocations[0]
                for i in self.lineLocations[1:]:
                    cv2.line(self.grabCutMask, (int(temp[0] * self.drawingRatio), int(temp[1] * self.drawingRatio)),
                             (int(i[0] * self.drawingRatio), int(i[1] * self.drawingRatio)),
                             self.lineType, int(5 * self.drawingRatio))
                    temp = i

                # Grab cut
                self.parent.MainUI.statusbar.showMessage('Processing...')
                self.parent.MainUI.progressBar.setValue(30)
                cv2.waitKey(1)
                cv2.waitKey(1)
                cv2.grabCut(self.grabCutTemp, self.grabCutMask, self.rect, self.bgdmodel, self.fgdmodel, 1,
                            cv2.GC_INIT_WITH_MASK)

                self.parent.MainUI.progressBar.setValue(80)
                cv2.waitKey(1)

                # Apply the mask on the image
                mask2 = np.where((self.grabCutMask == 1) + (self.grabCutMask == 3), 255, 0).astype('uint8')
                self.parent._GrabCutResult = mask2
                self.grabCutOutput = cv2.bitwise_and(self.grabCutTemp, self.grabCutTemp, mask=mask2)
                self.grabCutOutput = cv2.rectangle(self.grabCutOutput, (self.rect[0], self.rect[1]),
                                                   (self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]),
                                                   (255, 0, 0), int(self.drawingRatio))

                # Store the image for displaying
                self.grabCutOutput = cv2.addWeighted(self.grabCutTemp, 0.3, self.grabCutOutput, 0.8, 0)
                cv2.imwrite('grabCutOutput.jpg', self.grabCutOutput)
                self.parent.MainUI.progressBar.setValue(90)
                cv2.waitKey(1)

                # Display background image
                self.clear()
                w, h = self.parent.MainUI.graphicsView.width(), self.parent.MainUI.graphicsView.height()
                grabCutTemp = QtGui.QPixmap('grabCutOutput.jpg').scaled(w, h, Qt.KeepAspectRatio)
                self.addItem(QGraphicsPixmapItem(grabCutTemp))

                # Enable button
                self.parent.MainUI.redrawButton.setEnabled(True)

                # Display message
                self.parent.MainUI.statusbar.showMessage('Left mouse button to mark foreground, right mouse button to '
                                                         'mark background, press \'Next\' to continue')
                self.parent.MainUI.progressBar.setValue(100)


# This is the main window of the program
class myWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.MainUI = Ui_MainWindow()
        self.MainUI.setupUi(self)

        # Define files dir and key elements
        self._CamMatrixDir = None
        self._PhotoDir = None
        self._CurrentFileDir = None
        self._MainImageDir = None
        self._ImageWithContourDir = None

        self._MainImage = None
        self._ChessBoardCorners = None
        self._ChessboardDirection = None
        self._MainContour = None
        self._GrabCutResult = None

        self._DrawingContour = False
        self._ContourRedraw = None
        self._DrawingRatio = 1
        self._ManualSelectionDone = False

        self._CurveFitting = False
        self._SelectionMode = 2
        self._MaxImageSize = 3000
        # End defining

        # Load settings file
        self.loadSettings()

        # Load help document
        try:
            with open('help.txt') as f:
                helpDoc = f.read()
        except Exception as e:
            print('Error:', e)
            helpDoc = ''

        # Define Menu items
        self.MainUI.actionOpen.triggered.connect(self.openFiles)
        self.MainUI.actionCreateCamMatrix.triggered.connect(self.createNewCamMatrix)
        self.MainUI.actionSettings.triggered.connect(self.changeSettings)
        self.MainUI.actionExit.triggered.connect(self.closeButton)
        self.MainUI.actionHowToUse.triggered.connect(
            lambda: QMessageBox.information(self, 'How to use', helpDoc, buttons=QMessageBox.Ok))

        self.MainUI.actionAbout.triggered.connect(
            lambda: QMessageBox.information(self, 'About',
                                            'This app measures the area of a flat surface in a photograph\n'
                                            'Created by: qifwa493', buttons=QMessageBox.Ok))

        # Define Buttons
        self.MainUI.cancelButton.clicked.connect(self.cancelImage)
        self.MainUI.redrawButton.clicked.connect(self.redrawContour)
        self.MainUI.calculateButton.clicked.connect(self.calculateArea)

        #
        # Define GraphicsView
        self.paintingScene = myPainting(self)
        self.selectionScene = mySelection(self)
        self.scene = QGraphicsScene()
        self.MainUI.graphicsView.setScene(self.scene)

        self.MainUI.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.MainUI.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Ready and show main window
        self.MainUI.statusbar.showMessage('Ready')
        self.show()
        self.center()

    # Open files and start processing, this is the main function of the program
    def openFiles(self):
        # Clear the previous data and reset the program
        self.cancelImage()

        # Open files import dialog
        self.openFilesDialog = myOpenFilesDialog(self)

        openFilesResult = self.openFilesDialog.exec_()
        # If at least one file is imported, start process the image
        if openFilesResult == 10 or openFilesResult == 5:
            # Display image
            w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
            image = QtGui.QPixmap(self._PhotoDir).scaled(w, h, Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(image)
            self.scene.clear()
            self.scene.addItem(item)
            self.MainUI.cancelButton.setEnabled(True)
            cv2.waitKey(1)

            #
            # Pre-process the image and display it
            self.MainUI.statusbar.showMessage('Processing...')
            cv2.waitKey(1)
            self._MainImage = cv2.imread(self._PhotoDir)

            #
            # Undistort the image if a camera matrix is imported
            if openFilesResult == 10:
                try:
                    self.MainUI.statusbar.showMessage('Un-distorting...')
                    cv2.waitKey(1)
                    self._MainImage = undistortImage(self._MainImage, self._CamMatrixDir)
                    self.MainUI.progressBar.setValue(10)
                    print('Undistort completed')
                except Exception as e:
                    print('Error:', e)
                    QMessageBox.warning(self, 'Error undistort image', 'Error when undistort the image.\nImport '
                                                                       'correct Camera Matrix.',
                                        buttons=QMessageBox.Ok)
                    self.MainUI.statusbar.showMessage('Ready')
                    self.MainUI.progressBar.setValue(0)
                    return

            #
            # Perspective transform
            try:
                self.MainUI.statusbar.showMessage('Perspective transforming...')
                cv2.waitKey(1)
                # Find the chessboard corners
                showImg('main', self._MainImage, 1280)
                cv2.waitKey(0)
                cv2.destroyWindow('main')
                corners = findChessboardInImage(self._MainImage, Width=6, Height=9)

                if len(corners) == 0:
                    raise ValueError('No corner found!')

                # Get the points for perspective transform
                oldChessBoardCorners = getChessboardCorners(corners)
                # Find the orientation of the chessboard
                Dx = oldChessBoardCorners[1][0] - oldChessBoardCorners[0][0]
                Dy = oldChessBoardCorners[1][1] - oldChessBoardCorners[0][1]
                if Dx == 0:
                    self._ChessboardDirection = 100
                else:
                    self._ChessboardDirection = abs(Dy / Dx)
                backgroundSize = (15000, 15000)
                if self._ChessboardDirection < 1:
                    self._ChessBoardCorners = getNewPoints(Width=6, Height=9, Size=backgroundSize, Direction=1)
                else:
                    self._ChessBoardCorners = getNewPoints(Width=6, Height=9, Size=backgroundSize, Direction=2)

                # Transform, crop black border and save the image
                self._MainImage = cropImgPerspectively(self._MainImage, oldChessBoardCorners, self._ChessBoardCorners,
                                                       Size=backgroundSize)
                # showImg('after transform', self._MainImage, 800)
                # cv2.waitKey(0)
                # cv2.destroyWindow('after transform')
                self._MainImage = cropBlackBorder(self._MainImage)
                self._MainImage = reduceImgSize(self._MainImage, self._MaxImageSize)
                showImg('after cropBlackBorder', self._MainImage, 800)
                cv2.waitKey(0)
                cv2.destroyWindow('after cropBlackBorder')
                self._MainImageDir = self._PhotoDir.split('/')[-1].split('.')[0] + '_after.jpg'
                cv2.imwrite(self._MainImageDir, self._MainImage)
                self._CurrentFileDir = self._MainImageDir
                self.MainUI.progressBar.setValue(25)
                print('Perspective transform completed')

                # Display image
                w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
                image = QtGui.QPixmap(self._CurrentFileDir).scaled(w, h, Qt.KeepAspectRatio)
                item = QGraphicsPixmapItem(image)
                self.scene.clear()
                self.scene.addItem(item)
                self.MainUI.graphicsView.setScene(self.scene)
                cv2.waitKey(1)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error finding chessboard', 'Error when finding chessboard the '
                                                                      'image.\nImport image contains a chessboard.',
                                    buttons=QMessageBox.Ok)
                self.MainUI.statusbar.showMessage('Ready')
                self.MainUI.progressBar.setValue(0)
                return

            if self._SelectionMode == 1:
                # Perform post processing
                self.postProcessing()

            if self._SelectionMode == 2:
                # Perform manual area selection
                self.MainUI.progressBar.setValue(100)
                self.MainUI.statusbar.showMessage('Select the target area by drawing a rectangle')
                self.manualSelect()

        elif openFilesResult == 0:
            return
        else:
            print(openFilesResult)
            QMessageBox.warning(self, 'Error importing', 'Error when importing camera matrix or photo.\nTry to import '
                                                         'again.',
                                buttons=QMessageBox.Ok)

    def postProcessing(self):
        # Set button
        self.MainUI.redrawButton.setEnabled(False)
        self.MainUI.redrawButton.setText('Re-draw')

        #
        # Trace the possible contour
        try:
            self.MainUI.statusbar.showMessage('Finding contour...')
            cv2.waitKey(1)

            # Manual Section mode
            if self._SelectionMode == 2:
                # Find edges and filter our 1 possible contour
                imageWithEdges, possibleContour = findContours(self._MainImage, GrabCutMask=self._GrabCutResult,
                                                               Hull=False, MinArcLength=1000, Background=False,
                                                               ChessboardDirection=self._ChessboardDirection)

            # Auto selection mode
            else:
                # Find edges and filter our 1 possible contour
                imageWithEdges, possibleContour = findContours(self._MainImage, Hull=False, MinArcLength=1000,
                                                               Background=False,
                                                               ChessboardDirection=self._ChessboardDirection)

            self.MainUI.progressBar.setValue(50)

            showImg('imageWithEdge', imageWithEdges, 800)
            cv2.waitKey(0)

            closedLoop = False
            size = imageWithEdges.shape[:2]
            try:
                # Trace the possible contour
                self.MainUI.statusbar.showMessage('Tracing contour...')
                cv2.waitKey(1)
                imageWithEdges = cv2.cvtColor(imageWithEdges, cv2.COLOR_BGR2GRAY)
                ret, imageWithEdges = cv2.threshold(imageWithEdges, 50, 255, cv2.THRESH_BINARY)
                startingPoint = (possibleContour[0][0][1], possibleContour[0][0][0])
                showImg('imageWithEdge', imageWithEdges, 800)
                cv2.waitKey(0)
                self._MainContour, closedLoop = traceTheContour(imageWithEdges, startingPoint)
                self.MainUI.progressBar.setValue(75)
                print('Contour length after tracing:', len(self._MainContour))

                if self._CurveFitting:
                    try:
                        # Perform curve fitting
                        self._MainContour = contourFitting(self._MainContour, size, Order=5)
                        print('Contour length after fitting: ', len(self._MainContour))
                        # End curve fitting
                    except Exception as e:
                        print('Error:', e)
                        print('Failed to fit the contour, original contour will be used.')

            except Exception as e:
                print('Error:', e)
                print('Failed to trace the contour, raw data will be used.')
                self._MainContour = np.hstack((possibleContour[:, :, 1], possibleContour[:, :, 0]))

            # Draw the contour over the image
            self.MainUI.statusbar.showMessage('Drawing contour...')
            cv2.waitKey(1)
            imageWithContour = drawTheContour(size, self._MainContour.astype(int), LineThickness=3,
                                              Background=self._MainImage, CloseLoop=closedLoop)

            # Save the image
            self._ImageWithContourDir = self._MainImageDir.split('/')[-1].split('.')[0] + '_withContour.jpg'
            cv2.imwrite(self._ImageWithContourDir, imageWithContour)
            self._CurrentFileDir = self._ImageWithContourDir

            # Enable 'Calculate' button
            self.MainUI.calculateButton.setEnabled(True)
        except Exception as e:
            print('Error:', e)
            QMessageBox.warning(self, 'Error finding contour', 'Error when finding contour in the '
                                                               'image.\nTry drawing the contour manually.',
                                buttons=QMessageBox.Ok)
            self.MainUI.redrawButton.setEnabled(True)
            self.MainUI.statusbar.showMessage('Ready')
            self.MainUI.progressBar.setValue(100)

        #
        # Display image
        w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
        image = QtGui.QPixmap(self._CurrentFileDir).scaled(w, h, Qt.KeepAspectRatio)
        item = QGraphicsPixmapItem(image)
        self.scene.clear()
        self.MainUI.graphicsView.setScene(self.scene)
        self.scene.addItem(item)

        self.MainUI.progressBar.setValue(100)

        # Enable buttons
        self.MainUI.cancelButton.setEnabled(True)
        self.MainUI.redrawButton.setEnabled(True)
        self.MainUI.statusbar.showMessage('Ready')
        cv2.waitKey(1)

    def loadSettings(self):
        try:
            # If setting file exist and can be loaded
            with open('settings.txt') as f:
                settingsContent = json.loads(f.read())
                self._CurveFitting = settingsContent['CurveFitting']
                self._SelectionMode = settingsContent['SelectionMode']
                self._MaxImageSize = settingsContent['MaxImageSize']
            print('Settings loaded')

        except Exception as e:
            # If setting file can not be loaded
            print('Error loading settings:', e)
            print('Default settings will be used')

            settingsContent = json.dumps(dict(CurveFitting=self._CurveFitting,
                                              SelectionMode=self._SelectionMode,
                                              MaxImageSize=self._MaxImageSize), indent=4)
            # Create a new settings file
            with open('settings.txt', 'w') as f:
                f.write(settingsContent)

    def changeSettings(self):
        # Open settings dialog
        self.settingsDialog = mySettingsDialog(self)
        self.settingsDialog.exec_()

    def createNewCamMatrix(self):
        # Open create camera matrix dialog
        self.createCamMatrix = myCreateCamMatrix()
        self.createCamMatrix.exec_()

    def cancelImage(self):
        # Reset everything
        self.removeWorkingFiles()
        cv2.destroyAllWindows()

        self._CamMatrixDir = None
        self._PhotoDir = None
        self._CurrentFileDir = None
        self._MainImageDir = None
        self._ImageWithContourDir = None

        self._MainImage = None
        self._ChessBoardCorners = None
        self._ChessboardDirection = None
        self._MainContour = None

        self._DrawingContour = False
        self._ContourRedraw = None
        self._DrawingRatio = 1
        self._ManualSelectionDone = False

        self.MainUI.graphicsView.setCursor(Qt.ArrowCursor)
        self.paintingScene.clear()
        self.paintingScene.__init__(self)
        self.selectionScene.clear()
        self.selectionScene.__init__(self)
        self.scene.clear()
        self.MainUI.graphicsView.setScene(self.scene)
        self.MainUI.progressBar.setValue(0)
        self.MainUI.statusbar.showMessage('Ready')
        self.MainUI.cancelButton.setEnabled(False)
        self.MainUI.redrawButton.setEnabled(False)
        self.MainUI.redrawButton.setText('Re-draw')
        self.MainUI.calculateButton.setEnabled(False)

    def manualSelect(self):
        # Select the area manually
        try:
            # Initialize the graphicView
            self.selectionScene.clear()
            self.MainUI.graphicsView.setCursor(Qt.CrossCursor)
            self.MainUI.graphicsView.setScene(self.selectionScene)

            # Get the size of the graphicView and display background image
            w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
            drawingBackground = QtGui.QPixmap(self._MainImageDir).scaled(w, h, Qt.KeepAspectRatio)

            # Calculate the drawing ratio
            if w / h > self._MainImage.shape[1] / self._MainImage.shape[0]:
                self._DrawingRatio = self._MainImage.shape[0] / h
            else:
                self._DrawingRatio = self._MainImage.shape[1] / w

            self.selectionScene.addItem(QGraphicsPixmapItem(drawingBackground))

        except Exception as e:
            print('Error:', e)
            QMessageBox.warning(self, 'Error selecting area', 'Error when selecting area.',
                                buttons=QMessageBox.Ok)
            self.MainUI.graphicsView.setCursor(Qt.ArrowCursor)
            self.MainUI.graphicsView.setScene(self.scene)

    def redrawContour(self):
        if self._SelectionMode == 1 or (self._SelectionMode == 2 and self._ManualSelectionDone):
            # Re-draw the contour manually
            try:
                # Initialize the graphicView
                self.MainUI.calculateButton.setEnabled(True)
                self._ContourRedraw = None
                self._DrawingContour = True
                self.paintingScene.clear()
                self.MainUI.graphicsView.setCursor(Qt.CrossCursor)
                self.MainUI.graphicsView.setScene(self.paintingScene)

                # Get the size of the graphicView
                w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
                drawingBackground = QtGui.QPixmap(self._MainImageDir).scaled(w, h, Qt.KeepAspectRatio)

                self.paintingScene.addItem(QGraphicsPixmapItem(drawingBackground))

            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error re-draw the contour', 'Error when re-drawing the contour in the image',
                                    buttons=QMessageBox.Ok)
                self._DrawingContour = False
                self.MainUI.graphicsView.setCursor(Qt.ArrowCursor)
                self.MainUI.graphicsView.setScene(self.scene)

        # If under manual mode, after area selection, start post processing
        if self._SelectionMode == 2 and not self._ManualSelectionDone:
            showImg('grabCutResult', self._GrabCutResult, 1280)
            cv2.waitKey(0)

            self._ManualSelectionDone = True
            self.MainUI.redrawButton.setText('Redraw')
            self.MainUI.redrawButton.setEnabled(False)
            self.postProcessing()

    # This function calculates the area inside the contour
    def calculateArea(self):
        self._DrawingRatio = 1
        try:
            # If a manually draw contour exist
            if self._DrawingContour:
                self._DrawingContour = False
                w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
                # Create a black background
                black = np.zeros([h, w, 3], dtype=np.uint8)
                # Draw the contours to a black background
                for i in range(len(self._ContourRedraw) - 1):
                    pointA = self._ContourRedraw[i]
                    pointB = self._ContourRedraw[i + 1]
                    if pointA[0] + pointA[1] == 0 or pointB[0] + pointB[1] == 0:
                        continue
                    cv2.line(black, (pointA[1], pointA[0]), (pointB[1], pointB[0]), (255, 255, 255), 1)

                # Trace the contour
                self.MainUI.statusbar.showMessage('Tracing contour...')
                self.MainUI.progressBar.setValue(10)
                cv2.waitKey(1)
                black = cv2.cvtColor(black, cv2.COLOR_BGR2GRAY)
                ret, black = cv2.threshold(black, 127, 255, cv2.THRESH_BINARY)
                startingPoint = (self._ContourRedraw[0][0], self._ContourRedraw[0][1])
                self._ContourRedraw, closedLoop = traceTheContour(black, startingPoint)

                # Calculate the drawing ratio
                if self.MainUI.graphicsView.width() / self.MainUI.graphicsView.height() > self._MainImage.shape[1] / \
                        self._MainImage.shape[0]:
                    self._DrawingRatio = self._MainImage.shape[0] / self.MainUI.graphicsView.height()
                else:
                    self._DrawingRatio = self._MainImage.shape[1] / self.MainUI.graphicsView.width()
                # print(self._MainImage.shape[1])
                # print(self.MainUI.graphicsView.height())
                # print(self._DrawingRatio)
                self.MainUI.progressBar.setValue(50)
                cv2.waitKey(1)

            # Calculate area
            self.MainUI.statusbar.showMessage('Calculating...')
            cv2.waitKey(1)

            if self._ContourRedraw is None:
                contourPixelArea = sumArea(self._MainContour)
            else:
                contourPixelArea = sumArea(self._ContourRedraw)

            print('Pixels (Before):', contourPixelArea)
            contourPixelArea *= pow(self._DrawingRatio, 2)
            print('Pixels (After):', contourPixelArea)
            self.MainUI.progressBar.setValue(80)
            chessboardPixelArea = getChessboardPixelArea(self._MainImage)
            chessboardActualArea = 25 * 25 * 8 * 5
            ObjectArea = chessboardActualArea * (contourPixelArea / chessboardPixelArea)
            ObjectArea *= pow(10, -6)
            print('Area:', ObjectArea)
            print('')
            self.MainUI.progressBar.setValue(100)
            self.MainUI.statusbar.showMessage('Ready')
            # Display area
            self.showAreaDialog = myShowAreaDialog(ObjectArea)
            self.showAreaDialog.exec_()
        except Exception as e:
            print('Error:', e)
            QMessageBox.warning(self, 'Error calculating area', 'Error when calculating are image.\nRe-draw the '
                                                                'contour and try again.',
                                buttons=QMessageBox.Ok)

            self._DrawingContour = False
            self.MainUI.graphicsView.setCursor(Qt.ArrowCursor)
            self.paintingScene.clear()
            self._ContourRedraw = None
            self._DrawingRatio = 1
            self.MainUI.graphicsView.setScene(self.scene)
            self.MainUI.statusbar.showMessage('Ready')
            self.MainUI.progressBar.setValue(100)

    def closeButton(self):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.removeWorkingFiles()
            QApplication.instance().quit()

    def removeWorkingFiles(self):
        # Remove working files
        if self._MainImageDir is not None:
            try:
                print('Removing:', self._MainImageDir)
                os.remove(self._MainImageDir)
            except Exception as e:
                print(e)

        if self._ImageWithContourDir is not None:
            try:
                print('Removing:', self._ImageWithContourDir)
                os.remove(self._ImageWithContourDir)
            except Exception as e:
                print(e)

        if os.path.isfile('grabCutOutput.jpg'):
            try:
                print('Removing: grabCutOutput.jpg')
                os.remove('grabCutOutput.jpg')
            except Exception as e:
                print(e)

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.removeWorkingFiles()
            cv2.destroyAllWindows()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        # If Esc is pressed
        if e.key() == Qt.Key_Escape:
            self.close()

    def center(self):
        # Move the main window to the center of the screen upon starting
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # Resize the picture when the main window is resized
        if self._CurrentFileDir is not None and not self._DrawingContour:
            self.scene.clear()
            w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
            image = QtGui.QPixmap(self._CurrentFileDir).scaled(w, h, Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(image)
            self.scene.addItem(item)


sys._excepthook = sys.excepthook


# Display error message when Qt crashes
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

if __name__ == '__main__':
    # Enable High DPI scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = myWindow()

    # Start the main process
    sys.exit(app.exec_())
