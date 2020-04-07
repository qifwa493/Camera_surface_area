# -*- coding: utf-8 -*-

# A function for calculating area in a contour

import numpy as np


def sumArea(Points):
    area = 0

    # startingPoint = np.array((4000, 4000))
    # Use the first point of the contour as the starting point
    startingPoint = Points[0]
    temp = Points[-1]
    for p in Points:
        area += 0.5 * np.cross(temp - startingPoint, p - temp)
        temp = p

    return abs(area)
