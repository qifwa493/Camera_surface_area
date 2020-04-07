# -*- coding: utf-8 -*-

# A function for calculating area in a contour

import cv2
import numpy as np


def findChessboardInImage(Image, Width=6, Height=9):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # img_size = Image.shape[:2]
    gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (Height, Width), None)

    # If found, return corners
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        return corners2
    else:
        return []


def getChessboardCorners(Corners, Width=6, Height=9):
    # Get the 4 corner points of the chessboard
    points = Corners[0]
    for i in (Height - 1, (Width - 1) * Height, Width * Height - 1):
        points = np.vstack((points, Corners[i]))
    return points


def getChessboardPixelArea(Image, Width=6, Height=9):
    # Find the size of the chessboard
    corners = getChessboardCorners(findChessboardInImage(Image, Width=6, Height=9))
    x1 = int(corners[0][0])
    y1 = int(corners[0][1])
    x4 = int(corners[3][0])
    y4 = int(corners[3][1])

    dx = abs(x4 - x1)
    dy = abs(y4 - y1)

    if dx > dy:
        checkLength = dx / 8
    else:
        checkLength = dy / 8

    return (Width - 1) * checkLength * (Height - 1) * checkLength


def sumArea(Points):
    # Calculate the area
    area = 0

    # Use the first point of the contour as the starting point
    startingPoint = Points[0]
    temp = Points[1]
    for p in Points[2:]:
        area += 0.5 * np.cross(temp - startingPoint, p - startingPoint)
        temp = p

    return abs(area)

