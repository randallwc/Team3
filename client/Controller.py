import pygame

from CameraIface import CameraIface
from ImuIface import ImuIface
from VoiceIface import VoiceIface


class Controller:
    def __init__(self, num_z_levels):
        self.num_z_levels = num_z_levels

        self.use_face = True
        self.current_z = None
        self.xy_axis = ImuIface()
        self.z_axis = CameraIface(self.num_z_levels)
        self.voice = VoiceIface()
        self.pressing_down_level = False
        self.pressing_up_level = False

    def get_xy(self, screen_width, screen_height, x, y, speed, max_speed):
        # return self.get_xy_mouse()
        speed = min(speed, max_speed)
        x += speed * int(self.get_direction()['right'])
        x -= speed * int(self.get_direction()['left'])
        y += speed * int(self.get_direction()['down'])
        y -= speed * int(self.get_direction()['up'])
        # x += speed * self.xy_axis.x_gyro / 100
        # y += speed * self.xy_axis.y_gyro / 100
        if x > screen_width:
            x = screen_width
        elif x < 0:
            x = 0
        if y > screen_height:
            y = screen_height
        elif y < 0:
            y = 0
        return int(x), int(y)

    @staticmethod
    def get_xy_mouse():
        return pygame.mouse.get_pos()

    def get_direction(self):
        keys = pygame.key.get_pressed()
        return {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'space': keys[pygame.K_SPACE] or self.xy_axis.is_pushing or self.xy_axis.is_pushing,
            'down_level': keys[pygame.K_q],
            'up_level': keys[pygame.K_e],
        }

    @staticmethod
    def get_mouse():
        return {
            'left_click': pygame.mouse.get_pressed()[0],
            'right_click': pygame.mouse.get_pressed()[1],
        }

    def is_firing(self):
        # return self.get_mouse()['left_click']
        return self.get_direction()['space']

    def get_z(self, current_z: int):
        if self.use_face:
            self.current_z = self.z_axis.get_level()
        else:
            assert 0 <= current_z < self.num_z_levels
            self.current_z = current_z
            if self.get_direction()['down_level']:
                if not self.pressing_down_level:
                    self.pressing_down_level = True
                    self.current_z -= 1
            else:
                self.pressing_down_level = False

            if self.get_direction()['up_level']:
                if not self.pressing_up_level:
                    self.pressing_up_level = True
                    self.current_z += 1
            else:
                self.pressing_up_level = False

            if self.current_z < 0:
                self.current_z = 0
            elif self.current_z >= self.num_z_levels:
                self.current_z = self.num_z_levels - 1
        return self.current_z

    @staticmethod
    def is_moving():
        return any(pygame.key.get_pressed())

    def disconnect(self):
        self.xy_axis.client.disconnect()
