class CameraIface:
    def __init__(self, camera_width, camera_height, num_levels=3):
        # ... initialize the class with constant values here ...
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.num_levels = num_levels
        # ... add member variables here and if you don't know what they should be set to then say
        # self.variable_name = None

    def calibrate(self):
        # ... create a function that enters calibration mode here ...
        # ... then store that calibration in the class ...
        pass

    def get_object_position(self):
        # ... create a function that returns the x, y position of the ball here ...
        x = 0
        y = 0
        # ... write the code that takes a picture and then returns the center position of the ball ...
        return x, y
