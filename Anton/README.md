Source code:

> Calibration step by asking the user to take a picture of an object within the box
>
> Observe results of tracking

Sources:

> Reading Video Feed and Applying Colour Mask: https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
>
> Determining BGR Colour Range: https://stackoverflow.com/questions/48109650/how-to-detect-two-different-colors-using-cv2-inrange-in-python-opencv
>
> K-Means Clustering in OpenCV: https://docs.opencv.org/4.x/d1/d5c/tutorial_py_kmeans_opencv.html
>
> Calibration Step: https://stackoverflow.com/questions/34588464/python-how-to-capture-image-from-webcam-on-click-using-opencv

If the object you wish to track does NOT entirely fill up the box, then the calibration will not work as efficiently. Calibration bases everything off the image taken, so if the lighting changes suddenly, tracking may work unexpectedly. Because of its sensitivity, we may just switch over to a pre-existing library _dlib_ and adapt those to our desired features.
