# -*- coding: utf-8 -*-

import numpy as np

def sumArea(Points):
    area = 0
    startingPoint = np.array((4000, 4000))
    # startingPoint = Points[0]
    temp = Points[-1]
    for p in Points:
        area += 0.5 * np.cross(temp - startingPoint, p - temp)
        temp = p

    return abs(area)

