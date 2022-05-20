import pygame

from constants import ENEMY_DIRECTIONS, ENEMY_INFO, SCREEN_HEIGHT, SCREEN_WIDTH
from entity import Entity
from sounds import play_sound


class Enemy(Entity):
    def __init__(
            self,
            x,
            y,
            z,
            num_z_levels,
            enemy_type,
            enemy_id,
            health):
        self.enemy_type = enemy_type
        self.health = health
        self.good_enemies = self.get_good_enemies()
        self.bad_enemies = self.get_bad_enemies()
        self.image_path = self.get_image_path()
        self.time_alive_countdown = self.get_max_time_alive()
        self.x_speed = self.get_x_speed()
        self.y_speed = self.get_y_speed()
        self.current_direction = self.get_direction()
        self.id = enemy_id  # only used in multiplayer
        self.image_dimensions = self.get_image_dimensions()

        super().__init__(x, y, z, num_z_levels, self.image_path, self.image_dimensions)

    @staticmethod
    def get_good_enemies():
        def is_good(key):
            return ENEMY_INFO[key]['is_good']

        return list(filter(is_good, ENEMY_INFO))

    @staticmethod
    def get_bad_enemies():
        def is_bad(key):
            return not ENEMY_INFO[key]['is_good']

        return list(filter(is_bad, ENEMY_INFO))

    def get_image_dimensions(self):
        return ENEMY_INFO[self.enemy_type]['image_dimensions']

    def get_image_path(self):
        return ENEMY_INFO[self.enemy_type]['image_path']

    def get_death_sound(self):
        return ENEMY_INFO[self.enemy_type]['death_sound_path']

    def get_max_time_alive(self):
        return ENEMY_INFO[self.enemy_type]['max_time_alive']

    def get_x_speed(self):
        return ENEMY_INFO[self.enemy_type]['x_speed']

    def get_y_speed(self):
        return ENEMY_INFO[self.enemy_type]['y_speed']

    def get_direction(self):
        direction = ENEMY_INFO[self.enemy_type]['direction']
        if direction not in ENEMY_DIRECTIONS:
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

    def show(self, surface: pygame.surface.Surface,
             particle_surface: pygame.surface.Surface):
        super().show(surface, particle_surface)
        self.time_alive_countdown -= 1
        if self.time_alive_countdown <= 0 or self.health <= 0:
            self.should_display = False

    def show_diff_level(
            self,
            surface: pygame.surface.Surface,
            particle_surface: pygame.surface.Surface,
            is_above):
        if is_above:
            self.shape.set_alpha(255 // 2)
            text = 'above'
        else:
            self.shape.set_alpha(255 // 4)
            text = 'below'
        self.show(surface, particle_surface)
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

    def step(self):
        """Move enemy based on current_direction.

        Returns:
            False if enemy hits the bottom of the screen.
            True otherwise.
        """
        super().update_coordinates(self.x, self.y)

        if self.current_direction in ('right', 'left'):
            if self.current_direction == 'right':
                self.x += self.x_speed
            elif self.current_direction == 'left':
                self.x -= self.x_speed

            self.x = min(SCREEN_WIDTH, max(0, self.x))

            if self.x == SCREEN_WIDTH:
                self.current_direction = 'left'
                self.y += self.y_speed
            if self.x == 0:
                self.current_direction = 'right'
                self.y += self.y_speed

            # keep y within the screen
            self.y = min(SCREEN_HEIGHT * 3 // 4, max(0, self.y))
        elif self.current_direction == 'down':
            self.y += self.y_speed
            if self.y >= SCREEN_HEIGHT:
                return False
        else:
            raise Exception('invalid direction')
        return True
