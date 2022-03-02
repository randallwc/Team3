import Exceptions


class VoiceIface:
    def __init__(self):
        pass

    def listen_for_word(self, word: str, timeout: int):
        return Exceptions.NotImplementedException