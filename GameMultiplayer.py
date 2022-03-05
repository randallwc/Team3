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
import Server


class GameMultiplayer:
    def __init__(self, screen_width=1280, screen_height=720,
                 window_title='Sky Danger Ranger'):
        # pygame initialization
        pygame.init()
        ScreenManager.show_mouse(True)
        pygame.display.set_caption(window_title)
        pygame.display.set_icon(
            pygame.image.load(Paths.ranger_path)
        )

        self.clock = pygame.time.Clock()
        self.clouds = []
        self.enemies = []
        self.frame_rate = 60
        self.max_spawn_counter = 100
        self.network = Network.Network()
        self.server = Server.Server()
        self.server.fetchEnemies()  # Make socket call to fetch and set enemies
        self.num_clouds = 8
        self.num_z_levels = 1
        self.opponent_rangers = []
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.controller = Controller.Controller(self.network)
        self.screen_manager = ScreenManager.ScreenManager(
            Paths.sky_path, self.screen_width, self.screen_height)
        self.spawn_counter = self.max_spawn_counter
        self.db = DatabaseIface.DatabaseIface(self.network)
        self.multiplayer_socket = MultiplayerSocket.MultiplayerSocket(
            self.network)
        self.player = Player.Player(screen_width, screen_height, self.db)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def add_opponent_rangers(self, opponent: OpponentRanger):
        self.opponent_rangers.append(opponent)

    def add_cloud(self, cloud: Cloud):
        self.clouds.append(cloud)

    def run(self):
        # Did here so self.server.serverEnemies is not null,
        # tried it in init & didnt work
        self.enemy_info = self.server.serverEnemies
        self.enemy_types = list(self.enemy_info.keys())

        # create clouds
        for _ in range(self.num_clouds):
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

        # game loop
        running = True
        while running:
            # event handler
            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    running = False

            self.clock.tick(self.frame_rate)
            self.screen_manager.render_background()
            self.spawn_counter -= 1

            # render each cloud
            for cloud in self.clouds:
                cloud.show(self.screen_manager.surface)
                cloud.loop_around(self.screen_width, self.screen_height)

            # spawn an enemy every self.max_spawn_counter frames
            if self.spawn_counter <= 0:
                self.spawn_counter = self.max_spawn_counter
                current_enemy_type = choice(self.enemy_types)
                self.enemies.append(
                    Enemy.Enemy(
                        randrange(
                            0,
                            self.screen_width,
                            1),
                        100,
                        0,
                        1,
                        current_enemy_type,
                        self.enemy_info)
                )

            # ranger movement
            x, y = self.controller.get_xy(
                self.screen_width, self.screen_width,
                self.player.ranger.x, self.player.ranger.y,
                self.player.speed, self.player.max_speed
            )
            if self.controller.is_moving():
                # gradually increase speed when holding down key
                self.player.speed *= self.player.acceleration
            else:
                # reset speed
                self.player.speed = self.player.min_speed
            # update ranger coordinates
            self.player.ranger.update_coordinates(x, y)

            # show laser
            self.player.ranger.fire(
                self.controller.is_firing(),
                self.screen_manager.surface
            )

            # display all enemies
            for enemy in self.enemies:
                enemy.show(self.screen_manager.surface)
                enemy.step(self.screen_manager.screen_dimensions)
                if enemy.should_display:
                    # detect laser hits
                    if self.player.ranger.laser_is_deadly and self.player.ranger.x in enemy.get_x_hitbox():
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.current_score += enemy.handle_death()
                else:
                    # remove dead and timed out enemies
                    self.enemies.remove(enemy)

            # show ranger
            self.player.ranger.show(self.screen_manager.surface)

            # TODO -- if multiplayer then ...
            # TODO -- loop through opponent rangers and display each one.
            # TODO -- post all data to the multiplayer socket

            # show current score
            self.screen_manager.render_score(self.player.current_score)

            # update display
            pygame.display.update()
