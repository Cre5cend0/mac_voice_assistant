from start import initialize
from my_assistant import mac

import logging

from my_assistant import mac
from responses import mappings
import nltk

logging.basicConfig(filename="debug.log", format='%(levelname)s:%(asctime)s:%(name)s: %(message)s', level=logging.INFO)

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

if __name__ == '__main__':
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    mac_voice_assistant.train_model()
    mac_voice_assistant.save_model()
    mac.load_model()
    mac.begin_assisting()
