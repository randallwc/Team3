import pygame


class Entity:
    def __init__(self, x, y, z, num_z_levels, image_path, image_dimensions=None):
        self.x = x
        self.y = y
        self.z = z
        self.num_z_levels = num_z_levels
        self.image = image_path
        self.shape = pygame.image.load(self.image)
        self.top = x + self.shape.get_width() // 2
        self.left = y + self.shape.get_height() // 2
        self.should_display = True
        if image_dimensions is not None:
            self.scale_image(*image_dimensions)

    def set_level(self, current_level):
        if current_level in range(self.num_z_levels):
            self.z = current_level
        else:
            raise Exception("level invalid")

    def set_image(self, image_path):
        self.image = image_path
        self.shape = pygame.image.load(self.image)

    def update_coordinates(self, x, y):
        self.x = x
        self.y = y
        self.left = x - self.shape.get_width() // 2
        self.top = y - self.shape.get_height() // 2

    def show(self, surface: pygame.surface):
        self.update_coordinates(self.x, self.y)
        surface.blit(self.shape, (self.left, self.top))

    def scale_image(self, width, height):
        self.shape = pygame.transform.scale(self.shape, (width, height))
