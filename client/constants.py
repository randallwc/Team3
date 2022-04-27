from paths import (anton_death_sound_path, anton_path, armando_path, cow_path,
                   david2_death_sound_path, david2_path, david_path,
                   friendly_fire_sound_path, jc_death_sound_path, jc_path,
                   ricky_death_sound_path, ricky_path)

# screen stuff
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAME_RATE = 60

# game stuff
GAME_TIMER = 30_000
GAME_STATES = [
    'start',
    'play',
    'multiplayer_start',
    'multiplayer',
    'game_over']

# colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 50, 255)
GREY = (120, 120, 120)
LIGHT_BLUE = (0, 100, 255)
BACKGROUND_BLUE = (0, 191, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# fonts
FONT = 'Comic Sans'
FONT_SIZE = 20

ENEMY_INFO = {
    'jc': {
        'is_good': False,
        'death_sound_path': jc_death_sound_path,
        'image_path': jc_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 60,
        'direction': 'left'
    },
    'cow': {
        'is_good': True,
        'death_sound_path': friendly_fire_sound_path,
        'image_path': cow_path,
        'max_time_alive': 1000,
        'x_speed': 1,
        'y_speed': 98,
        'direction': 'right'
    },
    'ricky': {
        'is_good': False,
        'death_sound_path': ricky_death_sound_path,
        'image_path': ricky_path,
        'max_time_alive': 1000,
        'x_speed': 2,
        'y_speed': 86,
        'direction': 'left'
    },
    'david': {
        'is_good': False,
        'death_sound_path': None,
        'image_path': david_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 65,
        'direction': 'right'
    },
    'anton': {
        'is_good': False,
        'death_sound_path': anton_death_sound_path,
        'image_path': anton_path,
        'max_time_alive': 1000,
        'x_speed': 4,
        'y_speed': 81,
        'direction': 'right'
    },
    'armando': {
        'is_good': True,
        'death_sound_path': friendly_fire_sound_path,
        'image_path': armando_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 69,
        'direction': 'left'
    },
    'david2': {
        'is_good': False,
        'death_sound_path': david2_death_sound_path,
        'image_path': david2_path,
        'max_time_alive': 1000,
        'x_speed': 20,
        'y_speed': 50,
        'direction': 'right'
    },
}
