import pygame

from paths import laser_sound_path


def play_sound(file_path):
    pygame.mixer.Sound(file_path).play()


def play_laser_sound():
    play_sound(laser_sound_path)


def play_music(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()
    pygame.mixer.stop()


def is_playing_sounds() -> bool:
    return pygame.mixer.music.get_busy()
