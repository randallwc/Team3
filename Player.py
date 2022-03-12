import DatabaseIface
import Paths
import Ranger
import Sounds


class Player:
    def __init__(self, screen_width, screen_height,
                 database: DatabaseIface.DatabaseIface, num_z_levels):
        self.current_score = 0
        self.start_x = 0.5 * screen_width
        self.start_y = 0.9 * screen_height
        self.num_z_levels = num_z_levels
        self.start_z = self.num_z_levels // 2
        self.ranger = Ranger.Ranger(
            self.start_x,
            self.start_y,
            self.start_z,
            num_z_levels,
            screen_width,
            screen_height,
        )
        # TODO -- pull down scores from DatabaseIface
        self.scores = database.get_highscores()
        self.min_speed = 5
        self.max_speed = 20
        self.speed = self.min_speed
        self.acceleration = 1.1

    def handle_point_change(self, delta: int):
        if delta < 0:
            Sounds.play_sound(Paths.point_loss_sound_path)
        if delta > 0:
            Sounds.play_sound(Paths.point_gain_sound_path)
        self.current_score += delta
