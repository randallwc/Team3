from random import randrange, choice
import Cloud
import Controller
import DatabaseIface
import Enemy
import MultiplayerSocket
import Network
import OpponentRanger
import Paths
import Player
import ScreenManager
import pygame
import sys


class Game:
    def __init__(self, screen_width=1280, screen_height=720, window_title='Sky Danger Ranger'):
        self.network = Network.Network()
        self.db = DatabaseIface.DatabaseIface(self.network)
        self.multiplayer_socket = MultiplayerSocket.MultiplayerSocket(self.network)
        pygame.init()
        pygame.display.set_caption(window_title)
        ScreenManager.show_mouse(True)
        self.clock = pygame.time.Clock()
        self.clouds = []
        self.controller = Controller.Controller(self.network)
        self.enemies = []
        self.frame_rate = 60
        self.num_z_levels = 1
        self.opponent_rangers = []
        self.player = Player.Player()
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.screen_manager = ScreenManager.ScreenManager(Paths.sky_path, self.screen_width, self.screen_height)
        self.enemy_types = ['jc', 'ricky', 'cow']
        self.max_spawn_counter = 100
        self.spawn_counter = self.max_spawn_counter

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def add_opponent_rangers(self, opponent: OpponentRanger):
        self.opponent_rangers.append(opponent)

    def add_cloud(self, cloud: Cloud):
        self.clouds.append(cloud)

    def run(self):
        for _ in range(4):
            screen_x, screen_y = self.screen_manager.screen_dimensions
            self.add_cloud(
                Cloud.Cloud(
                    randrange(0, screen_x, 1),
                    randrange(0, screen_y, 1),
                    0,
                    self.num_z_levels,
                    Paths.cloud_path
                )
            )

        screen_x, screen_y = self.screen_manager.screen_dimensions

        while True:
            self.clock.tick(self.frame_rate)
            self.screen_manager.render_background()
            self.spawn_counter -= 1

            # render each cloud
            for cloud in self.clouds:
                cloud.show(self.screen_manager.surface)
                cloud.loop_around(self.screen_width, self.screen_height)

            # if the timer counted down or there are no enemies
            if self.spawn_counter <= 0 or not len(self.enemies):
                self.spawn_counter = self.max_spawn_counter
                current_enemy_type = choice(self.enemy_types)
                self.enemies.append(
                    Enemy.Enemy(randrange(0, screen_x, 1), 100, 0, 1, current_enemy_type)
                )

            # display all enemies
            for enemy in self.enemies:
                enemy.show(self.screen_manager.surface)

                # if you just clicked then this is true
                if self.player.laser_is_deadly:
                    self.player.update_coordinates()
                    # if the mouse is in the range of the enemy's x htibox then they lose health
                    if self.player.coordinates[0] in enemy.get_x_hitbox():
                        enemy.health = 0
                        self.player.current_score += enemy.handle_death()
                        print(self.player.current_score)

                # some enemies should not be shot, and you remove those when their health is gone
                # but your score does not increase
                if enemy.health <= 0:
                    self.enemies.remove(enemy)

            # get x and y coordinates from controller
            x, y = self.controller.get_xy()
            self.player.ranger.update_coordinates(x, y)

            # if player is clicking fire then show laser
            self.player.fire(
                self.controller.is_clicking(),
                self.screen_manager.surface
            )

            # show ranger
            self.player.ranger.show(self.screen_manager.surface)

            # show current score
            self.screen_manager.render_score(self.player.current_score)

            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    sys.exit()

            pygame.display.update()
