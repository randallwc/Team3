import pyttsx3

speech_engine = pyttsx3.init()
# finished-utterance: name=<str>, completed=<bool>


def on_start(name):
    print('[callback] starting', name)


def on_word(name, location, length):
    print('[callback] word', name, location, length)


def on_end(name, completed):
    print('[callback] finishing', name, completed)


speech_engine.connect('started-utterance', on_start)
speech_engine.connect('started-word', on_word)
speech_engine.connect('finished-utterance', on_end)
speech_engine.connect('error', lambda: print('error'))

speech_engine.say('what is up my dudes')
speech_engine.startLoop(False)
print('start loop')
while True:
    speech_engine.iterate()
    # if not speech_engine.isBusy():
    #     speech_engine.endLoop()
    #     break

print('done')
