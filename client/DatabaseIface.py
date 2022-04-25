import requests


# TODO -- create this class
class DatabaseIface:
    def __init__(self):
        self.is_local = True
        self.local_uri = 'http://localhost:8000'
        self.prod_uri = 'https://skydangerranger.herokuapp.com'
        self.used_uri = ''
        if self.is_local:
            self.used_uri = self.local_uri
        else:
            self.used_uri = self.prod_uri

    def get_highscores(self, n_scores, mode, score_kind):
        # n_scores, number of scores to return
        #mode, 'multiplayer' or 'singleplayer'
        #score_kind, 'lifetime' or 'singlegame'

        # let me answer that for you, no it has to be nScores and not n_scores
        # bad practice to send underscores through http requests,
        # different browsers handle differently, even though we don't use
        # browser
        obj = {
            'nScores': n_scores,
            'mode': mode
        }
        res = None
        if score_kind == 'lifetime':
            url = self.used_uri + '/api/v1/fetch/lifetime/highscores'
            res = requests.get(url, obj)
        elif score_kind == 'singlegame':
            url = self.used_uri + '/api/v1/fetch/singlegame/highscores'
            res = requests.get(url, obj)
        return res

    def add_highscore(self, new_score, username, mode):
        obj = {
            'username': username,
            'mode': mode,
            'score': new_score
        }
        url = self.used_uri + '/api/v1/insertscore'
        res = requests.post(url, obj)
