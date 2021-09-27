"""Creating an assistant Veena to help with the program execution and parsing"""

import time
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()


def save():
    r = sr.Recognizer()
    r.pause_threshold = 2
    with sr.Microphone() as source:
        print('Yes')

        audio = r.listen(source)
    with open('test.wav', 'wb') as wav:
        wav.write(audio.get_wav_data())


save()
