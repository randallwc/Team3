import Exceptions
import Entity
import Paths
import Sounds
import pygame


class Enemy(Entity.Entity):
    def __init__(self, x, y, z, num_z_levels, enemy_type, health=1, speed=0):
        self.good_enemies = ['jc', 'cow']
        self.bad_enemies = ['ricky']
        if enemy_type == 'jc':
            self.image_path = Paths.jc_path
        elif enemy_type == 'ricky':
            self.image_path = Paths.ricky_path
        elif enemy_type == 'cow':
            self.image_path = Paths.cow_path
        else:
            raise Exception('invalid enemy_type')
        super().__init__(x, y, z, num_z_levels, self.image_path)
        self.speed = speed
        self.enemy_type = enemy_type
        self.health = health
        self.scale_image(100, 100)
        self.time_alive = 0
        self.max_time_alive = 100

    def get_x_hitbox(self):
        return range(self.x - self.shape.get_width() // 2, self.x + self.shape.get_width() // 2)

    def play_death_sound(self):
        if self.health <= 0:
            if self.enemy_type in self.bad_enemies:
                Sounds.play_sound(Paths.ricky_death_sound_path)
            elif self.enemy_type in self.good_enemies:
                Sounds.play_sound(Paths.good_enemy_death_sound_path)

    def handle_death(self):
        self.play_death_sound()
        if self.enemy_type in self.good_enemies:
            return -1
        else:
            return 1

    def show(self, surface: pygame.surface):
        self.time_alive += 1
        if self.time_alive > self.max_time_alive and self.enemy_type in self.good_enemies:
            self.health = 0
        super().show(surface)
