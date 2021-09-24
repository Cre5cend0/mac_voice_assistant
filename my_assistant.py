import sys

import speech_recognition as sr
import pyttsx3 as tts
from neuralintents import GenericAssistant
import threading


class Assistant(GenericAssistant):

    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        super().__init__(intents, intent_methods, model_name)
        self.name = 'Mac'
        self.engine = tts.init()
        self.recogniser = sr.Recognizer()
        self.recogniser.energy_threshold = 20000
        self.set_rate()
        self.set_voice()
        self.set_volume()

    def set_intent_methods(self, intent_methods):
        self.intent_methods = intent_methods

    def set_name(self):
        self.speak('What shall I set it to?')
        name = self.listen()
        self.name = name

    def set_rate(self, wpm=200):
        self.engine.setProperty('rate', wpm)

    def set_voice(self, index=7):
        speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', speech_voices[index].id)

    def set_volume(self, level=0.7):
        self.speak('What shall I set it to?')
        text = self.listen()
        sentence_words = self._clean_up_sentence(text)
        print(sentence_words)
        if "%" in sentence_words:
            value = int(sentence_words[0])
            level = float(value) / 100
            print(level)
        self.engine.setProperty('volume', level)
        print(self.engine.getProperty('volume'))
        self.speak("It's done!")

    def save_recording(self):
        with sr.Microphone() as source:
            self.recogniser.adjust_for_ambient_noise(source, duration=0.5)
            print("listening")
            audio = self.recogniser.listen(source)
            print("processing...")
            self.engine.save_to_file(audio, 'test.mp3')

    def quit(self):
        self.speak('Goodbye!')
        sys.exit(0)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("listening")
            audio = self.recogniser.listen(source)
            print("processing...")
        text = ""
        try:  # recognize speech using Google Speech Recognition
            # to use another API key, use `r1.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r1.recognize_google(audio)`
            text = self.recogniser.recognize_google(audio)
        except sr.UnknownValueError:
            self.speak("I am sorry, could you repeat that for me please?")
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))
        return text.lower()

    def calibrate(self):
        self.speak(f"Hi, my name is {self.name}, your personal assistant. "
                   f"Before we start, I need to calibrate your voice levels. Say at least a few words please.")
        done = False
        while not done:
            with sr.Microphone() as source:
                self.recogniser.adjust_for_ambient_noise(source, duration=2)
                print('listening')
                audio = self.recogniser.listen(source)
            text = ""
            print("calibrating...")
            try:
                text = self.recogniser.recognize_google(audio)
                if text:
                    done = True
                    print('calibrated')
                    break
            except sr.UnknownValueError:
                self.speak("I am sorry, could you repeat that for me please?")
            except sr.RequestError as e:
                print("Could not request results from Speech Recognition service; {0}".format(e))


# main assistant object
mac = Assistant('intents.json')
mac.train_model()
mac.save_model()





# t1 = threading.Thread(target=mac.speak)
# t2 = threading.Thread(target=mac.listen)
#
# t1.start()
# t2.start()
