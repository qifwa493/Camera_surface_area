# -*- coding: utf-8 -*-


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


def maskChessboardAndBackground(ImageWithCB, ImageWithEdge, AfterGrabCut=False, SampleType=2, CBD=0):
    # This function will mask the chessboard and the background
    # The program will first locate the chessboard, pick sample color at the chessboard corners
    # Then find the target area based on histogram back projection
    # Lastly, create a mask to cover the background and the chessboard
    # SampleType=1: Pick only the top left and bottom right corners
    #           =2: Pick only the top right and bottom left corners
    #           =<other int numbers>: Pick all 4 corners

    # Locate the chessboard first
    corners = getChessboardCorners(findChessboardInImage(ImageWithCB, Width=6, Height=9))

    # Get the corners of the chessboard based on its orientation
    if CBD < 1:
        x1 = int(corners[0][0])
        y1 = int(corners[0][1])
        x4 = int(corners[3][0])
        y4 = int(corners[3][1])
    else:
        x1 = int(corners[1][0])
        y1 = int(corners[1][1])
        x4 = int(corners[2][0])
        y4 = int(corners[2][1])

    if x1 > x4:
        x1, x4 = swapValue(x1, x4)
        y1, y4 = swapValue(y1, y4)

    dx = int((x4 - x1) / 8)

    point1 = (x1 - 3 * dx, y1 - 3 * dx)
    point2 = (x4 + 3 * dx, y4 + 3 * dx)

    # Get the region of the chessboard
    roi_chessboard = ImageWithCB[point1[1]:point2[1], point1[0]:point2[0]]

    # Find the border of the chessboard by using edge detection
    roi_CB_gray = cv2.cvtColor(roi_chessboard, cv2.COLOR_BGR2GRAY)
    roi_CB_gray = cv2.bilateralFilter(roi_CB_gray, 9, 75, 75)
    roi_CB_edge = cv2.Canny(roi_CB_gray, 30, 60, L2gradient=True)

    # Find the bounding rectangle of the border
    x, y, w, h = cv2.boundingRect(roi_CB_edge)

    # Create a mask to cover the chessboard only if Grab Cut mask exist
    if AfterGrabCut:
        size = ImageWithEdge.shape[:2]
        mask = np.ones([size[0], size[1]], dtype=np.uint8)
        mask *= 255
        showImg('mask after creation', mask, 800)
        cv2.waitKey(0)
        mask = cv2.rectangle(mask, (point1[0] + x, point1[1] + y), (point1[0] + x + w, point1[1] + y + h), 0, -1)
        showImg('mask after covering chessboard', mask, 800)
        cv2.waitKey(0)
        ImageWithEdge = cv2.bitwise_and(ImageWithEdge, mask)
        showImg('after', ImageWithEdge, 800)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return ImageWithEdge

    # Get color samples from 4 corners of the chessboard
    sample_1 = ImageWithCB[(point1[1] + y - dx):(point1[1] + y), (point1[0] + x - dx):(point1[0] + x)]
    sample_2 = ImageWithCB[(point1[1] + y + h):(point1[1] + y + h + dx), (point1[0] + x - dx):(point1[0] + x)]
    sample_3 = ImageWithCB[(point1[1] + y - dx):(point1[1] + y), (point1[0] + x + w):(point1[0] + x + w + dx)]
    sample_4 = ImageWithCB[(point1[1] + y + h):(point1[1] + y + h + dx), (point1[0] + x + w):(point1[0] + x + w + dx)]

    if SampleType == 1:
        sampleColor = np.hstack((sample_1, sample_4))
    elif SampleType == 2:
        sampleColor = np.hstack((sample_2, sample_3))
    else:
        sampleColor = np.vstack((np.hstack((sample_1, sample_3)), np.hstack((sample_2, sample_4))))

    # Get the region of the target area by using histogram back projection
    roi_target = histogramBackprojection(sampleColor, ImageWithCB, applyMask=False)
    showImg('target', roi_target, 800)
    cv2.waitKey(0)
    # cv2.destroyWindow('target')

    # Find the bounding rectangle of the target area
    X, Y, W, H = cv2.boundingRect(roi_target)

    # Create a mask
    size = ImageWithEdge.shape[:2]
    mask = np.zeros([size[0], size[1]], dtype=np.uint8)
    lowerY = Y - dx
    lowerX = X - dx
    upperY = Y + H + dx
    upperX = X + W + dx
    # Check if the roi is outside the image
    if lowerY < 0:
        lowerY = 0
    if lowerX < 0:
        lowerX = 0
    if upperY > size[0]:
        upperY = size[0]
    if upperX > size[1]:
        upperX = size[1]
    mask = cv2.rectangle(mask, (lowerX, lowerY), (upperX, upperY), 255, -1)
    mask = cv2.rectangle(mask, (point1[0] + x, point1[1] + y), (point1[0] + x + w, point1[1] + y + h), 0, -1)
    showImg('mask', mask, 800)
    cv2.waitKey(0)
    # cv2.destroyWindow('mask')

    # Mask the chessboard and the background
    ImageWithEdge = cv2.bitwise_and(ImageWithEdge, mask)
    showImg('after', ImageWithEdge, 800)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return ImageWithEdge


def swapValue(Val_1, Val_2):
    return Val_2, Val_1


def closeMask(img):
    kernel = np.ones((5, 5), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    kernel = np.ones((9, 9), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)


def histogramBackprojection(roi, TargetImg, applyMask=False):
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hsvt = cv2.cvtColor(TargetImg, cv2.COLOR_BGR2HSV)

    # calculating object histogram
    roiHist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])

    # normalize histogram and apply backprojection
    cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)
    dst = cv2.calcBackProject([hsvt], [0, 1], roiHist, [0, 180, 0, 256], 1)

    # Convolute with circular disc to remove noise
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cv2.filter2D(dst, -1, disc, dst)

    # Threshold the mask
    ret, thresh = cv2.threshold(dst, 30, 255, cv2.THRESH_BINARY)
    thresh = closeMask(thresh)
    if applyMask is False:
        return thresh
    else:
        # Merge the mask into 3 channels
        thresh = cv2.merge((thresh, thresh, thresh))
        return cv2.bitwise_and(TargetImg, thresh)


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


if __name__ == '__main__':
    fileName = 'DSC_0631_after.jpg'
    image = cv2.imread(fileName)

    # image = maskBackground(image)
    # cv2.imwrite('maskBG.jpg', image)

    # image = maskChessboard(image, image)
    # cv2.imwrite('maskCB.jpg', image)

    edge = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = maskChessboardAndBackground(image, edge)

    showImg('im', image, 800)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cv2.imwrite('im.jpg', image)