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
        self.recognizer.energy_threshold = 100
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5
        self.recognizer.pause_threshold = 0.5

        # Initialize speech engine instance
        self.engine = tts.init()
        rate = self.engine.getProperty('rate')
        self.default_speak_rate = rate - 40
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

        self.mappings = {
            'set_volume' : self.set_volume,
            'set_voice'  : self.set_voice,
            'set_rate'   : self.set_rate,
            'set_name'   : self.set_name,
            'calibrate'  : self.recalibrate,
            'speak_time' : self.speak_time,
            'tell_joke'  : self.tell_joke,
            'stop_assist': self.quit_program
        }

    #  +++++++++++++++++++ Core methods  +++++++++++++++++++++++ #
    def set_intent_methods(self, intent_methods):
        for key, value in intent_methods.items():
            self.intent_methods[key] = value

    def set_default_intent_methods(self):
        for key, value in self.mappings.items():
            self.intent_methods[key] = value

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
        print('Adjusting for ambient noise')
        with self.microphone as source:
            print("Please do not speak during calibration")
            sleep(2)
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print('Calibrated, you can speak after the beep.')

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

    def listen(self, timeout=5, phrase_time_limit=3):
        with self.microphone as source:
            self.log.debug('listen thread started')
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)  # listen and put the resulting audio on the audio processing queue
            except sr.WaitTimeoutError:
                self.log.info('Microphone timed out, retrying...')
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            self.audio_queue.put(audio)
            result = self.thread_pool.apply_async(self.recognize)
            result.wait(timeout=5)
            self.log.debug('listen thread ended')

    def listen_for_audio(self, timeout=5, phrase_time_limit=3):
        with self.microphone as source:
            self.log.debug("Listening for audio")
            try:
                playsound(self.audio_file_path)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                self.log.info('Microphone timed out, retrying...')
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            self.log.debug("Finished listening for audio")
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
            self.log.debug("Transcribing for text")
            text = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.log.debug("Audio Unrecognized")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")
            self.log.error("RequestError", exc_info=True)
        finally:
            self.log.debug("Finished transcribing for text")
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
            result = task()
            self.tasks.task_done()
        else:
            result = task()
        self.log.debug('worker thread ended')
        return result

    def assist(self):
        path = self.get_audio_files_path()
        self.set_audio_file_path(path)
        self.calibrate()
        self.set_default_intent_methods()
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
    def set_rate(self, wpm=160):  # setting speech rate for assistant
        self.engine.setProperty('rate', wpm)
        print('Setting rate done')

    def set_voice(self):  # setting voice for assistant
        changed = False
        selected = []
        self.speak("Let me say a phrase in every available voice, and you can pick one you like.")
        for i in range(len(self.speech_voices)):
            self.engine.setProperty('voice', self.speech_voices[i].id)
            print(self.speech_voices[i])
            self.speak("This is the best route. Keep your horse to this path, and you'll be fine.")
            self.speak('Shall I set this voice?')
            audio = self.listen_for_audio()
            text = self.transcribe(audio)
            if text:
                print(text)
                if 'yes' in text.lower() or 'okay' in text.lower():
                    self.engine.setProperty('voice', self.speech_voices[i].id)
                    changed = True
                    self.speak('Very well, hope you like my new voice.')
                    break
                elif 'maybe' in text.lower():
                    selected.append(i)
                    continue
                elif "that's enough" in text.lower():
                    break
                else:
                    continue
        if len(selected) > 0:
            self.speak("Would you like to hear the shortlisted ones?")
            audio = self.listen_for_audio()
            text = self.transcribe(audio)
            if text:
                if 'yes' in text.lower() or 'okay' in text.lower():
                    for i in selected:
                        self.speak("After you cross the creek, be careful. Large roots come up out of the ground.")
                        self.speak('Shall I set this voice?')
                        audio = self.listen_for_audio()
                        text = self.transcribe(audio)
                        if text:
                            print(text)
                            if 'yes' in text.lower() or 'okay' in text.lower():
                                self.engine.setProperty('voice', self.speech_voices[i].id)
                                changed = True
                                self.speak('Very well, hope you like my new voice.')
                                break
                            elif "that's enough" in text.lower():
                                break
                            else:
                                continue
        if not changed:
            self.engine.setProperty('voice', self.speech_voices[self.default_voice].id)  # revert to default voice

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
