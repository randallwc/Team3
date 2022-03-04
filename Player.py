import Ranger
import DatabaseIface


class Player:
    def __init__(self, screen_width, screen_height, database: DatabaseIface.DatabaseIface, num_z_levels=3):
        self.current_score = 0
        self.start_x = 0.5*screen_width
        self.start_y = 0.9*screen_height
        self.start_z = 0
        self.ranger = Ranger.Ranger(self.start_x, self.start_y, self.start_z, num_z_levels)
        self.scores = database.get_highscores()  # TODO -- pull down scores from DatabaseIface
        self.min_speed = 5
        self.max_speed = 20
        self.speed = self.min_speed
        self.acceleration = 1.1
