import sys
from random import choice, randrange

import pygame

from Cloud import Cloud
from Controller import Controller
from DatabaseIface import DatabaseIface
from Enemy import Enemy
from MultiplayerSocket import MultiplayerSocket
from Paths import (anton_death_sound_path, anton_path, armando_path,
                   background_music_path, cloud_path, cow_path,
                   david2_death_sound_path, david2_path, david_path,
                   friendly_fire_sound_path, jc_death_sound_path, jc_path,
                   ranger_path, ricky_death_sound_path, ricky_path, sky_path)
from Player import Player
from ScreenManager import ScreenManager, show_mouse
from Sounds import play_music


class Game:
    def __init__(self, screen_width=1280, screen_height=720,
                 window_title='Sky Danger Ranger'):
        # pygame initialization
        pygame.init()
        show_mouse(True)
        pygame.display.set_caption(window_title)
        pygame.display.set_icon(
            pygame.image.load(ranger_path)
        )

        # member variables
        self.enemy_info = {
            'jc': {
                'is_good': False,
                'death_sound_path': jc_death_sound_path,
                'image_path': jc_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'cow': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': cow_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'ricky': {
                'is_good': False,
                'death_sound_path': ricky_death_sound_path,
                'image_path': ricky_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'david': {
                'is_good': False,
                'death_sound_path': None,
                'image_path': david_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'anton': {
                'is_good': False,
                'death_sound_path': anton_death_sound_path,
                'image_path': anton_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'armando': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': armando_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
            'david2': {
                'is_good': False,
                'death_sound_path': david2_death_sound_path,
                'image_path': david2_path,
                'max_time_alive': 1000,
                'x_speed': 20,
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right'])
            },
        }
        self.clock = pygame.time.Clock()
        self.clouds = []
        self.enemies = []
        self.max_num_enemies = 3
        self.enemy_types = list(self.enemy_info.keys())
        self.frame_rate = 60
        self.max_spawn_counter = 100
        self.num_clouds = 10
        self.num_z_levels = 3
        self.opponent_rangers = []
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.controller = Controller(self.num_z_levels)
        self.screen_manager = ScreenManager(
            sky_path, self.screen_width, self.screen_height)
        self.spawn_counter = self.max_spawn_counter
        self.db = DatabaseIface()
        self.multiplayer_socket = MultiplayerSocket()
        self.player = Player(
            screen_width,
            screen_height,
            self.db,
            self.num_z_levels)

    def run(self):
        # create clouds
        for _ in range(self.num_clouds):
            screen_x, screen_y = self.screen_manager.screen_dimensions
            self.clouds.append(
                Cloud(
                    randrange(0, screen_x, 1),
                    randrange(0, screen_y, 1),
                    0,
                    self.num_z_levels,
                    cloud_path
                )
            )

        # start music
        play_music(background_music_path)

        # game loop
        running = True
        while running:
            # event handler
            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    running = False
                    break

            self.clock.tick(self.frame_rate)
            self.screen_manager.render_background()

            # decrement the countdown until spawning new enemy
            self.spawn_counter -= 1

            # render each cloud
            for cloud in self.clouds:
                cloud.show(self.screen_manager.surface)
                cloud.loop_around(self.screen_width, self.screen_height)

            # spawn an enemy every self.max_spawn_counter frames
            if self.spawn_counter <= 0 and len(
                    self.enemies) < self.max_num_enemies:
                # reset spawn countdown timer
                self.spawn_counter = self.max_spawn_counter
                self.enemies.append(
                    Enemy(
                        randrange(
                            0,
                            self.screen_width,
                            1),
                        100,
                        randrange(0, self.num_z_levels, 1),
                        self.num_z_levels,
                        choice(self.enemy_types),
                        self.enemy_info)
                )

            # ranger movement
            x, y = self.controller.get_xy(
                self.screen_width, self.screen_width,
                self.player.ranger.x, self.player.ranger.y,
                self.player.speed, self.player.max_speed
            )

            # movement acceleration
            if self.controller.is_moving():
                # gradually increase speed when holding down key
                self.player.speed *= self.player.acceleration
            else:
                # reset speed
                self.player.speed = self.player.min_speed
            # update ranger coordinates
            self.player.ranger.update_coordinates(x, y)
            # update z axis
            self.player.ranger.set_level(
                self.controller.get_z(
                    self.player.ranger.z))

            # show laser
            self.player.ranger.fire(
                self.controller.is_firing(),
                self.screen_manager.surface
            )

            # display all enemies
            for enemy in self.enemies:
                enemy.step(self.screen_manager.screen_dimensions)
                # do logic on enemies in same level
                if enemy.z == self.player.ranger.z:
                    # TODO -- move this into a game function
                    if pygame.Rect.colliderect(
                            enemy.rect, self.player.ranger.rect):
                        if enemy.enemy_type in enemy.bad_enemies:
                            # TODO -- lower health instead of points
                            self.player.handle_point_change(-1)
                            # TODO -- remove enemy
                        if enemy.enemy_type in enemy.good_enemies:
                            # TODO -- get back health if you pick up a good
                            # enemy
                            self.player.handle_point_change(1)
                            enemy.health = 0
                    enemy.show(self.screen_manager.surface)

                    # detect laser hits
                    # TODO -- move this into a game function
                    if enemy.should_display \
                            and self.player.ranger.laser_is_deadly \
                            and self.player.ranger.x in enemy.get_x_hitbox() \
                            and self.player.ranger.y > enemy.y \
                            and self.player.ranger.z == enemy.z:
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.handle_point_change(enemy.handle_death())
                else:
                    # display enemies on other levels
                    is_above = enemy.z > self.player.ranger.z
                    enemy.show_diff_level(
                        self.screen_manager.surface, is_above)

                # remove dead and timed out enemies
                if not enemy.should_display:
                    self.enemies.remove(enemy)

            # show ranger
            self.player.ranger.show(self.screen_manager.surface)

            # TODO -- if multiplayer then ...
            # TODO -- loop through opponent rangers and display each one.
            # TODO -- post all data to the multiplayer socket

            # show current score
            self.screen_manager.render_score(self.player.current_score)

            # show current level minimap
            self.screen_manager.render_level(
                self.player.ranger.z, self.num_z_levels, self.enemies)

            # show fps
            self.screen_manager.render_fps(round(self.clock.get_fps()))

            # TODO -- show current health

            # update display
            pygame.display.update()

        print('quitting')
        self.controller.disconnect()
        pygame.quit()
        sys.exit()
