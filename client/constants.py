from paths import (anton_death_sound_path, anton_path, armando_path, cow_path,
                   david2_death_sound_path, david2_path, david_path,
                   friendly_fire_sound_path, jc_death_sound_path, jc_path,
                   meteor_path, meteor_sound_path, ricky_death_sound_path,
                   ricky_path)

# screen stuff
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAME_RATE = 60

# ui
DEFAULT_USERNAME = 'enter username'
DEFAULT_ROOM = 'enter roomid'

# game stuff
GAME_TIMER = 60_000
GAME_STATES = [
    'ask_username',
    'start',
    'levels',
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

# enemies
START_SPAWN_COUNT = 10
DEFAULT_MAX_NUM_ENEMIES = 5
DEFAULT_MAX_SPAWN_COUNTER = 100
ENEMY_DIRECTIONS = ['left', 'right', 'down']
ENEMY_CATEGORIES = ['good', 'bad', 'dodge']
ENEMY_DAMAGE_TO_RANGER_ON_COLLIDE = 0.5
ENEMY_DAMAGE_TO_RANGER_ON_WRONG_HIT = 0.25
DODGE_ENEMY_COLISION_DAMAGE = 0.75
ENEMY_INFO = {
    'jc': {
        'category': ENEMY_CATEGORIES[1],
        'death_sound_path': jc_death_sound_path,
        'image_path': jc_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 60,
        'direction': ENEMY_DIRECTIONS[0],
        'health': 3,
        'image_dimensions': (100, 100),
    },
    'cow': {
        'category': ENEMY_CATEGORIES[0],
        'death_sound_path': friendly_fire_sound_path,
        'image_path': cow_path,
        'max_time_alive': 1000,
        'x_speed': 1,
        'y_speed': 98,
        'direction': ENEMY_DIRECTIONS[1],
        'health': 1,
        'image_dimensions': (100, 100),
    },
    'ricky': {
        'category': ENEMY_CATEGORIES[2],
        'death_sound_path': ricky_death_sound_path,
        'image_path': ricky_path,
        'max_time_alive': 1000,
        'x_speed': 0,
        'y_speed': 5,
        'direction': ENEMY_DIRECTIONS[2],
        'health': 10,
        'image_dimensions': (300, 100),
    },
    'david': {
        'category': ENEMY_CATEGORIES[1],
        'death_sound_path': None,
        'image_path': david_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 65,
        'direction': ENEMY_DIRECTIONS[1],
        'health': 3,
        'image_dimensions': (100, 100),
    },
    'anton': {
        'category': ENEMY_CATEGORIES[1],
        'death_sound_path': anton_death_sound_path,
        'image_path': anton_path,
        'max_time_alive': 1000,
        'x_speed': 5,
        'y_speed': 68,
        'direction': ENEMY_DIRECTIONS[0],
        'health': 1,
        'image_dimensions': (100, 100),
    },
    'armando': {
        'category': ENEMY_CATEGORIES[0],
        'death_sound_path': friendly_fire_sound_path,
        'image_path': armando_path,
        'max_time_alive': 1000,
        'x_speed': 3,
        'y_speed': 69,
        'direction': ENEMY_DIRECTIONS[0],
        'health': 2,
        'image_dimensions': (100, 100),
    },
    'david2': {
        'category': ENEMY_CATEGORIES[1],
        'death_sound_path': david2_death_sound_path,
        'image_path': david2_path,
        'max_time_alive': 1000,
        'x_speed': 20,
        'y_speed': 50,
        'direction': ENEMY_DIRECTIONS[1],
        'health': 1,
        'image_dimensions': (100, 100),
    },
    'meteor': {
        'category': ENEMY_CATEGORIES[1],
        'death_sound_path': meteor_sound_path,
        'image_path': meteor_path,
        'max_time_alive': 1000,
        'x_speed': 0,
        'y_speed': 3,
        'direction': ENEMY_DIRECTIONS[2],
        'health': 1,
        'image_dimensions': (100, 200),
    },
}
