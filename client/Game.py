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
from ServerIface import ServerIface
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
                'x_speed': 3,
                'y_speed': 60,
                'direction': 'left'
            },
            'cow': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': cow_path,
                'max_time_alive': 1000,
                'x_speed': 1,
                'y_speed': 98,
                'direction': 'right'
            },
            'ricky': {
                'is_good': False,
                'death_sound_path': ricky_death_sound_path,
                'image_path': ricky_path,
                'max_time_alive': 1000,
                'x_speed': 2,
                'y_speed': 86,
                'direction': 'left'
            },
            'david': {
                'is_good': False,
                'death_sound_path': None,
                'image_path': david_path,
                'max_time_alive': 1000,
                'x_speed': 3,
                'y_speed': 65,
                'direction': 'right'
            },
            'anton': {
                'is_good': False,
                'death_sound_path': anton_death_sound_path,
                'image_path': anton_path,
                'max_time_alive': 1000,
                'x_speed': 4,
                'y_speed': 81,
                'direction': 'right'
            },
            'armando': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': armando_path,
                'max_time_alive': 1000,
                'x_speed': 3,
                'y_speed': 69,
                'direction': 'left'
            },
            'david2': {
                'is_good': False,
                'death_sound_path': david2_death_sound_path,
                'image_path': david2_path,
                'max_time_alive': 1000,
                'x_speed': 20,
                'y_speed': 50,
                'direction': 'right'
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

        self.game_state = 'start'  # in ['start', 'play', 'multiplayer']
        self.use_camera = True
        self.mouseup = False
        self.mousedown = False

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

        # For multiplayer use
        self.username = ''
        self.room_id = ''
        self.is_host = False
        self.multiplayer_info_asked = False

    def start_screen(self):
        # tick clock
        self.clock.tick(self.frame_rate)

        # display background
        self.screen_manager.render_background()

        # render 1/2 clouds
        for cloud in self.clouds[:len(self.clouds) // 2]:
            cloud.show(self.screen_manager.surface)
            cloud.loop_around(self.screen_width, self.screen_height)

        # show logo
        self.screen_manager.show_logo()

        # render 1/2 clouds
        for cloud in self.clouds[len(self.clouds) // 2:]:
            cloud.show(self.screen_manager.surface)
            cloud.loop_around(self.screen_width, self.screen_height)

        dark_blue = (0, 50, 255)
        light_blue = (0, 100, 255)
        # display buttons and update state
        if self.screen_manager.button(
                'Start Game',
                self.screen_height // 2,
                self.screen_width // 2,
                dark_blue,
                light_blue):
            self.game_state = 'play'

        # multiplayer button
        if self.screen_manager.button(
                'Multiplayer',
                self.screen_height // 2 + 100,
                self.screen_width // 2,
                dark_blue,
                light_blue):
            self.game_state = 'multiplayer'

        # camera toggle
        camera_inactive = light_blue
        camera_active = dark_blue
        if self.screen_manager.button(
                f'Toggle Camera {"off" if self.use_camera else "on"}',
                self.screen_height // 2 + 200,
                self.screen_width // 2,
                camera_active,
                camera_inactive) and self.mousedown:
            self.use_camera = not self.use_camera
            self.controller.use_face = self.use_camera
            camera_active, camera_inactive = camera_inactive, camera_active

        # update display
        pygame.display.update()

    def play(self):
        self.clock.tick(self.frame_rate)
        self.screen_manager.render_background()

        # decrement the countdown until spawning new enemy
        self.spawn_counter -= 1

        # render clouds
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

        # TODO -- might not need this but it is placeholder for now
        # updage game state
        self.game_state = 'play'

    def ask_player_info(self):
        if not self.multiplayer_info_asked:
            print(
                "Would you like to join an existing game(join) or create a new game(create)?: ")
            room_join_status = input().lower()
            self.is_host = True if room_join_status == 'create' else False

            # to make sure that 'other' isn't classified as 'join', a previous
            # bug
            while room_join_status != 'create' and room_join_status != 'join':
                print(
                    "\nLets try that again :/\nWould you like to join an existing game(join) or create a new game(create)?: ")
                room_join_status = input().lower()
                self.is_host = True if room_join_status == 'create' else False

            if self.is_host:
                room_id_question = "Pick a room ID for everyone to join!: "
            else:
                room_id_question = "What is the room ID that you'd like to join?: "
            print(room_id_question)
            self.room_id = "".join(input().split())
            print("What username would you like to use?")
            self.username = "".join(input().split())
            print(
                "is host:",
                'yes' if self.is_host else 'no',
                "room id",
                self.room_id,
                "username",
                self.username)
            # server setup
            self.server = ServerIface(self.username)
            self.server.connect(self.room_id, self.is_host)  # connect to room
            self.multiplayer_info_asked = True
            self.enemy_id_count = 0

    def play_multiplayer(self):
        self.clock.tick(self.frame_rate)
        self.screen_manager.render_background()

        # decrement the countdown until spawning new enemy
        self.spawn_counter -= 1

        # render clouds
        for cloud in self.clouds:
            cloud.show(self.screen_manager.surface)
            cloud.loop_around(self.screen_width, self.screen_height)

        # spawn an enemy every self.max_spawn_counter frames
        if self.spawn_counter <= 0 and len(
                self.enemies) < self.max_num_enemies:
            if self.server.is_host:
                # reset spawn countdown timer
                self.spawn_counter = self.max_spawn_counter
                self.enemy_id_count += 1
                new_enemy = Enemy(
                    randrange(0, self.screen_width, 1),
                    100,
                    randrange(0, self.num_z_levels, 1),
                    self.num_z_levels,
                    choice(self.enemy_types),
                    self.enemy_info,
                    self.enemy_id_count
                )

                self.server.append_new_enemy_to_server(new_enemy)
                self.enemies.append(new_enemy)

            else:
                # if there are enemies from server to be appended..
                while len(self.server.awaiting_new_enemies) > 0:
                    new_enemy = self.server.awaiting_new_enemies.pop()
                    new_enemy_instance = Enemy(
                        new_enemy['x'],
                        new_enemy['y'],
                        new_enemy['z'],
                        self.num_z_levels,
                        new_enemy['enemy_type'],
                        self.enemy_info,
                        new_enemy['id']
                    )
                    self.enemies.append(new_enemy_instance)

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

        # update server coordinates
        self.server.send_location_and_meta(
            x, y, self.player.ranger.z, self.controller.is_firing())

        # show laser
        self.player.ranger.fire(
            self.controller.is_firing(),
            self.screen_manager.surface
        )

        # display all enemies
        for enemy in self.enemies:

            # check if it has been removed from server, set should_display to
            # false if so
            if enemy.id in self.server.awaiting_enemy_despawn:
                enemy.should_display = False
                del self.server.awaiting_enemy_despawn[enemy.id]

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
                    self.server.remove_enemy_from_server(enemy.id)

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

        ################################################
        # Handle opponent rangers
        ################################################
        # Update Ranger Opponents list
        self.opponent_rangers = self.server.opponent_rangers

        # Update Ranger Opponents list
        opponent_dict = {}  # Here so when ranger disconnects, they unspawn
        for opponent_ranger in self.opponent_rangers:
            if opponent_ranger not in opponent_dict:
                opponent = Player(
                    self.screen_width,
                    self.screen_height,
                    self.db,
                    self.num_z_levels)
                opponent_dict[opponent_ranger] = opponent
        # Show and update coordinates of Ranger Opponents
        for opp in opponent_dict:
            try:
                coordinates_and_meta = self.server.opponent_ranger_coordinates[opp]
                opponent_dict[opp].ranger.update_coordinates(
                    coordinates_and_meta[0],
                    coordinates_and_meta[1]
                )
                opponent_dict[opp].ranger.fire(
                    coordinates_and_meta[3],
                    self.screen_manager.surface
                )
                opponent_dict[opp].ranger.show(self.screen_manager.surface)

            except BaseException:
                # for when opponent_ranger_coordinates is not yet updated,
                # we can try again on next rendering
                continue
        ################################################

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

        # TODO -- might not need this but it is placeholder for now
        # updage game state
        self.game_state = 'play_multiplayer'

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
            self.mouseup = False
            self.mousedown = False
            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouseup = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousedown = True

            # game states
            if self.game_state == 'start':
                self.start_screen()
            elif self.game_state == 'play':
                self.play()
            else:
                # multiplayer code?
                if not self.multiplayer_info_asked:
                    self.ask_player_info()
                self.play_multiplayer()

        print('quitting')
        self.controller.disconnect()
        self.server.disconnect()
        pygame.quit()
        sys.exit()
