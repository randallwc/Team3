import time
import uuid
from random import choice, randrange

import socketio

from MultiplayerEnemy import MultiplayerEnemy
from Paths import (anton_death_sound_path, anton_path, armando_path, cow_path,
                   david2_death_sound_path, david2_path, david_path,
                   friendly_fire_sound_path, jc_death_sound_path, jc_path,
                   ricky_death_sound_path, ricky_path, wrong_answer_sound_path)

# TODO -- create this class or decide on whether or not to delete it


class ServerIface:
    def __init__(self, username):
        self.socket = socketio.Client()
        # Localhost
        # self.socket.connect('http://localhost:8000', transports=['websocket'])
        # Production
        self.socket.connect(
            'https://skydangerranger.herokuapp.com/',
            transports=['websocket'])
        self.is_host = False
        self.room_id = ''
        self.socket_id = ''
        self.user_id = ''
        self.epoch_time = ''
        self.time_user_id = ''
        self.username = username

        self.opponent_rangers = []
        self.opponent_ranger_coordinates = {}

        # modulo counters to throttle socket messages
        self.send_location_counter = 0
        self.fetch_rangers_modulo_counter = 0
        self.set_opponent_rangers_modulo_counter = 0
        self.fetch_all_enemies_modulo_counter = 0

        # so we only update if changes are made
        self.curr_metadata = []  # x, y, z, is_firing

        # Will be all enemies spawned on host
        # everyone else uses host's enemies
        self.host_enemies = []
        self.host_enemies_dict = {}
        self.awaiting_new_enemies = []
        self.awaiting_enemy_despawn = {}

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

        @self.socket.on("new_host_appended_enemy")
        def append_new_server_enemy(data):
            self.awaiting_new_enemies.append(data)

        @self.socket.on('remove_enemy_from_client')
        def remove_enemy_from_client(data):
            enemy_id = data['id']
            self.awaiting_enemy_despawn[enemy_id] = True

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
            'time_user_id': self.time_user_id,  # epoch_time + user_id
            'username': self.username
        })

    def send_location_and_meta(self, x, y, z, is_firing):
        # modulo counter
        self.send_location_counter += 1
        # on initial load, or a change occurred
        change_occurred = len(self.curr_metadata) == 0 or (
            self.curr_metadata[0] != x or self.curr_metadata[1] != y or self.curr_metadata[2] != z or self.curr_metadata[3] != is_firing)

        if self.socket.connected and self.send_location_counter % 5 == 0 and change_occurred:
            # update local coordinates so we know what previous coordinates
            # were
            self.curr_metadata = [x, y, z, is_firing]

            # transmit to server
            self.socket.emit("update_my_coordinates_and_meta", {
                'x': x,
                'y': y,
                'z': z,
                'is_firing': is_firing
            })

    def append_new_enemy_to_server(self, enemy):
        if self.is_host and self.socket.connected:
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

    def update_enemy_coordinates(self, enemy_id, x, y):
        if self.is_host:
            self.socket.emit("host_updating_enemy_coordinates", {
                'id': enemy_id,
                'x': x,
                'y': y
            })

    def remove_enemy_from_server(self, enemy_id):
        self.socket.emit('remove_enemy', {"id": enemy_id})

    def disconnect(self):
        self.socket.disconnect()
