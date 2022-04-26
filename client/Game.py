import sys
import uuid
from random import choice, randrange
from typing import List

import pygame

from cloud import Cloud
from constants import (DARK_BLUE, ENEMY_INFO, FRAME_RATE, GAME_STATES,
                       GAME_TIMER, LIGHT_BLUE, SCREEN_HEIGHT, SCREEN_WIDTH)
from controller import Controller
from database_iface import DatabaseIface
from enemy import Enemy
from opponent_ranger import OpponentRanger
from particle_cloud import ParticleCloud
from paths import background_music_path, cloud_path, ranger_path, sky_path
from player import Player
from screen_manager import ScreenManager, set_caption, show_mouse
from server_iface import ServerIface
from sounds import is_playing_sounds, play_music, stop_music


class Game:
    def __init__(self):
        # pygame initialization
        pygame.init()
        show_mouse(True)
        pygame.display.set_caption('Sky Danger Ranger')
        pygame.display.set_icon(
            pygame.image.load(ranger_path)
        )

        # enemies
        self.enemies: List[Enemy] = []
        self.enemy_types = list(ENEMY_INFO.keys())
        self.max_num_enemies = 3
        self.max_spawn_counter = 100
        self.spawn_counter = self.max_spawn_counter

        # game state
        self.game_state = GAME_STATES[0]

        # game timer
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.start_time = 0

        # clouds
        self.clouds: List[Cloud] = []
        self.num_clouds = 10

        # particles
        self.dead_enemy_particle_clouds: List[ParticleCloud] = []

        # ranger laser
        self.fire_edge = False

        # mouse clicks
        self.mousedown = False
        self.mouseup = False

        # game settings
        self.num_z_levels = 3
        self.play_music = False
        self.use_camera = False

        # Controller settings
        self.controller = Controller(self.num_z_levels, self.use_camera)

        # Screen Manager settings
        self.screen_manager = ScreenManager(sky_path)

        # Player Settings
        self.player = Player(self.num_z_levels)

        # Multiplayer Information
        self.username = uuid.getnode()
        self.room_id = ''
        self.is_host = False
        self.server = None
        self.enemy_id_count = 0
        self.opponent_ranger_ids = []

        # Database Settings
        self.db = DatabaseIface()
        # n_scores, number of scores to return
        self.n_scores = 3
        # mode, 'multiplayer' or 'singleplayer'
        self.mode = 'singleplayer'
        # score_kind, 'lifetime' or 'singlegame'
        self.score_kind = 'lifetime'
        self.scores = self.db.get_highscores(
            self.n_scores, self.mode, self.score_kind)

    def _start_screen(self):
        # tick clock
        self.clock.tick(FRAME_RATE)

        # display background
        self.screen_manager.render_background()

        # render 1/2 clouds
        for cloud in self.clouds[:len(self.clouds) // 2]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        # show logo
        self.screen_manager.show_logo()

        # render 1/2 clouds
        for cloud in self.clouds[len(self.clouds) // 2:]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        # display buttons and update state
        if self.screen_manager.button(
                'Start Game',
                SCREEN_HEIGHT // 2,
                SCREEN_WIDTH // 2,
                DARK_BLUE,
                LIGHT_BLUE):
            self.game_state = 'play'
            self.start_time = pygame.time.get_ticks()

        # multiplayer button
        if self.screen_manager.button(
                'Multiplayer',
                SCREEN_HEIGHT // 2 + 100,
                SCREEN_WIDTH // 2,
                DARK_BLUE,
                LIGHT_BLUE):
            self.game_state = 'multiplayer_start'

        # camera toggle
        if self.screen_manager.button(
                f'Toggle Camera {"off" if self.use_camera else "on"}',
                SCREEN_HEIGHT // 2 + 200,
                SCREEN_WIDTH // 2,
                DARK_BLUE,
                LIGHT_BLUE) and self.mousedown:
            self.use_camera = not self.use_camera
        self.controller.use_camera(self.use_camera)

        # music toggle
        is_playing = is_playing_sounds()
        if self.screen_manager.button(
                f'sound {"off" if self.play_music else "on"}',
                SCREEN_HEIGHT - 100,
                100,
                DARK_BLUE,
                LIGHT_BLUE) and self.mousedown:
            self.play_music = not self.play_music
        if self.play_music and not is_playing:
            play_music(background_music_path)
        elif not self.play_music and is_playing:
            stop_music()

        # update display
        pygame.display.update()

    def _ask_player_info(self):
        prompt = "Would you like to join an existing game(join) "
        prompt += "or create a new game(create)?: "
        retry_prompt = "Lets try that again :/"
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
        set_caption(
            f'{"host" if self.is_host else "player"} in "{self.room_id}" named "{self.username}"')
        self.game_state = 'multiplayer'

    def _spawn_enemies(self):
        # if you joined a game
        if self.game_state == 'multiplayer' and not self.is_host:
            # if there are enemies from server to be appended.
            while len(self.server.awaiting_new_enemies) > 0:
                new_enemy = self.server.awaiting_new_enemies.pop()
                # TODO -- get each enemies' health
                self.enemies.append(
                    Enemy(
                        new_enemy['x'],
                        new_enemy['y'],
                        new_enemy['z'],
                        self.num_z_levels,
                        new_enemy['enemy_type'],
                        ENEMY_INFO,
                        new_enemy['id'])
                )
        # if you are the host or in single player
        elif self.spawn_counter <= 0 and len(self.enemies) < self.max_num_enemies:
            # reset spawn countdown timer
            self.spawn_counter = self.max_spawn_counter
            # add to enemy id count
            self.enemy_id_count += 1
            new_enemy = Enemy(
                randrange(0, SCREEN_WIDTH, 1),
                100,
                randrange(0, self.num_z_levels, 1),
                self.num_z_levels,
                choice(self.enemy_types),
                ENEMY_INFO,
                self.enemy_id_count
            )
            self.enemies.append(new_enemy)
            if self.game_state == 'multiplayer' and self.is_host:
                self.server.append_new_enemy_to_server(new_enemy)

    def _handle_enemy_collision(self, enemy: Enemy):
        # TODO -- send when enemy is collided with
        if pygame.Rect.colliderect(
                enemy.rect, self.player.ranger.rect):
            if enemy.enemy_type in enemy.bad_enemies:
                # TODO -- lower health instead of points
                self.player.handle_point_change(-10)
                # TODO -- send server that ranger was damaged
                # despawn bad enemy if touched
                enemy.health = 0
            if enemy.enemy_type in enemy.good_enemies:
                # TODO -- get back health if you pick up a good enemy
                self.player.handle_point_change(10)
                self.player.ranger.particle_cloud.coin_burst(10)
                # TODO -- send server that ranger gained health
                enemy.health = 0
        return enemy

    def _handle_enemy_laser_hit(self, enemy: Enemy):
        def _hit_enemy() -> bool:
            return enemy.should_display \
                and self.player.ranger.laser_is_deadly \
                and self.player.ranger.x in enemy.get_x_hitbox() \
                and self.player.ranger.y > enemy.y \
                and self.player.ranger.z == enemy.z

        if _hit_enemy():
            damage = 0.5
            enemy.got_hit(damage)
            if self.game_state == 'multiplayer':
                self.server.send_enemy_was_hit(enemy.id, enemy.health)
            # dead
            if enemy.health <= 0:
                # good enemy dead
                if enemy.enemy_type in enemy.good_enemies:
                    # auto get hurt if enemy is good and you killed it
                    self.player.handle_point_change(enemy.handle_death())
                    # TODO -- server send player was damaged
                # bad enemy dead
                else:
                    # gain points
                    self.player.handle_point_change(enemy.handle_death())
                    # show fire cloud
                    particle_cloud = ParticleCloud(enemy.x, enemy.y)
                    particle_cloud.fire_burst(10)
                    self.dead_enemy_particle_clouds.append(particle_cloud)
            # hurt
            elif enemy.health < 1:
                # any enemy that is hurt smokes
                enemy.particle_cloud.is_smoking = True
                # good enemy hurt
                if enemy.enemy_type in enemy.good_enemies:
                    # auto get hurt if enemy is good
                    self.player.handle_point_change(enemy.handle_death())
                    # TODO -- server send player was damaged
                # bad enemy hurt
                else:
                    pass
        return enemy

    def _display_enemies(self):
        for i, enemy in enumerate(self.enemies):
            if self.game_state == 'multiplayer':
                # if enemy was hurt by other players, make it smoke
                if enemy.id in self.server.enemies_hurt:
                    enemy.health = self.server.enemies_hurt[enemy.id]
                    if enemy.health <= 0:
                        # if enemy was bad, make it blow up upon death
                        if enemy.enemy_type in enemy.bad_enemies:
                            new_particle_cloud = ParticleCloud(
                                enemy.x, enemy.y)
                            new_particle_cloud.fire_burst(10)
                            self.dead_enemy_particle_clouds.append(
                                new_particle_cloud)
                        # TODO -- if enemy is good make ranger that hit it have
                        # a fire cloud
                    elif enemy.health < 1:
                        enemy.particle_cloud.is_smoking = True
                    del self.server.enemies_hurt[enemy.id]
                # check if it has been removed from server, set should_display to
                # false if so
                if enemy.id in self.server.awaiting_enemy_despawn:
                    enemy.should_display = False
                    del self.server.awaiting_enemy_despawn[enemy.id]

                # if this is the host
                # and there are new players awaiting the existing enemies
                if self.is_host and len(
                        self.server.new_players_awaiting_enemies) > 0 and enemy.should_display:
                    # do this in reverse so we don't shift any elements
                    # send this enemy to all players awaiting enemies
                    num_enemies_final_index = len(self.enemies) - 1
                    for index, player_id in reversed(
                            list(enumerate(self.server.new_players_awaiting_enemies))):
                        # send the enemy to new user
                        self.server.append_new_enemy_to_server(
                            enemy, player_id)

                        if i == num_enemies_final_index:
                            # we have finished sending the new users the
                            # current enemies
                            self.server.new_players_awaiting_enemies.pop(index)

            enemy.step()
            # do logic on enemies in same level
            if enemy.z == self.player.ranger.z:
                enemy = self._handle_enemy_collision(enemy)
                enemy.show(
                    self.screen_manager.surface,
                    self.screen_manager.transparent_surface)
                self._handle_enemy_laser_hit(enemy)
            else:
                # display enemies on other levels
                is_above = enemy.z > self.player.ranger.z
                enemy.show_diff_level(
                    self.screen_manager.surface,
                    self.screen_manager.transparent_surface,
                    is_above)
            if self.game_state == 'multiplayer' and not enemy.should_display:
                self.server.remove_enemy_from_server(enemy.id)
        self.enemies = [
            enemy for enemy in self.enemies if enemy.should_display]

    def _update_ranger_opponents(self):
        if self.game_state != 'multiplayer':
            return
        # get a list of ranger id's
        self.opponent_ranger_ids = self.server.opponent_rangers
        for opponent_ranger_id in self.opponent_ranger_ids:
            metadata = self.server.opponent_ranger_coordinates.get(
                opponent_ranger_id, None)
            if metadata is None:
                continue
            x, y, z, is_firing = metadata
            # create new rangers
            opponent_ranger = OpponentRanger(
                x,
                y,
                z,
                self.num_z_levels,
                opponent_ranger_id)
            opponent_ranger.update_coordinates(x, y)
            # hard code enemies to not have deadly lasers purely cosmetic
            opp_firing = False
            opponent_ranger.fire(
                is_firing,
                opp_firing,
                self.screen_manager.surface)
            opponent_ranger.show_diff_level(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface,
                self.player.ranger.z)

    def _update_ranger_server_coordinates(self):
        if self.game_state != 'multiplayer':
            return
        self.server.send_location_and_meta(
            self.player.ranger.x,
            self.player.ranger.y,
            self.player.ranger.z,
            self.controller.is_firing())

    def _game_over(self):
        # tick clock
        self.clock.tick(FRAME_RATE)

        # display background
        self.screen_manager.render_background()

        # render 1/2 clouds
        for cloud in self.clouds[:len(self.clouds) // 2]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        self.screen_manager.show_game_over()

        # render 1/2 clouds
        for cloud in self.clouds[len(self.clouds) // 2:]:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        self.screen_manager.render_final_scores(
            self.player.current_score, self.scores)

        message = 'Main Menu'
        if self.screen_manager.button(
                message,
                SCREEN_HEIGHT - 100,
                SCREEN_WIDTH // 2,
                DARK_BLUE,
                LIGHT_BLUE):
            self.game_state = 'start'
            # clear variables
            self.enemies = []
            start_x = 0.5 * SCREEN_WIDTH
            start_y = 0.9 * SCREEN_HEIGHT
            self.player.ranger.x = start_x
            self.player.ranger.y = start_y
            self.player.current_score = 0
            self.opponent_ranger_ids = []
            self.dead_enemy_particle_clouds = []
            self.spawn_counter = self.max_spawn_counter

        # update display
        pygame.display.update()

    def play(self):
        self.clock.tick(FRAME_RATE)
        self.screen_manager.render_background()

        # TODO -- if timer is over game over and display score
        if self.game_state == 'play':
            self.current_time = pygame.time.get_ticks()
            if abs(self.current_time - self.start_time) > GAME_TIMER:
                # TODO -- add score as high score
                # TODO -- fetch high scores
                self.game_state = 'game_over'

        # remove all particles
        self.screen_manager.reset_particles()

        # decrement the countdown until spawning new enemy
        self.spawn_counter -= 1

        # render clouds
        for cloud in self.clouds:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        # spawn an enemy every self.max_spawn_counter frames
        self._spawn_enemies()

        # ranger movement
        x, y = self.controller.get_xy(
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
        self._update_ranger_server_coordinates()

        # show laser
        self.player.ranger.fire(
            self.controller.is_firing(),
            self.fire_edge,
            self.screen_manager.surface
        )

        # display all enemies
        self._display_enemies()

        # show ranger
        self.player.ranger.show(
            self.screen_manager.surface,
            self.screen_manager.transparent_surface)

        # update ranger opponents
        self._update_ranger_opponents()

        # show current score
        self.screen_manager.render_score(self.player.current_score)

        # show current level minimap
        self.screen_manager.render_level(
            self.player.ranger.z, self.num_z_levels, self.enemies)

        # show fps
        self.screen_manager.render_fps(round(self.clock.get_fps()))

        # show timer
        if self.game_state == 'play':
            self.screen_manager.render_time(
                (GAME_TIMER - (self.current_time - self.start_time)) // 1000)

        # TODO -- show current health

        # show particles
        for particle_cloud in self.dead_enemy_particle_clouds:
            particle_cloud.show(self.screen_manager.transparent_surface)
        self.dead_enemy_particle_clouds = [
            cloud for cloud in self.dead_enemy_particle_clouds if len(
                cloud.particles) > 0]
        self.screen_manager.show_particles()

        # update display
        pygame.display.update()

    def run(self):
        # create clouds
        for _ in range(self.num_clouds):
            self.clouds.append(
                Cloud(
                    randrange(0, SCREEN_WIDTH, 1),
                    randrange(0, SCREEN_HEIGHT, 1),
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
                self._start_screen()
            elif self.game_state == 'play':
                self.play()
            elif self.game_state == 'multiplayer_start':
                self._ask_player_info()
            elif self.game_state == 'multiplayer':
                self.play()
            elif self.game_state == 'game_over':
                self._game_over()
            else:
                if self.game_state not in GAME_STATES:
                    print('error in game state')
                    sys.exit(1)
                print(self.game_state)

            # print('\r',
            #       'pc:', len(self.dead_enemy_particle_clouds),
            #       'en:', len(self.enemies),
            #       'ori:', len(self.opponent_ranger_ids),
            #       'cl', len(self.clouds),
            #       end='')

        print('quitting')
        self.controller.disconnect()
        if self.server is not None:
            self.server.disconnect()
        pygame.quit()
        sys.exit()
