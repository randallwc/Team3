from Exceptions import NotImplementedException


# TODO -- create this class
class DatabaseIface:
    def __init__(self):
        pass

    def get_highscores(self):
        return []

    def add_highscore(self, new_score):
        raise NotImplementedException