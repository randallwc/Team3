import math

import pygame

from constants import (BACKGROUND_BLUE, BLACK, FONT, FONT_SIZE, GAME_TIMER,
                       LIGHT_BLUE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE)
from paths import gameover_path, logo_path


def show_mouse(is_visible: bool):
    pygame.mouse.set_visible(is_visible)


def set_caption(caption: str):
    pygame.display.set_caption(caption)


class ScreenManager:
    def __init__(self, background_image_path):
        self.background_image_path = background_image_path
        self.pygame_loaded_background = pygame.image.load(
            self.background_image_path)
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transparent_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.game_over_logo = pygame.transform.rotozoom(
            pygame.image.load(gameover_path), 0, 0.1)
        self.game_over_rect = self.game_over_logo.get_rect()
        self.logo = pygame.transform.rotozoom(
            pygame.image.load(logo_path), 0, 0.5)
        self.logo_rect = self.logo.get_rect()

    def reset_particles(self):
        self.transparent_surface.fill((0, 0, 0, 0))

    def show_particles(self):
        self.surface.blit(self.transparent_surface, (0, 0))

    def _set_background(self, image_path):
        self.background_image_path = image_path
        self.pygame_loaded_background = pygame.image.load(image_path)

    def render_background(self, color=BACKGROUND_BLUE):
        self.surface.fill(color)

    def render_score(self, current_score: int):
        foreground_color = BLACK
        background_color = WHITE
        font = pygame.font.SysFont(FONT, FONT_SIZE)
        rendered_font = font.render(
            f'score: {current_score}',
            True,
            foreground_color,
            background_color)
        self.surface.blit(
            rendered_font,
            (SCREEN_WIDTH - 100 - rendered_font.get_width() // 2,
             SCREEN_HEIGHT - 100))

    def render_final_scores(
            self,
            current_score: int,
            scores_singlegame,
            scores_lifetime):
        foreground_color = BLACK
        font = pygame.font.SysFont(FONT, FONT_SIZE)
        top_of_scores = SCREEN_HEIGHT // 2 - 50
        singlegame_hs = []
        lifetime_hs = []
        # single game highscores
        singlegame_hs.append(
            font.render(
                'Single Game High Scores',
                True,
                foreground_color))
        for score in scores_singlegame:
            singlegame_hs.append(
                font.render(
                    f'{score["username"]}: {score["score"]}',
                    True,
                    foreground_color))
        # render singlegame_hs
        for i, rendered_font in enumerate(singlegame_hs):
            left = SCREEN_WIDTH // 3 - rendered_font.get_width() // 2
            top = top_of_scores + i * rendered_font.get_height()
            self.surface.blit(rendered_font, (left, top))
        # lifetime game high scores
        lifetime_hs.append(
            font.render(
                'Lifetime Game High Scores',
                True,
                foreground_color))
        for score in scores_lifetime:
            lifetime_hs.append(
                font.render(
                    f'{score["username"]}: {score["score"]}',
                    True,
                    foreground_color))
        # render lifetime_hs
        for i, rendered_font in enumerate(lifetime_hs):
            left = SCREEN_WIDTH * 2 // 3 - rendered_font.get_width() // 2
            top = top_of_scores + i * rendered_font.get_height()
            self.surface.blit(rendered_font, (left, top))
        # final score
        rendered_final_score = font.render(
            f'final score: {current_score}', True, foreground_color)
        left = SCREEN_WIDTH // 2 - rendered_final_score.get_width() // 2
        top = SCREEN_HEIGHT // 2 + 150
        self.surface.blit(rendered_final_score, (left, top))

    def render_time(self, current_time: int):
        diameter = 50
        outer_arc_width = 5
        inner_arc_width = 100
        distance_from_top_of_screen = 100
        foreground_color = BLACK
        percent = current_time / GAME_TIMER
        font = pygame.font.SysFont(FONT, FONT_SIZE)
        rendered_font = font.render(
            f'{current_time // 1000}', True, foreground_color)
        center = (SCREEN_WIDTH // 2, distance_from_top_of_screen)
        font_center = (
            center[0] - rendered_font.get_width() // 2,
            center[1] - rendered_font.get_height() // 2)
        rect = pygame.Rect(0, 0, diameter, diameter)
        rect.center = center
        pygame.draw.arc(
            self.surface,
            WHITE,
            rect,
            0,
            math.radians(
                360 *
                percent),
            inner_arc_width)
        self.surface.blit(rendered_font, font_center)
        pygame.draw.arc(
            self.surface,
            LIGHT_BLUE,
            rect,
            0,
            math.radians(
                360 *
                percent),
            outer_arc_width)

    def render_level(self, current_level: int, num_z_levels: int, enemies):
        def dist(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        def num_enemies_on_level(enemies, level):
            count = 0
            for enemy in enemies:
                if enemy.z == level or enemy.enemy_type in enemy.bullet_enemies:
                    count += 1
            return count

        line_x = SCREEN_WIDTH - 100
        line_top = (line_x, 50)
        line_bottom = (line_x, line_top[1] + 150)
        line_length = dist(line_top, line_bottom)
        line_color = WHITE
        line_thickness = 3
        circle_radius = 5
        pygame.draw.line(
            self.surface,
            line_color,
            line_top,
            line_bottom,
            line_thickness)
        for i in range(num_z_levels):
            if current_level == i:
                circle_color = (0, 0, 255)
                number_color = circle_color
            else:
                circle_color = WHITE
                number_color = line_color
            circle_center = (
                line_x, line_bottom[1] - line_length * (i / (num_z_levels - 1)))
            pygame.draw.circle(
                self.surface,
                circle_color,
                circle_center,
                circle_radius)
            num_cur_enemies = num_enemies_on_level(enemies, i)
            if num_cur_enemies > 0:
                font = pygame.font.SysFont(FONT, FONT_SIZE)
                rendered_font = font.render(
                    f'{num_enemies_on_level(enemies, i)}', True, number_color)
                text_x = line_x + 10
                text_y = line_bottom[1] - rendered_font.get_height() // 2 - \
                    line_length * (i / (num_z_levels - 1))
                self.surface.blit(rendered_font, (text_x, text_y))

    def render_fps(self, fps: int):
        foreground_color = BLACK
        background_color = WHITE
        font = pygame.font.SysFont(FONT, FONT_SIZE)
        rendered_font = font.render(
            f'fps: {fps}',
            True,
            foreground_color,
            background_color)
        self.surface.blit(rendered_font, (10, 10))

    def show_logo(self):
        self.surface.blit(
            self.logo,
            (SCREEN_WIDTH // 2 - self.logo_rect.width // 2,
             100 + self.logo_rect.height // 2))

    def show_game_over(self):
        logo_height = self.game_over_rect.height
        logo_width = self.game_over_rect.width
        self.surface.blit(
            self.game_over_logo,
            (SCREEN_WIDTH // 2 - logo_width // 2,
             logo_height // 2))

    def button(self, message, top, left, hover_color,
               default_color, padding=30, radius=10):
        font_size = FONT_SIZE

        def create_box(_font_size):
            font_color = WHITE

            # create text object
            font = pygame.font.SysFont(FONT, _font_size)
            _rendered_font = font.render(message, True, font_color)
            _rendered_font.get_rect()
            # size text
            _font_width = _rendered_font.get_width()
            _font_height = _rendered_font.get_height()

            # size box
            width = _font_width + padding
            height = _font_height + padding
            return pygame.Rect(left - width // 2, top - height // 2, width,
                               height), _font_width, _font_height, _rendered_font

        rect, font_width, font_height, rendered_font = create_box(font_size)
        x, y = pygame.mouse.get_pos()
        is_pressed = pygame.mouse.get_pressed()[0]
        is_colliding = rect.collidepoint(x, y)
        clicked = is_pressed and is_colliding
        if is_colliding:
            font_size += 5
            rect, font_width, font_height, rendered_font = create_box(
                font_size)
            color = hover_color
        else:
            color = default_color

        # render box
        rect = pygame.draw.rect(
            self.surface, color, rect, border_radius=radius)

        # place text
        font_left = rect.centerx - font_width // 2
        font_top = rect.centery - font_height // 2
        # render text
        self.surface.blit(rendered_font, (font_left, font_top))
        return clicked
