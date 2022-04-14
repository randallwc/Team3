import math

import pygame

from Paths import logo_path


def show_mouse(is_visible: bool):
    pygame.mouse.set_visible(is_visible)


class ScreenManager:
    def __init__(self, background_image_path, screen_width, screen_height):
        self.background_image_path = background_image_path
        self.pygame_loaded_background = pygame.image.load(
            self.background_image_path)
        self.screen_dimensions = (screen_width, screen_height)
        self.surface = pygame.display.set_mode((screen_width, screen_height))

    def set_background(self, image_path):
        self.background_image_path = image_path
        self.pygame_loaded_background = pygame.image.load(image_path)

    def render_background(self, color=(0, 191, 255)):
        self.surface.fill(color)

    def render_score(self, current_score: int):
        foreground_color = (0, 0, 0)
        background_color = (255, 255, 255)
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(
            f'score: {current_score}',
            True,
            foreground_color,
            background_color)
        self.surface.blit(
            rendered_font,
            (self.screen_dimensions[0] - 100,
             self.screen_dimensions[1] - 100))

    def render_level(self, current_level: int, num_z_levels: int, enemies):
        def dist(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        def num_enemies_on_level(enemies, level):
            count = 0
            for enemy in enemies:
                if enemy.z == level:
                    count += 1
            return count

        line_x = self.screen_dimensions[0] - 100
        line_top = (line_x, 50)
        line_bottom = (line_x, line_top[1] + 150)
        line_length = dist(line_top, line_bottom)
        line_color = (255, 255, 255)
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
                circle_color = (255, 255, 255)
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
                font = pygame.font.SysFont('Comic Sans', 20)
                rendered_font = font.render(
                    f'{num_enemies_on_level(enemies, i)}', True, number_color)
                text_x = line_x + 10
                text_y = line_bottom[1] - rendered_font.get_height() // 2 - \
                    line_length * (i / (num_z_levels - 1))
                self.surface.blit(rendered_font, (text_x, text_y))

    def render_fps(self, fps: int):
        foreground_color = (0, 0, 0)
        background_color = (255, 255, 255)
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(
            f'fps: {fps}',
            True,
            foreground_color,
            background_color)
        self.surface.blit(rendered_font, (10, 10))

    def show_logo(self):
        rendered_logo = pygame.image.load(logo_path)
        rendered_logo = pygame.transform.rotozoom(rendered_logo, 0, 0.5)
        rendered_logo_rect = rendered_logo.get_rect()
        logo_height = rendered_logo_rect.height
        logo_width = rendered_logo_rect.width
        self.surface.blit(
            rendered_logo,
            (self.screen_dimensions[0] // 2 - logo_width // 2,
             100 + logo_height // 2))

    def button(self, message, top, left, hover_color,
               default_color, padding=30, radius=10):
        font_color = (255, 255, 255)
        font_size = 20

        # create text object
        font = pygame.font.SysFont('Comic Sans', font_size)
        rendered_font = font.render(message, True, font_color)
        rendered_font.get_rect()
        # size text
        font_width = rendered_font.get_width()
        font_height = rendered_font.get_height()

        # size box
        width = font_width + padding
        height = font_height + padding

        rect = pygame.Rect(left - width // 2, top - height // 2, width, height)
        x, y = pygame.mouse.get_pos()
        is_pressed = pygame.mouse.get_pressed()[0]
        is_colliding = rect.collidepoint(x, y)
        clicked = is_pressed and is_colliding
        if is_colliding:
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
