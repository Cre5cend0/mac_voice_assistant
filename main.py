
from mac_voice_assistant.AI import Assistant

if __name__ == '__main__':
    mac = Assistant('mac_voice_assistant/default_intents.json', model_name='mac')
    mappings = {
        'set_volume': "set_volume",
        'set_rate'  : "set_rate",
        'set_name'  : "set_name",
        'calibrate' : "_calibrate",
        'speak_time': "speak_time",
        'tell_joke' : "tell_joke",
        'stop_assist': "quit_program"
    }
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    mac.train_model()
    mac.save_model()
    mac.load_model()
    mac.assist()
