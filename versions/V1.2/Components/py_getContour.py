# -*- coding: utf-8 -*-

# Functions for finding a possible contour in the target image

import cv2
import numpy as np


def showImg(winName, mat, Width=None, Height=None):
    # Get image size
    if Width is None or Height is None:
        Height, Width = mat.shape[:2]

    # Display image
    cv2.namedWindow(winName, 0)
    cv2.resizeWindow(winName, Width, Height)
    cv2.imshow(winName, mat)


def findContours(Image, MinArcLength=30, Hull=False, Background=True):
    gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)

    if Background:
        black = Image
    else:
        size = gray.shape[:2]
        black = np.zeros([size[0], size[1], 3], dtype=np.uint8)

    # Canny edge detection
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    meat = cv2.Canny(gray, 30, 60, L2gradient=True)
    # kernel = np.ones((7, 7), np.uint8)
    # meat = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Find contours
    # showImg('meat', meat, 900, 600)
    # cv2.waitKey(1)
    contours, hierarchy = cv2.findContours(meat, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    maxContour = contours[0]
    maxLength = 0
    count = 0
    filteredContours = []
    for c in contours:
        length = cv2.arcLength(c, True)


        if 7000 < length < 7500:
            maxContour = c


        # Find the long contour
        '''if length > MinArcLength:
            if length > maxLength:
                maxContour = c
                maxLength = length

        # Find all the contours that longer than the minimum arc length
        if length > MinArcLength:
            print('Contour ' + str(count) + ': ' + '{:.3f}'.format(length))
            print('Hierarchy: ' + str(hierarchy[0][count]))
            if Hull:
                c = cv2.convexHull(c)

            # Draw the contours
            temp = c[0]
            firstPoint = c[0]
            for point in c:
                cv2.line(black, (temp[0][0], temp[0][1]), (point[0][0], point[0][1]), (0, 0, 255), 3, lineType=cv2.LINE_AA)
                temp = point
            cv2.line(black, (temp[0][0], temp[0][1]), (firstPoint[0][0], firstPoint[0][1]), (0, 0, 255), 3, lineType=cv2.LINE_AA)

            # black = cv2.drawContours(black, hull, -1, (0, 0, 255), 3)

            showImg('temp', black)
            cv2.waitKey(0)

            count += 1
            # if count > 4:
            #     break

            filteredContours.append(c)'''

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
    showImg('res', res, 900, 600)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

