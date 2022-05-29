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
    # mac.train_model()
    # mac.save_model()
    mac.load_model()
    # mac.calibrate()
