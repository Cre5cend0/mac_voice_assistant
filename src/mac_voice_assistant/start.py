import logging

from my_assistant import mac
from responses import mappings
import nltk

logging.basicConfig(filename="debug.log", format='%(levelname)s:%(asctime)s:%(name)s: %(message)s', level=logging.INFO)

# nltk.download('punkt', quiet=True)
# nltk.download('wordnet', quiet=True)


def initialize():
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    # mac_voice_assistant.train_model()
    # mac_voice_assistant.save_model()
    mac.load_model()
    # mac_voice_assistant.calibrate()
