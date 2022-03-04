import CameraIface
import Exceptions
import ImuIface
import Network
import VoiceIface
import pygame


class Controller:
    def __init__(self, network: Network):
        self.xy_axis = ImuIface.ImuIface(network)
        self.z_axis = CameraIface.CameraIface()
        self.voice = VoiceIface.VoiceIface()

    def get_xy(self, screen_width, screen_height, x, y, speed, max_speed):
        # return self.get_xy_mouse()
        if speed > max_speed:
            speed = max_speed
        x += speed * int(self.get_keys()['right'])
        x -= speed * int(self.get_keys()['left'])
        y += speed * int(self.get_keys()['down'])
        y -= speed * int(self.get_keys()['up'])
        if x > screen_width:
            x = screen_width
        elif x < 0:
            x = 0
        if y > screen_height:
            y = screen_height
        elif y < 0:
            y = 0
        return int(x), int(y)

    def get_xy_mouse(self):
        return pygame.mouse.get_pos()

    def get_keys(self):
        keys = pygame.key.get_pressed()
        return {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'space': keys[pygame.K_SPACE],
        }

    def get_mouse(self):
        return {
            'left_click': pygame.mouse.get_pressed()[0],
            'right_click': pygame.mouse.get_pressed()[1],
        }

    def is_firing(self):
        # return self.get_mouse()['left_click']
        return self.get_keys()['space']

    def get_z(self):
        raise Exceptions.NotImplementedException

    def get_current_state(self):
        return Exceptions.NotImplementedException

    def is_moving(self):
        return any(pygame.key.get_pressed())
