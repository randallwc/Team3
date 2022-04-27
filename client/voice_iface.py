import speech_recognition as sr


class VoiceIface():
    def __init__(self):
        # debug
        print(sr.Microphone.list_microphone_names())

        # vars
        self.timeout = 5
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(1)
        self.stop_listening = None
        self.fast_flag = False
        self.fast_word = 'fast'
        self.clear_flag = False
        self.clear_word = 'clear'
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        self.recognizer.energy_threshold = 100
        print(self.recognizer.dynamic_energy_threshold)
        self.start_voice()

    def reset_words(self):
        self.fast_flag = False
        self.clear_flag = False

    def _voice_callback(self, recognizer, audio):
        print('callback')
        try:
            said = str(recognizer.recognize_google(audio)).lower().split()
            print(said)
            if self.fast_word in said:
                self.fast_flag = True
            if self.clear_word in said:
                self.clear_flag = True
        except sr.UnknownValueError:
            print('[ERROR] unknown')
        except sr.RequestError as e:
            print(f'[ERROR]; {e}')

    def start_voice(self):
        self.stop_listening = self.recognizer.listen_in_background(
            self.mic, self._voice_callback, phrase_time_limit=self.timeout)

    def stop_voice(self):
        if self.stop_listening is not None:
            self.stop_listening(wait_for_stop=False)
        else:
            print('not started')
