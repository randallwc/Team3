import os


def join_base(s: str):
    return os.path.join(os.path.join(os.path.dirname(__file__), 'static'), s)


anton_death_sound_path = join_base('anton.mp3')
anton_path = join_base('ant-pix.png')
armando_path = join_base('arm-pix.png')
background_music_path = join_base('soundtrack.mp3')
cloud_path = join_base('cloud1_transparent_30.png')
cow_path = join_base('cow-pix.png')
david2_death_sound_path = join_base('david.mp3')
david2_path = join_base('david2-pix.png')
david_path = join_base('david-pix.png')
friendly_fire_sound_path = join_base('friendly.mp3')
gameover_path = join_base('gameover.png')
jc_death_sound_path = join_base('jc.mp3')
jc_path = join_base('jcr-pix.png')
laser_sound_path = join_base('laser.mp3')
logo_path = join_base('sky_danger_ranger.png')
opponent_path = join_base('opp_ranger.png')
point_gain_sound_path = join_base('point.wav')
point_loss_sound_path = join_base('hurt.wav')
ranger_path = join_base('ranger.png')
ricky_death_sound_path = join_base('ricky_oof.mp3')
ricky_path = join_base('ricky-pix.png')
sky_path = join_base('background2.jpeg')
wrong_answer_sound_path = join_base('wrong_answer.mp3')
