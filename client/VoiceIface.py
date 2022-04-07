import speech_recognition as sr


# TODO -- create this class
class VoiceIface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.timeout = 5
        self.recognizer.operation_timeout = self.timeout
        self.recognizer.dynamic_energy_threshold = True

    def listen(self):
        with sr.Microphone() as source:
            print('calibrating... ', end='', flush=True)
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
            print('listening... ', end='', flush=True)
            audio = self.recognizer.listen(source, timeout=self.timeout)
            print('processing... ')
        out = ''
        try:
            out = str(self.recognizer.recognize_google(audio))
            print(out)
        except sr.UnknownValueError:
            print('saying not recognized')
        except sr.RequestError as e:
            print(f'network error: {e}')
        return out

    def get_last_word(self):
        phrase = self.listen()
        word = ''
        if phrase:
            word = phrase.split(' ')[-1]
        if word:
            return word
        else:
            return None

    def find_word(self, word: str):
        phrase = self.listen().lower()
        if phrase:
            return word.lower() in phrase.split(' ')
        else:
            return False
