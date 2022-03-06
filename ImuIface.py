import Network


# TODO -- create this class
class ImuIface:
    def __init__(self, network: Network):
        self.network = network
        # ... do initialization of socket ...

    def get_imu_info(self):
        x, y, is_idle, is_pushing = 0, 0, False, False
        # ...
        return {
            'x_tilt': x,  # x = variable with value from -100 to 100
            'y_tilt': y,  # y = variable with value from -100 to 100
            'is_idle': is_idle,  # is_idle = True or False
            'is_pushing': is_pushing,  # is_pushing = = True or False
        }
