import Exceptions
import socketio
import json
import Paths


# TODO -- create this class or decide on whether or not to delete it
class Server:
    def __init__(self):
        self.socket = socketio.Client()
        self.socket.connect('http://localhost:8000')
        self.serverEnemies = None
        self.isHost = False
        self.roomID = ''
        self.socketID = ''
        self.opponent_rangers = []

        self.idMapping = {
            '0': {
                'death_sound_path': Paths.jc_death_sound_path,
                'image_path': Paths.jc_path
            },
            '1': {
                'death_sound_path': Paths.friendly_fire_sound_path,
                'image_path': Paths.cow_path
            },
            '2': {
                'death_sound_path': Paths.ricky_death_sound_path,
                'image_path': Paths.ricky_path
            },
            '3': {
                'death_sound_path': Paths.wrong_answer_sound_path,
                'image_path': Paths.david_path
            },
            '4': {
                'death_sound_path': Paths.anton_death_sound_path,
                'image_path': Paths.anton_path
            },
            '5': {
                'death_sound_path': Paths.friendly_fire_sound_path,
                'image_path': Paths.armando_path
            },
            '6': {
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
                id = data[enemy]["id"]
                id = str(id)
                data[enemy]["death_sound_path"] = self.idMapping[id]["death_sound_path"]
                data[enemy]["image_path"] = self.idMapping[id]["image_path"]
            self.serverEnemies = data

        @self.socket.on("serverSendingOpponentRangersInGame")
        def setOpponentRangers(data):
            opponent_rangers = []
            for ranger in data["list"]:
                if ranger != self.socketID:
                    opponent_rangers.append(ranger)

            self.opponent_rangers = opponent_rangers

    def connect(self, roomID, mp_game_mode):
        if mp_game_mode != '0' and mp_game_mode != '1':
            raise Exception("Multiplayer game mode must be either 0 (join existing room) or 1 (create new room)")

        eventName = "joinExistingRoom" if mp_game_mode == '0' else "joinNewRoom"
        self.isHost = False if mp_game_mode == '0' else True
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

    def sendLocation(self, x, y):
        self.socket.emit("updateMyCoordinates", {
            'x':x,
            'y':y
        })

    def fetchRangerOpponents(self):
        self.socket.emit("fetchOpponentRangers")
