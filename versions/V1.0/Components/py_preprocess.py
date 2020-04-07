# -*- coding: utf-8 -*-

import cv2
import numpy as np
import pickle


def undistortImage(Image, CameraMatrix, StoreImage=False, ImageName='Image'):
    # Get the parameters
    with open(CameraMatrix, 'rb') as f:
        cameraMatrix = pickle.load(f)
        mtx = cameraMatrix['mtx']
        dist = cameraMatrix['dist']

    # Undistort
    dst = cv2.undistort(Image, mtx, dist, None, mtx)

    # Store the undistorted image
    if StoreImage:
        cv2.imwrite(ImageName + '_undistorted.jpg', dst)

    return dst


def findChessboardInImage(Image, Width=6, Height=9):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    img_size = Image.shape[:2]
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


def getNewPoints(Width=6, Height=9, Size=(8000, 8000)):
    # Get the 4 new points based on the chessboard size
    halfWidth = (Height - 1) * 50
    halfHeight = (Width - 1) * 50
    p1 = np.float32([Size[0] / 2 - halfWidth, Size[1] / 2 - halfHeight])
    p2 = np.float32([Size[0] / 2 + halfWidth, Size[1] / 2 - halfHeight])
    p3 = np.float32([Size[0] / 2 - halfWidth, Size[1] / 2 + halfHeight])
    p4 = np.float32([Size[0] / 2 + halfWidth, Size[1] / 2 + halfHeight])
    return np.vstack((p1, p2, p3, p4))


def cropImgPerspectively(Image, OldPoints, NewPoints, Size=(8000, 8000)):
    # From the Old and New points get the transform matrix, then crop image
    M = cv2.getPerspectiveTransform(OldPoints, NewPoints)
    return cv2.warpPerspective(Image, M, Size)