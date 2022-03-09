import pygame

import CameraIface
import Exceptions
import ImuIface
import Network
import VoiceIface


class Controller:
    def __init__(self, network: Network):
        self.current_z = None
        self.xy_axis = ImuIface.ImuIface(network)
        self.z_axis = CameraIface.CameraIface(100, 100)
        self.voice = VoiceIface.VoiceIface()
        self.pressing_down_level = False
        self.pressing_up_level = False

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
            'down_level': keys[pygame.K_q],
            'up_level': keys[pygame.K_e],
        }

    def get_mouse(self):
        return {
            'left_click': pygame.mouse.get_pressed()[0],
            'right_click': pygame.mouse.get_pressed()[1],
        }

    def is_firing(self):
        # return self.get_mouse()['left_click']
        return self.get_keys()['space']

    def get_z(self, current_z: int, num_levels: int):
        assert (0 <= current_z < num_levels)
        self.current_z = current_z
        if self.get_keys()['down_level']:
            if not self.pressing_down_level:
                self.pressing_down_level = True
                self.current_z -= 1
        else:
            self.pressing_down_level = False

        if self.get_keys()['up_level']:
            if not self.pressing_up_level:
                self.pressing_up_level = True
                self.current_z += 1
        else:
            self.pressing_up_level = False

        if self.current_z < 0:
            self.current_z = 0
        elif self.current_z >= num_levels:
            self.current_z = num_levels - 1

        return self.current_z

    def get_current_state(self):
        return Exceptions.NotImplementedException

    def is_moving(self):
        return any(pygame.key.get_pressed())
