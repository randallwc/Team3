import pygame.surface

from Paths import opponent_path
from Ranger import Ranger


# TODO -- create this class
class OpponentRanger(Ranger):
    def __init__(self, x, y, z, num_z_levels, screenwidth, screenheight,
                 image_path=opponent_path):
        super().__init__(x, y, z, num_z_levels, screenwidth, screenheight, image_path)

    def show_diff_level(self, surface: pygame.surface.Surface,
                        particle_surface: pygame.surface.Surface, cur_z: int):
        if self.z == cur_z:
            super().show(surface, particle_surface)
            return
        is_above = self.z > cur_z
        if is_above:
            self.shape.set_alpha(255 // 2)
            text = 'above'
        else:
            self.shape.set_alpha(255 // 4)
            text = 'below'
        super().show(surface, particle_surface)
        self.shape.set_alpha(255)
        # indicate above or below
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(f'{text}', True, (255, 255, 255))
        surface.blit(
            rendered_font,
            (self.rect.centerx - rendered_font.get_width() // 2, self.rect.bottom))
