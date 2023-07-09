import pyttsx3


def voiceChange():
    eng = pyttsx3.init()  # initialize an instance
    voice = eng.getProperty('voices')  # get the available voices
    # eng.setProperty('voice', voice[0].id) #set the voice to index 0 for male voice
    eng.setProperty('voice', voice[5].id)  # changing voice to index 1 for female voice
    eng.say(
        "This is a demonstration of how to convert index of voice using pyttsx3 library in python.")  # say method for passing text to be spoken
    eng.runAndWait()  # run and process the voice command


engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    engine.setProperty('voice', voice.id)
    print(voice.id)
    engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()
