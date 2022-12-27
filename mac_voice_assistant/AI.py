import datetime
import os
import sys
import time
import pyjokes
import playsound
import pyttsx3 as tts
import speech_recognition as sr

from queue import Queue
from .IA.IA import GenericAssistant
from playsound import playsound
from multiprocessing.pool import ThreadPool


class Assistant(GenericAssistant):
    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        super().__init__(intents, intent_methods, model_name)
        self.name = model_name

        self.audio_queue = Queue(maxsize=20)
        self.commands = Queue(maxsize=20)
        self.responses = Queue(maxsize=20)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 700
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

        self.CALIBRATED = False
        self.LISTENING = False
        self.SPEAKING = False

        self.thread_pool = ThreadPool(processes=5)

    #  +++++++++++++++++++ Core methods  +++++++++++++++++++++++ #
    def set_intent_methods(self, intent_methods):
        self.intent_methods = intent_methods

    def calibrate(self):
        while not self.CALIBRATED:
            with self.microphone as source:
                print("We need to calibrate your voice at least once before we start the program.")
                time.sleep(2)
                print("To calibrate your voice, please speak the following after the beep: 'A quick brown fox jumped "
                      "over the lazy dog'")
                time.sleep(2)
                playsound('audio_samples/beep.wav')
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source)

            print('Calibrating voice')
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    self.CALIBRATED = True
                    print(f'You said: {text}')
                    print('Voice calibrated')
                    break
            except sr.UnknownValueError:
                print("Unable to comprehend. Try again.")
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Speech Recognition service; {e}")

    def listen(self):
        playsound("audio_samples/beep.wav")
        with self.microphone as source:
            try:
                while True:
                    self.LISTENING = True
                    # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
                    audio = self.recognizer.listen(source)
                    self.audio_queue.put(audio)
                    self.thread_pool.apply(self.callback)
                    # result.wait()
            except KeyboardInterrupt:  # allow Cmd + C to shut down the program
                pass

    def callback(self):
        # this runs in a background thread
        audio = self.audio_queue.get(block=True, timeout=None)  # retrieve the next audio processing job from the main thread

        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # to use another API key, use `recogniser.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # segment = audio.get_segment(start_ms=0, end_ms=4000)
            text = self.recognizer.recognize_google(audio)
            # if self.name in text:
            # text = self.recognizer.recognize_google(audio)
            if len(text) > 0:
                text = text.lower()
                self.commands.put(text)
                result = self.thread_pool.apply_async(self.process_command)
                result.wait()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        finally:
            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue

    def process_command(self):
        command = self.commands.get(block=True, timeout=None)
        print(f'Executing command:{command}')
        response = self.request(command)
        print(f'Getting response:{response}')
        if response is None or response == '':
            self.thread_pool.apply_async(self.execute_task)
        elif response == 'quit':
            self.responses.put('Goodbye!')
            self.thread_pool.apply(self.speak)
            self.thread_pool.terminate()
            sys.exit(0)
        else:
            self.responses.put(response)
            self.thread_pool.apply(self.speak)
        self.commands.task_done()

    def speak(self):
        text = self.responses.get(block=True, timeout=None)
        self.engine.say(text)
        if self.engine._inLoop:
            self.engine.endLoop()
        self.engine.runAndWait()
        self.responses.task_done()

    def execute_task(self):
        task = self.tasks.get(block=True, timeout=None)
        task()
        self.tasks.task_done()

    def assist(self):
        self.calibrate()
        self.listen()

    def set_name(self):
        self.responses.put('What shall I set it to?')
        self.responses.join()
        self.listen_if_not_listening()
        name = self.commands.get(block=True, timeout=15)
        self.name = name
        self.responses.put(f'my name is {self.name}')
        self.responses.join()

    def cancel_all_commands(self):
        pass

    #  +++++++++++++++++++ Speech methods  +++++++++++++++++++++++ #
    def set_rate(self, wpm=160):  # setting default speech rate for assistant
        self.engine.setProperty('rate', wpm)
        print('Setting rate done')

    def set_voice(self, index=7):  # setting default voice for assistant
        speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', speech_voices[index].id)

    def set_volume(self, level=0.7):
        self.responses.put('What shall I set it to?')
        self.responses.join()
        self.listen_if_not_listening()
        text = self.commands.get(block=True, timeout=15)
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
        self.thread_pool.apply_async(self.speak)
        return

    def tell_joke(self):
        self.responses.put(pyjokes.get_joke())
        return

    def recalibrate(self):
        pass
