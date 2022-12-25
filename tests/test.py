"""Creating an assistant Veena to help with the program execution and parsing"""
import sys
import time
import speech_recognition as sr
import pyttsx3

# engine = pyttsx3.init()


# def save():
#     r = sr.Recognizer()
#     r.pause_threshold = 2
#     with sr.Microphone() as source:
#         print('Yes')
#
#         audio = r.listen(source)
#     with open('test.wav', 'wb') as wav:
#         wav.write(audio.get_wav_data())
#
#
# save()

import sys, time, random

typing_speed = 70  # wpm


def slow_type(t):
    for l in t:
        print(l, end="")
        time.sleep(0.07)

    print()


slow_type("Hi there, how are you? My name is Mac, your personal assistant.")
