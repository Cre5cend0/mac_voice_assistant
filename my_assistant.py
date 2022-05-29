import datetime
import logging
import sys
import threading
import time
import pyjokes

from queue import Queue, LifoQueue
import speech_recognition as sr
from neuralintents import GenericAssistant
from playsound import playsound
import pyttsx3 as tts

from text_typing import typingPrint

global STOP_LISTENING
global SPEAK_THREAD
global SPEAK_EVENT
global WORKER_THREAD


class Assistant(GenericAssistant):

    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        super().__init__(intents, intent_methods, model_name)
        self.name = 'Mac'
        self.commands = Queue(maxsize=20)
        self.responses = Queue(maxsize=20)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5
        self.recognizer.pause_threshold = 0.5

        self.engine = tts.init()
        self.default_speak_rate = 160
        self.default_voice = 7
        self.engine.setProperty('rate', self.default_speak_rate)
        self.speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.speech_voices[self.default_voice].id)

    #  +++++++++++++++++++ Core methods  +++++++++++++++++++++++ #
    def set_intent_methods(self, intent_methods):
        self.intent_methods = intent_methods

    def calibrate(self):
        CALIBRATED = False
        while not CALIBRATED:
            with self.microphone as source:
                print("We need to calibrate your voice at least once before we start the program.")
                time.sleep(2)
                print("To calibrate your voice, please speak the following after the beep: 'A quick brown fox jumped "
                      "over the lazy dog'")
                time.sleep(2)
                playsound('audio_sample_4.wav')
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source)

            print('Calibrating voice')
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    CALIBRATED = True
                    print('Voice calibrated')
                    break
            except sr.UnknownValueError:
                print("Unable to comprehend. Try again.")
                continue
            except sr.RequestError as e:
                print("Could not request results from Speech Recognition service; {0}".format(e))

    def callback(self, recognizer, audio):  # this is called from the background thread
        try:  # recognize speech using Google Speech Recognition
            logging.info('Requesting callback')
            print('Requesting callback')
            text = recognizer.recognize_google(
                audio)  # to use another API key, use `recogniser.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            text = text.lower()
            print(text)
            if len(text) > 0:
                self.commands.put(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))

    def listen(self):
        global STOP_LISTENING
        while True:
            logging.info('Listening')
            try:
                STOP_LISTENING = self.recognizer.listen_in_background(self.microphone, self.callback)
            except AssertionError:
                pass
            playsound("audio_sample_4.wav")
            command = self.commands.get(block=True, timeout=None)
            logging.info(f'Executing command:{command}')
            response = self.request(command)
            logging.info('Getting response')
            if response is None or response == '':
                pass
            elif response == 'quit':
                self.quit()
            else:
                self.responses.put(response)
                self.responses.join()

    def speak(self):
        global STOP_LISTENING
        while True:
            text = self.responses.get(block=True, timeout=None)
            STOP_LISTENING(wait_for_stop=True)
            logging.info('Speaking')
            self.engine.say(text)
            if self.engine._inLoop:
                self.engine.endLoop()
            self.engine.runAndWait()
            time.sleep(3)
            self.responses.task_done()

    def execute_task(self):
        while True:
            task = self.tasks.get(block=True, timeout=None)
            task()
            self.tasks.task_done()

    def begin_assisting(self):
        self.calibrate()
        global STOP_LISTENING
        global SPEAK_THREAD
        global WORKER_THREAD
        SPEAK_THREAD = threading.Thread(target=self.speak, daemon=True)
        WORKER_THREAD = threading.Thread(target=self.execute_task, daemon=True)
        SPEAK_THREAD.setName('Speaker')
        WORKER_THREAD.setName('Worker')
        SPEAK_THREAD.start()
        WORKER_THREAD.start()
        self.listen()

    def set_name(self):
        self.responses.put('What shall I set it to?')
        self.responses.join()
        name = self.commands.get(block=True, timeout=25)
        self.name = name
        self.responses.put(f'my name is {self.name}')
        self.responses.join()

    def quit(self):
        self.responses.put('Goodbye!')
        self.responses.join()
        print(threading.enumerate())
        sys.exit(0)

    def cancel_all_commands(self):
        pass

    #  +++++++++++++++++++ Speech methods  +++++++++++++++++++++++ #
    def set_rate(self, wpm=160):  # setting default speech rate for assistant
        self.engine.setProperty('rate', wpm)

    def set_voice(self, index=7):  # setting default voice for assistant
        speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', speech_voices[index].id)

    def set_volume(self, level=0.7):
        self.responses.put('What shall I set it to?')
        self.responses.join()
        text = self.commands.get(block=True, timeout=5)
        sentence_words = self._clean_up_sentence(text)
        print(sentence_words)
        if "%" in sentence_words:
            value = int(sentence_words[0])
            level = float(value) / 100
            print(level)
        self.engine.setProperty('volume', level)
        print(self.engine.getProperty('volume'))
        self.responses.put("It's done!")
        self.responses.join()

    #  +++++++++++++++++++ Standard methods  +++++++++++++++++++++++ #

    # def clear_screen(self):
    #     clear = lambda: os.system('cls')
    #     os.system("clear")

    def speak_time(self):
        """
        This method will take time and slice it "2020-06-05 17:50:14.582630" from 11 to 12 for hour
        and 14-15 for min and then speak function will be called and then it will speak the current
        time
        """
        time_now = str(datetime.datetime.now())
        # the time will be displayed like this "2020-06-05 17:50:14.582630"
        # and then after slicing we can get time
        hour = time_now[11:13]
        mins = time_now[14:16]
        self.responses.put(f"The time is {hour} Hours and {mins} Minutes")
        self.responses.join()
        return

    def tell_joke(self):
        self.responses.put(pyjokes.get_joke())
        self.responses.join()
        return


# main assistant object
mac = Assistant('intents.json')
