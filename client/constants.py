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
    'ask_username',
    'start',
    'play',
    'multiplayer_start',
    'multiplayer',
    'game_over']

# ranger speeds
MAX_RANGER_SPEED = 20.0
MAX_FAST_SPEED = 30.0
RANGER_ACCELERATION = 1.1
MAX_RANGER_ACCELERATION = 5.0
RANGER_DAMAGE = 1
RANGER_START_HEALTH = 1
MAX_RANGER_HEALTH = 2

# powerup scores
CLEAR_SCORE = 20
FIRE_SCORE = 10

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


ENEMY_DIRECTIONS = ['left', 'right', 'down']
ENEMY_DAMAGE_TO_RANGER_ON_COLLIDE = 0.5
ENEMY_DAMAGE_TO_RANGER_ON_WRONG_HIT = 0.25
ENEMY_INFO = {
    'jc': {
        'is_good': False,
        'death_sound_path': jc_death_sound_path,
        'image_path': jc_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 60,
        'direction': 'left',
        'health': 3,
        'image_dimensions': (100, 100),
    },
    'cow': {
        'is_good': True,
        'death_sound_path': friendly_fire_sound_path,
        'image_path': cow_path,
        'max_time_alive': 1000,
        'x_speed': 1,
        'y_speed': 98,
        'direction': 'right',
        'health': 1,
        'image_dimensions': (100, 100),
    },
    'ricky': {
        'is_good': False,
        'death_sound_path': ricky_death_sound_path,
        'image_path': ricky_path,
        'max_time_alive': 1000,
        'x_speed': 2,
        'y_speed': 86,
        'direction': 'left',
        'health': 2,
        'image_dimensions': (100, 100),
    },
    'david': {
        'is_good': False,
        'death_sound_path': None,
        'image_path': david_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 65,
        'direction': 'right',
        'health': 3,
        'image_dimensions': (100, 100),
    },
    'anton': {
        'is_good': False,
        'death_sound_path': anton_death_sound_path,
        'image_path': anton_path,
        'max_time_alive': 1000,
        'x_speed': 0,
        'y_speed': 3,
        'direction': 'down',
        'health': 1,
        'image_dimensions': (100, 100),
    },
    'armando': {
        'is_good': True,
        'death_sound_path': friendly_fire_sound_path,
        'image_path': armando_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 69,
        'direction': 'left',
        'health': 2,
        'image_dimensions': (100, 100),
    },
    'david2': {
        'is_good': False,
        'death_sound_path': david2_death_sound_path,
        'image_path': david2_path,
        'max_time_alive': 1000,
        'x_speed': 20,
        'y_speed': 50,
        'direction': 'right',
        'health': 1,
        'image_dimensions': (100, 100),
    },
}
