import time
import speech_recognition as sr
from speech import speak

stop_it = False


def callback(recognizer, audio):  # this is called from the background thread
    global stop_it
    text = ""
    try:  # recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(
            audio)  # to use another API key, use `r1.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")` instead of `r1.recognize_google(audio)'

    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
    print(text)
    return text.lower()


# r = sr.Recognizer()
# r.energy_threshold = 2000
# just_try_and_stop_me = r.listen_in_background(sr.Microphone(), callback)
#
# while True:
#     if stop_it:
#         just_try_and_stop_me(wait_for_stop=False)
#         break
#     time.sleep(0.1)
