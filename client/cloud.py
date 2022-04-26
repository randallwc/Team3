from random import randrange

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from entity import Entity


class Cloud(Entity):
    def __init__(self, x, y, z, num_z_levels,
                 image_path, speed=None, max_speed=10):
        super().__init__(x, y, z, num_z_levels, image_path)
        if speed is None:
            self.speed = randrange(1, max_speed, 1)
        else:
            self.speed = speed
        self.max_speed = max_speed

    def loop_around(self):
        self.y += self.speed
        if self.y < - self.shape.get_height() or self.y > SCREEN_HEIGHT + \
                self.shape.get_height():
            self.x = randrange(0, SCREEN_WIDTH, 1)
            self.y = - self.shape.get_height() // 2
            self.speed = randrange(1, self.max_speed, 1)
