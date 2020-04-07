# -*- coding: utf-8 -*-

import cv2
import numpy as np
from py_preprocess import *
from py_getContour import findContours
from py_traceTheContour import *
from py_getArea import *


def showImg(winName, mat, width=None, height=None):
    if width is None or height is None:
        height, width = mat.shape[:2]

    cv2.namedWindow(winName, 0)
    cv2.resizeWindow(winName, width, height)
    cv2.imshow(winName, mat)


if __name__ == '__main__':
    # Import image and cameraMatrix
    fileName = 'DSC_0631.jpg'
    cameraMatrix = 'calibrate_D300S_24-120mm_f4.p'
    image = cv2.imread(fileName)

    # Undistort the image
    image = undistortImage(image, cameraMatrix)

    # Find the chessboard corners
    corners = findChessboardInImage(image, Width=6, Height=9)

    # Get the points for perspective transform
    pointsOld = getChessboardCorners(corners)
    pointsNew = getNewPoints(Width=6, Height=9, Size=(8000, 8000))

    # Transform and save the image
    dst = cropImgPerspectively(image, pointsOld, pointsNew)
    fileName = fileName.split('.')[0] + '_after.jpg'
    cv2.imwrite(fileName, dst)

    size = dst.shape[:2]
    showImg('After transform', dst, 900, 600)
    cv2.waitKey(1)

    # Load the image after transformation
    image = cv2.imread(fileName)

    # Find edges and filter our 1 possible contour
    res, possibleContour = findContours(image, Hull=False, MinArcLength=1000, Background=False)

    # Save the result
    fileName = fileName.split('.')[0] + '_edges.jpg'
    cv2.imwrite(fileName, res)
    showImg('Edge', res, 900, 600)
    cv2.waitKey(1)

    # Load the image after 1 possible contour is found
    image = cv2.imread(fileName, 0)

    # Trace the possible contour
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    startingPoint = (possibleContour[0][0][1], possibleContour[0][0][0])
    contour, closedLoop = traceTheContour(image, startingPoint)

    print('isClosedContour: ' + str(closedLoop))
    res = drawTheContour(size, contour)

    # Save the result
    fileName = fileName.split('.')[0] + '_contour.jpg'
    cv2.imwrite(fileName, res)
    # showImg(fileName, res, 900, 600)

    # Get the area
    print('The area is: ' + str(sumArea(contour)) + ' pixels')

    cv2.waitKey(0)
    cv2.destroyAllWindows()

