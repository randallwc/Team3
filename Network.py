import Exceptions
import socketio


class Network:
    def __init__(self):
        self.socket = socketio.Client()

    def connect(self):
        raise Exceptions.NotImplementedException

    def disconnect(self):
        raise Exceptions.NotImplementedException

    def location(self):
        raise Exceptions.NotImplementedException

    def listen(self):
        raise Exceptions.NotImplementedException
