from constants import (MAX_RANGER_SPEED, RANGER_ACCELERATION, SCREEN_HEIGHT,
                       SCREEN_WIDTH)
from paths import point_gain_sound_path, point_loss_sound_path
from ranger import Ranger
from sounds import play_sound


class Player:
    def __init__(self, num_z_levels):
        self.current_score = 0
        self.start_x = 0.5 * SCREEN_WIDTH
        self.start_y = 0.9 * SCREEN_HEIGHT
        self.num_z_levels = num_z_levels
        self.start_z = self.num_z_levels // 2
        self.ranger = Ranger(
            self.start_x,
            self.start_y,
            self.start_z,
            num_z_levels
        )
        self.min_speed = 5.0
        self.max_speed = MAX_RANGER_SPEED
        self.speed = self.min_speed
        self.acceleration = RANGER_ACCELERATION

    def handle_point_change(self, delta: int):
        if delta < 0:
            self.ranger.particle_cloud.fire_burst(10)
            play_sound(point_loss_sound_path, 0.25)
        if delta > 0:
            play_sound(point_gain_sound_path, 0.25)
        self.current_score += delta
