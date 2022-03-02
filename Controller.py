import Exceptions
import VoiceIface
import CameraIface
import ImuIface
import pygame
import Network


class Controller:
    def __init__(self, network: Network):
        self.xy_axis = ImuIface.ImuIface(network)
        self.z_axis = CameraIface.CameraIface()
        self.voice = VoiceIface.VoiceIface()

    def get_xy(self):
        return pygame.mouse.get_pos()

    def is_clicking(self):
        return pygame.mouse.get_pressed()[0]

    def get_z(self):
        raise Exceptions.NotImplementedException

    def get_current_state(self):
        return Exceptions.NotImplementedException