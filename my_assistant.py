import datetime
import os
import sys
import threading
import time
import pyjokes

import speech_recognition as sr
from neuralintents import GenericAssistant
from playsound import playsound
import pyttsx3 as tts
from text_typing import typingPrint


class Assistant(GenericAssistant):

    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        super().__init__(intents, intent_methods, model_name)
        self.name = 'Mac'

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 20000

        self.engine = tts.init()
        self.default_speak_rate = 160
        self.default_voice = 7
        self.engine.setProperty('rate', self.default_speak_rate)
        self.speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.speech_voices[self.default_voice].id)

        self.commands = []

    #  +++++++++++++++++++ Speech methods  +++++++++++++++++++++++ #

    def speak(self, text):
        t1 = threading.Thread(target=self.engine.say, args=(text,))
        t1.start()
        t1.join()
        self.engine.runAndWait()

    def set_rate(self, wpm=160):  # setting default speech rate for assistant
        self.engine.setProperty('rate', wpm)

    def set_voice(self, index=7):  # setting default voice for assistant
        speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', speech_voices[index].id)

    def set_volume(self, level=0.7):
        self.speak('What shall I set it to?')
        if threading.current_thread() == threading.main_thread():
            print(True)
        print(self.commands)
        text = self.commands[0]
        sentence_words = self._clean_up_sentence(text)
        print(sentence_words)
        if "%" in sentence_words:
            value = int(sentence_words[0])
            level = float(value) / 100
            print(level)
        self.engine.setProperty('volume', level)
        print(self.engine.getProperty('volume'))
        self.speak("It's done!")

    #  +++++++++++++++++++ Core methods  +++++++++++++++++++++++ #

    def set_intent_methods(self, intent_methods):
        self.intent_methods = intent_methods

    def calibrate(self):
        CALIBRATED = False
        while not CALIBRATED:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.speak(f"Hi, my name is {self.name}, your personal assistant.")
                print(
                    "To calibrate your voice, please speak the following after the beep: 'A quick brown fox jumped "
                    "over the lazy dog'")
                time.sleep(1.5)
                playsound('beep_short.wav')
                audio = self.recognizer.listen(source)
            text = ""
            print("calibrating...")
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    CALIBRATED = True
                    print('calibrated')
                    self.clear_screen()
                    break
            except sr.UnknownValueError:
                self.speak("I am sorry, could you repeat that for me please?")
            except sr.RequestError as e:
                print("Could not request results from Speech Recognition service; {0}".format(e))

    def callback(self, recognizer, audio):  # this is called from the background thread
        text = ""
        try:  # recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(
                audio)  # to use another API key, use `recogniser.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))
        if text != "":
            self.commands.append(text.lower())

    def listen(self):
        done = False
        stop_it = False

        while not done:

            message = self.recognizer.listen_in_background(self.microphone, self.callback)
            playsound("beep_short.wav")

            while True:
                try:
                    for _ in self.commands:
                        response = self.request(_)
                        self.commands.remove(_)
                        if response is None:
                            pass
                        elif response == 'quit':
                            stop_it = True
                            print("stop")
                            break
                        elif response == '':
                            pass
                        else:
                            self.speak(response)

                    if stop_it:
                        message(wait_for_stop=False)
                        break
                    time.sleep(0.1)
                except TypeError:
                    pass
                except IndexError:
                    pass
            break

    def set_name(self):
        self.speak('What shall I set it to?')
        name = self.commands[0]
        self.name = name

    def quit(self):
        self.speak('Goodbye!')
        sys.exit(0)

    #  +++++++++++++++++++ Standard methods  +++++++++++++++++++++++ #

    def clear_screen(self):

        os.system("clear")

    def speak_time(self):
        """
         This method will take time and slice it "2020-06-05 17:50:14.582630" from 11 to 12 for hour
         and 14-15 for min and then speak function will be called and then it will speak the current
         time
         """
        time = str(datetime.datetime.now())
        # the time will be displayed like this "2020-06-05 17:50:14.582630"
        # and then after slicing we can get time
        hour = time[11:13]
        min = time[14:16]
        self.speak("The time is" + hour + "Hours and" + min + "Minutes")

    def tell_joke(self):
        self.speak(pyjokes.get_joke())


# main assistant object
mac = Assistant('intents.json')
