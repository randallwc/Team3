import Entity
import Paths


class OpponentRanger(Entity.Entity):
    def __init__(self, x, y, z, num_z_levels, image_path=Paths.opponent_path, current_score=0):
        super().__init__(x, y, z, num_z_levels, image_path, current_score)
