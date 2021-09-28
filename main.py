import os

from setup import initialize
from my_assistant import mac

if __name__ == '__main__':
    clear = lambda: os.system('cls')

    initialize()

    clear()
    mac.listen()
