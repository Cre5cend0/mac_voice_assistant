import pyttsx3 as tts
import threading

# initialising engine object for text to speech recognition
engine = tts.init()


def set_rate(wpm=160):  # setting default speech rate for assistant
    engine.setProperty('rate', wpm)


def set_voice(index=7):  # setting default voice for assistant
    speech_voices = engine.getProperty('voices')
    engine.setProperty('voice', speech_voices[index].id)


def speak(text):
    t1 = threading.Thread(target=engine.say, args=(text,))
    t1.start()
    t1.join()
    engine.runAndWait()

# def set_volume(self, level=0.7):
#     self.speak('What shall I set it to?')
#     text = self.listen()
#     sentence_words = self._clean_up_sentence(text)
#     print(sentence_words)
#     if "%" in sentence_words:
#         value = int(sentence_words[0])
#         level = float(value) / 100
#         print(level)
#     self.engine.setProperty('volume', level)
#     print(self.engine.getProperty('volume'))
#     self.speak("It's done!")

# def save_recording(self):
#     with sr.Microphone() as source:
#         self.recogniser.adjust_for_ambient_noise(source, duration=0.5)
#         print("listening")
#         audio = self.recogniser.listen(source)
#         print("processing...")
#         self.engine.save_to_file(audio, 'test.mp3')


# uncomment the below loop to listen to all the available voices
# for i in range(len(speech_voices)):
#     print(speech_voices[i])
#     engine.setProperty('voice', speech_voices[i].id)
#     engine.say("The quick brown fox jumped over the lazy dog.")
#     engine.runAndWait()

# 0 en_us,
# 7 en_bri,
# 10 en_scotland,
# 17 en_aus,
# 20 hi_India,
# 28 en_ireland,
# 32 en_IN,
# 33 en_US,
# 37 en_ZA,
# 39 en_IN,
# 40 en_US
