import Entity
import Paths
import pygame
import Sounds


class Ranger(Entity.Entity):
    def __init__(self, x, y, z, num_z_levels, image_path=Paths.ranger_path):
        super().__init__(x, y, z, num_z_levels, image_path)
        self.delta_laser_width = 1
        self.max_laser_width = 20
        self.min_laser_width = 7
        self.laser_color = (255, 0, 0)
        self.inner_laser_color = (255, 255, 255)
        self.current_laser_width = self.max_laser_width
        self.frames_clicking = 0
        self.laser_is_deadly = False

    def fire(self, is_firing: bool, surface: pygame.surface):
        # update coordinates
        if is_firing:
            self.laser_is_deadly = False
            self.frames_clicking += self.delta_laser_width

            # only fire once per click
            if self.frames_clicking < (self.max_laser_width - self.min_laser_width) \
                    and self.current_laser_width == self.max_laser_width:
                Sounds.play_laser_sound()
                self.laser_is_deadly = True

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
            self.laser_is_deadly = False
