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
        self.opponent_ranger_coordinates = {}

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

        @self.socket.on("updateOpponentRangerCoordinates")
        def updateOpponentRangerCoordinates(data):
            # set coordinates of opponent rangers
            self.opponent_ranger_coordinates[data["socketID"]] = (data['x'], data['y'], data['z'])


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
