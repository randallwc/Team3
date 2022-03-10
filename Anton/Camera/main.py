#!/usr/bin/env python3
import CameraIface

# create an instance of the camera interface class
myCameraIface = CameraIface.CameraIface(100,3)

# call the class method to calibrate the camera interface
myCameraIface.calibrate()

# then continuously print the position e.g. which level
for _ in range(100_000):
    print(myCameraIface.get_object_level())
    print(myCameraIface.get_object_position())
