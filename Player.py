import Exceptions
import Ranger
import Sounds
import pygame


class Player:
    def __init__(self, num_z_levels=3):
        self.ranger = Ranger.Ranger(0, 0, 0, num_z_levels)
        self.scores = []  # TODO -- pull down scores
        self.is_firing_laser = False
        self.max_laser_width = 20
        self.min_laser_width = 7
        self.current_laser_width = self.max_laser_width
        self.laser_color = (255, 0, 0)
        self.inner_laser_color = (255, 255, 255)
        self.current_score = 0
        self.coordinates = self.ranger.x, self.ranger.y
        self.frames_clicking = 0
        self.delta_laser_width = 1
        self.laser_is_deadly = False

    def update_coordinates(self):
        self.coordinates = self.ranger.x, self.ranger.y

    def fire(self, is_clicking: bool, surface: pygame.surface):
        # update coordinates
        self.update_coordinates()
        if is_clicking:
            self.laser_is_deadly = False
            self.frames_clicking += self.delta_laser_width

            # only fire once per click
            if self.frames_clicking < (self.max_laser_width - self.min_laser_width) \
                    and self.current_laser_width == self.max_laser_width:
                Sounds.play_laser_sound()
                self.laser_is_deadly = True

            # display red laser
            top_laser_coordinates = (self.ranger.x, 0)
            pygame.draw.line(
                surface,
                self.laser_color,
                self.coordinates,
                top_laser_coordinates,
                self.current_laser_width
            )

            # display inner white laser
            pygame.draw.line(
                surface,
                self.inner_laser_color,
                self.coordinates,
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
