#! /usr/bin/env python3

import pygame
import sys
import os

pygame.init()
clock = pygame.time.Clock()
screenwidth, screenheight = (1400, 850)
screen = pygame.display.set_mode((screenwidth, screenheight))

#Load background
bg = pygame.image.load(os.path.join("./static", "background2.jpeg"))
ranger_plane_file = os.path.join("./static", "rangership_50.png")
cloud1 = os.path.join("./static", "cloud1_transparent_30.png")

# pygame.mouse.set_visible(0)
pygame.display.set_caption('Sky Danger Ranger')

class Cloud:
    def __init__(self, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)

        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.x, self.y))

    def MoveDown(self, amt):
        # @will, was last trying to get this to work, it looks like self.y is updated but it doesnt update on screen
        print('later')
        self.y = amt
        print('gater', self.y)

class RangerShip:
    def __init__(self, screenheight, screenwidth, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)
        self.top = screenheight/2 - self.shape.get_height()
        self.left = screenwidth/2 - self.shape.get_width()/2

        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))

    def UpdateCoords(self, x, y):

        # x_direction = x - self.x
        # y_direction = y - self.y
        # angle = (180/math.pi) * -1 * math.atan2(y_direction, x_direction)
        # self.shape = pygame.transform.rotate(self.shape, int(angle))

        self.left = x-self.shape.get_width()/2
        self.top = y - self.shape.get_height()/2

while True:
    clock.tick(60)

    screen.blit(bg, (0,0))
    x, y = pygame.mouse.get_pos()

    # show cloud(s)
    cloud = Cloud(cloud1, screenwidth/2, 0)
    cloud.Show(screen)
    cloud.MoveDown(1000)


    # show ranger
    Ranger = RangerShip(screenheight, screenwidth, ranger_plane_file, x, y)
    Ranger.UpdateCoords(x, y)
    Ranger.Show(screen)

    # print(x, y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    pygame.display.update()

    # pygame.draw.rect(screen, (255, 255, 255), (x, y, 400, 400))
    pygame.display.update()
