import nltk

from my_assistant import mac

if __name__ == '__main__':

    done = False

    mac.calibrate()

    while not done:
        message = mac.listen()
        if message == "quit":
            done = True
        else:
            response = mac.request(message)
            if response is None:
                pass
            else:
                mac.speak(response)
