import speech_recognition as sr


class VoiceIface():
    def __init__(self):
        # debug
        mics = sr.Microphone.list_microphone_names()
        print(mics)

        # vars
        self.timeout = 5
        self.recognizer = sr.Recognizer()
        # mic_index = 1
        # mic_index = int(
        #     input(f'choose right mic by index [0,{len(mics)-1}]: '))
        # self.mic = sr.Microphone(mic_index)
        self.mic = sr.Microphone()
        self.stop_listening = None
        self.fast_flag = False
        self.fast_word = 'fast'
        self.clear_flag = False
        self.clear_word = 'clear'
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        self.recognizer.energy_threshold = 100
        self.recognizer.dynamic_energy_threshold = True
        self.start_voice()

    def reset_words(self):
        self.fast_flag = False
        self.clear_flag = False

    def _voice_callback(self, recognizer, audio):
        try:
            said = str(recognizer.recognize_google(audio)).lower().split()
            print(said)
            if self.fast_word in said:
                self.fast_flag = True
            if self.clear_word in said:
                self.clear_flag = True
        except sr.UnknownValueError:
            print('[ERROR] unknown')
            pass
        except sr.RequestError as e:
            print(f'[ERROR]; {e}')
            pass

    def start_voice(self):
        self.stop_listening = self.recognizer.listen_in_background(
            self.mic, self._voice_callback, phrase_time_limit=self.timeout)

    def stop_voice(self):
        if self.stop_listening is not None:
            self.stop_listening(wait_for_stop=False)
        else:
            print('not started')
