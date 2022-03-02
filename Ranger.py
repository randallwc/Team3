import Exceptions
import Entity
import Paths


class Ranger(Entity.Entity):
    def __init__(self, x, y, z, num_z_levels, image_path=Paths.ranger_path):
        super().__init__(x, y, z, num_z_levels, image_path)