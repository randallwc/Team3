from random import randrange, choice
import Cloud
import Controller
import DatabaseIface
import MultiplayerEnemy
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

        # Ask user if they want to join game or create new one
        # 0 is create new game, 1 is join new game
        mp_game_mode = None
        while mp_game_mode != '0' and mp_game_mode != '1':
            mp_game_mode = input(
                "Would you like to join an existing game(0) or create a new game(1)?: ")
            roomID = ""
            if mp_game_mode == '0':
                roomID = input("What is the room ID that you'd like to join?: ")
            elif mp_game_mode == '1':
                roomID = input("Pick a room ID for everyone to join!: ")
            roomIDStripped = "".join(roomID.split())

            username = input("What username would you like to use? One word only plz: ")
            usernameStripped= "".join(username.split())
            self.username = usernameStripped

            self.isHost = True if mp_game_mode == '1' else False
            self.roomID = roomIDStripped
            print(
                "Multiplayer game mode(isHost):",
                self.isHost,
                "roomID",
                roomIDStripped)

        # pygame initialization
        pygame.init()
        ScreenManager.show_mouse(True)
        pygame.display.set_caption(window_title)
        pygame.display.set_icon(
            pygame.image.load(Paths.ranger_path)
        )

        # Server setup
        self.server = Server.Server(self.username)
        self.server.fetchEnemies()  # Make socket call to fetch and set enemy types
        self.server.connect(self.roomID, self.isHost)  # connect to room
        self.enemy_id_count = 0

        self.clock = pygame.time.Clock()
        self.clouds = []
        self.enemies = []
        self.frame_rate = 60
        self.max_spawn_counter = 100
        self.network = Network.Network()
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

    def add_enemy(self, enemy: MultiplayerEnemy):
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
                # If you are host, you can spawn new enemies
                if self.server.isHost:
                    self.spawn_counter = self.max_spawn_counter
                    current_enemy_type = choice(self.enemy_types)
                    new_enemy = MultiplayerEnemy.MultiplayerEnemy(
                        randrange(
                            0,
                            self.screen_width,
                            1),
                        100,
                        0,
                        1,
                        current_enemy_type,
                        self.enemy_info,
                        self.enemy_id_count
                        )
                    self.enemies.append(new_enemy)
                    self.server.append_new_enemy_to_server(new_enemy)
                    self.enemy_id_count += 1

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
            # update server coordinates
            self.server.sendLocation(x, y, self.player.ranger.z)

            # show laser
            self.player.ranger.fire(
                self.controller.is_firing(),
                self.screen_manager.surface
            )

            ################################################
            ###Handle enemies
            ################################################
            self.server.fetch_all_entities()
            # display all enemies
            for enemy in self.enemies:
                enemy.countdown_time_alive()
                enemy.step(self.screen_manager.screen_dimensions)
                # Update server on where enemy stepped
                enemy_coords = enemy.get_coordinates()
                self.server.update_enemy_coords(enemy.id, enemy_coords[0], enemy_coords[1])
                if enemy.should_display:
                    # detect laser hits
                    if self.player.ranger.laser_is_deadly and self.player.ranger.x in enemy.get_x_hitbox():
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.current_score += enemy.handle_death()
                else:
                    # remove dead and timed out enemies
                    self.enemies.remove(enemy)
                    if self.server.isHost:
                        self.server.remove_enemy_from_server(enemy.id)

            for enemy in self.server.host_enemies:
                enemy.show(self.screen_manager.surface)

                # Update server on where enemy stepped
                if enemy.should_display:
                    # detect laser hits
                    if self.player.ranger.laser_is_deadly and self.player.ranger.x in enemy.get_x_hitbox():
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.current_score += enemy.handle_death()
                else:
                    # Not only host, if you hit it, you can remove it
                    self.server.remove_enemy_from_server(enemy.id)
            ################################################

            # show ranger
            self.player.ranger.show(self.screen_manager.surface)


            ################################################
            ###Handle opponent rangers
            ################################################
            self.server.fetchRangerOpponents()
            self.opponent_rangers = self.server.opponent_rangers

            # Update Ranger Opponents list
            opponent_dict = {}
            for opponent_ranger in self.opponent_rangers:
                if opponent_ranger not in opponent_dict:
                    opponent = Player.Player(self.screen_width, self.screen_height, self.db)
                    opponent_dict[opponent_ranger] = opponent
            # Show and update coords of Ranger Opponents
            for opp in opponent_dict:
                try:
                    coords = self.server.opponent_ranger_coordinates[opp]
                    opponent_dict[opp].ranger.update_coordinates(coords[0], coords[1])
                    opponent_dict[opp].ranger.show(self.screen_manager.surface)

                except:
                    # for when opponent_ranger_coordinates is not yet updated, we can try again on next rendering
                    continue

            # uncomment this to print out all opponent rangers' socketIDs
            #print('list of opponent rangers',self.server.opponent_rangers)
            ################################################

            # show current score
            self.screen_manager.render_score(self.player.current_score)

            # update display
            pygame.display.update()
