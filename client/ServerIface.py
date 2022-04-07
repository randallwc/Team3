import socketio
import uuid
import time
from random import choice
from MultiplayerEnemy import *


# TODO -- create this class or decide on whether or not to delete it


class ServerIface:
    def __init__(self, username):
        self.socket = socketio.Client()
        # Localhost
        self.socket.connect('http://localhost:8000')
        # Production
        # self.socket.connect('https://skydangerranger.herokuapp.com/')
        self.is_host = False
        self.room_id = ''
        self.socket_id = ''
        self.user_id = ''
        self.epoch_time = ''
        self.time_user_id = ''
        self.username = username

        self.opponent_rangers = []
        self.opponent_ranger_coordinates = {}

        # Will be all enemies spawned on host
        # everyone else uses host's enemies
        self.host_enemies = []

        self.enemy_info = {
            'jc': {
                'is_good': False,
                'death_sound_path': jc_death_sound_path,
                'image_path': jc_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'cow': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': cow_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'ricky': {
                'is_good': False,
                'death_sound_path': ricky_death_sound_path,
                'image_path': ricky_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'david': {
                'is_good': False,
                'death_sound_path': david2_death_sound_path,
                'image_path': david_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'anton': {
                'is_good': False,
                'death_sound_path': anton_death_sound_path,
                'image_path': anton_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'armando': {
                'is_good': True,
                'death_sound_path': friendly_fire_sound_path,
                'image_path': armando_path,
                'max_time_alive': 1000,
                'x_speed': randrange(1, 4, 1),
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
            'david2': {
                'is_good': False,
                'death_sound_path': david2_death_sound_path,
                'image_path': david2_path,
                'max_time_alive': 1000,
                'x_speed': 20,
                'y_speed': randrange(50, 100, 1),
                'direction': choice(['left', 'right']),
                'speed': randrange(1, 4, 1)
            },
        }

        @self.socket.on("welcome_client")
        def on_welcome(data):
            print("Server: ", data['message'])
            print("Socket ID: ", data['socket_id'])
            self.socket_id = data['socket_id']

        @self.socket.on("server_sending_opponent_rangers_in_game")
        def set_opponent_rangers(data):
            opponent_rangers = []
            for ranger in data["list"]:
                # if ranger in list is not current user
                if ranger != self.time_user_id:
                    opponent_rangers.append(ranger)
            self.opponent_rangers = opponent_rangers

        @self.socket.on("update_opponent_ranger_coordinates")
        def update_opponent_ranger_coordinates(data):
            # set coordinates of opponent rangers
            self.opponent_ranger_coordinates[data["time_user_id"]] = (
                    data['x'],
                    data['y'],
                    data['z'],
                    data['is_firing']
                )

        @self.socket.on("all_entities_to_client")
        def receiving_all_entities(data):
            # HANDLING ENEMIES
            # two steps
            # 1: remove old enemies
            # 2: add new enemies
            # 3 update coordinates of existing entities

            # remove old enemies
            # find which enemies on local version are no longer on server
            # version & remove them
            new_enemies = []
            # do this in reverse, so we don't skip any on deleting
            i = len(self.host_enemies) - 1
            while i >= 0:
                curr_enemy = self.host_enemies[i]
                # print(curr_enemy.id, data["enemies"].keys(), 'bees')
                if curr_enemy.id not in data["enemies"]:
                    self.host_enemies.pop(i)
                i -= 1

            # add new enemies
            # find new opponents
            # find enemy IDs in data["enemies"] that is not in host_enemies,
            # add new enemy object
            host_enemy_ids = list(data["enemies"].keys())
            for enemy in self.host_enemies:
                try:
                    host_enemy_ids.remove(enemy.id)
                except BaseException:
                    continue

            # all existing ids have been removed
            for new_enemy_id in host_enemy_ids:
                enemy_data = data["enemies"][new_enemy_id]

                # new enemy
                new_enemy = MultiplayerEnemy(
                    enemy_data['x'],
                    enemy_data['y'],
                    enemy_data['z'],
                    enemy_data['num_z_levels'],
                    enemy_data['enemy_type'],
                    self.enemy_info,
                    new_enemy_id
                )
                self.host_enemies.append(new_enemy)

            for enemy in self.host_enemies:
                enemy.update_coordinates(
                    data["enemies"][enemy.id]['x'], data["enemies"][enemy.id]['y'])

    def connect(self, room_id, is_host):
        event_name = "join_new_room" if is_host else "join_existing_room"
        self.is_host = is_host
        self.room_id = room_id
        self.epoch_time = int(time.time())
        self.user_id = uuid.getnode()
        # concatinating for local testing, so user id is still unique
        self.time_user_id = self.epoch_time + self.user_id

        self.socket.emit(event_name, {
            'room_id': room_id,
            'user_id': self.user_id,
            'epoch_time': self.epoch_time,
            'time_user_id': self.time_user_id, # epoch_time + user_id
            'username': 'dummyusername'
        })

    def fetch_enemies(self):
        self.socket.emit('fetch_enemies')

    def send_location_and_meta(self, x, y, z, is_firing):
        if self.socket.connected:
            self.socket.emit("update_my_coordinates_and_meta", {
                'x': x,
                'y': y,
                'z': z,
                'is_firing': is_firing
            })

    def fetch_ranger_opponents(self):
        self.socket.emit("fetch_opponent_rangers")

    def fetch_all_entities(self):
        if self.socket.connected:
            self.socket.emit('fetch_all_entities')

    def append_new_enemy_to_server(self, enemy):
        if self.is_host:
            coordinates = enemy.get_coordinates()
            stripped_enemy = {
                'x': coordinates[0],
                'y': coordinates[1],
                'z': coordinates[2],
                'id': enemy.id,
                'enemy_type': enemy.enemy_type,
                'health': enemy.health,
                'num_z_levels': enemy.num_z_levels
            }
            self.socket.emit('host_appending_new_enemy', stripped_enemy)

    def update_enemy_coordinates(self, id, x, y):
        if self.is_host:
            self.socket.emit("host_updating_enemy_coordinates", {
                'id': id,
                'x': x,
                'y': y
            })

    def remove_enemy_from_server(self, id):
        self.socket.emit('remove_enemy', {"id": id})

    def disconnect(self):
        self.socket.disconnect()
