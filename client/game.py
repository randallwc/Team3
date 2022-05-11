import sys
from random import choice, randrange
from typing import List

import pygame
import pygame_gui
import pyttsx3

from cloud import Cloud
from constants import (CLEAR_SCORE, DARK_BLUE, ENEMY_INFO, FIRE_SCORE,
                       FRAME_RATE, GAME_STATES, GAME_TIMER, LIGHT_BLUE,
                       MAX_FAST_SPEED, MAX_RANGER_ACCELERATION,
                       MAX_RANGER_SPEED, RANGER_ACCELERATION, RED,
                       SCREEN_HEIGHT, SCREEN_WIDTH)
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
        self.display_caption = 'Sky Danger Ranger'
        pygame.init()
        show_mouse(True)
        pygame.display.set_caption(self.display_caption)
        pygame.display.set_icon(
            pygame.image.load(ranger_path)
        )

        # ui stuff
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        # self.manager.set_visual_debug_mode(True)

        # username
        width = SCREEN_WIDTH // 4
        height = SCREEN_HEIGHT // 12
        left = SCREEN_WIDTH // 2 - width // 2
        top = SCREEN_HEIGHT // 2 - height // 2
        unamerect = pygame.Rect(left, top, width, height)
        self.username_gui = pygame_gui.elements.UITextEntryLine(
            unamerect, self.manager)
        self.username_gui.set_text('enter username')

        # is host
        width = SCREEN_WIDTH // 4
        height = SCREEN_HEIGHT // 12
        left = SCREEN_WIDTH // 2 - width // 2
        top = SCREEN_HEIGHT // 2 - height // 2 - 50
        ishostrect = pygame.Rect(left, top, width, height)
        self.is_host_gui = pygame_gui.elements.UIDropDownMenu(
            ['host', 'player'], 'choose one', ishostrect, self.manager)
        self.is_host_gui.hide()

        # room id
        width = SCREEN_WIDTH // 4
        height = SCREEN_HEIGHT // 12
        left = SCREEN_WIDTH // 2 - width // 2
        top = SCREEN_HEIGHT // 2 - height // 2 + 50
        unamerect = pygame.Rect(left, top, width, height)
        self.roomid_gui = pygame_gui.elements.UITextEntryLine(
            unamerect, self.manager)
        self.roomid_gui.set_text('enter roomid')
        self.roomid_gui.hide()

        # Screen Manager settings
        self.screen_manager = ScreenManager(sky_path)

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
        self.time_delta = None

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
        self.play_music = True
        self.use_camera = False

        # powerup flags
        self.fast_timer = 0
        self.max_fast_timer = 500
        self.clear_flag = False
        self.max_clear_cooldown = 500
        self.clear_cooldown = 0
        self.speech_engine = pyttsx3.init()

        # Controller settings
        self.controller = None

        # Player Settings
        self.player = Player(self.num_z_levels)

        # Multiplayer Information
        self.username = None
        self.room_id = None
        self.is_host = None
        self.server = None
        self.enemy_id_count = 0
        self.opponent_ranger_ids = []

        # Database Settings
        self.db = DatabaseIface()
        self.scores_singlegame = []
        self.scores_lifetime = []

    def _ask_for_username(self):
        # break out if got username
        if self.username is not None:
            self.game_state = 'start'
            self.username_gui.hide()
            set_caption(f'{self.username} {self.display_caption}')
            self.controller = Controller(
                self.num_z_levels, self.use_camera, self.username)
            return

        # display background
        self.screen_manager.render_background()

        # show elements
        self.username_gui.show()

        # render clouds
        for cloud in self.clouds:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        self.manager.draw_ui(self.screen_manager.surface)

        # update display
        pygame.display.update()

    def _ask_player_info(self):
        # break out if got is host and room name
        if self.username is not None and self.room_id is not None and self.is_host is not None:
            cap = f'{"host" if self.is_host else "player"} in '
            cap += f'"{self.room_id}" named "{self.username}"'
            set_caption(cap)
            self.game_state = 'multiplayer'
            self.server = ServerIface(self.username)
            self.server.connect(self.room_id, self.is_host)
            self.is_host_gui.hide()
            self.roomid_gui.hide()
            self.start_time = pygame.time.get_ticks()
            return

        # display background
        self.screen_manager.render_background()

        # show elements
        self.is_host_gui.show()
        self.roomid_gui.show()

        # render clouds
        for cloud in self.clouds:
            cloud.show(
                self.screen_manager.surface,
                self.screen_manager.transparent_surface)
            cloud.loop_around()

        self.manager.draw_ui(self.screen_manager.surface)

        # update display
        pygame.display.update()

    def _clear_variables(self):
        # clear variables
        self.controller.voice.reset_words()
        self.dead_enemy_particle_clouds = []
        self.enemies = []
        self.opponent_ranger_ids = []
        self.player.acceleration = RANGER_ACCELERATION
        self.player.current_score = 0
        self.player.max_speed = MAX_RANGER_SPEED
        self.player.ranger.particle_cloud.is_coin_bursting = False
        self.player.ranger.particle_cloud.reset()
        self.player.ranger.x = 0.5 * SCREEN_WIDTH
        self.player.ranger.y = 0.9 * SCREEN_HEIGHT
        self.spawn_counter = self.max_spawn_counter
        # reset room info
        self.room_id = None
        self.is_host = None
        if not self.speech_engine.isBusy():
            self.speech_engine.endLoop()

    def _start_screen(self):
        # clear all variables
        self._clear_variables()

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
                        new_enemy['id'],
                        new_enemy['health'])
                )
        # if you are the host or in single player
        elif self.spawn_counter <= 0 and len(self.enemies) < self.max_num_enemies:
            # reset spawn countdown timer
            self.spawn_counter = self.max_spawn_counter
            # add to enemy id count
            self.enemy_id_count += 1
            new_enemy_type = choice(self.enemy_types)
            new_enemy = Enemy(
                randrange(0, SCREEN_WIDTH, 1),
                100,
                randrange(0, self.num_z_levels, 1),
                self.num_z_levels,
                new_enemy_type,
                ENEMY_INFO,
                self.enemy_id_count,
                ENEMY_INFO[new_enemy_type]['health']
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
            damage = 1
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
            elif enemy.health < ENEMY_INFO[enemy.enemy_type]['health']:
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
                    elif enemy.health < ENEMY_INFO[enemy.enemy_type]['health']:
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
                enemy = self._handle_enemy_laser_hit(enemy)
                enemy.show(
                    self.screen_manager.surface,
                    self.screen_manager.transparent_surface)
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
        if self.clear_flag:
            for enemy in self.enemies:
                enemy.health = 0

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
            self.player.current_score,
            self.scores_singlegame,
            self.scores_lifetime)

        message = 'Main Menu'
        if self.screen_manager.button(
                message,
                SCREEN_HEIGHT - 100,
                SCREEN_WIDTH // 2,
                DARK_BLUE,
                LIGHT_BLUE):
            self.game_state = 'start'

        # render fps
        self.screen_manager.render_fps(round(self.clock.get_fps()))

        # update display
        pygame.display.update()

    def play(self):
        # background render
        self.screen_manager.render_background()

        if not self.speech_engine.isBusy():
            self.speech_engine.endLoop()

        # fast powerup
        wants_fast = self.controller.voice.fast_flag
        self.fast_timer = max(self.fast_timer - 1, 0)
        if wants_fast:
            if self.player.current_score >= FIRE_SCORE and self.fast_timer == 0:
                self.fast_timer = self.max_fast_timer
                self.player.acceleration = MAX_RANGER_ACCELERATION
                self.player.max_speed = MAX_FAST_SPEED
                self.player.ranger.particle_cloud.is_coin_bursting = True
            else:
                point_diff = abs(self.player.current_score - FIRE_SCORE)
                say_string = f"you can't speed up yet you need {point_diff} more points"
                self.speech_engine.say(say_string)
                self.speech_engine.startLoop(False)
                self.speech_engine.iterate()
        elif self.fast_timer == 0:
            self.player.acceleration = RANGER_ACCELERATION
            self.player.max_speed = MAX_RANGER_SPEED
            self.player.ranger.particle_cloud.is_coin_bursting = False

        # wipe powerup
        wants_wipe = self.controller.voice.clear_flag
        self.clear_cooldown = max(self.clear_cooldown - 1, 0)
        if wants_wipe and self.player.current_score >= CLEAR_SCORE:
            self.clear_flag = True
            self.clear_cooldown = self.max_clear_cooldown
        elif not wants_fast and wants_wipe:
            point_diff = abs(self.player.current_score - CLEAR_SCORE)
            say_string = f'you need {point_diff} more points to kill all enemies'
            self.speech_engine.say(say_string)
            self.speech_engine.startLoop(False)
            self.speech_engine.iterate()
        if self.clear_cooldown < self.max_clear_cooldown:
            self.clear_flag = False
        if self.clear_cooldown > self.max_clear_cooldown - 10:
            self.screen_manager.render_background(RED)

        # end powerups
        self.controller.voice.reset_words()

        if self.game_state in ('play', 'multiplayer'):
            self.current_time = pygame.time.get_ticks()
            if abs(self.current_time - self.start_time) > GAME_TIMER:
                self.game_state = 'game_over'

                # add highscores
                assert self.username is not None
                mode = 'singleplayer' if self.game_state == 'play' else 'multiplayer'
                self.db.add_highscore(
                    self.player.current_score, self.username, mode)

                # get highscores
                self.scores_singlegame = self.db.get_highscores(
                    5, mode, 'singlegame')
                self.scores_lifetime = self.db.get_highscores(
                    5, mode, 'lifetime')

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
        if self.game_state in ('play', 'multiplayer'):

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
            # tick clock
            self.time_delta = self.clock.tick(FRAME_RATE) / 1000.0

            # event handler
            self.mouseup = False
            self.mousedown = False
            if self.controller is not None:
                self.fire_edge = self.controller.fire_edge()
            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouseup = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousedown = True
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.username_gui:
                        self.username = event.text
                    if event.ui_element == self.roomid_gui:
                        self.room_id = event.text
                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.is_host_gui:
                        self.is_host = event.text == 'host'

                self.manager.process_events(event)

            self.manager.update(self.time_delta)

            # game states
            if self.game_state == 'ask_username':
                self._ask_for_username()
            elif self.game_state == 'start':
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

        print('quitting')
        if self.controller is not None:
            self.controller.disconnect()
        if self.server is not None:
            self.server.disconnect()
        pygame.quit()
        sys.exit()
