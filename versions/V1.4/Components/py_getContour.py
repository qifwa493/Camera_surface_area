# -*- coding: utf-8 -*-

# Functions for finding a possible contour in the target image

import cv2
import numpy as np
from Components.py_maskImage import maskChessboardAndBackground


def showImg(winName, mat, Width=None, Height=None):
    # Get image size
    # if Width is None or Height is None:
    #     Height, Width = mat.shape[:2]

    dim = None

    # if both the width and height are None
    if Width is None and Height is None:
        dim = mat.shape[:2]

    # check to see if the width is None
    elif Width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = Height / float(mat.shape[0])
        dim = (int(mat.shape[1] * r), Height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = Width / float(mat.shape[1])
        dim = (Width, int(mat.shape[0] * r))

    # Display image
    cv2.namedWindow(winName, 0)
    cv2.resizeWindow(winName, dim[0], dim[1])
    cv2.imshow(winName, mat)


def findContours(Image, GrabCutMask=None, MinArcLength=30, Hull=False, Background=True, ChessboardDirection=0):
    # This function finds all possible contours and return some based on the selection criteria
    showImg('Image', Image, 800)
    cv2.waitKey(0)

    # Create a grayscale image if grab cut mask is not exist
    if GrabCutMask is None:
        gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    else:
        gray = GrabCutMask.copy()

    # Canny edge detection
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    imgWithEdge = cv2.Canny(gray, 30, 60, L2gradient=True)

    # Put a mask over the chessboard and crop the background
    if GrabCutMask is None:
        imgWithEdge = maskChessboardAndBackground(Image, imgWithEdge, CBD=ChessboardDirection)
    else:
        imgWithEdge = maskChessboardAndBackground(Image, imgWithEdge, AfterGrabCut=True, CBD=ChessboardDirection)

    # Create a black background if contours are not to be drawn on the original background
    if Background:
        black = Image
    else:
        size = imgWithEdge.shape[:2]
        black = np.zeros([size[0], size[1], 3], dtype=np.uint8)

    # Find all possible contours
    contours, hierarchy = cv2.findContours(imgWithEdge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    maxContour = contours[0]
    maxLength = 0
    count = 0
    filteredContours = []
    for c in contours:
        length = cv2.arcLength(c, True)

        # if 7000 < length < 7500:
        #     maxContour = c

        # Find the longest contour
        if length > MinArcLength:
            if length > maxLength:
                maxContour = c
                maxLength = length

        # Find all the contours that longer than the minimum arc length
        if length > MinArcLength:
            # print('Contour ' + str(count) + ': ' + '{:.3f}'.format(length))
            # print('Hierarchy: ' + str(hierarchy[0][count]))
            if Hull:
                c = cv2.convexHull(c)

            # Draw the contours
            temp = c[0]
            firstPoint = c[0]
            for point in c:
                cv2.line(black, (temp[0][0], temp[0][1]), (point[0][0], point[0][1]), (0, 0, 255), 1)
                temp = point
            cv2.line(black, (temp[0][0], temp[0][1]), (firstPoint[0][0], firstPoint[0][1]), (0, 0, 255), 1)

            # black = cv2.drawContours(black, hull, -1, (0, 0, 255), 3)

            # Display the contours one by one
            showImg('Contours', black, 1280)
            cv2.waitKey(0)

            count += 1
            # if count > 4:
            #     break

            filteredContours.append(c)

    # Draw the contours
    print('Contour length: ' + '{:.3f}'.format(cv2.arcLength(maxContour, True)))
    temp = maxContour[0]
    firstPoint = maxContour[0]
    for i in range(len(maxContour)):
        point = maxContour[i]
        cv2.line(black, (temp[0][0], temp[0][1]), (point[0][0], point[0][1]), (255, 255, 255), 1)
        temp = point
    cv2.line(black, (temp[0][0], temp[0][1]), (firstPoint[0][0], firstPoint[0][1]), (255, 255, 255), 1)
    return black, maxContour


if __name__ == '__main__':
    fileName = 'DSC_0631_after.jpg'
    image = cv2.imread(fileName)

    res, contours = findContours(image, Hull=False, MinArcLength=1000, Background=False)

    # cv2.imwrite(fileName.split('.')[0] + '_edges.jpg', res)
    showImg('res', res, 800)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
