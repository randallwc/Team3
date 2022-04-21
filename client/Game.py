import sys
from random import choice, randrange
from typing import List

import pygame

from Cloud import Cloud
from Controller import Controller
from DatabaseIface import DatabaseIface
from Enemy import Enemy
from MultiplayerSocket import MultiplayerSocket
from OpponentRanger import OpponentRanger
from Paths import (anton_death_sound_path, anton_path, armando_path,
                   background_music_path, cloud_path, cow_path,
                   david2_death_sound_path, david2_path, david_path,
                   friendly_fire_sound_path, jc_death_sound_path, jc_path,
                   ranger_path, ricky_death_sound_path, ricky_path, sky_path)
from Player import Player
from ScreenManager import ScreenManager, show_mouse
from ServerIface import ServerIface
from Sounds import play_music, stop_music, is_playing_sounds


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
        self.clouds: List[Cloud] = []
        self.enemies: List[Enemy] = []
        self.max_num_enemies = 3
        self.enemy_types = list(self.enemy_info.keys())
        self.frame_rate = 60
        self.max_spawn_counter = 100
        self.num_clouds = 10
        self.num_z_levels = 3
        self.opponent_ranger_ids = []
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.game_state = 'start'  # in ['start', 'play', 'multiplayer']
        self.use_camera = False
        self.mouseup = False
        self.mousedown = False
        self.fire_edge = False
        self.play_music = True

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
        self.controller.use_face = self.use_camera

        # For multiplayer use
        self.username = ''
        self.room_id = ''
        self.is_host = False
        self.multiplayer_info_asked = False
        self.server = None
        self.enemy_id_count = 0

    def start_screen(self):
        # tick clock
        self.clock.tick(self.frame_rate)

        # display background
        self.screen_manager.render_background()

        # render 1/2 clouds
        for cloud in self.clouds[:len(self.clouds) // 2]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around(self.screen_width, self.screen_height)

        # show logo
        self.screen_manager.show_logo()

        # render 1/2 clouds
        for cloud in self.clouds[len(self.clouds) // 2:]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
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
        if self.screen_manager.button(
                f'Toggle Camera {"off" if self.use_camera else "on"}',
                self.screen_height // 2 + 200,
                self.screen_width // 2,
                dark_blue,
                light_blue) and self.mousedown:
            self.use_camera = not self.use_camera
        self.controller.use_face = self.use_camera

        # music toggle
        is_playing = is_playing_sounds()
        if self.screen_manager.button(
                f'sound {"off" if self.play_music else "on"}',
                self.screen_height - 100,
                100,
                dark_blue,
                light_blue) and self.mousedown:
            self.play_music = not self.play_music
        if self.play_music and not is_playing:
            play_music(background_music_path)
        elif not self.play_music and is_playing:
            stop_music()

        # update display
        pygame.display.update()

    def ask_player_info(self):
        prompt = "Would you like to join an existing game(join) "
        prompt += "or create a new game(create)?: "
        retry_prompt = "Lets try that again :/"
        if not self.multiplayer_info_asked:
            print(prompt)
            room_join_status = input().lower().strip()
            self.is_host = bool(room_join_status == 'create')

            # to make sure that 'other' isn't classified as 'join', a previous
            # bug
            while room_join_status not in ('create', 'join'):
                print(retry_prompt, prompt, sep='\n')
                room_join_status = input().lower()
                self.is_host = bool(room_join_status == 'create')

            if self.is_host:
                room_id_question = "Pick a room ID for everyone to join!: "
            else:
                room_id_question = "What is the room ID that you'd like to join?: "
            print(room_id_question)
            self.room_id = "".join(input().split())
            print("What username would you like to use?")
            self.username = "".join(input().split())
            print("is host:", 'yes' if self.is_host else 'no')
            print("room id:", self.room_id)
            print("username:", self.username)
            # server setup
            self.server = ServerIface(self.username)
            self.server.connect(self.room_id, self.is_host)  # connect to room
            self.multiplayer_info_asked = True
            pygame.display.set_caption(
                f'{"host" if self.is_host else "player"} in "{self.room_id}" named "{self.username}"')

    def spawn_enemies(self):
        # if you joined a game
        if self.game_state == 'multiplayer' and not self.is_host:
            # if there are enemies from server to be appended.
            while len(self.server.awaiting_new_enemies) > 0:
                new_enemy = self.server.awaiting_new_enemies.pop()
                self.enemies.append(
                    Enemy(
                        new_enemy['x'],
                        new_enemy['y'],
                        new_enemy['z'],
                        self.num_z_levels,
                        new_enemy['enemy_type'],
                        self.enemy_info,
                        new_enemy['id'])
                )
        # if you are the host or in single player
        elif self.spawn_counter <= 0 and len(self.enemies) < self.max_num_enemies:
            # reset spawn countdown timer
            self.spawn_counter = self.max_spawn_counter
            # add to enemy id count
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
            self.enemies.append(new_enemy)
            if self.game_state == 'multiplayer' and self.is_host:
                self.server.append_new_enemy_to_server(new_enemy)

    def display_enemies(self):
        for enemy in self.enemies:
            if self.game_state == 'multiplayer':
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
                enemy.show(
                    self.screen_manager.surface,
                    self.screen_manager.transparent_surface)

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
                    if self.game_state == 'multiplayer':
                        self.server.remove_enemy_from_server(enemy.id)
            else:
                # display enemies on other levels
                is_above = enemy.z > self.player.ranger.z
                enemy.show_diff_level(
                    self.screen_manager.surface,
                    self.screen_manager.transparent_surface,
                    is_above)

            # remove dead and timed out enemies
            if not enemy.should_display:
                self.enemies.remove(enemy)

    def update_ranger_opponents(self):
        if self.game_state == 'play':
            return
        if self.game_state != 'multiplayer':
            print('error in game state')
            sys.exit(1)
        # get a list of ranger id's
        self.opponent_ranger_ids = self.server.opponent_rangers
        for opponent_ranger in self.opponent_ranger_ids:
            metadata = self.server.opponent_ranger_coordinates.get(
                opponent_ranger, None)
            if metadata is None:
                continue
            x, y, z, is_firing = metadata
            # create new rangers
            opponent_ranger = OpponentRanger(
                x, y, z, self.num_z_levels, self.screen_width, self.screen_height)
            opponent_ranger.update_coordinates(x, y)
            opp_firing = False  # TODO -- hard code enemies to not have deadly lasers purely cosmetic
            opponent_ranger.fire(
                is_firing,
                opp_firing,
                self.screen_manager.surface)
            opponent_ranger.show_diff_level(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface,
                self.player.ranger.z)

    def update_ranger_server_coordinates(self):
        if self.game_state == 'multiplayer':
            self.server.send_location_and_meta(
                self.player.ranger.x,
                self.player.ranger.y,
                self.player.ranger.z,
                self.controller.is_firing())
        elif self.game_state != 'play':
            print('error in game state')
            sys.exit(1)

    def play(self):
        self.clock.tick(self.frame_rate)
        self.screen_manager.render_background()

        # remove all particles
        self.screen_manager.reset_particles()

        # decrement the countdown until spawning new enemy
        self.spawn_counter -= 1

        # render clouds
        for cloud in self.clouds:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around(self.screen_width, self.screen_height)

        # spawn an enemy every self.max_spawn_counter frames
        self.spawn_enemies()

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
        self.update_ranger_server_coordinates()

        # show laser
        self.player.ranger.fire(
            self.controller.is_firing(),
            self.fire_edge,
            self.screen_manager.surface
        )

        # display all enemies
        self.display_enemies()

        # show ranger
        self.player.ranger.show(
            self.screen_manager.surface,
            self.screen_manager.transparent_surface)

        # update ranger opponents
        self.update_ranger_opponents()

        # show current score
        self.screen_manager.render_score(self.player.current_score)

        # show current level minimap
        self.screen_manager.render_level(
            self.player.ranger.z, self.num_z_levels, self.enemies)

        # show fps
        self.screen_manager.render_fps(round(self.clock.get_fps()))

        # TODO -- show current health

        # show particles
        self.screen_manager.show_particles()

        # update display
        pygame.display.update()

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
        if self.play_music:
            play_music(background_music_path)

        # game loop
        running = True
        while running:
            # event handler
            self.mouseup = False
            self.mousedown = False
            self.fire_edge = self.controller.fire_edge()
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
            elif self.game_state == 'multiplayer':
                if not self.multiplayer_info_asked:
                    self.ask_player_info()
                self.play()
            else:
                print('error in game state')
                sys.exit(1)

        print('quitting')
        self.controller.disconnect()
        if self.server is not None:
            self.server.disconnect()
        pygame.quit()
        sys.exit()
