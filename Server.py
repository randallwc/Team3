import Exceptions
import socketio
import json
import Paths
import MultiplayerEnemy

# TODO -- create this class or decide on whether or not to delete it
class Server:
    def __init__(self, username):
        self.socket = socketio.Client()
        self.socket.connect('http://localhost:8000')
        self.serverEnemies = None
        self.isHost = False
        self.roomID = ''
        self.socketID = ''
        self.opponent_rangers = []
        self.opponent_ranger_coordinates = {}
        self.username = username


        # Will be all enemies spawned on host
        # everyone else uses host's enemies
        self.host_enemies = []

        self.idMapping = {
            'jc': {
                'death_sound_path': Paths.jc_death_sound_path,
                'image_path': Paths.jc_path
            },
            'cow': {
                'death_sound_path': Paths.friendly_fire_sound_path,
                'image_path': Paths.cow_path
            },
            'ricky': {
                'death_sound_path': Paths.ricky_death_sound_path,
                'image_path': Paths.ricky_path
            },
            'david': {
                'death_sound_path': Paths.wrong_answer_sound_path,
                'image_path': Paths.david_path
            },
            'anton': {
                'death_sound_path': Paths.anton_death_sound_path,
                'image_path': Paths.anton_path
            },
            'armando': {
                'death_sound_path': Paths.friendly_fire_sound_path,
                'image_path': Paths.armando_path
            },
            'david2': {
                'death_sound_path': Paths.david2_death_sound_path,
                'image_path': Paths.david2_path
            },
        }

        @self.socket.on("WelcomeClient")
        def on_welcome(data):
            print("Server: ", data['message'])
            self.socketID = data['socketID']

        @self.socket.on("enemyInfoToClient")
        def setEnemiesFromServer(data):
            for enemy in data:
                data[enemy]["death_sound_path"] = self.idMapping[enemy]["death_sound_path"]
                data[enemy]["image_path"] = self.idMapping[enemy]["image_path"]
            self.serverEnemies = data

        @self.socket.on("serverSendingOpponentRangersInGame")
        def setOpponentRangers(data):
            opponent_rangers = []
            for ranger in data["list"]:
                if ranger != self.socketID:
                    opponent_rangers.append(ranger)
            self.opponent_rangers = opponent_rangers

        @self.socket.on("updateOpponentRangerCoordinates")
        def updateOpponentRangerCoordinates(data):
            # set coordinates of opponent rangers
            self.opponent_ranger_coordinates[data["socketID"]] = (data['x'], data['y'], data['z'])

        @self.socket.on("allEntitiesToClient")
        def receiving_all_entities(data):
            ############ HANDLING ENEMIES
            #two steps
            #1: remove old enemies
            #2: add new enemies
            #3 update coordinates of existing entities

            ### remove old enemies
            # find which enemies on local version are no longer on server version & remove them
            new_enemies = []
            #do this in reverse so we don't skip any on deleting
            i = len(self.host_enemies) - 1
            while i >= 0:
                curr_enemy = self.host_enemies[i]
                #print(curr_enemy.id, data["enemies"].keys(), 'bees')
                if curr_enemy.id not in data["enemies"]:
                    self.host_enemies.pop(i)
                i -= 1

            ### add new enemies
            #find new opponents
            #find enemy IDs in data["enemies"] that is not in host_enemies, add new enemy object
            host_enemy_ids = list(data["enemies"].keys())
            for enemy in self.host_enemies:
                try:
                    host_enemy_ids.remove(enemy.id)
                except:
                    continue

            # all existing ids have been removed
            for new_enemy_id in host_enemy_ids:
                enem_data = data["enemies"][new_enemy_id]

                # new enemy
                new_enemy = MultiplayerEnemy.MultiplayerEnemy(
                    enem_data['x'],
                    enem_data['y'],
                    enem_data['z'],
                    enem_data['num_z_levels'],
                    enem_data['enemy_type'],
                    self.serverEnemies,
                    new_enemy_id
                    )
                self.host_enemies.append(new_enemy)

            for enemy in self.host_enemies:
                enemy.update_coordinates(data["enemies"][enemy.id]['x'], data["enemies"][enemy.id]['y'])

    def connect(self, roomID, isHost):
        eventName = "joinNewRoom" if isHost else "joinExistingRoom"
        self.isHost = isHost
        self.roomID = roomID
        self.socket.emit(eventName, {
            'roomID': roomID
        })

    def disconnect(self):
        raise Exceptions.NotImplementedException

    def location(self):
        raise Exceptions.NotImplementedException

    def listen(self):
        raise Exceptions.NotImplementedException

    def fetchEnemies(self):
        self.socket.emit('fetchEnemies')

    def sendLocation(self, x, y, z):
        self.socket.emit("updateMyCoordinates", {
            'x': x,
            'y': y,
            'z': z
        })

    def fetchRangerOpponents(self):
        self.socket.emit("fetchOpponentRangers")

    def fetch_all_entities(self):
        self.socket.emit('fetchAllEntities')

    def append_new_enemy_to_server(self, enemy):
        if self.isHost:
            coords = enemy.get_coordinates()
            stripped_enemy = {
                'x': coords[0],
                'y': coords[1],
                'z': coords[2],
                'id': enemy.id,
                'enemy_type':enemy.enemy_type,
                'health': enemy.health,
                'num_z_levels':enemy.num_z_levels
            }
            self.socket.emit('hostAppendingNewEnemy', stripped_enemy)
    def update_enemy_coords(self, id, x, y):
        if self.isHost:
            self.socket.emit("hostUpdatingEnemyCoordinates",{
                'id': id,
                'x': x,
                'y':y
            })

    def remove_enemy_from_server(self, id):
        self.socket.emit('removeEnemy', {"id": id})