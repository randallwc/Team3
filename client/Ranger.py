import pygame

from Entity import Entity
from Paths import ranger_path
from Sounds import play_laser_sound


class Ranger(Entity):
    def __init__(self, x, y, z, num_z_levels, screen_width,
                 screen_height, image_path=ranger_path):
        super().__init__(x, y, z, num_z_levels, image_path)
        self.delta_laser_width = 1
        self.max_laser_width = 20
        self.min_laser_width = 7
        self.laser_color = (255, 0, 0)
        self.inner_laser_color = (255, 255, 255)
        self.current_laser_width = self.max_laser_width
        self.frames_clicking = 0
        self.laser_is_deadly = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.health = 1
        self.is_alive = True

    # TODO -- add got damaged function that decreases health and changes
    # is_alive

    def update_coordinates(self, x, y):
        x = max(x, 0)
        x = min(self.screen_width, x)
        y = max(y, 0)
        y = min(self.screen_height, y)
        super().update_coordinates(x, y)

    def fire(self, is_firing: bool, fire_edge: bool, surface: pygame.surface.Surface):
        self.laser_is_deadly = fire_edge
        # update coordinates
        if is_firing:
            self.frames_clicking += self.delta_laser_width

            # only fire once per click
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
