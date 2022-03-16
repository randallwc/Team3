from Entity import *
from Paths import *


# TODO -- create this class
class OpponentRanger(Entity):
    def __init__(self, x, y, z, num_z_levels,
                 image_path=opponent_path, current_score=0):
        super().__init__(x, y, z, num_z_levels, image_path, current_score)
