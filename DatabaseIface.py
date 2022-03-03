import Exceptions
import Network


# TODO -- create this class
class DatabaseIface:
    def __init__(self, network: Network):
        self.network = network

    def get_highscores(self):
        return []

    def add_highscore(self, new_score):
        raise Exceptions.NotImplementedException
