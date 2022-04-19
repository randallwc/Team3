import pygame

from Entity import Entity
from Sounds import play_sound


class Enemy(Entity):
    def __init__(self, x, y, z, num_z_levels, enemy_type,
                 enemy_info, enemy_id = 1, health=1, image_dimensions=(100, 100)):
        self.enemy_info = enemy_info
        self.enemy_type = enemy_type
        self.health = health
        self.directions = ['left', 'right']

        self.good_enemies = self.get_good_enemies()
        self.bad_enemies = self.get_bad_enemies()
        self.image_path = self.get_image_path()
        self.time_alive_countdown = self.get_max_time_alive()
        self.x_speed = self.get_x_speed()
        self.y_speed = self.get_y_speed()
        self.current_direction = self.get_direction()
        self.id = enemy_id # only used in multiplayer

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

    def get_x_speed(self):
        return self.enemy_info[self.enemy_type]['x_speed']

    def get_y_speed(self):
        return self.enemy_info[self.enemy_type]['y_speed']

    def get_direction(self):
        direction = self.enemy_info[self.enemy_type]['direction']
        if direction not in self.directions:
            raise Exception('invalid direction')
        return direction

    def get_x_hitbox(self):
        return range(self.x - self.shape.get_width() // 2,
                     self.x + self.shape.get_width() // 2)

    def play_death_sound(self):
        if self.health <= 0:
            if self.get_death_sound():
                play_sound(self.get_death_sound())

    def handle_death(self):
        self.play_death_sound()
        return 1 if self.enemy_type in self.bad_enemies else -1

    def show(self, surface: pygame.surface.Surface):
        super().show(surface)
        self.time_alive_countdown -= 1
        if self.time_alive_countdown <= 0 or self.health <= 0:
            self.should_display = False

    def show_diff_level(self, surface: pygame.surface.Surface, is_above):
        if is_above:
            self.shape.set_alpha(255 // 2)
            text = 'above'
        else:
            self.shape.set_alpha(255 // 4)
            text = 'below'
        self.show(surface)
        self.shape.set_alpha(255)
        # indicate above or below
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(f'{text}', True, (255, 255, 255))
        surface.blit(
            rendered_font,
            (self.rect.centerx -
             rendered_font.get_width() //
             2,
             self.rect.bottom))

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
        super().update_coordinates(self.x, self.y)
        screen_width, screen_height = screen_dimensions

        if self.current_direction == 'right':
            self.x += self.x_speed
        elif self.current_direction == 'left':
            self.x -= self.x_speed

        if self.x >= screen_width:
            self.y += self.y_speed
            self.current_direction = self.directions[0]  # left
            self.x = screen_width
        if self.x <= 0:
            self.y += self.y_speed
            self.current_direction = self.directions[1]
            self.x = 0

        # keep y within the screen
        if self.y >= screen_height // 2:
            self.y = screen_height // 2
        elif self.y <= 0:
            self.y = 0
