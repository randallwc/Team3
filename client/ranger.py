import pygame

from constants import (MAX_RANGER_HEALTH, RANGER_START_HEALTH, RED,
                       SCREEN_HEIGHT, SCREEN_WIDTH)
from entity import Entity
from paths import ranger_path
from sounds import play_laser_sound


class Ranger(Entity):
    def __init__(self, x, y, z, num_z_levels, image_path=ranger_path):
        super().__init__(x, y, z, num_z_levels, image_path)
        self.delta_laser_width = 1
        self.max_laser_width = 20
        self.min_laser_width = 7
        self.laser_color = RED
        self.inner_laser_color = (255, 255, 255)
        self.current_laser_width = self.max_laser_width
        self.frames_clicking = 0
        self.laser_is_deadly = False
        self.health = RANGER_START_HEALTH
        self.is_alive = True

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = max(0, min(MAX_RANGER_HEALTH, value))
        if self._health <= 0:
            self.is_alive = False
        else:
            self.is_alive = True

    def update_coordinates(self, x, y):
        super().update_coordinates(min(max(x, 0), SCREEN_WIDTH), min(max(y, 0), SCREEN_HEIGHT))

    def fire(self, is_firing: bool, fire_edge: bool,
             surface: pygame.surface.Surface, color=RED):
        self.laser_color = color
        self.laser_is_deadly = fire_edge
        # update coordinates
        if is_firing:
            self.frames_clicking += self.delta_laser_width

            # only fire once per action
            if fire_edge:
                play_laser_sound()

            # display red laser
            top_laser_coordinates = (self.x, 0)
            pygame.draw.line(
                surface,
                self.laser_color,
                (self.x, self.y),
                top_laser_coordinates,
                self.current_laser_width
            )

            # display inner white laser
            pygame.draw.line(
                surface,
                self.inner_laser_color,
                (self.x, self.y),
                top_laser_coordinates,
                self.current_laser_width // 2
            )

            # make laser size decrease
            self.current_laser_width -= self.delta_laser_width

            # make sure that the laser doesn't have a value less than min
            if self.current_laser_width < self.min_laser_width:
                self.current_laser_width = self.min_laser_width
        else:
            # when not clicking reset laser width and the countdown
            self.current_laser_width = self.max_laser_width
            self.frames_clicking = 0
