import Exceptions
import Network


class DatabaseIface:
    def __init__(self, network: Network):
        self.network = network

    def get_highscores(self):
        raise Exceptions.NotImplementedException

    def add_highscore(self, new_score):
        raise Exceptions.NotImplementedException
