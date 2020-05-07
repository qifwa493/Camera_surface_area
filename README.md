# camera_surface_area

**A program to measure the area of a flat surface in an image**

## Intro

This program uses OpenCV to process images, the detection process can be done automatically or manually

The program is wrapped with a user interface developed using PyQt5

Place the reference object (a 7*10 OpenCV chessboard) on the surface that you want to measure, take a picture of the scene, import the picture to the program, then make the measurement

## Packages

**The program requires Python (3.7.4 or newer); OpenCV (4.1 or newer); Numpy (1.17 or newer); PyQt5 to run**

- To install OpenCV for Python:
```
pip install opencv-python
```

- To install PyQt5:
```
pip install PyQt5
```

- Numpy should be installed automatically when installing OpenCV, to install Numpy manually:
```
pip install numpy
```

## Run the program

Different versions of the program are stored under the folder _versions_, the latest version is  _V1.5_

**To run the program, go to _versions/V1.5/_ and run:**
```
py_cameraSurfaceAreaGUI.py
```

**Work flow:**
1. Import _Camera Matrix_
2. Import an image
3. Detect the object to measure automatically or manually (change in the settings)
4. Re-draw the contour if needed
5. calculate the area

**An utility function is provided in the program called _Create Camera Matrix_ for creating the camera matrix to calibrate your camera**

_Note: adjust "ChessBoardUnitSize" parameter in the Settings according to the actual printout_

Pictures in the folder _pics/_ can be used to create a camera matrix, camera model: Nikon D300S with 24 mm f4 lens

Pictures in the folder _versions/V1.5/Test/D300S_24mm/_ are some sample picture for testing

## Demo

-	Auto-detection of the target area:

https://youtu.be/9O0A501VXk4

-	Manual-detection by using Grab Cut:

https://youtu.be/hkaNAndmqEw

-	Manual define by using Re-draw:

https://youtu.be/5JNYB7r19UE

-	Creation of Camera Matrix:

https://youtu.be/Bt9RyqS8rFI
