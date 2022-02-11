#! /usr/bin/env python3

#################### IMPORTS ####################

import pygame
import sys
import os
from time import sleep
from random import randrange

#################### TODOs ####################
'''
- [x] make cloud appear
- [x] make plane follow cursor
- [ ] make multiple clouds appear
- [ ] make enemies appear
- [ ] make enemies take damage
- [ ] make enemies deal damage
- [ ] make amo boxes appear
- [ ] make plane shoot
- [ ] make plane GIF render plane flying
- [ ] ...
'''
#################### CLASSES ####################
class Cloud:
    def __init__(self, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)
        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.x, self.y))

    def SetX(self, val):
        self.x = val

    def GetX(self):
        return self.x

    def SetY(self, val):
        self.y = val

    def GetY(self):
        return self.y

    def GetCoords(self):
        return (self.x, self.y)

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
        self.left = x-self.shape.get_width()/2
        self.top = y-self.shape.get_height()/2

#################### INIT ####################
pygame.init()
clock = pygame.time.Clock()
screenwidth, screenheight = (1280, 720)
screen = pygame.display.set_mode((screenwidth, screenheight))

# Load Assets
background_path = os.path.join("./static", "background2.jpeg")
background_image = pygame.image.load(background_path)
ranger_path = os.path.join("./static", "rangership_50.png")
cloud_path = os.path.join("./static", "cloud1_transparent_30.png")
laser_path = os.path.join("./static", "laser.mp3")

pygame.mouse.set_visible(0)
pygame.display.set_caption('Sky Danger Ranger')

# initialize cloud object
cloud = Cloud(cloud_path, randrange(0,screenwidth, 1), 0)

# initialize ranger object
Ranger = RangerShip(screenheight, screenwidth, ranger_path, 0, 0)

# replace 200 with the actual height of the cloud
# so we can continue to spawn in the cloud when it
# goes out of view
BOUND = 200

# laser info
maxLineWidth = 20
lineWidth = maxLineWidth
minLineWidth = 0
isClicking = False # TODO move this into a screen class
laser_sound = pygame.mixer.Sound(laser_path)
isPlayingLaserSound = False

#################### MAIN LOOP ####################
while True:
    # loop clock
    clock.tick(60)

    # re render the background
    screen.blit(background_image, (0,0))

    # get coordinates of mouse
    x, y = pygame.mouse.get_pos()

    # show cloud
    cloud.Show(screen)
    cloud.SetY(cloud.GetY()+10)
    if cloud.GetY() < -BOUND or cloud.GetY() > screenheight + BOUND:
        cloud.SetX(randrange(0, screenwidth,1))
        cloud.SetY(-100) # TODO change this to be variable based on the cloud size

    # display laser
    if isClicking:
        if lineWidth == maxLineWidth:
            pygame.mixer.Sound.play(laser_sound)
        pygame.draw.line(screen, (255,0,0), (x,y), (x,0), lineWidth)
        lineWidth -= 1
        if lineWidth < minLineWidth:
            lineWidth = minLineWidth

    # show ranger
    Ranger.UpdateCoords(x, y)
    Ranger.Show(screen)

    # check for quit signal
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            isClicking = True
        if event.type == pygame.MOUSEBUTTONUP:
            isClicking = False
            lineWidth = maxLineWidth

    pygame.display.update()
