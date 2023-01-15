import datetime
import os
import sys
import pyjokes
import playsound
import pyttsx3 as tts
import speech_recognition as sr

from time import sleep
from queue import Empty
from .IA.IA import GenericAssistant
from playsound import playsound


class Assistant(GenericAssistant):
    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        super().__init__(intents, intent_methods, model_name)

        # Initialize Recognizer and Microphone instances
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 700
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5
        self.recognizer.pause_threshold = 0.5

        # Initialize speech engine instance
        self.engine = tts.init()
        self.default_speak_rate = 160
        self.default_voice = 2
        self.engine.setProperty('rate', self.default_speak_rate)
        self.speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.speech_voices[self.default_voice].id)

        # Initialize Refs
        self.CALIBRATED = False
        self.SPEAKING = False
        self.LISTENING = False
        self.STOP_LISTENING = False
        self.audio_file_path = 'mac_voice_assistant/audio_samples/beep.wav'

    #  +++++++++++++++++++ Core methods  +++++++++++++++++++++++ #
    def set_intent_methods(self, intent_methods):
        self.intent_methods = intent_methods

    def get_audio_files_path(self):
        default_audio_path = self.audio_file_path
        if os.path.exists(default_audio_path):
            return default_audio_path
        else:
            for path in sys.path:
                if 'site-packages' in path:
                    return path + '/mac_voice_assistant/audio_samples/beep.wav'

    def set_audio_file_path(self, path):
        self.audio_file_path = path

    def calibrate(self):
        while not self.CALIBRATED:
            with self.microphone as source:
                print("We need to calibrate your voice at least once before we start the program.")
                sleep(2)
                print(
                    "To calibrate your voice, please speak the following after the beep: 'A quick brown fox jumped "
                    "over the lazy dog'")
                sleep(2)
                playsound(self.audio_file_path)
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
                self.log.info("UnknownValueError")
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Speech Recognition service: {e}")
                self.log.error("RequestError", exc_info=True)

    def run(self):
        playsound(self.audio_file_path)
        while True:
            text = None
            task = None
            try:
                try:
                    text = self.responses.get_nowait()
                except Empty:
                    pass

                try:
                    task = self.tasks.get_nowait()
                except Empty:
                    pass

                if text:
                    self.speak(text)
                    self.responses.task_done()
                if task:
                    self.execute_task(task)
                    self.tasks.task_done()

                self.listen()

            except KeyboardInterrupt:
                break

    def listen(self):
        with self.microphone as source:
            self.log.debug('listen thread started')
            audio = self.recognizer.listen(source)  # listen and put the resulting audio on the audio processing queue
            self.audio_queue.put(audio)
            result = self.thread_pool.apply_async(self.recognize)
            result.wait(timeout=5)
            self.log.debug('listen thread ended')

    def listen_for_audio(self):
        with self.microphone as source:
            audio = self.recognizer.listen(source)
            return audio

    def recognize(self):
        # this runs in a background thread
        self.log.debug('recognizer thread called')
        audio = self.audio_queue.get(block=True, timeout=10)  # retrieve next job from the main thread
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # to use another API key, use `recogniser.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # segment = audio.get_segment(start_ms=0, end_ms=4000)
            text = self.recognizer.recognize_google(audio)
            if len(text) > 0:
                self.process(text.lower())
        except sr.UnknownValueError:
            self.log.debug("Unrecognized command")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")
            self.log.error("RequestError", exc_info=True)
        finally:
            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue
            self.log.debug('recognizer thread ended')

    def transcribe(self, audio):
        text = None
        try:
            text = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.log.debug("Audio Unrecognized")
            print(f"{sr.UnknownValueError}:Could not recognize audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")
            self.log.error("RequestError", exc_info=True)
        finally:
            return text

    def process(self, command=None):
        self.log.debug('process thread called')
        if command is None:
            command = self.commands.get(block=True, timeout=10)
            self.log.debug(f'Executing command:{command}')
            response = self.request(command)
            self.log.debug(f'Getting response:{response}')
            method = response[0]
            text = response[1]
            if method and (text == '' or text is None):
                self.tasks.put(method)
            elif method:
                self.tasks.put(method)
                self.responses.put(text)
            elif not method:
                self.responses.put(text)
            self.commands.task_done()
        else:
            self.log.debug(f'Executing command:{command}')
            response = self.request(command)
            self.log.debug(f'Getting response:{response}')
            method = response[0]
            text = response[1]
            if method and (text == '' or text is None):
                self.tasks.put(method)
            elif method:
                self.tasks.put(method)
                self.responses.put(text)
            elif not method:
                self.responses.put(text)
        self.log.debug('process thread ended')

    def speak(self, text=None):
        self.SPEAKING = True
        self.log.debug('speak thread called')

        def onEnd(name, completed):
            self.SPEAKING = False
            self.log.debug('finished speaking')

        if text is None:
            text = self.responses.get(block=True, timeout=10)
            self.engine.connect('finished-utterance', onEnd)
            self.engine.say(text)
            self.engine.runAndWait()
            self.responses.task_done()
        else:
            self.engine.connect('finished-utterance', onEnd)
            self.engine.say(text)
            self.engine.runAndWait()
        self.log.debug('speak thread ended')

    def execute_task(self, task=None):
        self.log.debug('worker thread called')
        if task is None:
            task = self.tasks.get(block=True, timeout=None)
            result = eval("self." + task + "()")
            self.tasks.task_done()
        else:
            result = eval("self." + task + "()")
        self.log.debug('worker thread ended')
        return result

    def assist(self):
        path = self.get_audio_files_path()
        self.set_audio_file_path(path)
        # if not self.CALIBRATED:
        #     self.calibrate()
        self.run()

    def set_name(self):
        self.speak("What shall I set my name as?")
        audio = self.listen_for_audio()
        name = self.transcribe(audio)
        self.model_name = name
        self.speak(f'my name is {self.model_name}')

    def cancel_all_commands(self):
        pass

    def quit_program(self):
        self.thread_pool.terminate()
        sys.exit(0)

    #  +++++++++++++++++++ Speech methods  +++++++++++++++++++++++ #
    def set_rate(self, wpm=160):  # setting default speech rate for assistant
        self.engine.setProperty('rate', wpm)
        print('Setting rate done')

    def set_voice(self, index=2):  # setting default voice for assistant
        speech_voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', speech_voices[index].id)

    def set_volume(self, level=0.7):
        self.speak('What shall I set the volume to?')
        audio = self.listen_for_audio()
        text = self.transcribe(audio)
        sentence_words = self._clean_up_sentence(text)
        print(sentence_words)
        if "%" in sentence_words:
            value = int(sentence_words[0])
            level = float(value) / 100
            print(level)
        self.engine.setProperty('volume', level)
        print(self.engine.getProperty('volume'))
        self.speak("It's done!")

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
        self.speak(f"The time is {hour} Hours and {mins} Minutes")

    def tell_joke(self):
        self.speak(pyjokes.get_joke())

    def recalibrate(self):
        self.CALIBRATED = False
        self.calibrate()
