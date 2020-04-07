# -*- coding: utf-8 -*-

import cv2
import numpy as np


neighbors = np.array([[-1, 0], [0, 1], [1, 0], [0, -1],
                      [-1, -1], [-1, 1], [1, -1], [1, 1]], dtype=np.int8)


def existPoint(Visited, x, y):
    for p in Visited:
        if p[0] == x and p[1] == y:
            return True

    return False


def findNextPoint(Image, x, y, Points):
    for n in neighbors:
        x1 = x + n[0]
        y1 = y + n[1]
        if 0 <= x1 <= Image.shape[0] and 0 <= y1 <= Image.shape[1]:
            print(str(x1) + ', ' + str(y1))
            print('Pixel value:', Image[x1][y1])
            if Image[x1][y1]:
                if not existPoint(Points, x1, y1):
                    print('found')
                    return x1, y1

    return None


def searchForNearestPoint(Image, StartingPoint, Points, Range=20):
    # This function searches for the nearest point

    # Create a list for visited pixels, a list for the queue
    visited = Points[1:].copy()
    queue = visited[-2:].copy()

    # Search in the queue
    while len(queue):
        # Get and remove the first element of the queue
        s = queue[0]
        queue = np.delete(queue, 0, 0)

        # Check the neighbor pixels of the current pixel
        for n in neighbors:
            x1 = s[0] + n[0]
            y1 = s[1] + n[1]
            print('Searching for the nearest point at: ' + str(x1) + ', ' + str(y1))
            if 0 <= x1 <= Image.shape[0] and 0 <= y1 <= Image.shape[1]:

                if not existPoint(visited, x1, y1):
                    # If the pixel has not been visited
                    queue = np.vstack((queue, [x1, y1]))
                    visited = np.vstack((visited, [x1, y1]))
                    # Check if the pixel is an edge
                    if Image[x1][y1]:
                        return x1, y1
                else:
                    # If the pixel has been visited
                    # Check if the pixel is the first point of the contour
                    if x1 == Points[0][0] and y1 == Points[0][1]:
                        return x1, y1

        # If the searching range exceeded the range, end the search
        if abs(queue[-1][-2] - StartingPoint[0]) > Range:
            return None


def drawTheContour(Size, Points, Background=None, CloseLoop=False):
    # This function draws the contour on a black background

    # Create a black background
    if Background is None:
        black = np.zeros([Size[0], Size[1], 3], dtype=np.uint8)
    else:
        black = Background.copy()

    temp = Points[0]
    firstPoint = Points[0]
    for i in range(len(Points)):
        point = Points[i]
        cv2.line(black, (temp[1], temp[0]), (point[1], point[0]), (0, 0, 255), 1)
        temp = point

    if CloseLoop:
        cv2.line(black, (temp[1], temp[0]), (firstPoint[1], firstPoint[0]), (0, 0, 255), 1)

    return black


def traceTheContour(Image, StartingPoint, Points=None):
    # This function trace a contour from a given starting point

    # Create a list to store the points
    if Points is None:
        Points = np.array([(StartingPoint[0], StartingPoint[1])], dtype=np.uint32)
    isClosedLoop = False

    # Tracing points
    nextPoint = list(Points[-1])
    while True:
        nextPoint = findNextPoint(Image, nextPoint[0], nextPoint[1], Points)
        if nextPoint is not None:
            print('return: ' + str(nextPoint[0]) + ', ' + str(nextPoint[1]))
            Points = np.vstack((Points, [nextPoint[0], nextPoint[1]]))
            print('Points\' shape: ' + str(Points.shape))
        else:
            # Check if the last point is next to the first point
            for n in neighbors:
                x1 = Points[-1][-2] + n[0]
                y1 = Points[-1][-1] + n[1]
                if x1 == Points[0][0] and y1 == Points[0][1]:
                    isClosedLoop = True
                    print('Closed')
                    return Points, isClosedLoop

            # If the last point is not next to the first point
            # Try to search for the nearest edge in the given range
            if not isClosedLoop:
                nearestPoint = searchForNearestPoint(Image, (Points[-1][-2], Points[-1][-1]), Points)
                if nearestPoint is not None:
                    print('Nearest point found: ' + str(nearestPoint[0]) + ', ' + str(nearestPoint[1]))
                    Points = np.vstack((Points, [nearestPoint[0], nearestPoint[1]]))
                    # Check if the point is the first point
                    if nearestPoint[0] == Points[0][0] and nearestPoint[1] == Points[0][1]:
                        isClosedLoop = True
                        print('Closed')
                        return Points, isClosedLoop
                    return traceTheContour(Image, (nearestPoint[0], nearestPoint[1]), Points)
                else:
                    return Points, isClosedLoop


def sumArea(Points):
    area = 0
    basePoint = np.array((218, 250), dtype=np.float64)
    # startingPoint = Points[0]
    Points = Points.astype('float64')
    temp = Points[-1]
    print(type(temp[0]))
    for p in Points:
        smallPiece = 0.5 * np.cross(temp - basePoint, p - temp)
        # a = temp - basePoint
        # smallPiece = 0.5 *
        area += smallPiece
        temp = p
        print(smallPiece)

    return abs(area)


if __name__ == '__main__':
    fileName = 'after.jpg'
    image = cv2.imread(fileName, 0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    startingPoint = (3291, 3099)
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contour, closedLoop = traceTheContour(image, startingPoint)

    print(sumArea(contour))

    print('isClosedContour: ' + str(closedLoop))
    size = image.shape[:2]
    res = drawTheContour(size, contour)

    fileName = fileName.split('.')[0] + '_contour.jpg'
    # cv2.imwrite(fileName, res)
    cv2.imshow(fileName, res)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
