# -*- coding: utf-8 -*-

# Functions for fitting the contour are provided here

import numpy as np
import cv2
from Components.py_traceTheContour import drawTheContour


# This function takes in points with x and y coordinates and perform poly fit
def polyFitting(xRaw, yRaw, n, Line=False):
    x_fit = np.polyfit(range(len(xRaw)), xRaw, n)
    y_fit = np.polyfit(range(len(yRaw)), yRaw, n)
    p_x = np.poly1d(x_fit)
    p_y = np.poly1d(y_fit)

    if Line:
        # If the segment is a line, return on the staring and the ending points
        return p_x([0, len(xRaw)]), p_y([0, len(yRaw)])
    else:
        return p_x(range(len(xRaw))), p_y(range(len(yRaw)))


# This function merges the lines found by the Hough line transform
def HoughLineMerging(Contour, Lines):
    # Define two arrays to store line locations and directions
    segmentsL = np.zeros([Contour.shape[0], 1], dtype=np.int)
    segmentsR = np.zeros([Contour.shape[0], 1], dtype=np.int)
    for l in Lines:
        # Iterate thought every line
        counter = 0
        x1, y1, x2, y2 = l[0][0], l[0][1], l[0][2], l[0][3]
        lineDirection = int(np.arctan2([y2 - y1], [x2 - x1]) * 180 / np.pi)
        # Match the line in the contour
        for p in Contour:
            # Compare every point in the contour to match the line
            # Mark the position of the starting point
            if abs(p[1] - x1) < 3 and abs(p[0] - y1) < 3:
                pointHead = counter
                counter = 0
                # Search for the end point
                for pp in Contour:
                    # Mark the position of the ending point and store the segment in the array
                    # Store the line direction at the same time
                    if abs(pp[1] - x2) < 3 and abs(pp[0] - y2) < 3:
                        if pointHead < counter:
                            np.put(segmentsL, range(pointHead, counter + 1), 1, mode='clip')
                            np.put(segmentsR, range(pointHead, counter + 1), lineDirection, mode='clip')
                            break
                        else:
                            np.put(segmentsL, range(counter, pointHead + 1), 1, mode='clip')
                            np.put(segmentsR, range(counter, pointHead + 1), lineDirection, mode='clip')
                            break
                    counter += 1
                break
            counter += 1

    return np.hstack((segmentsL, segmentsR))


# This function divide the lines in different segments based on their direction, then store their locations
def lineSegmentation(Segments):
    counter = 0
    isLine = False
    lineDirection = 0
    lineStart = 0
    lineSegments_temp = np.array([0, 0], dtype=np.uint8)
    for i in Segments:
        # If the segments is a line, start counting
        if i[0] == 1:
            if isLine is False:
                isLine = True
                lineDirection = i[1]
                lineStart = counter
            else:
                # If the direction changed, store the existing line and start a new line
                if abs(i[1] - lineDirection) > 2:
                    lineSegments_temp = np.vstack((lineSegments_temp, [lineStart, counter]))
                    lineDirection = i[1]
                    lineStart = counter
        if i[0] == 0:
            # If the line ended, store the location
            if isLine:
                isLine = False
                lineSegments_temp = np.vstack((lineSegments_temp, [lineStart, counter]))

        counter += 1

    return lineSegments_temp


# This function splits the Contour and fits them with polynomial equations
def contourFitting(Contour, Size, Threshold=100, MinLineLength=40, MaxLineGap=30, Order=5):
    # Extract the X and Y coordinates from the contour first
    X = Contour[:, 1].astype(float)
    Y = Contour[:, 0].astype(float)

    # Draw the contour on a black background
    contourOnImg = drawTheContour(Size, Contour, Color=(255, 255, 255))
    gray = cv2.cvtColor(contourOnImg, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('contour', gray)
    # cv2.waitKey(0)

    # Preform Hough Line Transform to find straight lines
    lines = cv2.HoughLinesP(gray, 1, np.pi / 180, Threshold, minLineLength=MinLineLength, maxLineGap=MaxLineGap)
    # Draw the lines for checking
    # black = np.zeros([size[0], size[1], 3], dtype=np.uint8)
    # for i in lines:
    #     x1, y1, x2, y2 = i[0][0], i[0][1], i[0][2], i[0][3]
    #     cv2.line(black, (x1, y1), (x2, y2), (0, 255, 0), 1)
    #     cv2.circle(black, (x1, y1), 3, (255, 0, 0), thickness=-1)
    #     cv2.circle(black, (x2, y2), 3, (0, 0, 255), thickness=-1)
    #     cv2.imshow('img', black)
    #     cv2.waitKey(0)

    # Merge the lines found by the Hough Line Transform
    segments = HoughLineMerging(Contour, lines)

    # Store the location of each line segments
    lineSegments = lineSegmentation(segments)

    # Fit the contour segment by segment
    x_t_fit = np.array([], dtype=float)
    y_t_fit = np.array([], dtype=float)

    for i in range(1, len(lineSegments)):
        # Fit the curve between two lines
        x_temp = X[lineSegments[i - 1][1]:lineSegments[i][0]]
        y_temp = Y[lineSegments[i - 1][1]:lineSegments[i][0]]
        if len(x_temp) != 0 and len(y_temp) != 0:
            x_temp, y_temp = polyFitting(x_temp, y_temp, Order)
            x_t_fit = np.hstack((x_t_fit, x_temp))
            y_t_fit = np.hstack((y_t_fit, y_temp))

        # Fit the straight line
        x_temp = X[lineSegments[i][0]:lineSegments[i][1]]
        y_temp = Y[lineSegments[i][0]:lineSegments[i][1]]
        x_temp, y_temp = polyFitting(x_temp, y_temp, Order, Line=True)
        x_t_fit = np.hstack((x_t_fit, x_temp))
        y_t_fit = np.hstack((y_t_fit, y_temp))

    # Fit the last part of the curve
    x_temp = X[lineSegments[-1][1]:]
    y_temp = Y[lineSegments[-1][1]:]
    if len(x_temp) > 1 and len(y_temp) > 1:
        x_temp, y_temp = polyFitting(x_temp, y_temp, Order)
        x_t_fit = np.hstack((x_t_fit, x_temp))
        y_t_fit = np.hstack((y_t_fit, y_temp))

    # Return the fitted contour
    return np.transpose(np.vstack((y_t_fit, x_t_fit)))


if __name__ == '__main__':
    from py_traceTheContour import traceTheContour
    # image = cv2.imread('DSC_0631.jpg', 0)
    image = cv2.imread('dots.jpg', 0)
    cv2.imshow('before', image)
    cv2.waitKey(1)
    # background = cv2.imread('DSC_0631.jpg')

    # startingPoint = (798, 1653)
    startingPoint = (250, 103)

    # Find the contour first
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contour, closedLoop = traceTheContour(image, startingPoint, Range=5)
    print('isClosedContour: ' + str(closedLoop))

    # Fit the contour
    size = image.shape[:2]
    contour_fit = contourFitting(contour, size, Threshold=100, MinLineLength=40, MaxLineGap=30, Order=5)

    # Draw the fitted curve
    res = drawTheContour(size, contour_fit.astype(np.int), Background=None)
    print('Contour length before fitting:', len(contour))
    print('Contour length after fitting: ', len(contour_fit))

    cv2.imshow('after', res)
    cv2.imwrite('after.jpg', res)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
