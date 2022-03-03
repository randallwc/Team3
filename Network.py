import Exceptions
import socketio


# TODO -- create this class or decide on whether or not to delete it
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
