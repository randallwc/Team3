import pygame

black = (0, 0, 0)
white = (255, 255, 255)


class Entity:
    def __init__(self, x, y, z, num_z_levels,
                 image_path, image_dimensions=None):
        self.x = x
        self.y = y
        self.z = z
        self.num_z_levels = num_z_levels
        self.image_path = image_path
        self.shape = self.set_image(self.image_path)

        if image_dimensions is not None:
            self.scale_image(*image_dimensions)

        # get rect for collisions
        self.rect = self.shape.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.shape.get_width()
        self.rect.height = self.shape.get_height()

        # set top and left for rendering
        self.top = x + self.shape.get_width() // 2
        self.left = y + self.shape.get_height() // 2

        self.should_display = True

    def set_level(self, current_level):
        if current_level in range(self.num_z_levels):
            self.z = current_level
        else:
            raise Exception("level invalid")

    def set_image(self, image_path):
        self.image_path = image_path
        self.shape = pygame.image.load(self.image_path)
        return self.shape

    def update_coordinates(self, x, y):
        self.x = x
        self.y = y
        self.left = x - self.shape.get_width() // 2
        self.top = y - self.shape.get_height() // 2
        self.rect.x = self.left
        self.rect.y = self.top
        self.rect.width = self.shape.get_width()
        self.rect.height = self.shape.get_height()

    def show(self, surface: pygame.surface):
        self.update_coordinates(self.x, self.y)
        surface.blit(self.shape, (self.left, self.top))
        # self.show_rect(surface)

    def show_rect(self, surface: pygame.surface, color=white):
        for i in range(4):
            pygame.draw.rect(
                surface,
                color,
                (self.rect.x - i,
                 self.rect.y - i,
                 self.rect.width,
                 self.rect.height),
                1)

    def scale_image(self, width, height):
        # this ruins the rectangle
        self.shape = pygame.transform.scale(self.shape, (width, height))
        self.rect = self.shape.get_rect()
