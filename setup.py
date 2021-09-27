from my_assistant import mac
from responses import mappings
from speech import set_rate, set_voice
import nltk

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)


def initialize():
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    set_rate()
    set_voice()
    mac.train_model()
    mac.save_model()
    mac.calibrate()
