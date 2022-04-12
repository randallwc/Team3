from random import randrange

import pygame

from Entity import Entity
from Sounds import play_sound


class MultiplayerEnemy(Entity):
    def __init__(self, x, y, z, num_z_levels, enemy_type,
                 enemy_info, enemy_id, health=1, image_dimensions=(100, 100)):
        self.enemy_info = enemy_info
        self.enemy_type = enemy_type
        self.health = health

        self.good_enemies = self.get_good_enemies()
        self.bad_enemies = self.get_bad_enemies()
        self.image_path = self.get_image_path()
        self.time_alive_countdown = self.get_max_time_alive()
        self.speed = self.get_speed()
        self.id = enemy_id

        super().__init__(x, y, z, num_z_levels, self.image_path, image_dimensions)

    def get_good_enemies(self):
        def is_good(key):
            return self.enemy_info[key]['is_good']

        return list(filter(is_good, self.enemy_info))

    def get_bad_enemies(self):
        def is_bad(key):
            return not self.enemy_info[key]['is_good']

        return list(filter(is_bad, self.enemy_info))

    def get_image_path(self):
        return self.enemy_info[self.enemy_type]['image_path']

    def get_death_sound(self):
        return self.enemy_info[self.enemy_type]['death_sound_path']

    def get_max_time_alive(self):
        return self.enemy_info[self.enemy_type]['max_time_alive']

    def get_speed(self):
        return self.enemy_info[self.enemy_type]['speed']

    def get_x_hitbox(self):
        return range(self.x - self.shape.get_width() // 2,
                     self.x + self.shape.get_width() // 2)

    def play_death_sound(self):
        if self.health <= 0:
            play_sound(self.get_death_sound())

    def handle_death(self):
        self.play_death_sound()
        return 1 if self.enemy_type in self.bad_enemies else -1

    def show(self, surface: pygame.surface.Surface):
        super().show(surface)
        self.time_alive_countdown -= 1
        if self.time_alive_countdown <= 0:
            self.should_display = False

    def got_hit(self, damage_amount):
        self.health -= damage_amount

        if self.health <= 0:
            # no negative healths
            self.health = 0
            # if dead it shouldn't display
            self.should_display = False

    # TODO -- make this take a pattern argument e.g. circle or snake and then
    # make it move in those patterns
    def step(self, screen_dimensions):
        screen_width, screen_height = screen_dimensions
        # TODO make account for z value
        # make it wiggle
        self.x += randrange(-self.speed, self.speed + 1, 1)
        self.y += randrange(-self.speed, self.speed + 1, 1)

        # keep it within the screen
        if self.x > screen_width:
            self.x = screen_width - self.speed
        elif self.x < 0:
            self.x = self.speed

        if self.y > screen_height:
            self.y = screen_height - self.speed
        elif self.y < 0:
            self.y = self.speed

    def countdown_time_alive(self):
        self.time_alive_countdown -= 1
        if self.time_alive_countdown <= 0:
            self.should_display = False
