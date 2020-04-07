# -*- coding: utf-8 -*-

__version__ = '1.0'

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from Components.UI.UI_mainWindow import *
from Components.UI.UI_openDialog import *
from Components.UI.UI_areaDialog import *
from Components.UI.UI_cameraMatrix import *

from Components.py_preprocess import *
from Components.py_getContour import findContours
from Components.py_traceTheContour import *
from Components.py_getArea import *
from Components.py_cameraMatrix import *
import cv2


# This dialog shows the final result
class myShowAreaDialog(QDialog):
    def __init__(self, Area):
        super().__init__()
        self.showAreaDialogUI = Ui_areaDialog()
        self.showAreaDialogUI.setupUi(self)

        self.showAreaDialogUI.areaLineEdit.setText('{:.3f}'.format(Area))

        self.showAreaDialogUI.areaOKButton.clicked.connect(self.close)


# This dialog imports Camera Matrix and Photo
class myOpenFilesDialog(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()
        self.openDialogUI = Ui_openDialog()
        self.openDialogUI.setupUi(self)
        self.cameraMatrixDir = None
        self.pictureDir = None

        self.openDialogUI.importCamMatrixButton.clicked.connect(self.importCameraMatrix)
        self.openDialogUI.importPhotoButton.clicked.connect(self.importTargetPicture)

    def importCameraMatrix(self):
        fname = QFileDialog.getOpenFileName(self, 'Import Camera Matrix', filter='P (*.P)\n All Formats (*.*)')

        if fname[0]:
            self.cameraMatrixDir = fname[0]
            self.openDialogUI.cameraMatrixDirLabel.setText(fname[0])

    def importTargetPicture(self):
        fname = QFileDialog.getOpenFileName(self, 'Import picture', filter='JPEG (*.JPG; *.JPEG)\n PNG (*.PNG)\n All '
                                                                           'Formats (*.*)')

        if fname[0]:
            self.pictureDir = fname[0]
            self.openDialogUI.photoDirLabel.setText(fname[0])

    def accept(self):
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
                location = self._PhotosDir[0][0][:-len(self._PhotosDir[0][0].split('/')[-1])] + self._CameraModel + '_Matrix.p '
                self.CreateCamMatrixUI.createCamMatButton.setText('Create')
                self.CreateCamMatrixUI.createCamMatButton.setEnabled(True)
                QMessageBox.information(self, 'Completed',
                                        'Camera matrix created at: ' + location,
                                        buttons=QMessageBox.Ok)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error creating camera matrix',
                                    'Error when creating camera matrix.\nTry agina with different photos.',
                                    buttons=QMessageBox.Ok)


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
        self._MainContour = None


        # Define Menu items
        self.MainUI.actionOpen.triggered.connect(self.openFiles)
        self.MainUI.actionCreateCamMatrix.triggered.connect(self.createNewCamMatrix)
        self.MainUI.actionExit.triggered.connect(self.closeButton)
        self.MainUI.actionHowToUse.triggered.connect(lambda: QMessageBox.information(self, 'How to use',
                                                                                     'Coming soon',
                                                                                     buttons=QMessageBox.Ok))
        self.MainUI.actionAbout.triggered.connect(
            lambda: QMessageBox.information(self, 'About',
                                            'This app measures the area of a flat surface in a photograph\n'
                                            'Created by: qifwa493', buttons=QMessageBox.Ok))

        # Define Buttons
        self.MainUI.cancelButton.clicked.connect(self.cancelImage)
        self.MainUI.redrawButton.clicked.connect(lambda: QMessageBox.information(self, 'How to use',
                                                                                 'Coming soon',
                                                                                 buttons=QMessageBox.Ok))
        self.MainUI.calculateButton.clicked.connect(self.calculateArea)

        # Define GraphicsView
        self.scene = QGraphicsScene()
        self.MainUI.graphicsView.setScene(self.scene)
        self.MainUI.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.MainUI.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Ready and show main window
        self.MainUI.statusbar.showMessage('Ready')
        self.show()
        self.center()

    def openFiles(self):
        # Open files import dialog
        self.openFilesDialog = myOpenFilesDialog(self)

        # If both files are imported, start process the image
        if self.openFilesDialog.exec_() == 10:
            #
            # Pre-process the image and display it
            self.MainUI.statusbar.showMessage('Processing...')
            cv2.waitKey(1)
            self._MainImage = cv2.imread(self._PhotoDir)

            #
            # Undistort the image
            try:
                self.MainUI.statusbar.showMessage('Un-distorting...')
                cv2.waitKey(1)
                self._MainImage = undistortImage(self._MainImage, self._CamMatrixDir)
                self.MainUI.progressBar.setValue(10)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error undistort image', 'Error when undistort the image.\nImport correct '
                                                                   'Camera Matrix.', buttons=QMessageBox.Ok)
                self.MainUI.statusbar.showMessage('Ready')
                self.MainUI.progressBar.setValue(0)
                return

            #
            # Perspective transform
            try:
                self.MainUI.statusbar.showMessage('Perspective transforming...')
                cv2.waitKey(1)
                # Find the chessboard corners
                corners = findChessboardInImage(self._MainImage, Width=6, Height=9)

                if len(corners) == 0:
                    raise ValueError('No corner found!')

                # Get the points for perspective transform
                oldChessBoardCorners = getChessboardCorners(corners)
                self._ChessBoardCorners = getNewPoints(Width=6, Height=9, Size=(8000, 8000))

                # Transform and save the image
                self._MainImage = cropImgPerspectively(self._MainImage, oldChessBoardCorners, self._ChessBoardCorners)
                self._MainImageDir = self._PhotoDir.split('/')[-1].split('.')[0] + '_after.jpg'
                cv2.imwrite(self._MainImageDir, self._MainImage)
                self._CurrentFileDir = self._MainImageDir
                self.MainUI.progressBar.setValue(25)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error finding chessboard', 'Error when finding chessboard the '
                                                                      'image.\nImport image contains a chessboard.',
                                    buttons=QMessageBox.Ok)
                self.MainUI.statusbar.showMessage('Ready')
                self.MainUI.progressBar.setValue(0)
                return

            #
            # Trace the possible contour
            try:
                self.MainUI.statusbar.showMessage('Finding contour...')
                cv2.waitKey(1)
                # Find edges and filter our 1 possible contour
                imageWithEdges, possibleContour = findContours(self._MainImage, Hull=False, MinArcLength=1000, Background=False)
                self.MainUI.progressBar.setValue(50)

                # Trace the possible contour
                self.MainUI.statusbar.showMessage('Tracing contour...')
                cv2.waitKey(1)
                imageWithEdges = cv2.cvtColor(imageWithEdges, cv2.COLOR_BGR2GRAY)
                ret, imageWithEdges = cv2.threshold(imageWithEdges, 127, 255, cv2.THRESH_BINARY)
                startingPoint = (possibleContour[0][0][1], possibleContour[0][0][0])
                self._MainContour, closedLoop = traceTheContour(imageWithEdges, startingPoint)
                self.MainUI.progressBar.setValue(75)

                # Draw the contour over the image
                self.MainUI.statusbar.showMessage('Drawing contour...')
                cv2.waitKey(1)
                size = imageWithEdges.shape[:2]
                imageWithContour = drawTheContour(size, self._MainContour, Background=self._MainImage, CloseLoop=closedLoop)

                # Save the image
                self._ImageWithContourDir = self._MainImageDir.split('/')[-1].split('.')[0] + '_withContour.jpg'
                cv2.imwrite(self._ImageWithContourDir, imageWithContour)
                self._CurrentFileDir = self._ImageWithContourDir

                # Enable 'Calculate' button if closed loop found
                if not closedLoop:
                    QMessageBox.warning(self, 'No closed loop found', 'No closed loop contour found in the '
                                                                      'image.\nTry drawing the contour manually.',
                                        buttons=QMessageBox.Ok)
                else:
                    self.MainUI.calculateButton.setEnabled(True)
            except Exception as e:
                print('Error:', e)
                QMessageBox.warning(self, 'Error finding contour', 'Error when finding contour in the '
                                                                      'image.\nTry drawing the contour manually.',
                                    buttons=QMessageBox.Ok)
                self.MainUI.statusbar.showMessage('Ready')
                self.MainUI.progressBar.setValue(0)

            #
            # Display image
            w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
            image = QtGui.QPixmap(self._CurrentFileDir).scaled(w, h, Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(image)
            self.scene.addItem(item)

            self.MainUI.progressBar.setValue(100)

            # Enable buttons
            self.MainUI.cancelButton.setEnabled(True)
            self.MainUI.redrawButton.setEnabled(True)
            self.MainUI.statusbar.showMessage('Ready')

    def createNewCamMatrix(self):
        # Open create camera matrix dialog
        self.createCamMatrix = myCreateCamMatrix()
        self.createCamMatrix.exec_()

    def cancelImage(self):
        # Reset everything
        self.removeWorkingFiles()
        self.scene.clear()
        self._PhotoDir = None
        self._CurrentFileDir = None
        self._MainImageDir = None
        self._ImageWithContourDir = None

        self._MainImage = None
        self._ChessBoardCorners = None
        self._MainContour = None
        self.MainUI.progressBar.setValue(0)
        self.MainUI.cancelButton.setEnabled(False)
        self.MainUI.redrawButton.setEnabled(False)
        self.MainUI.calculateButton.setEnabled(False)

    def calculateArea(self):
        try:
            self.MainUI.statusbar.showMessage('Calculating...')
            cv2.waitKey(1)
            self.MainUI.progressBar.setValue(0)
            pixelArea = sumArea(self._MainContour)
            print('Pixels:', pixelArea)
            self.MainUI.progressBar.setValue(80)
            chessboardArea = 800 * 400
            ObjectArea = (25 * 25 * 8 * 5) * pixelArea/chessboardArea
            ObjectArea *= pow(10, -6)
            print('Area:', ObjectArea)
            self.MainUI.progressBar.setValue(100)
            self.MainUI.statusbar.showMessage('Ready')
            self.showAreaDialog = myShowAreaDialog(ObjectArea)
            self.showAreaDialog.exec_()
        except Exception as e:
            print('Error:', e)
            QMessageBox.warning(self, 'Error calculating area', 'Error when calculating are image.\nRe-draw the '
                                                                'contour and try again.',
                                buttons=QMessageBox.Ok)
            self.MainUI.statusbar.showMessage('Ready')
            self.MainUI.progressBar.setValue(0)

    def closeButton(self):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

    def removeWorkingFiles(self):
        # Remove working files
        try:
            print('Removing:', self._MainImageDir)
            os.remove(self._MainImageDir)
        except Exception as e:
            print(e)
        try:
            print('Removing:', self._ImageWithContourDir)
            os.remove(self._ImageWithContourDir)
        except Exception as e:
            print(e)

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.removeWorkingFiles()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self._CurrentFileDir is not None:
            self.scene.clear()
            w, h = self.MainUI.graphicsView.width(), self.MainUI.graphicsView.height()
            image = QtGui.QPixmap(self._CurrentFileDir).scaled(w, h, Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(image)
            self.scene.addItem(item)


if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = myWindow()
    sys.exit(app.exec_())
