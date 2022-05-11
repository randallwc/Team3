import json
import sys

import requests


class DatabaseIface:
    def __init__(self):
        self.local_uri = 'http://localhost:8000'
        self.jc_uri = 'https://skydangerranger.herokuapp.com'
        self.will_uri = 'https://skydr.herokuapp.com'
        self.used_uri = self.will_uri

    def get_highscores(self, n_scores, mode, score_kind):
        # n_scores, number of scores to return
        # mode, 'multiplayer' or 'singleplayer'
        # score_kind, 'lifetime' or 'singlegame'

        # let me answer that for you, no it has to be nScores and not n_scores
        # bad practice to send underscores through http requests,
        # different browsers handle differently, even though we don't use
        # browser
        obj = {
            'nScores': n_scores,
            'mode': mode
        }
        res = None
        assert score_kind in ('lifetime', 'singlegame')
        assert mode in ('multiplayer', 'singleplayer')
        if score_kind == 'lifetime':
            url = self.used_uri + '/api/v1/fetch/lifetime/highscores'
            res = requests.get(url, obj)
        elif score_kind == 'singlegame':
            url = self.used_uri + '/api/v1/fetch/singlegame/highscores'
            res = requests.get(url, obj)

        try:
            return json.loads(res.text)['scores']
        except json.JSONDecodeError:
            print('[ERROR] database not set up')
            if requests.get(
                    f'{self.used_uri}/api/v1/createhighscoresobject').ok:
                print('[DEBUG] database successfully setup relaunch')
            else:
                print('[ERROR] big dog database issue idk what\' up')
            sys.exit(1)

    def add_highscore(self, new_score, username, mode):
        assert mode in ('multiplayer', 'singleplayer')
        obj = {
            'username': username,
            'mode': mode,
            'score': new_score
        }
        url = self.used_uri + '/api/v1/insertscore'
        requests.post(url, obj)
