# -*- coding: utf-8 -*-

# Functions for creating Camera Matrix are provided in this file

import numpy as np
import cv2
import glob
import pickle


def calibrate_camera(FileDirs, CameraModel, storeParameters=True):
    # Termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    img_size = []

    for fname in FileDirs:
        img = cv2.imread(fname)
        img_size = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            # img = cv2.drawChessboardCorners(img, (9, 6), corners2, ret)

    # Calculate the parameters
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_size, None, None)

    # Store the parameters
    if storeParameters:
        cameraMatrix = {'mtx': mtx, 'dist': dist}
        camMatrixName = FileDirs[0][:-len(FileDirs[0].split('/')[-1])] + CameraModel + '_Matrix.p'
        with open(camMatrixName, 'wb') as f:
            pickle.dump(cameraMatrix, f)

    return mtx, dist


if __name__ == '__main__':
    # load test image
    myImg = cv2.imread('DSC_0629.JPG')
    CameraModel = 'D300S_24-120mm_f4'

    images = glob.glob('*.jpg')

    # get the parameters
    mtx, dist = calibrate_camera(images, CameraModel)

    # undistort
    dst = cv2.undistort(myImg, mtx, dist, None, mtx)

    # cv2.imwrite('calibresult.png', dst)

    cv2.namedWindow('original', 0)
    cv2.resizeWindow('original', 900, 600)
    cv2.imshow('original', myImg)

    cv2.namedWindow('undistort', 0)
    cv2.resizeWindow('undistort', 900, 600)
    cv2.imshow('undistort', dst)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
