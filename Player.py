import Ranger
import DatabaseIface


class Player:
    def __init__(self, screen_width, screen_height, database: DatabaseIface.DatabaseIface, num_z_levels=3):
        self.current_score = 0
        self.ranger = Ranger.Ranger(0.5*screen_width, 0.9*screen_height, 0, num_z_levels)
        self.scores = database.get_highscores()  # TODO -- pull down scores from DatabaseIface
        self.min_speed = 5
        self.max_speed = 20
        self.speed = self.min_speed
        self.acceleration = 1.05
