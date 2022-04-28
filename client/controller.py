import pygame

from camera_iface import CameraIface
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from imu_iface import ImuIface
from voice_iface import VoiceIface


class Controller:
    def __init__(self, num_z_levels: int, use_camera: bool, username: str):
        self.num_z_levels = num_z_levels

        self._use_camera = use_camera
        self.current_z = None
        self.imu = ImuIface(username)
        self.camera = CameraIface(self.num_z_levels, self._use_camera)
        self.voice = VoiceIface()
        self.pressing_down_level = False
        self.pressing_up_level = False
        self._previous_fire_val = False

    def use_camera(self, use_camera: bool):
        self._use_camera = use_camera
        self.camera.use_camera = self._use_camera
        self.camera.toggle_camera()

    def get_xy(self, x, y, speed, max_speed):
        # return self.get_xy_mouse()
        speed = min(speed, max_speed)
        x += speed * int(self.get_direction()['right'])
        x -= speed * int(self.get_direction()['left'])
        y += speed * int(self.get_direction()['down'])
        y -= speed * int(self.get_direction()['up'])
        return (int(min(max(x, 0), SCREEN_WIDTH)),
                int(min(max(y, 0), SCREEN_HEIGHT)))

    @staticmethod
    def get_xy_mouse():
        return pygame.mouse.get_pos()

    def get_direction(self):
        keys = pygame.key.get_pressed()
        camup = False
        camdown = False
        camleft = False
        camright = False
        if self._use_camera:
            dirs = self.camera.get_directions()
            camup = dirs['up']
            camdown = dirs['down']
            camleft = dirs['left']
            camright = dirs['right']
        return {
            'up': keys[pygame.K_UP] or keys[pygame.K_w] or camup,
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s] or camdown,
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a] or camleft,
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d] or camright,
            'space': keys[pygame.K_SPACE] or self.imu.is_shooting,
            'down_level': keys[pygame.K_q] or self.imu.is_downward_push,
            'up_level': keys[pygame.K_e] or self.imu.is_upward_push,
        }

    def is_firing(self):
        # return self.get_mouse()['left_click']
        return self.get_direction()['space']

    def fire_edge(self) -> bool:
        # is_firing signal
        # -------           -------
        #        \         /
        #         \_______/
        # trigger ^       ^ don't trigger
        is_firing = self.is_firing()
        prev_val = self._previous_fire_val
        self._previous_fire_val = is_firing
        if is_firing and not prev_val:
            return True
        return False

    def get_z(self, current_z: int):
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

    def is_moving(self):
        out = any(pygame.key.get_pressed())
        if self._use_camera:
            out |= any(self.camera.directions.values())
        return out

    def disconnect(self):
        self.imu.client.disconnect()
