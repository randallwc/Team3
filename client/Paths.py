import os


def join_base(s: str):
    return os.path.join('static', s)


anton_death_sound_path = join_base('anton.mp3')
anton_path = join_base('ant.png')
armando_path = join_base('arm.png')
cloud_path = join_base('cloud1_transparent_30.png')
cow_path = join_base('cow.png')
david2_death_sound_path = join_base('david.mp3')
david2_path = join_base('david2.png')
david_path = join_base('david.png')
friendly_fire_sound_path = join_base('friendly.mp3')
jc_death_sound_path = join_base('jc.mp3')
jc_path = join_base('jcr.png')
laser_sound_path = join_base('laser.mp3')
opponent_path = None
point_gain_sound_path = join_base('point.wav')
point_loss_sound_path = join_base('hurt.wav')
ranger_path = join_base('rangership_50.png')
ricky_death_sound_path = join_base('ricky_oof.mp3')
ricky_path = join_base('ricky.png')
sky_path = join_base('background2.jpeg')
wrong_answer_sound_path = join_base('wrong_answer.mp3')
