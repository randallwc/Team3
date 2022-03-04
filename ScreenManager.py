import pygame


def show_mouse(is_visible: bool):
    pygame.mouse.set_visible(is_visible)


class ScreenManager:
    def __init__(self, background_image_path, screen_width, screen_height):
        self.background_image_path = background_image_path
        self.pygame_loaded_background = pygame.image.load(self.background_image_path)
        self.screen_dimensions = (screen_width, screen_height)
        self.surface = pygame.display.set_mode((screen_width, screen_height))

    def set_background(self, image_path):
        self.background_image_path = image_path
        self.pygame_loaded_background = pygame.image.load(image_path)

    def render_background(self):
        self.surface.blit(self.pygame_loaded_background, (0, 0))

    def render_score(self, current_score: int):
        fgcolor = (0, 0, 0)
        bgcolor = (255, 255, 255)
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(f'score: {current_score}', True, fgcolor, bgcolor)
        self.surface.blit(rendered_font, (self.screen_dimensions[0] - 100, self.screen_dimensions[1] - 100))
