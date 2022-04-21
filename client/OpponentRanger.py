from Paths import opponent_path
from Ranger import Ranger


# TODO -- create this class
class OpponentRanger(Ranger):
    def __init__(self, x, y, z, num_z_levels, screenwidth, screenheight,
                 image_path=opponent_path):
        super().__init__(x, y, z, num_z_levels, screenwidth, screenheight, image_path)
