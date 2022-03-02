import Exceptions


class CameraIface:
    def __init__(self):
        pass

    def calibrate(self):
        raise Exceptions.NotImplementedException

    def get_object_position(self):
        raise Exceptions.NotImplementedException